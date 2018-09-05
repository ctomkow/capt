
# system imports
import json

# 3rd part imports
import requests

# local imports
from connector.connector import Connector


class Switch(Connector):

    # --- POST calls

    # Forcing a sync is broken only with switches on IOS-XE 03.03.03 code base
    def sync(self, dev_ipv4_address):
        url = "https://{}/webacs/api/v3/op/devices/syncDevices.json".format(self.cpi_ipv4_address)
        payload = {"syncDevicesDTO": {"devices": {"device": [{"address": "{}".format(dev_ipv4_address)}]}}}
        result = self.error_handling(requests.post, 5, url, False, self.username, self.password, payload)

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
        return self.parse_json.value(result.json(), key_list, self.logger)

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
        return self.parse_json.value(result.json(), key_list, self.logger)

    def conf_if_bas(self, dev_id, interface, description, access_vlan):
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
                                    "value": "{}".format(description)
                                }, {
                                    "name": "StaticAccessVLan",
                                    "value": "{}".format(access_vlan)
                                }]
                            }
                        }]
                    },
                    "templateName": "API_CALL_conf_if_bas"
                }
            }
        result = self.error_handling(requests.put, 5, url, False, self.username, self.password, payload)
        key_list = ['mgmtResponse', 'cliTemplateCommandJobResult', 0, 'jobName']
        return self.parse_json.value(result.json(), key_list, self.logger)


    # --- GET calls

    def id_by_ip(self, dev_ipv4_address):
        url = "https://{}/webacs/api/v3/data/Devices.json?ipAddress=\"{}\"".format(self.cpi_ipv4_address,
                                                                                   dev_ipv4_address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def id_by_mac(self, address):

        url = "https://{}/webacs/api/v3/data/Devices.json?macAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def sync_status(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'collectionStatus']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def sync_time(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'collectionTime']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def reachability(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'reachability']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def software_version(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'softwareVersion']
        return self.parse_json.value(result.json(), key_list, self.logger)

    # Switch chassis info
    def stack_members(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'chassis', 'chassis']
        return self.parse_json.value(result.json(), key_list, self.logger)

    # CDP neighbour info gets populated when the device syncs
    def cdp_neighbours(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'cdpNeighbors', 'cdpNeighbor']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def ports(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'ethernetInterfaces', 'ethernetInterface']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def port_detail_dict(self, dev_id, interface_name):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'ethernetInterfaces', 'ethernetInterface']
        interface_list_of_dicts = self.parse_json.value(result, key_list, self.logger)

        for interface_dict in interface_list_of_dicts:
            for key in interface_dict:  # iterating over dict's return keys only
                if interface_dict[key] == interface_name:
                    return interface_dict

    def json_detailed(self, dev_id):
        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

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
