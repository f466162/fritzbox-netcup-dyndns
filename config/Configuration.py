from typing import List

import yaml


class Domain:
    _name: str
    _arecords: List[str]

    def __init__(self):
        self.name: str = 'invalid.example'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def arecords(self):
        return self._arecords

    @arecords.setter
    def arecords(self, value):
        self._arecords = value

    def add_record(self, value: str):
        self.arecords.append(value)


class Fritzbox:
    _address: str
    _user: str
    _password: str
    _tls: bool
    _timeout: int

    def __init__(self):
        self.address: str = 'fritz.box'
        self.user: str = 'invalid'
        self.password: str = 'invalid'
        self.tls: bool = True
        self.timeout: int = 10

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value: str):
        self._user = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = value

    @property
    def tls(self):
        return self._tls

    @tls.setter
    def tls(self, value: bool):
        self._tls = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        self._timeout = value


class Netcup:
    _customer_number: int
    _api_key: str
    _api_pw: str

    def __init__(self):
        self.customer_number: int = 0
        self.api_key: str = 'invalid'
        self.api_pw: str = 'invalid'

    @property
    def customer_number(self):
        return self._customer_number

    @customer_number.setter
    def customer_number(self, value):
        self._customer_number = value

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def api_pw(self):
        return self._api_pw

    @api_pw.setter
    def api_pw(self, value):
        self._api_pw = value


class Options:
    _ipv6_node_id: str
    _loglevel: str
    _interval: int

    def __init__(self):
        self.interval: int = 300
        self.loglevel: str = 'INFO'
        self.ipv6_node_id: str = '::1'

    @property
    def ipv6_node_id(self):
        return self._ipv6_node_id

    @ipv6_node_id.setter
    def ipv6_node_id(self, value: str):
        self._ipv6_node_id = value

    @property
    def loglevel(self):
        return self._loglevel

    @loglevel.setter
    def loglevel(self, value: str):
        self._loglevel = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value: int):
        self._interval = value


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
