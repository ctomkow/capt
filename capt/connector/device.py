# system imports
import json


# 3rd part imports
import requests
import re


# local imports
from connector.connector import Connector


class Device(Connector):
    def ids_by_desc(self, desc, sw_name):
        modified_desc_list = self.parse_desc.desc_id_split(desc)

        if sw_name is not None:
            url = "https://{}/webacs/api/v3/data/InventoryDetails.json?.and_filter=true&summary.deviceName=contains({}){}&.case_sensitive=false".format(
                self.cpi_ipv4_address,sw_name, modified_desc_list)
        else:
            url = "https://{}/webacs/api/v3/data/InventoryDetails.json?.and_filter=true{}&.case_sensitive=false".format(self.cpi_ipv4_address, modified_desc_list)
        id_list = []
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        # create a
        key_list = ['queryResponse', '@count']
        occurance_count = self.parse_json.value(result.json(),key_list,self.logger)
        for i in range(occurance_count):
            key_list = ['queryResponse', 'entityId', i, '$']
            id_list.append(self.parse_json.value(result.json(),key_list, self.logger))

        return id_list

    def id_by_ip(self, dev_ip_address):

        url = "https://{}/webacs/api/v3/data/Devices.json?ipAddress={}&.case_sensitive=false".format(
            self.cpi_ipv4_address, dev_ip_address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        dev_id = self.parse_json.value(result.json(), key_list, self.logger)
        return dev_id

    def id_by_hostname(self, dev_hostname):

        url = "https://{}/webacs/api/v3/data/Devices.json?deviceName=contains({})&.case_sensitive=false".format(
            self.cpi_ipv4_address, dev_hostname)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        dev_id = self.parse_json.value(result.json(), key_list, self.logger)
        return dev_id

    def json_basic(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

    def json_detailed(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

    # --- print API calls, mainly for testing

    def print_client_basic(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        print(json.dumps(result.json(), indent=4))
