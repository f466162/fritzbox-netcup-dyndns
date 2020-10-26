#!/usr/bin/env python

import logging
import signal
import sys
import time

from fritzconnection.lib.fritzstatus import FritzStatus

from configuration import Configuration
from netcup import Netcup

logger = logging.getLogger(__name__)
config = Configuration()

def main(addresses: tuple):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(processName)s/%(module)s[%(process)d]: %(message)s "
                               "[%(pathname)s:%(lineno)d]")

    fritzbox = FritzStatus(address=config.address,
                           user=config.user,
                           password=config.password,
                           use_tls=config.tls,
                           timeout=config.timeout)

    logger.info("Fritzbox API: Connection established, address={}".format(config.address))

    if fritzbox.is_connected:
        if addresses[0] != fritzbox.external_ip or addresses[1] != fritzbox.external_ipv6:
            netcup = Netcup(config.nc_customer_number, config.nc_api_key, config.nc_api_pw)

            netcup.login()
            dnsrecords = netcup.getRecords(config.domain)
            updates = list()

            for entry in dnsrecords:
                if config.host and entry['type'] == 'A':
                    entry['destination'] = fritzbox.external_ip
                    updates.append(entry)

                    logger.info("IPv4 update queued: {}".format(fritzbox.external_ip))

                    break

            for entry in dnsrecords:
                if config.host and entry['type'] == 'AAAA':
                    entry['destination'] = fritzbox.external_ipv6
                    updates.append(entry)

                    logger.info("IPv6 update queued: {}".format(fritzbox.external_ipv6))

                    break

            netcup.updateRecords(config.domain, updates)
            netcup.logout()
        else:
            logger.info("No IP address change detected")
    else:
        logger.error("Connection to {} failed".format(config.address))

    return fritzbox.external_ip, fritzbox.external_ipv6


def shutdown(signum, stack):
    logger.info("Shutting down, signal={}".format(signum))
    sys.exit()


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

addresses = 'init', 'init'

while True:
    addresses = main(addresses)
    time.sleep(config.interval)
