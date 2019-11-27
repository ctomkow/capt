
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

    def ids_by_desc(self, desc, sw_name):
        modified_desc_list = self.parse_var.desc_id_split(desc,"&ethernetInterface.description=contains(")

        if sw_name is not None:
            url = "https://{}/webacs/api/v3/data/InventoryDetails.json?.and_filter=true&summary.deviceName=contains({}){}&.case_sensitive=false".format(
                self.cpi_ipv4_address,sw_name, modified_desc_list)
        else:
            url = "https://{}/webacs/api/v3/data/InventoryDetails.json?.and_filter=true{}&.case_sensitive=false".format(self.cpi_ipv4_address, modified_desc_list)

        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)

        list_json = self.parse_json.value(result.json(),['queryResponse', 'entityId'], self.logger)
        id_list = self.parse_json.ids_list(list_json)


        return id_list

    def ids_by_location(self, sw_location):
        if sw_location == "all":
            url = "https://{}/webacs/api/v3/data/Devices.json?.and_filter=true&.group=Edge%20Networking%20Devices&.maxResults=1000".format(
                self.cpi_ipv4_address)
        else:
            url = "https://{}/webacs/api/v3/data/Devices.json?.and_filter=true&.group=Edge%20Networking%20Devices&deviceName=startsWith({})".format(
                self.cpi_ipv4_address, sw_location)

        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)

        list_json = self.parse_json.value(result.json(),['queryResponse', 'entityId'], self.logger)
        id_list = self.parse_json.ids_list(list_json)

        return id_list


    def id_by_mac(self, address):

        url = "https://{}/webacs/api/v3/data/Devices.json?macAddress=\"{}\"".format(self.cpi_ipv4_address, address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def id_by_hostname(self, dev_hostname):

        url = "https://{}/webacs/api/v3/data/Devices.json?deviceName=contains({})&.case_sensitive=false".format(
            self.cpi_ipv4_address, dev_hostname)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        dev_id = self.parse_json.value(result.json(), key_list, self.logger)
        return dev_id

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

    def physical_ports(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'physicalPorts', 'physicalPort']
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

    def json_basic(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

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

    def find_config_archive_id(self, dev_id):

        url = "https://{}/webacs/api/v3/data/ConfigVersions.json?deviceName={}".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def config_archive_by_id(self, dev_id):

        url = "https://{}/webacs/api/v3/data/ConfigVersions/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'configVersionsDTO', 'fileInfos', 'fileInfo']
        temp = self.parse_json.value(result.json(), key_list, self.logger)
        for i in temp:
            if i['fileState'] == 'RUNNINGCONFIG':
                config_id = i['fileId']
                return config_id

    def config_archive_content(self, dev_id):

        url = "https://{}/webacs/api/v1/op/configArchiveService/extractSanitizedFile.json?fileId={}".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['mgmtResponse', 'extractFileResult']
        return self.parse_json.value(result.json(), key_list, self.logger)