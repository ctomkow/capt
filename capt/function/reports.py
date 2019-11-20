# A container for reporting functions

from connector.switch import Switch
from json_parser import JsonParser
import time
import sys
import re

class Reports:

    def __init__(self):

        self.parse_json = JsonParser()

    def port_count (self, args, config, logger):
        sw_list = []
        ports_up, ports_down = 0,0
        ignore = ['Te','/1/','49','50','51','52']
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        # exit out of loop if no matches
        if len(dev_id_list) < 1:
            print ('No switches found.')
            sys.exit(1)
        for curr_id in dev_id_list:
            time.sleep(1)
            dev_result = api_call.json_detailed(curr_id)
            dev_name = dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
            sw_list.append(dev_name)
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
            self.verbose_printer("{}: UP: {} | Down: {}".format(dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName'], up, down), args.verbose, logger)
            self.csv_printer("[],{},[]".format(dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName'], up, down), args.csv, logger)
            #print (str(dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName'])+','+str(up)+','+str(down)) # CSV Format
            ports_up += up
            ports_down += down
        total = ports_up + ports_down
        print (sw_list)
        print ('UP: ' + str(ports_up) + ' | Down: ' + str(ports_down) + ' | Total: ' + str(total))

    def dev_count (self, args, config, logger):
        sw_list = []
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        ap, phone, switch = 0,0,0
        if len(dev_id_list) < 1:
            print('No switches found.')
            sys.exit(1)
        for curr_id in dev_id_list:
            dev_result = api_call.json_detailed(curr_id)
            dev_name = dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
            sw_list.append(dev_name)
            time.sleep(1)
            cdp = api_call.cdp_neighbours(curr_id)
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
                self.verbose_printer('{}, {}, {}'.format(cdp_curr['neighborDevicePlatformType'], cdp_curr['neighborDeviceName'], cdp_curr['nearEndInterface']), args.verbose, logger)
        print (sw_list)
        print ('Total APs: ' + str(ap))
        print ('Total Phones: ' + str(phone))

    def vlanmap (self, args, config, logger):
        ignore = ['Te', '/1/', '49', '50', '51', '52']
        vlan_total = []
        sw_list = []
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        # exit out of loop if no matches
        if len(dev_id_list) < 1:
            print('No switches found.')
            sys.exit(1)
        for curr_id in dev_id_list:
            vlan_counts = {}
            time.sleep(1)
            port_list = api_call.ports(curr_id)
            physical_list = api_call.physical_ports(curr_id)
            dev_result = api_call.json_detailed(curr_id)
            dev_name = dev_result['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
            self.verbose_printer('### {} ###'.format(dev_name), args.verbose, logger)
            sw_list.append(dev_name)
            find_config = api_call.find_config_archive_id(dev_name)
            config_id = api_call.config_archive_by_id(find_config)
            config_archive = api_call.config_archive_content(config_id)
            vlan_ids = re.findall(r'(?:vlan\s)(\d{1,4})(?:\\n\sname\s)(.*?)(?:\\n\!)', str(config_archive))
            for port in port_list:
                if not any(x in port['name'] for x in ignore):
                    for physical_port in physical_list:
                        if physical_port['name'] == port['name']:
                            if str(port['accessVlan']) not in vlan_counts.keys():
                                vlan_counts[str(port['accessVlan'])] = []
                            vlan_counts[str(port['accessVlan'])].append(str(port['name']))
            for id in vlan_counts.keys():
                vlan_counts[id] = len(vlan_counts[id])
            ids = dict(vlan_ids)
            for n in vlan_counts.keys():
                if n in ids.keys():
                    self.verbose_printer('VLAN {}, {}, {}'.format(n, ids[n], vlan_counts[n]), args.verbose, logger)
                    self.csv_printer("{},{},{},{}".format(dev_name, n, ids[n], vlan_counts[n]), args.csv, logger)
                    vlan_total.append(['VLAN' + str(n),str(ids[n]),vlan_counts[n]])
        new = {}
        for v in vlan_total:
            if v[0] not in new.keys():
                new[v[0]] = 0
            new[v[0]] = new[v[0]] + v[2]
        names = {}
        for v in vlan_total:
            if v[0] not in names.keys():
                names[v[0]] = []
            if v[1] not in names[v[0]]:
                names[v[0]].append(v[1])
        print (sw_list)
        for key, value in names.items():
            if key in new.keys():
                print (key, value, new[key])

    def verbose_printer (self, print_string, flag, logger):
        if flag:
            logger.info(print_string)

    def csv_printer (self, print_string, flag, logger):
        if flag:
            logger.info(print_string)



