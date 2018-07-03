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


    def __init__(self, uname, passwd, cpi_ipv4_addr, log):

        global username
        global password
        global cpi_ipv4_address
        global logger

        username = uname
        password = passwd
        cpi_ipv4_address = cpi_ipv4_addr
        logger = log

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


    #--- POST calls

    # Forcing a sync is broken only with switches on IOS-XE 03.03.03 code base
    def sync(self, dev_ipv4_address):

        url = "https://{}/webacs/api/v3/op/devices/syncDevices.json".format(cpi_ipv4_address)
        payload = { "syncDevicesDTO" : { "devices" : { "device" : [ { "address" : "{}".format(dev_ipv4_address) } ] } } }
        result = self.error_handling(requests.post, 5, url, False, username, password, payload)

    #--- end POST calls

    #--- PUT calls (usually requires templates built in Prime to execute)

    def reload_switch(self, dev_id, timeout):

        url = "https://{}/webacs/api/v3/op/cliTemplateConfiguration/deployTemplateThroughJob.json".format(cpi_ipv4_address)
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
        result = self.error_handling(requests.put, 5, url, False, username, password, payload)
        job_id = result.json()['mgmtResponse']['cliTemplateCommandJobResult'][0]['jobName']
        return job_id

    #--- end PUT calls

    #--- Prime job execution and handling

    def job_complete(self, job_id):

        url = "https://{}/webacs/api/v3/data/JobSummary.json?jobName=\"{}\"".format(cpi_ipv4_address, job_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        result_list = result.json()['queryResponse']['entityId'][0]['@displayName']
        status = [x.strip() for x in result_list.split(',')]
        if status[-1] == "COMPLETED": # if last element in list = COMPLETED
            return True
        else:
            return False

    def job_successful(self, job_id):

        url = "https://{}/webacs/api/v3/op/jobService/runhistory.json?jobName=\"{}\"".format(cpi_ipv4_address, job_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        status = result.json()['mgmtResponse']['job'][0]['runInstances']['runInstance'][0]['resultStatus']
        if status == "SUCCESS":
            return True
        elif status == "FAILURE":
            return False

    #--- end Prime job handling

    #--- GET calls

    def get_sync_status(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['collectionStatus']

    def get_sync_time(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['collectionTime']

    # device id is needed for most future API calls
    def get_switch_id(self, dev_ipv4_address):

        url = "https://{}/webacs/api/v3/data/Devices.json?ipAddress=\"{}\"".format(cpi_ipv4_address, dev_ipv4_address)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entityId'][0]['$']

    def get_access_point_id(self, name):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?name=\"{}\"".format(cpi_ipv4_address, name)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entityId'][0]['$']

    def get_reachability(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['reachability']

    def get_software_version(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['devicesDTO']['softwareVersion']

    # Switch chassis info
    def get_stack_members(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']

    # CDP neighbour info gets populated when the device syncs
    def get_cdp_neighbours(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['cdpNeighbors']['cdpNeighbor']

    def get_switch_ports(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']

    def get_access_point_ip(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        return result.json()['queryResponse']['entity'][0]['accessPointsDTO']['ipAddress']

    # a decorator-like method for error handling
    def error_handling(self, api_call_method, base_case, *args):

        try:
            if api_call_method == requests.get: # a GET api call
                req = api_call_method(args[0], verify=args[1], auth=(args[2], args[3]))
            elif api_call_method == requests.post: # a POST api call
                req = api_call_method(args[0], verify=args[1], auth=(args[2], args[3]), json=args[4])
            elif api_call_method == requests.put: # a PUT api call
                req = api_call_method(args[0], verify=args[1], auth=(args[2], args[3]), json=args[4])
            else:
                pass
            req.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if req.status_code == 503 or req.status_code == 403:
                # too many requests at once
                logger.warning("Too many API calls at once. Slight delay before retrying. Status code: {}".format(req.status_code))
                time.sleep(random.uniform(1.0, 5.0))

                base_case -= 1 # decrement base_case by one
                if base_case == 0:
                    logger.critical("Recursive error handler's base case reached. Abandoning API calls.")
                    logger.critical(api_call_method)
                    logger.critical(args[0])
                    sys.exit(1)
                
                logger.debug("Base case just before recursive call: {}".format(base_case))
                if api_call_method == requests.get:
                    req = self.error_handling(api_call_method, base_case, args[0], args[1], args[2], args[3])
                elif api_call_method == requests.post or api_call_method == requests.put:
                    req = self.error_handling(api_call_method, base_case, args[0], args[1], args[2], args[3], args[4])
                else:
                    logger.critical("Recursive API call failed")
                    sys.exit(1)
            elif req.status_code == 401:
                logger.critical("Bad authentication. Check credentials.")
                logger.critical(error)
                sys.exit(1)
            else:
                logger.critical("API call failed.")
                logger.critical(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            logger.critical(e)
            sys.exit(1)
        finally:
            return req

    # --- print API calls, mainly for testing

    def test(self):
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?name=\"ESQ_4-430_5e3c\""
        result = self.error_handling(requests.get, 5, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    def print_info(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Devices/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    def print_detailed_info(self, dev_id):

        url = "https://{}/webacs/api/v3/data/InventoryDetails/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    def print_client_summary(self, dev_id):

        url = "https://{}/webacs/api/v3/data/Clients/{}.json".format(cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, username, password)
        print(json.dumps(result.json(), indent=4))

    # --- end print API calls, mainly for testing