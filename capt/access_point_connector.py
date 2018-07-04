# system imports

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


class AccessPointConnector(Connector):


    def get_id(self, name):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?name=\"{}\"".format(self.cpi_ipv4_address, name)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_ip(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'accessPointsDTO', 'ipAddress']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)
