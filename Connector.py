# Craig Tomkow
# May 22, 2018
#
# Connector class to pull state from Cisco Prime Infrastructure
# Note: Use API v3 in calls (released in Prime 3.3
#       When Prime goes to 3.4, change to APIv4

# system imports
import urllib3
import time
import sys

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

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


    def print_info(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        print(json.dumps(req.json(), indent=4))

    def print_detailed_info(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        print(json.dumps(req.json(), indent=4))

    # Forcing a sync is broken only with switches on IOS-XE 03.03.03 code base
    def sync(self, dev_ipv4_address):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/op/devices/syncDevices.json"
        payload = { "syncDevicesDTO" : { "devices" : { "device" : [ { "address" : f"{dev_ipv4_address}" } ] } } }

        try:
            req = requests.post(url, verify=False, auth=(username, password), json=payload)
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

    def get_sync_status(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entity'][0]['devicesDTO']['collectionStatus']

    def get_sync_time(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entity'][0]['devicesDTO']['collectionTime']

    # device id is needed for most future API calls
    def get_dev_id(self, dev_ipv4_address):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices.json?ipAddress=\"{dev_ipv4_address}\""

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.get_dev_id(dev_ipv4_address)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entityId'][0]['$']

    def get_reachability(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entity'][0]['devicesDTO']['reachability']

    def get_software_version(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/Devices/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entity'][0]['devicesDTO']['softwareVersion']

    # Switch chassis info
    def get_stack_members(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']

    # CDP neighbour info gets populated when the device syncs
    def get_cdp_neighbours(self, dev_id):

        url = f"https://{cpi_ipv4_address}/webacs/api/v3/data/InventoryDetails/{dev_id}.json"

        try:
            req = requests.get(url, verify=False, auth=(username, password))
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                time.sleep(1)
                self.print_info(dev_id)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)

        return req.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['cdpNeighbors']['cdpNeighbor']



