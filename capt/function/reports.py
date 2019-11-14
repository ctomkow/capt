# A container for reporting functions

from connector.switch import Switch
from json_parser import JsonParser
import time

class Reports:

    def __init__(self):

        self.parse_json = JsonParser()

    def port_count (self, args, config, logger):
        ports_up, ports_down = 0,0
        ignore = ['Te','/1/','49','50','51','52']
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        # exit out of loop if no matches
        print (len(dev_id_list))
        if len(dev_id_list) < 1:
            sys.exit(1)
        for curr_id in dev_id_list:
            time.sleep(1)
            dev_result = api_call.json_detailed(curr_id)
            port_list = api_call.ports(curr_id)
            physical_list = api_call.physical_ports(curr_id)
            up, down = 0,0
            for port in port_list:
                if not any(x in port['name'] for x in ignore):
                    for physical_port in physical_list:
                        if physical_port['name'] == port['name']:
                            if port['operationalStatus'] == 'UP':
                                up +=1
                            elif port['operationalStatus'] == 'DOWN':
                                down +=1
            #self.verbose_printer("{}: UP: {} | Down: {}".format(dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName'], up, down), args.verbose, logger)
            print (str(dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName'])+','+str(up)+','+str(down))
            ports_up += up
            ports_down += down
        total = ports_up + ports_down
        print ('UP: ' + str(ports_up) + ' | Down: ' + str(ports_down) + ' | Total: ' + str(total))

    def dev_count (self, args, config, logger):
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        ap, phone, switch = 0,0,0
        if len(dev_id_list) < 1:
            sys.exit(1)
        for curr_id in dev_id_list:
            time.sleep(1)
            cdp = api_call.cdp_neighbours(curr_id)
            print (cdp)
            for cdp_curr in cdp:
                a,s,p = 0,0,0
                if 'AIR' in cdp_curr['neighborDevicePlatformType']:
                    a +=1
                if 'cisco WS-' in cdp_curr['neighborDevicePlatformType']:
                    s += 1
                if 'Cisco IP Phone' in cdp_curr['neighborDevicePlatformType']:
                    p += 1
                ap += a
                phone += p
                switch += s
                print (str(cdp_curr['neighborDevicePlatformType']) + ' : ' + str(cdp_curr['neighborDeviceName']) + ' : ' + str(cdp_curr['nearEndInterface']))
        print (ap)
        print (switch)
        print (phone)


    def verbose_printer (self, print_string, flag, logger):
        if flag:
            logger.info(print_string)




