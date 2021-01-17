#!/usr/bin/env python

import logging
import signal
import sys
import time
import math
import random

from fritzconnection.lib.fritzstatus import FritzStatus

from configuration import Configuration
from netcup import Netcup

logger = logging.getLogger(__name__)
config = Configuration()


def main(addresses: tuple):
    logging.basicConfig(level=config.loglevel,
                        format="%(asctime)s %(levelname)s %(processName)s/%(module)s[%(process)d]: %(message)s "
                               "[%(pathname)s:%(lineno)d]")

    fritzbox = FritzStatus(address=config.address,
                           user=config.user,
                           password=config.password,
                           use_tls=config.tls,
                           timeout=config.timeout)

    logger.debug("Fritzbox API: Connection established, address={}".format(config.address))

    if fritzbox.is_connected:
        if addresses[0] != fritzbox.external_ip or addresses[1] != fritzbox.external_ipv6:
            netcup = Netcup(config.nc_customer_number, config.nc_api_key, config.nc_api_pw)

            netcup.login()
            dnsrecords = netcup.getRecords(config.domain)
            updates = list()

            for a_record in config.host.split(','):
                queue_update_for_record(dnsrecords, fritzbox, a_record, updates)

            netcup.updateRecords(config.domain, updates)
            netcup.logout()
        else:
            logger.debug("No IP address change detected")
    else:
        logger.error("Connection to {} failed".format(config.address))

    return fritzbox.external_ip, fritzbox.external_ipv6


def queue_update_for_record(dnsrecords, fritzbox, a_record, updates):
    for entry in dnsrecords:
        if entry['hostname'] == a_record:
            if entry['type'] == 'A':
                entry['destination'] = fritzbox.external_ip
                updates.append(entry)

                logger.info("A update: {} -> {}".format(a_record, fritzbox.external_ip))

            if entry['type'] == 'AAAA':
                entry['destination'] = fritzbox.external_ipv6
                updates.append(entry)

                logger.info("AAAA update: {} -> {}".format(a_record, fritzbox.external_ipv6))


def shutdown(signum, stack):
    logger.info("Shutting down, signal={}".format(signum))
    sys.exit()


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

last_addresses = 'init', 'init'

while True:
    # Store last addresses
    last_addresses = main(last_addresses)

    # Sleep up to config.interval + 10% to relax hard timing
    skew = random.randint(0, max(1, math.floor(config.interval * 0.1)))
    logger.debug("Next check for updating DNS records in {} (skew = {})".format(config.interval + skew, skew))
    time.sleep(config.interval + skew)
