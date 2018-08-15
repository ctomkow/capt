# system imports
import json


# 3rd part imports
import requests
import re


# local imports
from connector.connector import Connector


class Device(Connector):
    def ids_by_desc(self, desc):
#        # Split the description string if it is comma seperated
#        desc_list = desc.split(",")
#        modified_desc_list = ""
#        # Iterate through descriptions to remove characters that cause issues
#        for desc_iterator in desc_list:
#            stripped_desc = re.sub(r'(\(|\))', r"", desc_iterator)
#            modified_desc_list = modified_desc_list + "&ethernetInterface.description=contains(" + stripped_desc + ")"
        modified_desc_list = self.parse_desc.desc_id_split(desc)

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
