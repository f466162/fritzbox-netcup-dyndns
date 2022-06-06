from typing import List

import yaml

from config.ConfigurationParts import Domain, Fritzbox, Netcup, Options


class Configuration(yaml.YAMLObject):
    _options: Options
    _fritzbox: Fritzbox
    _netcup: Netcup
    _domains: List[Domain]

    def __init__(self, options: Options, fritzbox: Fritzbox, netcup: Netcup, domains: List[Domain]):
        self.options = options
        self.fritzbox = fritzbox
        self.netcup = netcup
        self.domains = domains

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value: Options):
        self._options = value

    @property
    def fritzbox(self):
        return self._fritzbox

    @fritzbox.setter
    def fritzbox(self, value):
        self._fritzbox = value

    @property
    def netcup(self):
        return self._netcup

    @netcup.setter
    def netcup(self, value: Netcup):
        self._netcup = value

    @property
    def domains(self):
        return self._domains

    @domains.setter
    def domains(self, value: List[Domain]):
        self._domains = value

    def add_domain(self, domain: Domain):
        self.domains.append(domain)
