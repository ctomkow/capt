# A catch all container for functions that have not been assigned a different container
# system imports
import sys
import time

# local imports
from function.find import Find
from connector.switch import Switch
from connector.access_point import AccessPoint
from connector.alarms import Alarms
from json_parser import JsonParser
import config

#3rd party imports
import netmiko


class Tools:

    def __init__(self):
        self.find = Find()
        self.parse_json = JsonParser()

    def checkAlarms(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):
        alarm_api_call = Alarms(cpi_username, cpi_password, cpi_ipv4_address, logger)
        device_api_call = AccessPoint(cpi_username, cpi_password, cpi_ipv4_address, logger)
        crit_list = alarm_api_call.get_critical_alarm_ids()

        for alarm_id in crit_list:
            time.sleep(0.3)
            mac = alarm_api_call.devname_by_alarm_id(alarm_id)
            dev_id=device_api_call.id_by_alarm_mac_detailed(mac)
            dev_result = device_api_call.json_detailed(dev_id)

            #logger.info("------- Matching Switch #{}--------".format(dev_id_list.index(curr_id) + 1))
            dev_dict = {}
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'name']
            dev_dict['name'] = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'model']
            dev_dict['model'] = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'reachabilityStatus']
            dev_dict['status'] = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                        'neighborName']
            dev_dict['nb_name'] = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                        'neighborPort']
            dev_dict['nb_port'] = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                        'neighborIpAddress']
            dev_dict['nb_ip'] = self.parse_json.value(dev_result, key_list, logger)
            logger.info(
                "AP:#{}-{}:{}\n Neighbor:{}/{}:{}".format(dev_dict['name'], dev_dict['model'], dev_dict['status'],
                                                            dev_dict['nb_name'], dev_dict['nb_ip'],
                                                            dev_dict['nb_port']))
            if values_dict['toggle']:
                #modify this to use SNMP?
                logger.info("Performing Shut/No Shut on {}({}): {}".format(dev_dict['nb_name'], dev_dict['nb_ip'],
                                                                               dev_dict['nb_port']))

                #net_connect =
                Answer = input('Do you want to reset the port: (y/n)?')
                if "y" in Answer.lower():
                    print("do the reload")




