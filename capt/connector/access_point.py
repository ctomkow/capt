
# system imports

# 3rd part imports
import requests

# local imports
from json_parser import JsonParser
from connector.connector import Connector


class AccessPoint(Connector):

    # legacy api_call
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

    def get_id_by_mac(self, mac):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?ethernetMac=\"{}\"".format(self.cpi_ipv4_address, mac)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    # Can't seem to filter API call on ipAddress (I tried AccessPoints and AccessPointDetail)
    def get_id_by_ip(self, ip):

        pass

    def get_json_basic(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

    def get_json_detailed(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPointDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()