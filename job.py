import ipaddress
import logging
import sys
from logging import Logger

from fritzconnection.lib.fritzstatus import FritzStatus

from configuration import Configuration
from netcup import Netcup
from sentry import set_sentry_tag


class Job():
    config: Configuration
    logger: logging.Logger
    last_addresses: tuple[str, str]
    dns_targets: dict[str, set[str]]
    netcup: Netcup

    def __init__(self, config: Configuration, logger: Logger):
        self.config = config
        self.logger = logger
        self.last_addresses = 'init', 'init'
        self.dns_targets = {}
        self.netcup = Netcup(self.logger, self.config.nc_customer_number, self.config.nc_api_key, self.config.nc_api_pw)

    def check_and_update(self):
        fritzbox = FritzStatus(address=self.config.address,
                               user=self.config.user,
                               password=self.config.password,
                               use_tls=self.config.tls,
                               timeout=self.config.timeout)

        ipv4_address = fritzbox.external_ip
        ipv6_address = self.exposed_host_ipv6(fritzbox)

        self.logger.debug("Fritzbox API: Connection established, address={}".format(self.config.address))

        if not self.dns_targets:
            self.dns_targets = self.get_dns_targets()

        if fritzbox.is_connected:
            if self.last_addresses[0] != ipv4_address or self.last_addresses[1] != ipv6_address:
                self.netcup.login()

                for zone in self.dns_targets:
                    self.update_dns_records(zone, self.dns_targets[zone], ipv4_address, ipv6_address)

                self.netcup.logout()
            else:
                self.logger.debug("No IP address change detected")
        else:
            self.logger.error("Connection to {} failed".format(self.config.address))

        self.last_addresses = ipv4_address, ipv6_address

    def update_dns_records(self, target_zone, target_records, ipv4_address, ipv6_address):
        live_records = self.netcup.getRecords(target_zone)
        updates = list()

        for record in target_records:
            set_sentry_tag(self.config, record, target_zone)
            self.queue_update_for_record(live_records, ipv4_address, ipv6_address, record, updates)

        self.netcup.updateRecords(target_zone, updates)

    def exposed_host_ipv6(self, fritzbox):
        ipv6_addr_segments: int = fritzbox.ipv6_prefix.count(':')
        ipv6_network: str

        if ipv6_addr_segments == 5:
            ipv6_network = fritzbox.ipv6_prefix[:-1]
        elif ipv6_addr_segments == 4:
            ipv6_network = fritzbox.ipv6_prefix
        else:
            self.logger.error("Invalid count of segments: %s" % ipv6_addr_segments)
            sys.exit(1)

        return ipaddress.IPv6Address("%s%s" % (ipv6_network, self.config.ipv6_node_id)).exploded

    def queue_update_for_record(self, dnsrecords, ipv4_address, ipv6_address, a_record, updates):
        for entry in dnsrecords:
            if entry['hostname'] == a_record:
                if entry['type'] == 'A':
                    entry['destination'] = ipv4_address
                    updates.append(entry)

                    self.logger.info("A update: {} -> {}".format(a_record, ipv4_address))

                if entry['type'] == 'AAAA':
                    entry['destination'] = ipv6_address
                    updates.append(entry)

                    self.logger.info("AAAA update: {} -> {}".format(a_record, ipv6_address))

    def get_dns_targets(self):
        dns_targets = dict()

        for dns_target in self.config.dns_targets.split(";"):
            dns_target = dns_target.strip().split(":")
            zone = dns_target[0]
            records = dns_target[1].strip().split(",")

            for record in records:
                dns_targets.setdefault(zone, set()).add(record)

        return dns_targets
