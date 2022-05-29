from environs import Env

from config.Configuration import Configuration, Domain, Fritzbox, Netcup, Options


class ConfigurationEnvironment:
    ipv6_node_id: str
    loglevel: str
    interval: int
    host: str
    domain: str
    nc_api_pw: str
    nc_api_key: str
    nc_customer_number: int
    timeout: int
    tls: bool
    password: str
    user: str
    address: str

    def __init__(self):
        env = Env()
        env.read_env()

        self.address = env.str('FB_NC_DYNDNS_FB_ADDRESS', 'fritz.box')
        self.user = env.str('FB_NC_DYNDNS_FB_USER')
        self.password = env.str('FB_NC_DYNDNS_FB_PASSWORD')
        self.tls = env.bool('FB_NC_DYNDNS_FB_TLS', True)
        self.timeout = env.int('FB_NC_DYNDNS_FB_TIMEOUT', 10)
        self.nc_customer_number = env.int('FB_NC_DYNDNS_NC_CUSTNO')
        self.nc_api_key = env.str('FB_NC_DYNDNS_NC_API_KEY')
        self.nc_api_pw = env.str('FB_NC_DYNDNS_NC_API_PW')
        self.domain = env.str('FB_NC_DYNDNS_DOMAIN')
        self.host = env.str('FB_NC_DYNDNS_HOST')
        self.interval = env.int('FB_NC_DYNDNS_INTERVAL', 300)
        self.loglevel = env.str('FB_NC_DYNDNS_LOGLEVEL', 'INFO')
        self.ipv6_node_id = env.str('FB_NC_DYNDNS_IPV6_NODE_ID')

    def to_config_object(self):
        options = Options()
        options.interval = self.interval
        options.loglevel = self.loglevel
        options.ipv6_node_id = self.ipv6_node_id

        fritzbox = Fritzbox()
        fritzbox.address = self.address
        fritzbox.user = self.user
        fritzbox.password = self.password
        fritzbox.tls = self.tls
        fritzbox.timeout = self.timeout

        netcup = Netcup()
        netcup.customer_number = self.nc_customer_number
        netcup.api_key = self.nc_api_key
        netcup.api_pw = self.nc_api_pw

        domain = Domain()
        domain.name = self.domain
        domain.a_records = self.host.split(',')

        return Configuration(options, fritzbox, netcup, [domain])
