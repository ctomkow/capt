# Craig Tomkow
# May 22, 2018
#
# Connector class to pull state from Cisco Prime Infrastructure
# Note: Use API v3 in calls (released in Prime 3.3
#       When Prime goes to 3.4, change to APIv4
#       syncDevices call only exists in API v1 it looks like according to documentation (and v1 is depreciated)


# 3rd part imports
import requests
import json


class Connector:


    def __init__(self, uname, passwd, cpi_ipv4_addr):

        global username
        global password
        global cpi_ipv4_address

        username = uname
        password = passwd
        cpi_ipv4_address = cpi_ipv4_addr


    def print_info(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"
        req = requests.get(url, verify=False, auth=(username, password))
        print(json.dumps(req.json(), indent=4))

    def print_detailed_info(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"
        req = requests.get(url, verify=False, auth=(username, password))
        print(json.dumps(req.json(), indent=4))

    # Forcing a sync is broken
    def sync(self, dev_ipv4_address):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/op/devices/syncDevices.json"
        payload = { "syncDevicesDTO" : { "devices" : { "device" : [ { "address" : f"{dev_ipv4_address}" } ] } } }
        req = requests.post(url, verify=False, auth=(username, password), json=payload)

    # device id is needed for most future API calls
    def get_dev_id(self, dev_ipv4_address):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices.json?ipAddress=\"{dev_ipv4_address}\""
        req = requests.get(url, verify=False, auth=(username, password))
        return req.json()['queryResponse']['entityId'][0]['$']

    def get_reachability(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"
        req = requests.get(url, verify=False, auth=(username, password))
        return req.json()['queryResponse']['entity'][0]['devicesDTO']['reachability']

    # Switch chassis info
    def get_stack_members(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"
        req = requests.get(url, verify=False, auth=(username, password))
        return req.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']

    # CDP neighbour info gets populated when the device syncs
    def get_cdp_neighbours(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"
        req = requests.get(url, verify=False, auth=(username, password))
        return req.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['cdpNeighbors']



