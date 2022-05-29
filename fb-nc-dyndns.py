#!/usr/bin/env python
import ipaddress
import logging
import math
import random
import signal
import sys
import time

from fritzconnection.lib.fritzstatus import FritzStatus

from config.Configuration import Configuration, Domain
from config.ConfigurationEnv import ConfigurationEnvironment
from netcup import Netcup

logger = logging.getLogger(__name__)

config: Configuration = ConfigurationEnvironment().to_config_object()
config.options.loglevel = logging.getLevelName(config.options.loglevel)


def main(addresses: tuple):
    logging.basicConfig(level=config.options.loglevel,
                        format="%(asctime)s %(levelname)s %(processName)s/%(module)s[%(process)d]: %(message)s "
                               "[%(pathname)s:%(lineno)d]")

    fritzbox = FritzStatus(address=config.fritzbox.address,
                           user=config.fritzbox.user,
                           password=config.fritzbox.password,
                           use_tls=config.fritzbox.tls,
                           timeout=config.fritzbox.timeout)

    exposed_host_ipv6: str = ipaddress.IPv6Address(fritzbox.ipv6_prefix[:-1] + config.options.ipv6_node_id).exploded

    logger.debug("Fritzbox API: Connection established, address={}".format(config.fritzbox.address))

    if fritzbox.is_connected:
        if addresses[0] != fritzbox.external_ip or addresses[1] != exposed_host_ipv6:
            netcup = Netcup(config.netcup.customer_number, config.netcup.api_key, config.netcup.api_pw)

            ####
            netcup.login()
            ####

            for domain in config.domains:
                process_domain(fritzbox, exposed_host_ipv6, netcup, domain)

            ####
            netcup.logout()
            ####
        else:
            logger.debug("No IP address change detected")
    else:
        logger.error("Connection to {} failed".format(config.fritzbox.address))

    return fritzbox.external_ip, exposed_host_ipv6


def process_domain(fritzbox, exposed_host_ipv6, netcup, domain:Domain):
    updates = list()
    dnsrecords = netcup.get_records(domain.name)

    for a_record in domain.arecords:
        queue_update_for_record(dnsrecords, fritzbox, exposed_host_ipv6, a_record, updates)

    netcup.update_records(domain.name, updates)


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
    if config.options._interval > 0:
        # Sleep up to config.interval + 10% to relax hard timing
        skew = random.randint(0, max(1, math.floor(config.options._interval * 0.1)))
        logger.debug("Next check for updating DNS records in {} (skew = {})".format(config.options._interval + skew, skew))
        time.sleep(config.options._interval + skew)
    else:
        break
