import json
import logging

import requests

NETCUP_API_URL: str = 'https://ccp.netcup.net/run/webservice/servers/endpoint.php?JSON'


class Netcup:
    logger: logging.Logger
    customer_number: int
    api_key: str
    api_password: str
    http_session: requests.Session
    api_session: str

    def __init__(self, logger: logging.Logger, customer_number: int, api_key: str, api_password: str):
        self.logger = logger
        self.customer_number = customer_number
        self.api_key = api_key
        self.api_password = api_password

        self.http_session = requests.Session()

        self.http_session.headers.update({
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json; charset=utf-8"
        })

    def login(self):
        action = 'login'
        param = {'customernumber': self.customer_number,
                 'apikey': self.api_key,
                 'apipassword': self.api_password}

        response = self.send_http_request(action, param)
        self.api_session = response["responsedata"]["apisessionid"]

    def logout(self):
        action = 'logout'
        param = {'customernumber': self.customer_number,
                 'apikey': self.api_key,
                 'apisessionid': self.api_session}

        self.send_http_request(action, param)
        self.api_session = 'invalid'
        self.http_session.close()

    def getRecords(self, domain: str):
        action = 'infoDnsRecords'
        param = {'customernumber': self.customer_number,
                 'apikey': self.api_key,
                 'apisessionid': self.api_session,
                 'domainname': domain}

        response = self.send_http_request(action, param)

        return response['responsedata']['dnsrecords']

    def updateRecords(self, domain: str, records: list):
        action = 'updateDnsRecords'
        param = {'customernumber': self.customer_number,
                 'apikey': self.api_key,
                 'apisessionid': self.api_session,
                 'domainname': domain,
                 'dnsrecordset': {
                     'dnsrecords': records
                 }}

        return self.send_http_request(action, param)

    def handle_response(self, action: str, response: requests.Response):
        payload = json.loads(response.text)
        message = "Netcup API: action={}, HTTP status={}, API status={}".format(action, response.reason,
                                                                                payload["status"])

        if response.ok:
            self.logger.info(message)

            if payload["status"] == "error":
                self.logger.error("API error message: {}".format(payload["longmessage"]))
                raise Exception()
        else:
            self.logger.error(message)
            response.raise_for_status()

        return payload

    def send_http_request(self, action: str, param: dict):
        payload = json.dumps({
            'action': action,
            'param': param
        })

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('Requesting action={} with payload={}'.format(action, payload))

        response = self.handle_response(action, self.http_session.post(NETCUP_API_URL, payload))

        return response
