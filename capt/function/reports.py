# A container for reporting functions

from connector.switch import Switch
from json_parser import JsonParser
import time
import sys
import re
import csv

class Reports:

    def __init__(self):

        self.parse_json = JsonParser()
        self.sw_list = []
        self.filename = str(time.time())

    def port_count (self, args, config, logger): # Version 1.0 - complete until additional feedback
        ports_up, ports_down = 0,0 # Global ports Up / Down for all devices being reported on
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter) # API call to get list of devices to be reported on
        self.no_results(dev_id_list) # Exit if 0 results
        self.csv_printer(['Device Name', 'IP Address', 'Device Type', 'Device Model(s)', 'Stack Size', 'Serial Number(s)', 'Connected', 'Notconnect', 'Total', '% Used', 'Reachability'], args.csv, logger)
        for curr_id in dev_id_list:
            time.sleep(0.35)  # Prevents too many API calls too fast
            inventory_dto = api_call.json_detailed(curr_id) # API Call for current device ID's inventory details
            device_detail = self.device_details(inventory_dto) # Populates dictionary wil device details
            self.sw_list.append(device_detail['dev_name']) # This list will contain all devices reported on
            up, down = 0,0 # Ports Up / Down for current device ID
            true_port_list = self.true_port_list(inventory_dto, device_detail['dev_type']) # Returns port list without uplinks and virtual interfaces (except 29xx stackables)
            for port in true_port_list:
                if port['operationalStatus'] == 'UP':
                    up +=1
                elif port['operationalStatus'] == 'DOWN':
                    down +=1
            self.verbose_printer("{}: UP: {} | Down: {}".format(device_detail['dev_name'], up, down), args.verbose, logger)
            self.csv_printer([device_detail['dev_name'], device_detail['ip_address'], device_detail['dev_type'], device_detail['stack_models'], device_detail['stack_size'], device_detail['serial_numbers'], up, down, (up+down), str(round(((up/(up+down))*100)))+'%', device_detail['reachability']], args.csv, logger)
            ports_up += up # Appends current ID values to global Up count
            ports_down += down # Appends current ID values to global Down count
        total_ports = ports_up + ports_down
        print (self.sw_list)
        print ('UP: ' + str(ports_up) + ' | Down: ' + str(ports_down) + ' | Total: ' + str(total_ports))

    def vlanmap (self, args, config, logger): # Version 0.8 - still messy
        vlan_total = [] # Global list for vlan counts
        op = {} # Global dictionary for operational status
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        self.no_results(dev_id_list) # Exit if 0 results
        self.csv_printer(['Device Name', 'VLAN ID', 'VLAN Name', 'Count', 'Connected'], args.csv, logger)
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)
            time.sleep(1)
            vlan_counts = {} # Vlan counts for curr_id
            op_status = {} # operational status for curr_id
            device_detail = self.device_details(inventory_dto)
            self.verbose_printer('### {} ###'.format(device_detail['dev_name']), args.verbose, logger)
            self.sw_list.append(device_detail['dev_name'])
            find_config = api_call.find_config_archive_id(device_detail['dev_name'])
            config_id = api_call.config_archive_by_id(find_config)
            config_archive = api_call.config_archive_content(config_id)
            vlan_ids = re.findall(r'(?:vlan\s)(\d{1,4})(?:\\n\sname\s)(.*?)(?:\\n\!)', str(config_archive)) # Find VLAN names in config
            true_port_list = self.true_port_list(inventory_dto, device_detail['dev_type'])
            for port in true_port_list:
                try:
                    if str(port['accessVlan']) not in vlan_counts.keys():
                        vlan_counts[str(port['accessVlan'])] = []
                    vlan_counts[str(port['accessVlan'])].append(str(port['name']))
                    if 'VLAN' + str(port['accessVlan']) not in op_status.keys():
                        op_status['VLAN' + str(port['accessVlan'])] = 0
                    if port['operationalStatus'] == 'UP':
                        op_status['VLAN' + str(port['accessVlan'])] += 1
                except Exception as err:
                    continue

            for id in op_status:
                if id not in op.keys():
                    op[id] = op_status[id]
                else:
                    op[id] = op[id] + op_status[id]
            for id in vlan_counts.keys():
                vlan_counts[id] = len(vlan_counts[id])
            ids = dict(vlan_ids)

            for n in vlan_counts.keys():
                if n in ids.keys():
                    self.verbose_printer('VLAN {}, {}, {}'.format(n, ids[n], vlan_counts[n]), args.verbose, logger)
                    self.csv_printer([device_detail['dev_name'], n, ids[n], vlan_counts[n], op_status['VLAN' + str(n)]], args.csv, logger)
                    vlan_total.append(['VLAN' + str(n),str(ids[n]),vlan_counts[n]])
            if len(vlan_counts) < 1:
                print (str(device_detail['dev_name']) + ' failed.')
                self.sw_list.remove(device_detail['dev_name'])
            else:
                print (str(device_detail['dev_name']) + ' complete')
        print ('------------------------------')
        final_count = {}
        for vlan in vlan_total:
            if vlan[0] not in final_count.keys():
                final_count[vlan[0]] = 0
            final_count[vlan[0]] = final_count[vlan[0]] + vlan[2]
        vlan_names = {}
        for vlan in vlan_total:
            if vlan[0] not in vlan_names.keys():
                vlan_names[vlan[0]] = []
            if vlan[1] not in vlan_names[vlan[0]]:
                vlan_names[vlan[0]].append(vlan[1])
        print (self.sw_list)
        self.filename = str(time.time())
        self.csv_printer(['VLAN ID', 'Name(s)', 'Connected', 'Configured'], args.csv, logger)
        for key, value in vlan_names.items():
            if key in final_count.keys():
                print (str(key) + str(value) + ': ' + str(op[key]) + ' CONNECTED out of ' + str(final_count[key]) + ' CONFIGURED')
                self.csv_printer([key, value, op[key], final_count[key]], args.csv, logger)

    def device_details (self, inventory_dto):
        detail_detial = {}
        detail_detial['dev_name'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
        detail_detial['ip_address'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['ipAddress']
        detail_detial['dev_type'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceType']
        detail_detial['reachability'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['reachability']
        chassis = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']
        serial_numbers = []
        stack_models = []
        for switch in chassis:
            try:
                serial_numbers.append(switch['serialNr'])
                stack_models.append(switch['modelNr'])
            except Exception as err:
                continue
        detail_detial['stack_size'] = len(stack_models)
        detail_detial['serial_numbers'] = serial_numbers
        detail_detial['stack_models'] = stack_models
        return detail_detial

    def true_port_list (self, inventory_dto, dev_type):
        ethernet_interfaces = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']
        ignore = ['Te', '/1/', '49', '50', '51', '52', '1/1', '1/2', '1/3', '1/4', '0/0', 'Port-channel', 'FastEthernet1'] # Uplink interfaces
        if '-24' in dev_type:
            ignore.extend(('25', '26', '27', '28'))
        if 'Cisco Catalyst 35xx Stack-able Ethernet Switch' in dev_type:
            ignore.extend(('0/13', '0/14', '0/15', '0/16'))
        if 'Cisco Catalyst 3560-' in dev_type:
            ignore.extend(('GigabitEthernet0/1', 'GigabitEthernet0/2', 'GigabitEthernet0/3', 'GigabitEthernet0/4'))
        if 'Cisco Catalyst 2960-' in dev_type:
            ignore.extend(('GigabitEthernet0/1', 'GigabitEthernet0/2', 'GigabitEthernet0/3', 'GigabitEthernet0/4'))
        if 'Cisco Catalyst 2950' in dev_type:
            ignore.extend(('GigabitEthernet0/1', 'GigabitEthernet0/2'))
        if 'Cisco Catalyst 3560CG-8' in dev_type:
            ignore.extend(('GigabitEthernet0/9', 'GigabitEthernet0/10'))
        if 'Cisco Catalyst 3560V2' in dev_type:
            ignore.extend(('GigabitEthernet0/1', 'GigabitEthernet0/2'))
        true_port_list = []
        for interface in ethernet_interfaces:
            if interface['name'] != 'FastEthernet0':
                    if not any(x in interface['name'] for x in ignore):
                        true_port_list.append(interface)
        return true_port_list

    def no_results (self, dev_id_list):
        if len(dev_id_list) < 1:         # exit out of loop if no matches
            print('No switches found.')
            sys.exit(1)
        else:
            print(str(len(dev_id_list)) + ' switch(es) found.')
            return

    def verbose_printer (self, print_string, flag, logger):
        if flag:
            logger.info(print_string)

    def csv_printer (self, csv_string, flag, logger):
        if flag:
            outputFile = open(str(self.filename) + '.csv', 'a', newline='')
            outputWriter = csv.writer(outputFile)
            outputWriter.writerow(csv_string)
            outputFile.close()

    def dev_count (self, args, config, logger): # Version 0.5 - not very useful right now
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter) # API call to get list of devices to be reported on
        ap, phone = 0,0 # Initial devices counts
        self.no_results(dev_id_list) # Exit if 0 results
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)
            time.sleep(1)
            device_detail = self.device_details(inventory_dto)
            self.sw_list.append(device_detail['dev_name'])
            cdp = api_call.cdp_neighbours(curr_id)
            for cdp_curr in cdp:
                a,p = 0,0
                if 'AIR' in cdp_curr['neighborDevicePlatformType']:
                    a +=1
                if 'Cisco IP Phone' in cdp_curr['neighborDevicePlatformType']:
                    p += 1
                ap += a
                phone += p
                self.verbose_printer('{}, {}, {}'.format(cdp_curr['neighborDevicePlatformType'], cdp_curr['neighborDeviceName'], cdp_curr['nearEndInterface']), args.verbose, logger)
        print (self.sw_list)
        print ('Total APs: ' + str(ap))
        print ('Total Phones: ' + str(phone))


