
# system imports
import json

# 3rd part imports
import requests

# local imports
from json_parser import JsonParser
from connector.connector import Connector


class Switch(Connector):

    # --- POST calls

    # Forcing a sync is broken only with switches on IOS-XE 03.03.03 code base
    def sync(self, dev_ipv4_address):
        url = "https://{}/webacs/api/v3/op/devices/syncDevices.json".format(self.cpi_ipv4_address)
        payload = {"syncDevicesDTO": {"devices": {"device": [{"address": "{}".format(dev_ipv4_address)}]}}}
        result = self.error_handling(requests.post, 5, url, False, self.username, self.password, payload)

    # --- end POST calls

    # --- PUT calls (usually requires templates built in Prime to execute)

    def reload(self, dev_id, timeout):
        url = "https://{}/webacs/api/v3/op/cliTemplateConfiguration/deployTemplateThroughJob.json".format(
            self.cpi_ipv4_address)
        payload = \
            {
                "cliTemplateCommand": {
                    "targetDevices": {
                        "targetDevice": [{
                            "targetDeviceID": "{}".format(dev_id),
                            "variableValues": {
                                "variableValue": [{
                                    "name": "waittimeout",
                                    "value": "{}".format(timeout)
                                }]
                            }
                        }]
                    },
                    "templateName": "API_CALL_reload_switch"
                }
            }
        result = self.error_handling(requests.put, 5, url, False, self.username, self.password, payload)
        key_list = ['mgmtResponse', 'cliTemplateCommandJobResult', 0, 'jobName']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def conf_if_vlan(self, dev_id, interface, sw_port_type, access_vlan):
        url = "https://{}/webacs/api/v3/op/cliTemplateConfiguration/deployTemplateThroughJob.json".format(
            self.cpi_ipv4_address)
        payload = \
            {
                "cliTemplateCommand": {
                    "targetDevices": {
                        "targetDevice": [{
                            "targetDeviceID": "{}".format(dev_id),
                            "variableValues": {
                                "variableValue": [{
                                    "name": "InterfaceName",
                                    "value": "{}".format(interface)
                                }, {
                                    "name": "Description",
                                    "value": ""
                                }, {
                                    "name": "A1",
                                    "value": "{}".format(sw_port_type)
                                }, {
                                    "name": "StaticAccessVLan",
                                    "value": "{}".format(access_vlan)
                                }, {
                                    "name": "TrunkAllowedVLan",
                                    "value": ""
                                }, {
                                    "name": "VoiceVlan",
                                    "value": ""
                                }, {
                                    "name": "NativeVLan",
                                    "value": ""
                                }, {
                                    "name": "PortFast",
                                    "value": ""
                                }, {
                                    "name": "duplexField",
                                    "value": ""
                                }, {
                                    "name": "spd",
                                    "value": ""
                                }]
                            }
                        }]
                    },
                    "templateName": "API_CALL_conf_if_vlan"
                }
            }
        result = self.error_handling(requests.put, 5, url, False, self.username, self.password, payload)
        key_list = ['mgmtResponse', 'cliTemplateCommandJobResult', 0, 'jobName']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    # --- end PUT calls

    # --- GET calls

    def get_id_by_ip(self, dev_ipv4_address):
        url = "https://{}/webacs/api/v3/data/Devices.json?ipAddress=\"{}\"".format(self.cpi_ipv4_address,
                                                                                   dev_ipv4_address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_id_by_mac(self, address):

        url = "https://{}/webacs/api/v3/data/Devices.json?macAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_sync_status(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'collectionStatus']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_sync_time(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'collectionTime']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_reachability(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'reachability']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_software_version(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'softwareVersion']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    # Switch chassis info
    def get_stack_members(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'chassis', 'chassis']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    # CDP neighbour info gets populated when the device syncs
    def get_cdp_neighbours(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'cdpNeighbors', 'cdpNeighbor']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    def get_ports(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'ethernetInterfaces', 'ethernetInterface']
        return JsonParser.get_value(JsonParser, result.json(), key_list, self.logger)

    # --- print API calls, mainly for testing

    def print_json_info(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        print(json.dumps(result.json(), indent=4))

    def print_json_detailed_info(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        print(json.dumps(result.json(), indent=4))

    # --- end print API calls, mainly for testing