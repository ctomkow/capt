# Craig Tomkow
# May 22, 2018
#
# Connector class to pull state from Cisco Prime Infrastructure
# Note: Use API v3 in calls!!!


# 3rd part imports
import requests


class Connector:


    def __init__(self, uname, passwd, cpi_ipv4_addr):

        global username
        global password
        global cpi_ipv4_address

        username = uname
        password = passwd
        cpi_ipv4_address = cpi_ipv4_addr

    def get_dev_id(self, dev_ipv4_address):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices.json?ipAddress=\"{dev_ipv4_address}\""
        req = requests.get(url, verify=False, auth=(username, password))
        return req.json()['queryResponse']['entityId'][0]['$']

    def is_reachable(self):

        pass

    def get_stack_members(self):

        pass

    def get_cdp_neighbours(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"
        req = requests.get(url, verify=False, auth=(username, password))
        return req.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['cdpNeighbors']



