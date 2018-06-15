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
import random

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

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    def print_detailed_info(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    def print_client_summary(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Clients/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    # Forcing a sync is broken only with switches on IOS-XE 03.03.03 code base
    def sync(self, dev_ipv4_address):

        url = "https://{}/webacs/api/v3/op/devices/syncDevices.json".format(cpi_ipv4_address)
        payload = { "syncDevicesDTO" : { "devices" : { "device" : [ { "address" : "{}".format(dev_ipv4_address) } ] } } }
        result = self.error_handling(requests.post, url, False, username, password, payload)

    def get_sync_status(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['collectionStatus']

    def get_sync_time(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['collectionTime']

    # device id is needed for most future API calls
    def get_dev_id(self, dev_ipv4_address):

        url = "https://{}/webacs/api/v3/data/Devices.json?ipAddress=\"{}\"".format(cpi_ipv4_address, dev_ipv4_address)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entityId'][0]['$']

    def get_reachability(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['reachability']

    def get_software_version(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['softwareVersion']

    # Switch chassis info
    def get_stack_members(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']

    # CDP neighbour info gets populated when the device syncs
    def get_cdp_neighbours(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['cdpNeighbors']['cdpNeighbor']

    def get_switch_ports(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']

    # a decorator-like method for error handling
    def error_handling(self, api_call_method, *args):

        try:
            if len(args) == 4: # a GET api call
                req = api_call_method(args[0], verify=args[1], auth=(args[2], args[3]))
            elif len(args) == 5: # a POST api call
                req = api_call_method(args[0], verify=args[1], auth=(args[2], args[3]), json=args[4])
            else:
                pass
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503:
                # too many requests at once
                print("Too many API calls at once. Slight delay before retrying")
                time.sleep(random.uniform(1.5, 3.5))
                req = self.error_handling(api_call_method, args[0], args[1], args[2], args[3])
            elif req.status_code == 401:
                print("Bad authentication. Check credentials.")
                print(error)
                sys.exit(1)
            else:
                print(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            print(e)
            sys.exit(1)
        finally:
            return req

