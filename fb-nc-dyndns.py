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

if config.sentry_url:
    logger.info("Enabling Sentry")
    sentry_sdk.init(config.sentry_url, traces_sample_rate=1.0)
    sentry_sdk.set_tag("domain", config.domain)
    sentry_sdk.set_tag("hostname", platform.node())
else:
    logger.info("Sentry not enabled")


def main(addresses: tuple):
    fritzbox = FritzStatus(address=config.address,
                           user=config.user,
                           password=config.password,
                           use_tls=config.tls,
                           timeout=config.timeout)

    ipv6_addr_segments: int = fritzbox.ipv6_prefix.count(':')
    ipv6_network: str

    if ipv6_addr_segments == 5:
        ipv6_network = fritzbox.ipv6_prefix[:-1]
    elif ipv6_addr_segments == 4:
        ipv6_network = fritzbox.ipv6_prefix
    else:
        logger.error("Invalid count of segments: %s" % (ipv6_addr_segments))
        sys.exit(1)

    exposed_host_ipv6: str = ipaddress.IPv6Address("%s%s" % (ipv6_network, config.ipv6_node_id)).exploded

    logger.debug("Fritzbox API: Connection established, address={}".format(config.address))

    if fritzbox.is_connected:
        if addresses[0] != fritzbox.external_ip or addresses[1] != exposed_host_ipv6:
            netcup = Netcup(config.nc_customer_number, config.nc_api_key, config.nc_api_pw)

            netcup.login()
            dnsrecords = netcup.getRecords(config.domain)
            updates = list()

            for a_record in config.host.split(','):
                queue_update_for_record(dnsrecords, fritzbox, exposed_host_ipv6, a_record, updates)

            netcup.updateRecords(config.domain, updates)
            netcup.logout()
        else:
            logger.debug("No IP address change detected")
    else:
        logger.error("Connection to {} failed".format(config.address))

    return fritzbox.external_ip, exposed_host_ipv6


def queue_update_for_record(dnsrecords, fritzbox, exposed_host_ipv6, a_record, updates):
    for entry in dnsrecords:
        if entry['hostname'] == a_record:
            if entry['type'] == 'A':
                entry['destination'] = fritzbox.external_ip
                updates.append(entry)

                logger.info("A update: {} -> {}".format(a_record, fritzbox.external_ip))

            if entry['type'] == 'AAAA':
                entry['destination'] = exposed_host_ipv6
                updates.append(entry)

                logger.info("AAAA update: {} -> {}".format(a_record, exposed_host_ipv6))


def shutdown(signum, stack):
    logger.info("Shutting down, signal={}".format(signum))
    sys.exit()


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

last_addresses = 'init', 'init'

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
