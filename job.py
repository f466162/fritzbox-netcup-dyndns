import ipaddress
from ipaddress import IPv4Address, IPv6Address

from sentry import Sentry

DNS_RECORD_TYPE_AAAA = 'AAAA'
DNS_RECORD_TYPE_A = 'A'
LOCALHOST_V6: IPv6Address = ipaddress.IPv6Address("::1")
LOCALHOST_V4: IPv4Address = ipaddress.IPv4Address("127.0.0.1")

import logging
import sys
from logging import Logger

from fritzconnection.lib.fritzstatus import FritzStatus

from configuration import Configuration
from netcup import Netcup


class Job():
    config: Configuration
    logger: logging.Logger
    last_addresses: tuple[ipaddress.IPv4Address, ipaddress.IPv6Address]
    dns_targets: dict[str, set[str]]
    netcup: Netcup
    sentry: Sentry
    ipv4_address: ipaddress.IPv4Address
    ipv6_address: ipaddress.IPv6Address

    def __init__(self, config: Configuration, logger: Logger, sentry: Sentry):
        self.config = config
        self.logger = logger
        self.last_addresses = LOCALHOST_V4, LOCALHOST_V6
        self.dns_targets = {}
        self.netcup = Netcup(self.logger, self.config.nc_customer_number, self.config.nc_api_key, self.config.nc_api_pw)
        self.ipv4_address = LOCALHOST_V4
        self.ipv6_address = LOCALHOST_V6
        self.sentry = sentry

    def check_and_update(self):
        fritzbox: FritzStatus = FritzStatus(address=self.config.address,
                                            user=self.config.user,
                                            password=self.config.password,
                                            use_tls=self.config.tls,
                                            timeout=self.config.timeout)

        self.ipv4_address = ipaddress.IPv4Address(fritzbox.external_ip)
        self.ipv6_address = self.exposed_host_ipv6(fritzbox)

        self.logger.debug("Fritzbox API: Connection established, address={}".format(self.config.address))

        if not self.dns_targets:
            self.dns_targets = self.get_dns_targets()

        if fritzbox.is_connected:
            if self.last_addresses[0] != self.ipv4_address or self.last_addresses[1] != self.ipv6_address:
                self.netcup.login()

                for zone in self.dns_targets:
                    self.update_dns_records(zone, self.dns_targets[zone])

                self.netcup.logout()
            else:
                self.logger.debug("No IP address change detected")
        else:
            self.logger.error("Connection to {} failed".format(self.config.address))

        self.last_addresses = self.ipv4_address, self.ipv6_address

    def update_dns_records(self, target_zone: str, target_records: set[str]):
        live_records = self.netcup.getRecords(target_zone)
        updates: list[str] = list()

        for record in target_records:
            self.sentry.set_sentry_tag(record, target_zone)
            self.queue_update_for_record(live_records, record, updates)

        self.netcup.updateRecords(target_zone, updates)

    def exposed_host_ipv6(self, fritzbox: FritzStatus):
        ipv6_addr_segments: int = fritzbox.ipv6_prefix.count(':')
        ipv6_network: str

        if ipv6_addr_segments == 5:
            ipv6_network = fritzbox.ipv6_prefix[:-1]
        elif ipv6_addr_segments == 4:
            ipv6_network = fritzbox.ipv6_prefix
        else:
            self.logger.error("Invalid count of segments: %s" % ipv6_addr_segments)
            sys.exit(1)

        return ipaddress.IPv6Address("%s%s" % (ipv6_network, self.config.ipv6_node_id))

    def queue_update_for_record(self, dnsrecords, record_to_change, updates):
        for entry in dnsrecords:
            if entry['hostname'] == record_to_change:
                if entry['type'] == DNS_RECORD_TYPE_A:
                    entry['destination'] = self.ipv4_address.exploded
                    updates.append(entry)

                    self.logger.info(
                        "{} update: {} -> {}".format(DNS_RECORD_TYPE_A, record_to_change, self.ipv4_address))

                if entry['type'] == DNS_RECORD_TYPE_AAAA:
                    entry['destination'] = self.ipv6_address.exploded
                    updates.append(entry)

                    self.logger.info(
                        "{} update: {} -> {}".format(DNS_RECORD_TYPE_AAAA, record_to_change, self.ipv6_address))

    def get_dns_targets(self):
        dns_targets = dict()

        for dns_target in self.config.dns_targets.split(";"):
            dns_target = dns_target.strip().split(":")
            zone = dns_target[0]
            records = dns_target[1].strip().split(",")

            for record in records:
                dns_targets.setdefault(zone, set()).add(record)

        return dns_targets
