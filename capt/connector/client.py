
# system imports
import json


# 3rd part imports
import requests
import re


# local imports
from connector.connector import Connector


class Client(Connector):

    def id_by_ip(self, address):

        url = "https://{}/webacs/api/v3/data/Clients.json?ipAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def id_by_mac(self, address):

        url = "https://{}/webacs/api/v3/data/Clients.json?macAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def ids_by_desc(self, desc):
        id_list = []
        # Call var_parser functions to parse the description string
        modified_desc_list = self.parse_var.desc_id_split(desc, "&ifDescr=contains(")

        url = "https://{}/webacs/api/v3/data/ClientDetails.json?.and_filter=true{}&.case_sensitive=false".format(self.cpi_ipv4_address, modified_desc_list)

        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        # create a list of the returned ids
        list_json = self.parse_json.value(result.json(),['queryResponse', 'entityId'], self.logger)
        id_list = self.parse_json.ids_list(list_json)

        return id_list

    def json_basic(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/Clients/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

    def json_detailed(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/ClientDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

    # --- print API calls, mainly for testing

    def print_client_basic(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Clients/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        print(json.dumps(result.json(), indent=4))

    # --- end print API calls, mainly for testing
