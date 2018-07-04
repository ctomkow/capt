# system imports
import urllib3
import time
import sys
import random

# 3rd part imports
import requests
import json

# local imports
try:
    from .json_parser import JsonParser
    from .connector import Connector
except (ImportError, SystemError):
    from json_parser import JsonParser
    from connector import Connector


class DeviceConnector(Connector):


    def get_id_by_ip(self, address, logger):

        url = "https://{}/webacs/api/v3/data/Clients.json?ipAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return JsonParser.get_value(JsonParser, result.json(), key_list, logger)

    def get_id_by_mac(self, address, logger):

        url = "https://{}/webacs/api/v3/data/Clients.json?macAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return JsonParser.get_value(JsonParser, result.json(), key_list, logger)

    def get_json_details(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/ClientDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()
