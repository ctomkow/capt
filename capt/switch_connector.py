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


class SwitchConnector(Connector):

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
        job_id = result.json()['mgmtResponse']['cliTemplateCommandJobResult'][0]['jobName']
        return job_id

    # --- end PUT calls

    def get_id(self, dev_ipv4_address):
        url = "https://{}/webacs/api/v3/data/Devices.json?ipAddress=\"{}\"".format(self.cpi_ipv4_address,
                                                                                   dev_ipv4_address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entityId'][0]['$']

    #--- GET calls

    def get_sync_status(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['collectionStatus']

    def get_sync_time(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['collectionTime']

    def get_reachability(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['reachability']

    def get_software_version(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['softwareVersion']

    # Switch chassis info
    def get_stack_members(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']

    # CDP neighbour info gets populated when the device syncs
    def get_cdp_neighbours(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['cdpNeighbors']['cdpNeighbor']

    def get_ports(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']