from typing import List

import yaml


class Domain:
    name: str
    a_records: List[str]

    def __init__(self):
        self.name: str = 'invalid.example'
        self.a_records: List[str] = ['a', 'b', 'c']

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        self.name = value

    @property
    def records(self):
        return self.a_records

    @a_records.setter
    def records(self, value):
        self.a_records = value

    def add_record(self, value: str):
        self.records.append(value)


class Fritzbox:
    address: str
    user: str
    password: str
    tls: bool
    timeout: int

    def __init__(self):
        self.address: str = 'fritz.box'
        self.user: str = 'invalid'
        self.password: str = 'invalid'
        self.tls: bool = True
        self.timeout: int = 10

    @property
    def address(self):
        return self.address

    @address.setter
    def address(self, value: str):
        self.address = value

    @property
    def user(self):
        return self.user

    @user.setter
    def user(self, value: str):
        self.user = value

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, value: str):
        self.password = value

    @property
    def tls(self):
        return self.tls

    @tls.setter
    def tls(self, value: bool):
        self.tls = value

    @property
    def timeout(self):
        return self.timeout

    @timeout.setter
    def timeout(self, value: int):
        self.timeout = value


class Netcup:
    customer_number: int
    api_key: str
    api_pw: str

    def __init__(self):
        self.customer_number: int = 0
        self.api_key: str = 'invalid'
        self.api_pw: str = 'invalid'

    @property
    def customer_number(self):
        return self.customer_number

    @customer_number.setter
    def customer_number(self, value):
        self.customer_number = value

    @property
    def api_key(self):
        return self.api_key

    @api_key.setter
    def api_key(self, value):
        self.api_key = value

    @property
    def api_pw(self):
        return self.api_pw

    @api_pw.setter
    def api_pw(self, value):
        self.api_pw = value


class Options:
    ipv6_node_id: str
    loglevel: str
    interval: int

    def __init__(self):
        self.interval: int = 300
        self.loglevel: str = 'INFO'
        self.ipv6_node_id: str = '::1'

    @property
    def ipv6_node_id(self):
        return self.ipv6_node_id

    @ipv6_node_id.setter
    def ipv6_node_id(self, value: str):
        self.ipv6_node_id = value

    @property
    def loglevel(self):
        return self.loglevel

    @loglevel.setter
    def loglevel(self, value: str):
        self.loglevel = value

    @property
    def interval(self):
        return self.interval

    @interval.setter
    def interval(self, value: int):
        self.interval = value


class Configuration(yaml.YAMLObject):
    options: Options
    fritzbox: Fritzbox
    netcup: Netcup
    domains: List[Domain]

    def __init__(self, options: Options, fritzbox: Fritzbox, netcup: Netcup, domains: List[Domain]):
        self.options = options
        self.fritzbox = fritzbox
        self.netcup = netcup
        self.domains = domains

    @property
    def options(self):
        return self.options

    @options.setter
    def options(self, value: Options):
        self.options = value

    @property
    def fritzbox(self):
        return self.fritzbox

    @fritzbox.setter
    def fritzbox(self, value):
        self.fritzbox = value

    @property
    def netcup(self):
        return self.netcup

    @netcup.setter
    def netcup(self, value: Netcup):
        self.netcup = value

    @property
    def domains(self):
        return self.domains

    @domains.setter
    def domains(self, value: List[Domain]):
        self.domains = value

    def add_domain(self, domain: Domain):
        self.domains.append(domain)
