#!/usr/bin/env python
import ipaddress
import logging
import math
import platform
import random
import signal
import sys
import time
import sentry_sdk

from fritzconnection.lib.fritzstatus import FritzStatus

from configuration import Configuration
from netcup import Netcup

logger = logging.getLogger(__name__)

config = Configuration()
config.loglevel = logging.getLevelName(config.loglevel)
logging.basicConfig(level=config.loglevel,
                    format="%(asctime)s %(levelname)s %(processName)s/%(module)s[%(process)d]: %(message)s "
                           "[%(pathname)s:%(lineno)d]")


def main(addresses: tuple):
    fritzbox = FritzStatus(address=config.address,
                           user=config.user,
                           password=config.password,
                           use_tls=config.tls,
                           timeout=config.timeout)

    ipv4_address = fritzbox.external_ip
    ipv6_address = exposed_host_ipv6(fritzbox)

    logger.debug("Fritzbox API: Connection established, address={}".format(config.address))

    if fritzbox.is_connected:
        if addresses[0] != ipv4_address or addresses[1] != ipv6_address:
            netcup = Netcup(config.nc_customer_number, config.nc_api_key, config.nc_api_pw)
            netcup.login()

            for zone in dns_targets:
                update_dns_records(netcup, zone, dns_targets[zone], ipv4_address, ipv6_address)

            netcup.logout()
        else:
            logger.debug("No IP address change detected")
    else:
        logger.error("Connection to {} failed".format(config.address))

    return ipv4_address, ipv6_address


def update_dns_records(netcup, target_zone, target_records, ipv4_address, ipv6_address):
    live_records = netcup.getRecords(target_zone)
    updates = list()

    for record in target_records:
        if config.sentry_url:
            sentry_sdk.set_tag("domain", ("%s.%s" % (record, target_zone)))

        queue_update_for_record(live_records, ipv4_address, ipv6_address, record, updates)

    netcup.updateRecords(target_zone, updates)


def exposed_host_ipv6(fritzbox):
    ipv6_addr_segments: int = fritzbox.ipv6_prefix.count(':')
    ipv6_network: str
    if ipv6_addr_segments == 5:
        ipv6_network = fritzbox.ipv6_prefix[:-1]
    elif ipv6_addr_segments == 4:
        ipv6_network = fritzbox.ipv6_prefix
    else:
        logger.error("Invalid count of segments: %s" % ipv6_addr_segments)
        sys.exit(1)
    return ipaddress.IPv6Address("%s%s" % (ipv6_network, config.ipv6_node_id)).exploded


def queue_update_for_record(dnsrecords, ipv4_address, ipv6_address, a_record, updates):
    for entry in dnsrecords:
        if entry['hostname'] == a_record:
            if entry['type'] == 'A':
                entry['destination'] = ipv4_address
                updates.append(entry)

                logger.info("A update: {} -> {}".format(a_record, ipv4_address))

            if entry['type'] == 'AAAA':
                entry['destination'] = ipv6_address
                updates.append(entry)

                logger.info("AAAA update: {} -> {}".format(a_record, ipv6_address))


def get_dns_targets():
    dns_targets = dict()

    for dns_target in config.dns_targets.split(";"):
        dns_target = dns_target.strip().split(":")
        zone = dns_target[0]
        records = dns_target[1].strip().split(",")

        for record in records:
            dns_targets.setdefault(zone, set()).add(record)

    return dns_targets


def shutdown(signum, stack):
    logger.info("Shutting down, signal={}".format(signum))
    sys.exit()


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

if config.sentry_url:
    logger.info("Enabling Sentry")
    sentry_sdk.init(config.sentry_url, traces_sample_rate=1.0)
    sentry_sdk.set_tag("hostname", platform.node())
else:
    logger.info("Sentry not enabled")

last_addresses = 'init', 'init'
dns_targets = get_dns_targets()

# Control loop
while True:
    # Store last addresses
    last_addresses = main(last_addresses)

    # If an interval is set > 0, sleep and run again
    if config.interval > 0:
        # Sleep up to config.interval + 10% to relax hard timing
        skew = random.randint(0, max(1, math.floor(config.interval * 0.1)))
        logger.debug("Next check for updating DNS records in {} (skew = {})".format(config.interval + skew, skew))
        time.sleep(config.interval + skew)
    else:
        break
