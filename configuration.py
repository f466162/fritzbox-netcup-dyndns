from environs import Env


class Configuration:
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
