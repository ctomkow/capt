# A catch all container for functions that have not been assigned a different container
# system imports
import sys
import time
import subprocess
import smtplib

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

    def checkAlarms(self, args, config, logger):
        # email_string = ""
        num_successful=0
        num_failed=0
        alarm_api_call = Alarms(config, logger)
        device_api_call = AccessPoint(config, logger)
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
            logger.info("Processing Alarm {} / {} ID: {} ".format(crit_list.index(alarm_id)+1,len(crit_list),alarm_id))
            logger.info("AP: {} Model:{} Status:{}".format(dev_dict['name'], dev_dict['model'], dev_dict['status']))
            logger.info("Neighbor:{}({}):{}".format(dev_dict['nb_name'], dev_dict['nb_ip'], dev_dict['nb_port']))
            time.sleep(1)  # don't test for sync status too soon (CPI delay and all that)
            if args.toggle:
                Return = self.ap_reload(args,dev_dict["nb_ip"],dev_dict["nb_port"])
                success_string = "Shut/No Shut on {}({}): {}".format(dev_dict['nb_name'], dev_dict['nb_ip'],
                                                                       dev_dict['nb_port'])

                if Return.returncode == 0:
                    success_string += " Successful"
                    num_successful += 1
                    alarm_api_call.acknowledge_by_alarm_id(alarm_id) #acknowledge alarm
                else:
                    success_string += " FAILED"
                    num_failed += 1
                logger.info(success_string)
                # email_string += success_string + "\n"
        #logger.debug(email_string)

        logger.info("Total {} Alarms".format(len(crit_list)))
        logger.info("{} ports successfully reloaded ".format(num_successful))
        logger.info("{} ports failed to reload".format(num_failed))

    def ap_reload (self,args, ip,port):
        time.sleep(1)  # don't test for sync status too soon (CPI delay and all that)

        arg_run_list = "dnmt direct tools AP_Poke {} {} ".format(ip, port)
        if args.batch:
            arg_run_list += "-s"

        Return_val = subprocess.run(arg_run_list, shell=True)  ###<TODO> EXTERNAL CALL to DNMT

        return Return_val


    def un_ack_alarms(self, args, config, logger):

        alarm_api_call = Alarms(config, logger)
        crit_list = alarm_api_call.get_acked_critical_alarm_ids()

        for alarm_id in crit_list:
            alarm_api_call.unacknowledge_by_alarm_id(alarm_id) #acknowledge alarm


    def slow_aps(self, args, config, logger):

        api_call = AccessPoint(config, logger)
        device_api_call = AccessPoint(config, logger)
        dev_id_list = device_api_call.get_slow_ports()

        if len(dev_id_list) < 1:
            sys.exit(1)
        for curr_id in dev_id_list:
            result = api_call.json_detailed(curr_id)
            logger.info("------- Occurrence #{}--------\n".format(dev_id_list.index(curr_id) + 1))

            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor',0,'neighborName']
            neigh_name = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor',0,'neighborIpAddress']
            neigh_ip = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor',0,'neighborPort']
            interface = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor',0,'interfaceSpeed']
            speed = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'name']
            name = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'model']
            model = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'locationHierarchy']
            map_location = self.parse_json.value(result, key_list, logger)
            #
            logger.info("ap name :{}".format(name))
            logger.info("ap model :{}".format(model))
            logger.info("switch name :{}".format(neigh_name))
            logger.info("switch ip   :{}".format(neigh_ip))
            logger.info("interface   :{}".format(interface))
            logger.info("speed :{}".format(speed))
            logger.info("map location :{}".format(map_location))

            if args.toggle:
                Return = self.ap_reload(args, neigh_ip, interface)
                success_string = "Shut/No Shut on {}({}): {}".format(neigh_name, neigh_ip,interface)

                if Return.returncode == 0:
                    success_string += " Successful"
                else:
                    success_string += " FAILED"
                logger.info(success_string)

                #<TODO move this and previous into a function to reuse, add a sync before>
                # time.sleep(60)  # Give the AP some time to start up
                # result = api_call.json_detailed(curr_id)
                # logger.info("------- Occurrence #{} POST RELOAD--------\n".format(dev_id_list.index(curr_id) + 1))
                #
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                #             'neighborName']
                # neigh_name = self.parse_json.value(result, key_list, logger)
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                #             'neighborIpAddress']
                # neigh_ip = self.parse_json.value(result, key_list, logger)
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                #             'neighborPort']
                # interface = self.parse_json.value(result, key_list, logger)
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0,
                #             'interfaceSpeed']
                # speed = self.parse_json.value(result, key_list, logger)
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'name']
                # name = self.parse_json.value(result, key_list, logger)
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'model']
                # model = self.parse_json.value(result, key_list, logger)
                # key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'locationHierarchy']
                # map_location = self.parse_json.value(result, key_list, logger)
                # #
                # logger.info("ap name :{}".format(name))
                # logger.info("ap model :{}".format(model))
                # logger.info("switch name :{}".format(neigh_name))
                # logger.info("switch ip   :{}".format(neigh_ip))
                # logger.info("interface   :{}".format(interface))
                # logger.info("speed :{}".format(speed))
                # logger.info("map location :{}".format(map_location))
                # End reload
            else:
                time.sleep(1)  # sleep at the end of each to prevent overruns when running without toggle





