# A container for reporting functions

from connector.switch import Switch
from json_parser import JsonParser
import time
import sys
import re
import csv
from datetime import datetime


class Reports:

    def __init__(self):

        self.parse_json = JsonParser()
        self.sw_list = []
        self.filename = str(sys.argv[2])+str(datetime.now().strftime("%d-%m-%Y_%H%M%S"))
        self.cdp_neighbors = []

    def device_dictionary(self, inventory_dto):
        device_detail = {}
        try:
            chassis = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['chassis']['chassis']
        except Exception as err:
            return
        ethernet_interfaces = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces'][
            'ethernetInterface']
        dev_type = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceType']
        dev_name = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
        stack = len(chassis)
        for switch in chassis:
            if 'Provisioned' in switch['description']:
                continue
            if stack == 1:
                switch['name'] = 'Switch 1'
            if 'Switch' not in switch['name']:
                switch['name'] = 'Switch ' + str(switch['name'])
            device_detail[switch['name']] = {}
            device_detail[switch['name']]['serial_number'] = switch['serialNr']
            device_detail[switch['name']]['stack_model'] = switch['modelNr']
            device_detail[switch['name']]['dev_type'] = \
            inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceType']
            device_detail[switch['name']]['dev_name'] = \
            inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['deviceName']
            device_detail[switch['name']]['ip_address'] = \
            inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['ipAddress']
            device_detail[switch['name']]['reachability'] = \
            inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['reachability']
            device_detail[switch['name']]['stack_size'] = len(chassis)
            device_detail[switch['name']]['ports'] = []
            device_detail[switch['name']]['stack_id'] = switch['name']
            try:
                device_detail[switch['name']]['sw_version'] = inventory_dto['queryResponse']['entity'][0]['inventoryDetailsDTO']['summary']['softwareVersion']
            except Exception as err:
                device_detail[switch['name']]['sw_version'] = "Prime Error"
                continue
        for switch in device_detail:
            ignore = ['Te', '/1/', '49', '50', '51', '52', '1/1', '1/2', '1/3', '1/4', '0/0', 'Port-channel',
                      'FastEthernet1']
            if '24' in dev_type:
                ignore.extend(('25', '26', '27', '28'))
            if '3560-' in dev_type or '3560C-' in dev_type or '3560V' in dev_type or '2960-' in dev_type or '2960C-' in dev_type or '2950' in dev_type:
                ignore.extend(('GigabitEthernet0/1', 'GigabitEthernet0/2', 'GigabitEthernet0/3', 'GigabitEthernet0/4'))
            if '3560CG-8P' in dev_type:
                ignore.extend(('GigabitEthernet0/9', 'GigabitEthernet0/10'))
            if '12' in device_detail[switch]['stack_model']:
                ignore.extend(('13', '14', '15', '16'))
            while stack != 0:
                for port in ethernet_interfaces:
                    if len(chassis) > 1:
                        if ('Ethernet' + str(stack)) in port['name']:
                            if not any(x in port['name'] for x in ignore):
                                try:
                                    device_detail['Switch ' + str(stack)]['ports'].append(port)
                                except Exception as err:
                                    continue
                    else:
                        if not any(x in port['name'] for x in ignore):
                            if port['name'] != 'FastEthernet0':
                                if 'Ethernet2' not in port['name']:
                                    device_detail['Switch ' + str(stack)]['ports'].append(port)
                stack -= 1
        temp = []
        if 'Cisco Catalyst 29xx Stack-able Ethernet Switch' in dev_type:  # Fixes 2960Xs having extra ports when part of a stack
            for switch in device_detail:
                if device_detail[switch]['stack_model'] == 'WS-C2960X-24PS-L':
                    for port in device_detail[switch]['ports']:
                        if '0/25' in port['name'] or '0/26' in port['name'] or '0/27' in port['name'] or '0/28' in port['name']:
                            continue
                        else:
                            temp.append(port)
                    device_detail[switch]['ports'] = temp

        return device_detail

    def vlan_dict(self, api_call, device_detail):
        access_error = 'FALSE'
        find_config = api_call.find_config_archive_id(
            device_detail['Switch 1']['dev_name'])  # API calls for config archive
        config_id = api_call.config_archive_by_id(find_config)  # API calls for config archive
        time.sleep(0.15)  # Prevents too many API calls too fast
        config_archive = api_call.config_archive_content(config_id)  # API calls for config archive
        vlan_config = re.findall(r'(?:vlan\s)(\d{1,4})(?:\\n\sname\s)(.*?)(?:\\n\!)',
                                 str(config_archive))  # Find VLAN names in config
        interface_vlan = re.findall(r'(?:interface\s)(Vlan\d{1,4})(?:.*\n){1,3}(?:\sip\saddress\s)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',str(config_archive))
        for switch in device_detail:
            device_detail[switch]['VLANS'] = {}
            for port in device_detail[switch]['ports']:
                try:
                    if 'VLAN ' + str(port['accessVlan']) not in device_detail[switch]['VLANS'].keys():
                        device_detail[switch]['VLANS']['VLAN ' + str(port['accessVlan'])] = {'Name': 'None', 'UP': 0,
                                                                                             'DOWN': 0}
                    if port['operationalStatus'] == 'UP':
                        device_detail[switch]['VLANS']['VLAN ' + str(port['accessVlan'])]['UP'] += 1
                    elif port['operationalStatus'] == 'DOWN':
                        device_detail[switch]['VLANS']['VLAN ' + str(port['accessVlan'])]['DOWN'] += 1
                except Exception as err:
                    access_error = 'TRUE'
                    continue
        if access_error == 'FALSE':
            for vlan in vlan_config:
                for switch in device_detail:
                    for id in device_detail[switch]['VLANS']:
                        if str(vlan[0]) in id:
                            device_detail[switch]['VLANS'][id]['Name'] = vlan[1].lower()
        return device_detail, access_error

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
        vlan_config = re.findall(r'(?:vlan\s)(\d{1,4})(?:\\n\sname\s)(.*?)(?:\\n\!)',
                                 str(config_archive))  # Find VLAN names in config
        interface_vlan = re.findall(r'(?:interface\s)(Vlan\d{1,4})(?:\\n\sip\saddress\s)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            str(config_archive))
        return vlan_config, interface_vlan

    def verbose_printer(self, print_string, flag, logger):
        if flag:
            logger.info(print_string)

    def csv_printer(self, csv_string, flag, logger):
        if flag:
            outputFile = open(str(self.filename) + '.csv', 'a', newline='')
            outputWriter = csv.writer(outputFile)
            outputWriter.writerow(csv_string)
            outputFile.close()

    def port_count(self, args, config, logger):  # Version 1.0 - works
        ports_up, ports_down = 0, 0  # Global ports Up / Down for all devices being reported on
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(
            args.building_filter)  # API call to get list of devices to be reported on
        self.no_results(dev_id_list)  # Exit if 0 results
        self.csv_printer(
            ['Device Name', 'Building', 'IP Address', 'Serial Number', 'Device Model', 'Stack Size', 'Connected',
             'Notconnect', 'Total', '% Used', 'Reachability'], args.csv, logger)
        for curr_id in dev_id_list:
            time.sleep(0.35)  # Prevents too many API calls too fast
            inventory_dto = api_call.json_detailed(curr_id)  # API Call for current device ID's inventory details
            device_detail = self.device_dictionary(inventory_dto)  # Populates dictionary with device details
            self.sw_list.append(device_detail['Switch 1']['dev_name'])  # This list will contain all devices reported on
            for switch in device_detail.keys():
                up, down = 0, 0  # Ports Up / Down for current device ID
                for port in device_detail[switch]['ports']:
                    if port['operationalStatus'] == 'UP':
                        up += 1
                    elif port['operationalStatus'] == 'DOWN':
                        down += 1
                if up != 0 and down != 0:
                    utilization = str(round(((up / (up + down)) * 100))) + '%'
                else:
                    utilization = "unknown"
                ports_up += up  # Appends current ID values to global Up count
                ports_down += down  # Appends current ID values to global Down count
                self.verbose_printer(
                    "{}({}): {} Connected | {} Notconnect | {} Total".format(device_detail['Switch 1']['dev_name'],
                                                                             device_detail[switch]['serial_number'], up,
                                                                             down, (up + down)), args.verbose, logger)
                self.csv_printer([device_detail[switch]['dev_name'], ', '.join([device_detail[switch]['dev_name'][:3]]),
                                  device_detail[switch]['ip_address'], \
                                  device_detail[switch]['serial_number'], device_detail[switch]['stack_model'],
                                  len(device_detail.keys()), up, down, (up + down), \
                                  utilization, device_detail[switch]['reachability']], args.csv, logger)
        print(self.sw_list)
        print("{} Connected | {} Notconnect | {} Total".format(ports_up, ports_down, (ports_up + ports_down)))

    def service_matrix(self, args, config, logger):
        building_summary = {}
        error_list = []
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(
            args.building_filter)  # API call to get list of devices to be reported on
        self.no_results(dev_id_list)  # Exit if 0 results
        self.csv_printer(['Device Name', 'Building', 'IP Address', 'Device Type', 'Device Model(s)', 'Stack',
                          'Serial Number(s)', 'Reachability', 'UWS', 'VoIP', 'LC', 'PoS', 'Parking', 'SUTV',
                          'Wireless Display', 'Connected', 'Notconnect', 'Port Count', '% Used', 'Uplink', 'CDP Neighbors', 'SW Ver', 'Management VLAN'], args.csv,
                         logger)
        for curr_id in dev_id_list:
            try:
                inventory_dto = api_call.json_detailed(curr_id)  # API Call for current device ID's inventory details
                time.sleep(0.15)
                device_detail = self.device_dictionary(inventory_dto)  # Populates dictionary wil device details
                # try:
                #     if 'ADM353' in device_detail['Switch 1']['dev_name']:
                #         continue
                #     if 'VAN-RB-' in device_detail['Switch 1']['dev_name']:
                #         continue
                # except Exception as err:
                #     continue
                self.sw_list.append(device_detail['Switch 1']['dev_name'])  # This list will contain all devices reported on
                up, down, ap, phone, lc, pos, parking, sutv, kramer = 0, 0, 0, 0, 0, 0, 0, 0, 0  # Services for Service Matrix
                print(device_detail['Switch 1']['dev_name'] + ' started.')
                time.sleep(0.15)
                vlan_config, int_vlan = self.vlan_names(api_call, device_detail)
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
                                if 'onecard_pos' in vlan_names[str(port['accessVlan'])] or 'pos' in vlan_names[
                                    str(port['accessVlan'])]:
                                    pos += 1
                                if 'ancillary_parking' in vlan_names[str(port['accessVlan'])] or 'parking' in vlan_names[
                                    str(port['accessVlan'])]:
                                    parking += 1
                                if 'su_sutv' in vlan_names[str(port['accessVlan'])] or 'sutv' in vlan_names[
                                    str(port['accessVlan'])]:
                                    sutv += 1
                                if 'ist_kramer' in vlan_names[str(port['accessVlan'])] or 'kramer' in vlan_names[
                                    str(port['accessVlan'])]:
                                    kramer += 1
                        except Exception as err:
                            continue
                cdp_uplink = []
                cdp = api_call.cdp_neighbours(curr_id)  # API calls for CDP Neighbors
                for cdp_curr in cdp:
                    try:
                        if 'AIR' in cdp_curr['neighborDevicePlatformType'] or 'AXI' in cdp_curr['neighborDevicePlatformType']:  # Count APs
                            ap += 1
                        if 'Cisco IP Phone' in cdp_curr['neighborDevicePlatformType']:  # Count IP Phones
                            phone += 1
                        if 'corenet' in cdp_curr['neighborDeviceName'] or 'edgenet' in cdp_curr['neighborDeviceName']:  # Populates uplinks
                            if cdp_curr['neighborDeviceName'] not in cdp_uplink:
                                cdp_uplink.append(cdp_curr['neighborDeviceName'] +': '+cdp_curr['farEndInterface'])
                    except Exception as err:
                        continue
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
            except Exception as err:
                error_list.append(curr_id)
                continue
            try:
                self.csv_printer([device_detail[switch]['dev_name'], ', '.join([device_detail[switch]['dev_name'][:3]]), \
                                  device_detail[switch]['ip_address'], device_detail[switch]['dev_type'], \
                                  ', '.join(self.stack_models(device_detail)), len(device_detail.keys()), \
                                  ', '.join(self.serial_numbers(device_detail)), device_detail[switch]['reachability'],
                                  ap, phone, lc, \
                                  pos, parking, sutv, kramer, up, down, (up + down), \
                                  str(round(((up / (up + down)) * 100))) + '%', core, cdp_uplink, device_detail[switch]['sw_version'], int_vlan], args.csv, logger)
            except Exception as err:
                self.csv_printer([device_detail[switch]['dev_name'], ', '.join([device_detail[switch]['dev_name'][:3]]), \
                                  device_detail[switch]['ip_address'], device_detail[switch]['dev_type'], \
                                  ', '.join(self.stack_models(device_detail)), len(device_detail.keys()), \
                                  ', '.join(self.serial_numbers(device_detail)), device_detail[switch]['reachability'],
                                  ap, phone, lc, \
                                  pos, parking, sutv, kramer, up, down, (up + down), \
                                  '?', core, cdp_uplink, device_detail[switch]['sw_version'], int_vlan], args.csv, logger)
            building_code = device_detail[switch]['dev_name'][:3].upper()
            if building_code not in building_summary.keys():
                building_summary[building_code] = {'Up': 0, 'Down': 0}
                building_summary[building_code]['Up'] += up
                building_summary[building_code]['Down'] += down
            else:
                building_summary[building_code]['Up'] += up
                building_summary[building_code]['Down'] += down
        print('Job Complete.')
        print(error_list)
        #print(building_summary)
        #for i in building_summary:
        #   print(i + ',' + str(building_summary[i]['Up']) + ',' + str(building_summary[i]['Down']))

    def vlanmap_edge(self, args, config, logger):  # Version 0.8 - still messy
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        self.no_results(dev_id_list)  # Exit if 0 results
        self.csv_printer(['Device List', 'VLAN ID', 'VLAN Name', 'Connected', 'Configured'], args.csv, logger)
        vlan_total = {}
        t_up, t_down = 0, 0
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)
            time.sleep(1)
            device_detail = self.device_dictionary(inventory_dto)
            device_detail, access_error = self.vlan_dict(api_call, device_detail)
            self.sw_list.append(device_detail['Switch 1']['dev_name'])
            if len(device_detail['Switch 1']['VLANS']) == 0:
                print('{} VLAN KEYERROR'.format(device_detail['Switch 1']['dev_name']))
                continue
            vlan_map = {}
            up, down = 0, 0
            for switch in device_detail:
                for vlan in device_detail[switch]['VLANS']:
                    if str(device_detail[switch]['VLANS'][vlan]) not in vlan_map.keys():
                        vlan_map[vlan] = {'UP': up, 'DOWN': down}
                    vlan_map[vlan]['UP'] += device_detail[switch]['VLANS'][vlan]['UP']
                    vlan_map[vlan]['DOWN'] += device_detail[switch]['VLANS'][vlan]['DOWN']
                    vlan_map[vlan]['Name'] = device_detail[switch]['VLANS'][vlan]['Name']
            self.verbose_printer(vlan_map, args.verbose, logger)
            for vlan in vlan_map:
                if vlan not in vlan_total.keys():
                    vlan_total[vlan] = {'Name': [], 'UP': t_up, 'DOWN': t_down}
                if vlan_map[vlan]['Name'] not in vlan_total[vlan]['Name']:
                    vlan_total[vlan]['Name'].append(vlan_map[vlan]['Name'])
                vlan_total[vlan]['UP'] += vlan_map[vlan]['UP']
                vlan_total[vlan]['DOWN'] += vlan_map[vlan]['DOWN']
        print(self.sw_list)
        for vlan_id in vlan_total:
            print('{},{},CONNECTED:{},CONFIGURED:{}'.format(vlan_id, vlan_total[vlan_id]['Name'],
                                                            vlan_total[vlan_id]['UP'],
                                                            (vlan_total[vlan_id]['UP'] + vlan_total[vlan_id]['DOWN'])))
            self.csv_printer([self.sw_list, vlan_id, vlan_total[vlan_id]['Name'], vlan_total[vlan_id]['UP'],
                              (vlan_total[vlan_id]['UP'] + vlan_total[vlan_id]['DOWN'])], args.csv, logger)
        print('Job Complete.')

    def service_matrix_per_sn(self, args, config, logger):
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(
            args.building_filter)  # API call to get list of devices to be reported on
        self.no_results(dev_id_list)  # Exit if 0 results
        self.csv_printer(
            ['Device Name', 'Building', 'IP Address', 'Device Type', 'Device Model(s)', 'Stack Size', 'Stack_ID', \
             'Serial Number(s)', 'Reachability', 'VoIP', 'APs-UP', 'AP-Configured', 'LC-UP', 'LC-Configured', \
             'PoS-UP', 'PoS-Configured', 'Parking-UP', 'Parking-Configured', 'SUTV-UP', 'SUTV-Configured', \
             'WirelessDisplay-UP', 'WirelessDisplay-Configured', 'Connected', 'Notconnect', 'Port Count', \
             '% Used'], args.csv, logger)
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)  # API Call for current device ID's inventory details
            time.sleep(0.25)
            device_detail = self.device_dictionary(inventory_dto)  # Populates dictionary wil device details
            self.sw_list.append(device_detail['Switch 1']['dev_name'])  # This list will contain all devices reported on
            device_detail, access_error = self.vlan_dict(api_call, device_detail)
            cdp = api_call.cdp_neighbours(curr_id)  # API calls for CDP Neighbors
            for switch in device_detail:
                up, down, uws, ap, phone, lc, pos, parking, sutv, kramer = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  # Services for Service Matrix
                c_ap, c_lc, c_pos, c_parking, c_sutv, c_kramer = 0, 0, 0, 0, 0, 0
                if access_error == 'TRUE':
                    ap, lc, pos, parking, sutv, kramer = 'X', 'X', 'X', 'X', 'X', 'X'  # Services for Service Matrix
                    c_ap, c_lc, c_pos, c_parking, c_sutv, c_kramer = 'X', 'X', 'X', 'X', 'X', 'X'
                for port in device_detail[switch]['ports']:
                    if port['operationalStatus'] == 'UP':
                        up += 1
                    elif port['operationalStatus'] == 'DOWN':
                        down += 1
                try:
                    if up != 0 or down != 0:
                        utilization = str(round(((up / (up + down)) * 100))) + '%'
                    else:
                        utilization = "unknown"
                except Exception as err:
                    utilization = "unknown"
                if len(device_detail[switch]['VLANS']) > 0:
                    for vlan in device_detail[switch]['VLANS']:
                        if '-ap' in device_detail[switch]['VLANS'][vlan]['Name'] or 'uws' in \
                                device_detail[switch]['VLANS'][vlan]['Name'] or 'wireless' in \
                                device_detail[switch]['VLANS'][vlan]['Name']:
                            ap += device_detail[switch]['VLANS'][vlan]['UP']
                            c_ap += (device_detail[switch]['VLANS'][vlan]['UP'] + device_detail[switch]['VLANS'][vlan][
                                'DOWN'])
                        if 'ist_labs' in device_detail[switch]['VLANS'][vlan]['Name'] or 'labs' in \
                                device_detail[switch]['VLANS'][vlan]['Name']:
                            lc += device_detail[switch]['VLANS'][vlan]['UP']
                            c_lc += (device_detail[switch]['VLANS'][vlan]['UP'] + device_detail[switch]['VLANS'][vlan][
                                'DOWN'])
                        if 'debit' in device_detail[switch]['VLANS'][vlan]['Name'] or 'credit' in \
                                device_detail[switch]['VLANS'][vlan]['Name']:
                            pos += device_detail[switch]['VLANS'][vlan]['UP']
                            c_pos += (device_detail[switch]['VLANS'][vlan]['UP'] + device_detail[switch]['VLANS'][vlan][
                                'DOWN'])
                        if 'onecard' in device_detail[switch]['VLANS'][vlan]['Name'] or 'pos' in \
                                device_detail[switch]['VLANS'][vlan]['Name']:
                            pos += device_detail[switch]['VLANS'][vlan]['UP']
                            c_pos += (device_detail[switch]['VLANS'][vlan]['UP'] + device_detail[switch]['VLANS'][vlan][
                                'DOWN'])
                        if 'parking' in device_detail[switch]['VLANS'][vlan]['Name']:
                            parking += device_detail[switch]['VLANS'][vlan]['UP']
                            c_parking += (device_detail[switch]['VLANS'][vlan]['UP'] +
                                          device_detail[switch]['VLANS'][vlan]['DOWN'])
                        if 'sutv' in device_detail[switch]['VLANS'][vlan]['Name']:
                            sutv += device_detail[switch]['VLANS'][vlan]['UP']
                            c_sutv += (device_detail[switch]['VLANS'][vlan]['UP'] +
                                       device_detail[switch]['VLANS'][vlan]['DOWN'])
                        if 'kramer' in device_detail[switch]['VLANS'][vlan]['Name']:
                            kramer += device_detail[switch]['VLANS'][vlan]['UP']
                            c_kramer += (device_detail[switch]['VLANS'][vlan]['UP'] +
                                         device_detail[switch]['VLANS'][vlan]['DOWN'])
                for c in cdp:
                    if 'Phone' in c['neighborDevicePlatformType']:
                        for port in device_detail[switch]['ports']:
                            if c['nearEndInterface'] in port['name']:
                                phone += 1
                print('{} {} complete.'.format(device_detail[switch]['dev_name'], device_detail[switch]['stack_id']))
                self.csv_printer([device_detail[switch]['dev_name'], ', '.join([device_detail[switch]['dev_name'][:3]]), \
                                  device_detail[switch]['ip_address'], device_detail[switch]['dev_type'], \
                                  device_detail[switch]['stack_model'], len(device_detail.keys()),
                                  device_detail[switch]['stack_id'], \
                                  device_detail[switch]['serial_number'], device_detail[switch]['reachability'], phone, \
                                  ap, c_ap, lc, c_lc, pos, c_pos, parking, c_parking, sutv, c_sutv, kramer, c_kramer, \
                                  up, down, (up + down), utilization], args.csv, logger)

    def vlanmap(self, args, config, logger):  # Version 0.8 - still messy
        ba_dict = {}
        api_call = Switch(config, logger)
        dev_id_list = api_call.ids_by_location(args.building_filter)
        self.no_results(dev_id_list)  # Exit if 0 results
        #temp
        anc = ['ASP-RB-4ZZ-01.edgenet.ualberta.ca', 'ECP-KIOSK-01.edgenet.ualberta.ca', 'ECV1-TR-01.edgenet.ualberta.ca', 'ECV2-TR-01.edgenet.ualberta.ca', 'ECV2-TR-02.edgenet.ualberta.ca', 'ECV3-TR-01.edgenet.ualberta.ca', 'ECV4-TR-01.edgenet.ualberta.ca', 'ECV7-TR-01.edgenet.ualberta.ca', 'ECV8-TR-01.edgenet.ualberta.ca', 'ECV9-TR-210-01.edgenet.ualberta.ca', 'ECV9-TR-247-01.edgenet.ualberta.ca', 'ECV9-TR-410-01.edgenet.ualberta.ca', 'ECV9-TR-447-01.edgenet.ualberta.ca', 'H33-TR-B01-01.edgenet.ualberta.ca', 'HUB-RB-9104-01.edgenet.ualberta.ca', 'HUB-RB-9209-01.edgenet.ualberta.ca', 'HUB-RB-RVSL-01.edgenet.ualberta.ca', 'INT-TR-120-01.edgenet.ualberta.ca', 'JCP-TR-GATE-01.edgenet.ualberta.ca', 'JCP-TR-KIOSK-01.edgenet.ualberta.ca', 'LIS-RB-1045-01.edgenet.ualberta.ca', 'LIS-RB-2045A-01.edgenet.ualberta.ca', 'LIS-TR-1026-01.edgenet.ualberta.ca', 'TCH-TR-208-01.edgenet.ualberta.ca', 'TCH-TR-258-01.edgenet.ualberta.ca', 'TCH-TR-408-01.edgenet.ualberta.ca', 'TCH-TR-458-01.edgenet.ualberta.ca', 'MAH-TR-025-01.edgenet.ualberta.ca', 'MAH-TR-1103-01.edgenet.ualberta.ca', 'MPL-RB-4ZZ-01.edgenet.ualberta.ca', 'PCH-TR-108-01.edgenet.ualberta.ca', 'PCH-TR-108-02.edgenet.ualberta.ca', 'PLH-RB-352-01.edgenet.ualberta.ca', 'PLH-TR-120a-01.edgenet.ualberta.ca', 'PLH-TR-164a-01.edgenet.ualberta.ca', 'PLH-TR-424-01.edgenet.ualberta.ca', 'SCP-TR-202-01.edgenet.ualberta.ca', 'SCP-TR-202-02.edgenet.ualberta.ca', 'SFH-TR-1056-01.edgenet.ualberta.ca', 'SFH-TR-1063B-01.edgenet.ualberta.ca', 'SFH-TR-1063B-02.edgenet.ualberta.ca', 'TMH-TR-112-01.edgenet.ualberta.ca', 'UTR-TR-111-01.edgenet.ualberta.ca', 'WCP-RB-287-01.edgenet.ualberta.ca', 'WCP-RB-287-02.edgenet.ualberta.ca', 'WCP-TR-207-01.edgenet.ualberta.ca']
        #anc = ['TCH']
        #temp
        for curr_id in dev_id_list:
            inventory_dto = api_call.json_detailed(curr_id)
            time.sleep(0.15)
            device_detail = self.device_dictionary(inventory_dto)
            try:
                #temp
                if any(x in device_detail['Switch 1']['dev_name'] for x in anc):
                    print('skipped')
                    continue
                #temp

                if 'ADM353' in device_detail['Switch 1']['dev_name']:
                    continue
                if 'VAN-RB-' in device_detail['Switch 1']['dev_name']:
                    continue
            except Exception as err:
                continue
            device_detail, access_error = self.vlan_dict(api_call, device_detail)
            core_switch, core_port, edge_nei = self.core_uplink(api_call, curr_id)
            #edge_nei.append(device_detail['Switch 1']['dev_name'])
            for core in core_switch:
                if core == '269GSB.corenet.ualberta.ca' or core == 'GSB-RM-269-01.corenet.ualberta.ca':
                    core = 'gsb-ef-175-1.corenet.ualberta.ca'
                if core not in ba_dict.keys():
                    ba_dict[core] = {}
                try:
                    for switch in device_detail:
                        for vlan in device_detail[switch]['VLANS']:
                            if vlan not in ba_dict[core].keys():
                                ba_dict[core][vlan] = {'Names': [], 'Connected': 0, 'Configured': 0, 'HSRP': core_switch, 'IP Subnet': 'No IP Address', 'Description': 'No Description', 'VRF' : 'No VRF', 'Edge Devices' : []}
                            if device_detail[switch]['VLANS'][vlan]['Name'] not in ba_dict[core][vlan]['Names']:
                                ba_dict[core][vlan]['Names'].append(device_detail[switch]['VLANS'][vlan]['Name'])
                            ba_dict[core][vlan]['Connected'] += device_detail[switch]['VLANS'][vlan]['UP']
                            ba_dict[core][vlan]['Configured'] += (device_detail[switch]['VLANS'][vlan]['UP'] + device_detail[switch]['VLANS'][vlan]['DOWN'])
                            for hsrp in core_switch:
                                if hsrp != core:
                                    ba_dict[core][vlan]['HSRP'] = hsrp
                            ba_dict[core][vlan]['Core Interface'] = core_port
                            #ba_dict[core][vlan]['Edge Switches'] = edge_nei
                            if device_detail['Switch 1']['dev_name'] not in ba_dict[core][vlan]['Edge Devices']:
                                ba_dict[core][vlan]['Edge Devices'].append(device_detail['Switch 1']['dev_name'])
                except Exception as err:
                    continue
            print (device_detail['Switch 1']['dev_name'] + ' complete.')
        ba_dict = self.interface_vlan(api_call, ba_dict)
        self.csv_printer(['Core Switch', 'VLAN ID', 'IP Subnet', 'Interface Description', 'VRF', 'Core_port(s)', 'VLAN Name(s)', 'Connected', 'Configured', 'HSRP', 'Edge Switches'], args.csv, logger)
        for ba in ba_dict.keys():
            for vlan_id in ba_dict[ba].keys():
                self.csv_printer([ba, vlan_id, ba_dict[ba][vlan_id]['IP Subnet'], ba_dict[ba][vlan_id]['Description'], ba_dict[ba][vlan_id]['VRF'], ba_dict[ba][vlan_id]['Core Interface'], ba_dict[ba][vlan_id]['Names'], ba_dict[ba][vlan_id]['Connected'], ba_dict[ba][vlan_id]['Configured'], ba_dict[ba][vlan_id]['HSRP'], ba_dict[ba][vlan_id]['Edge Devices']], args.csv, logger)

    def core_uplink(self, api_call, curr_id):
        cdp_nei = []
        edge_nei = []
        core = False
        core_port = []
        cdp = api_call.cdp_neighbours(curr_id)
        time.sleep(0.15)  # API calls for CDP Neighbors
        for cdp_curr in cdp:
            if 'corenet' in cdp_curr['neighborDeviceName']:
                if cdp_curr['neighborDeviceName'] not in cdp_nei:
                    cdp_nei.append(cdp_curr['neighborDeviceName'])
                if cdp_curr['farEndInterface'] not in core_port:
                    core_port.append(cdp_curr['farEndInterface'])
            elif 'edgenet' in cdp_curr['neighborDeviceName']:
                edge_nei.append(cdp_curr['neighborDeviceName'])
        if len(cdp_nei) == 0:
            for switch in edge_nei:
                if core == True:
                    break
                next_hops = api_call.ids_by_location(switch)
                for hop in next_hops:
                    if core == True:
                        break
                    cdp = api_call.cdp_neighbours(hop)
                    time.sleep(0.15)
                    for cdp_curr in cdp:
                        if 'corenet' in cdp_curr['neighborDeviceName']:
                            if cdp_curr['neighborDeviceName'] not in cdp_nei:
                                cdp_nei.append(cdp_curr['neighborDeviceName'])
                            if cdp_curr['farEndInterface'] not in core_port:
                                core_port.append(cdp_curr['farEndInterface'])
                        elif 'edgenet' in cdp_curr['neighborDeviceName']:
                            if cdp_curr['neighborDeviceName'] not in edge_nei:
                                edge_nei.append(cdp_curr['neighborDeviceName'])
                    if len(cdp_nei) != 0:
                        core = True
        return cdp_nei, core_port, edge_nei

    def interface_vlan (self, api_call, ba_dict):
        for ba in ba_dict:
            find_config = api_call.find_config_archive_id(ba)  # API calls for config archive
            config_id = api_call.config_archive_by_id(find_config)  # API calls for config archive
            time.sleep(0.15)  # Prevents too many API calls too fast
            config = api_call.config_archive_content(config_id)  # API calls for config archive
            config_archive = (str(config).replace('\\n', '\n'))
            subnet_desc = re.findall(r'(?:interface\s)(Vlan\d{1,4})(?:\n\sdescription\s)(.*?)\n', str(config_archive))
            vrf_info = re.findall(r'(?:interface\s)(Vlan\d{1,4})(?:.*\n){1,3}(?:\svrf\sforwarding)(.*?)\n', str(config_archive))
            ip_subnet = re.findall(r'(?:interface\s)(Vlan\d{1,4})(?:.*\n){1,3}(?:\sip\saddress\s)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',str(config_archive))
            for desc in subnet_desc:
                temp = (re.sub(r'Vlan', r'VLAN ', desc[0]), desc[1])
                if temp[0] in ba_dict[ba].keys():
                    ba_dict[ba][temp[0]]['Description'] = temp[1]
            for vrf in vrf_info:
                temp = (re.sub(r'Vlan', r'VLAN ', vrf[0]), vrf[1])
                if temp[0] in ba_dict[ba].keys():
                    ba_dict[ba][temp[0]]['VRF'] = temp[1]
            for ip in ip_subnet:
                temp = (re.sub(r'Vlan', r'VLAN ', ip[0]), ip[1])
                if temp[0] in ba_dict[ba].keys():
                    ba_dict[ba][temp[0]]['IP Subnet'] = temp[1]
        return ba_dict


