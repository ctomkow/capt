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

    def device_dictionary(self, inventory_dto):
        device_detail = {}
        chassis = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']
        ethernet_interfaces = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']
        dev_type = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceType']
        stack = len(chassis)
        for switch in chassis:
            try:
                if 'Provisioned' in switch['description']:
                    continue
                if stack == 1:
                    switch['name'] = 'Switch 1'
                if 'Switch' not in switch['name']:
                    switch['name'] = 'Switch ' + str(switch['name'])
                device_detail[switch['name']] = {}
                device_detail[switch['name']]['serial_number'] = switch['serialNr']
                device_detail[switch['name']]['stack_model'] = switch['modelNr']
                device_detail[switch['name']]['dev_type'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceType']
                device_detail[switch['name']]['dev_name'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
                device_detail[switch['name']]['ip_address'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['ipAddress']
                device_detail[switch['name']]['reachability'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['reachability']
                device_detail[switch['name']]['stack_size'] = len(chassis)
                device_detail[switch['name']]['ports'] = []
            except Exception as err:
                continue
        for switch in chassis:
            ignore = ['Te', '/1/', '49', '50', '51', '52', '1/1', '1/2', '1/3', '1/4', '0/0', 'Port-channel', 'FastEthernet1']
            if '24' in device_detail[switch['name']]['stack_model']:
                ignore.extend(('25', '26', '27', '28'))
            if '3560-' in dev_type or '3560C' in dev_type or '3560V' in dev_type or '2960-' in dev_type or '2960C' in dev_type or '2950' in dev_type:
                ignore.extend(('GigabitEthernet0/1', 'GigabitEthernet0/2', 'GigabitEthernet0/3', 'GigabitEthernet0/4'))
            if '12' in device_detail[switch['name']]['stack_model']:
                ignore.extend(('13', '14', '15', '16'))
            while stack != 0:
                for port in ethernet_interfaces:
                    if len(chassis) > 1:
                        if ('Ethernet' + str(stack)) in port['name']:
                            if not any(x in port['name'] for x in ignore):
                                device_detail['Switch ' + str(stack)]['ports'].append(port)
                    else:
                        if not any(x in port['name'] for x in ignore):
                            if port['name'] != 'FastEthernet0':
                                device_detail['Switch ' + str(stack)]['ports'].append(port)
                stack -= 1

        return device_detail

    def serial_numbers(self, device_detail):
        serial_numbers = []
        for switch in device_detail:
            serial_numbers.append(device_detail[switch]['serial_number'])
        return serial_numbers

    def stack_models(self, device_detail):
        stack_models = []
        for switch in device_detail:
            stack_models.append(device_detail[switch]['stack_model'])
        return stack_models

    def no_results(self, dev_id_list):
        if len(dev_id_list) < 1:  # exit out of loop if no matches
            print('No switches found.')
            sys.exit(1)
        else:
            print(str(len(dev_id_list)) + ' switch(es) found.')

    def vlan_names(self, api_call, device_detail):
        find_config = api_call.find_config_archive_id(
            device_detail['Switch 1']['dev_name'])  # API calls for config archive
        config_id = api_call.config_archive_by_id(find_config)  # API calls for config archive
        time.sleep(0.25)  # Prevents too many API calls too fast
        config_archive = api_call.config_archive_content(config_id)  # API calls for config archive
        vlan_config = re.findall(r'(?:vlan\s)(\d{1,4})(?:\\n\sname\s)(.*?)(?:\\n\!)',str(config_archive))  # Find VLAN names in config
        return vlan_config

    def verbose_printer(self, print_string, flag, logger):
        if flag:
            logger.info(print_string)

    def csv_printer(self, csv_string, flag, logger):
        if flag:
            outputFile = open(str(self.filename) + '.csv', 'a', newline='')
            outputWriter = csv.writer(outputFile)
            outputWriter.writerow(csv_string)
            outputFile.close()

    def port_count (self, args, config, logger): # Version 1.0 - works
        ports_up, ports_down = 0,0 # Global ports Up / Down for all devices being reported on
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter) # API call to get list of devices to be reported on
        self.no_results(dev_id_list) # Exit if 0 results
        self.csv_printer(['Device Name', 'Building', 'IP Address', 'Serial Number', 'Device Model', 'Stack Size', 'Connected', 'Notconnect', 'Total', '% Used', 'Reachability'], args.csv, logger)
        for curr_id in dev_id_list:
            time.sleep(0.35)  # Prevents too many API calls too fast
            inventory_dto = api_call.json_detailed(curr_id) # API Call for current device ID's inventory details
            device_detail = self.device_dictionary(inventory_dto) # Populates dictionary with device details
            self.sw_list.append(device_detail['Switch 1']['dev_name']) # This list will contain all devices reported on
            for switch in device_detail.keys():
                up, down = 0, 0  # Ports Up / Down for current device ID
                for port in device_detail[switch]['ports']:
                    if port['operationalStatus'] == 'UP':
                        up +=1
                    elif port['operationalStatus'] == 'DOWN':
                        down +=1
                ports_up += up  # Appends current ID values to global Up count
                ports_down += down  # Appends current ID values to global Down count
                self.verbose_printer("{}({}): {} Connected | {} Notconnect | {} Total".format(device_detail['Switch 1']['dev_name'],device_detail[switch]['serial_number'], up, down, (up+down)), args.verbose, logger)
                self.csv_printer([device_detail[switch]['dev_name'], ', '.join([device_detail[switch]['dev_name'][:3]]), device_detail[switch]['ip_address'], \
                                 device_detail[switch]['serial_number'], device_detail[switch]['stack_model'], len(device_detail.keys()), up, down, (up+down),\
                                 str(round(((up / (up + down)) * 100))) + '%', device_detail[switch]['reachability']], args.csv, logger)
        print (self.sw_list)
        self.verbose_printer("{} Connected | {} Notconnect | {} Total".format(ports_up, ports_down, (ports_up + ports_down)), args.verbose, logger)

    def service_matrix (self, args, config, logger):
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)  # API call to get list of devices to be reported on
        self.no_results(dev_id_list)  # Exit if 0 results
        self.csv_printer(['Device Name', 'Building', 'IP Address', 'Device Type', 'Device Model(s)', 'Stack', \
                          'Serial Number(s)', 'Reachability', 'UWS', 'VoIP', 'LC', 'PoS', 'Parking', 'SUTV', 'Kramer', \
                          'Connected', 'Notconnect', 'Total', '% Used', 'CDP Neighbors', 'Uplink'], args.csv, logger)
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)  # API Call for current device ID's inventory details
            device_detail = self.device_dictionary(inventory_dto)  # Populates dictionary wil device details
            self.sw_list.append(device_detail['Switch 1']['dev_name'])  # This list will contain all devices reported on
            up, down, ap, phone, lc, pos, parking, sutv, kramer = 0, 0, 0, 0, 0, 0, 0, 0, 0  # Services for Service Matrix
            vlan_config = self.vlan_names(api_call, device_detail)
            vlan_names = {}
            for vlan in vlan_config:
                vlan_names[vlan[0]] = vlan[1].lower()
            for switch in device_detail:
                for port in device_detail[switch]['ports']:
                    if port['operationalStatus'] == 'UP':
                        up += 1
                    elif port['operationalStatus'] == 'DOWN':
                        down += 1
                    try:
                        if str(port['accessVlan']) in vlan_names.keys():
                            if 'ist_labs' in vlan_names[str(port['accessVlan'])] or 'labs' in vlan_names[str(port['accessVlan'])]:
                                lc += 1
                            if 'ancillary_debit' in vlan_names[str(port['accessVlan'])]:
                                pos += 1
                            if 'onecard_pos' in vlan_names[str(port['accessVlan'])] or 'pos' in vlan_names[str(port['accessVlan'])]:
                                pos += 1
                            if 'ancillary_parking' in vlan_names[str(port['accessVlan'])] or 'parking' in vlan_names[str(port['accessVlan'])]:
                                parking += 1
                            if 'su_sutv' in vlan_names[str(port['accessVlan'])] or 'sutv' in vlan_names[str(port['accessVlan'])]:
                                sutv += 1
                            if 'ist_kramer' in vlan_names[str(port['accessVlan'])] or 'kramer' in vlan_names[str(port['accessVlan'])]:
                                kramer += 1
                    except Exception as err:
                        continue
            cdp_uplink = []
            cdp = api_call.cdp_neighbours(curr_id)  # API calls for CDP Neighbors
            for cdp_curr in cdp:
                if 'AIR' in cdp_curr['neighborDevicePlatformType']:  # Count APs
                    ap += 1
                if 'Cisco IP Phone' in cdp_curr['neighborDevicePlatformType']:  # Count IP Phones
                    phone += 1
                if 'corenet' in cdp_curr['neighborDeviceName'] or 'edgenet' in cdp_curr['neighborDeviceName']:  # Populates uplinks
                    if cdp_curr['neighborDeviceName'] not in cdp_uplink:
                        cdp_uplink.append(cdp_curr['neighborDeviceName'])
            if any('-ef-' in s for s in cdp_uplink):
                core = 'BA'
            elif any('-ba-' in s for s in cdp_uplink):
                core = 'BA'
            elif any('-ds-' in s for s in cdp_uplink):
                core = 'DS'
            elif any('edgenet' in s for s in cdp_uplink):
                core = 'CHAIN'
            else:
                core = 'unknown'
            print(device_detail[switch]['dev_name'] + ' complete.')
            self.csv_printer([device_detail[switch]['dev_name'], ', '.join([device_detail[switch]['dev_name'][:3]]),\
                              device_detail[switch]['ip_address'], device_detail[switch]['dev_type'],\
                              ', '.join(self.stack_models(device_detail)), len(device_detail.keys()),\
                              ', '.join(self.serial_numbers(device_detail)), device_detail[switch]['reachability'], ap, phone, lc,\
                              pos, parking, sutv, kramer, up, down, (up + down),\
                              str(round(((up / (up + down)) * 100))) + '%', cdp_uplink, core], args.csv, logger)

    def vlanmap(self, args, config, logger):  # Version 0.8 - still messy
        vlan_total = []  # Global list for vlan counts
        op = {}  # Global dictionary for operational status
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        self.no_results(dev_id_list)  # Exit if 0 results
        self.csv_printer(['Device Name', 'VLAN ID', 'VLAN Name', 'Count', 'Connected'], args.csv, logger)
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)
            time.sleep(1)
            vlan_counts = {}  # Vlan counts for curr_id
            op_status = {}  # operational status for curr_id
            device_detail = self.device_dictionary(inventory_dto)
            self.verbose_printer('### {} ###'.format(device_detail['Switch 1']['dev_name']), args.verbose, logger)
            self.sw_list.append(device_detail['Switch 1']['dev_name'])
            vlan_ids = self.vlan_names(api_call, device_detail)
            for switch in device_detail.keys():
                for port in device_detail[switch]['ports']:
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
            if 'VLAN1' in op_status.keys():
                ids['1'] = 'VLAN 1'

            for n in vlan_counts.keys():
                if n in ids.keys():
                    self.verbose_printer('VLAN {}, {}, {}'.format(n, ids[n], vlan_counts[n]), args.verbose, logger)
                    self.csv_printer(
                        [device_detail['Switch 1']['dev_name'], n, ids[n], vlan_counts[n], op_status['VLAN' + str(n)]],
                        args.csv, logger)
                    vlan_total.append(['VLAN' + str(n), str(ids[n]), vlan_counts[n]])
            if len(vlan_counts) < 1:
                print(str(device_detail['Switch 1']['dev_name']) + ' failed.')
                self.sw_list.remove(device_detail['Switch 1']['dev_name'])
            else:
                print(str(device_detail['Switch 1']['dev_name']) + ' complete')
        print('------------------------------')
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
        print(self.sw_list)
        self.filename = (str(self.filename) + '-total')
        self.csv_printer(['VLAN ID', 'Name(s)', 'Connected', 'Configured'], args.csv, logger)
        for key, value in vlan_names.items():
            if key in final_count.keys():
                print(str(key) + str(value) + ': ' + str(op[key]) + ' CONNECTED out of ' + str(
                    final_count[key]) + ' CONFIGURED')
                self.csv_printer([key, value, op[key], final_count[key]], args.csv, logger)
