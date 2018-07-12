
# system imports
import urllib3
import time
import sys
import random
import json

# 3rd part imports
import requests

# local imports
from json_parser import JsonParser


class Connector:

    def __init__(self, uname, passwd, cpi_ipv4_addr, log):

        self.username = uname
        self.password = passwd
        self.cpi_ipv4_address = cpi_ipv4_addr
        self.logger = log
        self.parse_json = JsonParser()

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # --- Prime job execution and handling

    def job_complete(self, job_id):

        url = "https://{}/webacs/api/v3/op/jobService/runhistory.json?jobName=\"{}\"".format(self.cpi_ipv4_address, job_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['mgmtResponse', 'job', 0, 'runInstances', 'runInstance', 0, 'runStatus']
        status = self.parse_json.value(result.json(), key_list, self.logger)

        if status == "COMPLETED": # job complete
            return True
        elif status == "RUNNING": # job running
            return False
        else:
            # ADD CRITICAL LOGGING HERE
            print('critical, job not run correctly')
            sys.exit(1)

    def job_successful(self, job_id):

        url = "https://{}/webacs/api/v3/op/jobService/runhistory.json?jobName=\"{}\"".format(self.cpi_ipv4_address, job_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['mgmtResponse', 'job', 0, 'runInstances', 'runInstance', 0, 'resultStatus']
        status = self.parse_json.value(result.json(), key_list, self.logger)
        if status == "SUCCESS":
            return True
        elif status == "FAILURE":
            return False

    # --- end Prime job handling

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
                self.logger.warning("Too many API calls at once. Slight delay before retrying. Status code: {}".format(req.status_code))
                time.sleep(random.uniform(1.0, 5.0))

                base_case -= 1 # decrement base_case by one
                if base_case == 0:
                    self.logger.critical("Recursive error handler's base case reached. Abandoning API calls.")
                    self.logger.critical(api_call_method)
                    self.logger.critical(args[0])
                    sys.exit(1)

                self.logger.debug("Base case just before recursive call: {}".format(base_case))
                if api_call_method == requests.get:
                    req = self.error_handling(api_call_method, base_case, args[0], args[1], args[2], args[3])
                elif api_call_method == requests.post or api_call_method == requests.put:
                    req = self.error_handling(api_call_method, base_case, args[0], args[1], args[2], args[3], args[4])
                else:
                    self.logger.critical("Recursive API call failed")
                    sys.exit(1)
            elif req.status_code == 401:
                self.logger.critical("Bad authentication. Check credentials.")
                self.logger.critical(error)
                sys.exit(1)
            else:
                self.logger.critical("API call failed.")
                self.logger.critical(error)
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            # catch-all failure, exit program
            self.logger.critical(e)
            sys.exit(1)
        finally:
            return req

    # --- print API calls, mainly for testing

    def test(self):
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?name=\"ESQ_4-430_5e3c\""
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        print(json.dumps(result.json(), indent=4))

    # --- end print API calls, mainly for testing
