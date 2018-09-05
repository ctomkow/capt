
# system imports
import socket
import sys

# local imports
from connector.device import Device
from connector.client import Client
from connector.access_point import AccessPoint
from json_parser import JsonParser



class Find:

    def __init__(self):

        self.parse_json = JsonParser()


    def ip_client(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.id_by_ip(values_dict['address'])
        result = api_call.json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
        tmp = self.parse_json.value(result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp) # resolve fqdn to IP. Prime resolves IP if possible
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
        mac_addr = self.parse_json.value(result, key_list, logger)

        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        logger.info("interface   :{}".format(interface))
        logger.info("description :{}".format(description))
        logger.info("vlan        :{};{}".format(vlan, vlan_name))
        logger.info("mac addr    :{}".format(mac_addr))
        return neigh_name, neigh_ip, interface, description, vlan, vlan_name, mac_addr

    def ip_ap(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        ap_api_call = AccessPoint(cpi_username, cpi_password, cpi_ipv4_address, logger)
        client_api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        client_id = client_api_call.id_by_ip(values_dict['address'])
        ap_id = ap_api_call.id_by_ip(values_dict['address'])
        ap_result = ap_api_call.json_detailed(ap_id)
        client_result = client_api_call.json_detailed(client_id)

        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborName']
        neigh_name = self.parse_json.value(ap_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborIpAddress']
        tmp = self.parse_json.value(ap_result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible
        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborPort']
        interface = self.parse_json.value(ap_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = self.parse_json.value(client_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = self.parse_json.value(client_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'ethernetMac']
        mac_addr = self.parse_json.value(ap_result, key_list, logger)

        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        logger.info("interface   :{}".format(interface))
        logger.info("vlan        :{};{}".format(vlan, vlan_name))
        logger.info("ap mac addr :{}".format(mac_addr))
        return neigh_name, neigh_ip, interface, vlan, vlan_name, mac_addr

    def ip_phone(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.id_by_ip(values_dict['address'])
        result = api_call.json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
        tmp = self.parse_json.value(result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
        mac_addr = self.parse_json.value(result, key_list, logger)

        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        logger.info("interface   :{}".format(interface))
        logger.info("description :{}".format(description))
        logger.info("vlan        :{};{}".format(vlan, vlan_name))
        logger.info("mac addr    :{}".format(mac_addr))
        return neigh_name, neigh_ip, interface, description, vlan, vlan_name, mac_addr

    def mac_client(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.id_by_mac(values_dict['address'])
        result = api_call.json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
        tmp = self.parse_json.value(result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp) # resolve fqdn to IP. Prime resolves IP if possible
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ipAddress', 'address']
        ip_addr = self.parse_json.value(result, key_list, logger)

        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        logger.info("interface   :{}".format(interface))
        logger.info("description :{}".format(description))
        logger.info("vlan        :{};{}".format(vlan, vlan_name))
        logger.info("ip addr     :{}".format(ip_addr))
        return neigh_name, neigh_ip, interface, description, vlan, vlan_name, ip_addr

    def mac_ap(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        ap_api_call = AccessPoint(cpi_username, cpi_password, cpi_ipv4_address, logger)
        client_api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        client_id = client_api_call.id_by_mac(values_dict['address'])
        ap_id = ap_api_call.id_by_mac(values_dict['address'])
        ap_result = ap_api_call.json_detailed(ap_id)
        client_result = client_api_call.json_detailed(client_id)

        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborName']
        neigh_name = self.parse_json.value(ap_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborIpAddress']
        tmp = self.parse_json.value(ap_result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible
        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborPort']
        interface = self.parse_json.value(ap_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = self.parse_json.value(client_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = self.parse_json.value(client_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'ipAddress']
        ip_addr = self.parse_json.value(ap_result, key_list, logger)

        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        logger.info("interface   :{}".format(interface))
        logger.info("vlan        :{};{}".format(vlan, vlan_name))
        logger.info("ap ip addr :{}".format(ip_addr))
        return neigh_name, neigh_ip, interface, vlan, vlan_name, ip_addr

    def mac_phone(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.id_by_mac(values_dict['address'])
        result = api_call.json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
        tmp = self.parse_json.value(result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = self.parse_json.value(result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ipAddress', 'address']
        ip_addr = self.parse_json.value(result, key_list, logger)

        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        logger.info("interface   :{}".format(interface))
        logger.info("description :{}".format(description))
        logger.info("vlan        :{};{}".format(vlan, vlan_name))
        logger.info("ip addr    :{}".format(ip_addr))
        return neigh_name, neigh_ip, interface, description, vlan, vlan_name, ip_addr

    def desc(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address,sw_name, logger):
    # 400 critical error is thrown if description is not found
        api_call = Device(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id_list = api_call.ids_by_desc(values_dict['description'].strip(),sw_name)

        logger.info(" # of switches with Matching occurrences of \"{}\" found: {}  ".format(values_dict['description'], len(dev_id_list)))
        # exit out of loop if no matches
        if len(dev_id_list) < 1:
            sys.exit(1)
        for curr_id in dev_id_list:
            dev_result = api_call.json_basic(curr_id)  # Modify this to go through multiple
            result = api_call.json_detailed(curr_id)  # Modify this to go through multiple
            logger.info("------- Matching Switch #{}--------".format(dev_id_list.index(curr_id) + 1))

            key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'deviceName']
            neigh_name = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'ipAddress']
            tmp = self.parse_json.value(dev_result, key_list, logger)
            neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible

           ###########currently working out how to grab items that match values[description]_dict.

            dev_interfaces = result['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']
            dev_found_interfaces =[]
            for dev_int in dev_interfaces:
                if 'description' in dev_int:
                #currently not working with comma seperated values. Check if each value in
                #similar to device/ids_by_desc split and remove brackets. abstract function?
                    desc_list=values_dict['description'].split(",")

#                    if values_dict['description'] in dev_int['description']:
                    if all (x in dev_int['description'] for x in desc_list):
                        dev_found_interfaces.append(dev_int)
            ######
            logger.info("switch name :{}".format(neigh_name))
            logger.info("switch ip   :{}".format(neigh_ip))
            logger.info("---- found {} description match on switch ----".format(len(dev_found_interfaces)))
            for dev_int in dev_found_interfaces:
                logger.info("---- matching description #{} ----".format(dev_found_interfaces.index(dev_int) + 1))
                self.desc_printer(dev_int,"interface      :",'name',logger)
                self.desc_printer(dev_int,"description    :",'description',logger)
                self.desc_printer(dev_int,"vlan           :",'accessVlan',logger)
                self.desc_printer(dev_int,"mac address    :",'macAddress',logger)
                self.desc_printer(dev_int,"status         :",'operationalStatus',logger)
                self.desc_printer(dev_int,"port mode      :",'desiredVlanMode',logger)
                self.desc_printer(dev_int,"allowed vlans  :",'allowedVlanIds',logger)
                self.desc_printer(dev_int,"speed          :",'speed',logger)
                self.desc_printer(dev_int,"duplex         :",'duplexMode',logger)


        return dev_found_interfaces

    def desc_active(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):
        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id_list = api_call.ids_by_desc(values_dict['description'].strip())

        logger.info("Occurrences of \"{}\" found: {}  ".format(values_dict['description'], len(dev_id_list)))
        # exit out of loop if no matches
        if len(dev_id_list) < 1:
            sys.exit(1)
        for curr_id in dev_id_list:
            result = api_call.json_detailed(curr_id)  # Modify this to go through multiple
            logger.info("------- Occurrence #{}--------\n".format(dev_id_list.index(curr_id)+1))

            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
            neigh_name = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
            tmp = self.parse_json.value(result, key_list, logger)
            neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
            interface = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
            description = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
            vlan = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
            vlan_name = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
            mac_addr = self.parse_json.value(result, key_list, logger)

            logger.info("switch name :{}".format(neigh_name))
            logger.info("switch ip   :{}".format(neigh_ip))
            logger.info("interface   :{}".format(interface))
            logger.info("description :{}".format(description))
            logger.info("vlan        :{};{}".format(vlan, vlan_name))
            logger.info("mac addr    :{}".format(mac_addr))
        return neigh_name, neigh_ip, interface, description, vlan, vlan_name, mac_addr

    def core(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):
    # 400 critical error is thrown if description is not found
        api_call = Device(cpi_username, cpi_password, cpi_ipv4_address, logger)

        # check address to see if hostname or IP
        if "-" in values_dict['address']:
            dev_id = api_call.id_by_hostname(values_dict['address'].strip())
        else:
            dev_id = api_call.id_by_ip(values_dict['address'].strip())


        dev_result = api_call.json_basic(dev_id)
        result = api_call.json_detailed(dev_id)

        #create list of vlan interfaces (L3 & vlan database)
        dev_ip_interfaces = result['queryResponse']['entity'][0]['inventoryDetailsDTO']['ipInterfaces']['ipInterface']
        dev_vlan_interfaces = result['queryResponse']['entity'][0]['inventoryDetailsDTO']['vlanInterfaces']['vlanInterface']
        dev_modules = result['queryResponse']['entity'][0]['inventoryDetailsDTO']['modules']['module']

        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'deviceName']
        neigh_name = self.parse_json.value(dev_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'ipAddress']
        tmp = self.parse_json.value(dev_result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible

#####if looking for a port add logic here( search for '/')
        if "/" in  values_dict['search_crit']:
            dev_interfaces = result['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces']['ethernetInterface']
            dev_found_interfaces =[]
            for dev_int in dev_interfaces:
                #if values_dict['search_crit'] in dev_int['name']:
                if dev_int['name'].endswith(values_dict['search_crit']):
                    dev_found_interfaces.append(dev_int)
            ######
            logger.info("switch name :{}".format(neigh_name))
            logger.info("switch ip   :{}".format(neigh_ip))
            #dev_module is not working with BA switches
            #dev_module = self.list_parse_ends(values_dict['search_crit'], 'description', dev_modules, logger)
            #self.desc_printer(dev_module, "Transciever info   :", 'description', logger)
            #logger.info("---- found {} description match on switch ----".format(len(dev_found_interfaces)))
            for dev_int in dev_found_interfaces:
                self.desc_printer(dev_int,"Admin Status       :",'adminStatus',logger)
                self.desc_printer(dev_int,"Operational Status :",'operationalStatus',logger)
                self.desc_printer(dev_int,"Port               :",'name',logger)
                self.desc_printer(dev_int,"speed              :",'speed',logger)
                if 'description' in dev_int:
                    self.desc_printer(dev_int,"description        :",'description',logger)
                if 'desiredVlanMode' in dev_int:
                    if dev_int['desiredVlanMode'] == "ACCESS":
                        self.desc_printer(dev_int,"Switchport Mode     :",'desiredVlanMode',logger)
                        self.desc_printer(dev_int,"Access Vlan         :", 'accessVlan', logger)
                        self.vlan(str(dev_int['accessVlan']), dev_vlan_interfaces, dev_ip_interfaces, logger)
                    elif dev_int['desiredVlanMode'] == "TRUNK":
                        self.desc_printer(dev_int,"Switchport Mode     :",'desiredVlanMode',logger)
                        self.desc_printer(dev_int, "Allowed Vlans       :", 'allowedVlanIds', logger)
                elif 'desiredVlanMode' not in dev_int and dev_int['operationalStatus'] == 'UP':
                    logger.info("This is a routed interface -- future functionality")
                    #dev_vlan = self.vlan_parse(values_dict['search_crit'], dev_vlan_interfaces, dev_ip_interfaces,logger)

        else:
            #dev_vlan = self.vlan_parse(values_dict['search_crit'],dev_vlan_interfaces,dev_ip_interfaces,logger)
            self.vlan(values_dict['search_crit'],dev_vlan_interfaces,dev_ip_interfaces,logger)
            #


        return result

    def int(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, interface, logger):
        # 400 critical error is thrown if description is not found
        api_call = Device(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.id_by_ip(values_dict['address'].strip())
        dev_result = api_call.json_basic(dev_id)
        result = api_call.json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'deviceName']
        neigh_name = self.parse_json.value(dev_result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'ipAddress']
        tmp = self.parse_json.value(dev_result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible

        dev_interfaces = result['queryResponse']['entity'][0]['inventoryDetailsDTO']['ethernetInterfaces'][
            'ethernetInterface']
        found_match = []
        for dev_int in dev_interfaces:
            if dev_int['name'].endswith(interface):
                found_match = dev_int
        ######
        logger.info("switch name :{}".format(neigh_name))
        logger.info("switch ip   :{}".format(neigh_ip))
        self.desc_printer(found_match, "interface      :", 'name', logger)
        self.desc_printer(found_match, "description    :", 'description', logger)
        self.desc_printer(found_match, "vlan           :", 'accessVlan', logger)
        self.desc_printer(found_match, "voice vlan     :", 'voiceVlan', logger)
        self.desc_printer(found_match, "mac address    :", 'macAddress', logger)
        self.desc_printer(found_match, "status         :", 'operationalStatus', logger)
        self.desc_printer(found_match, "port mode      :", 'desiredVlanMode', logger)
        self.desc_printer(found_match, "allowed vlans  :", 'allowedVlanIds', logger)
        self.desc_printer(found_match, "speed          :", 'speed', logger)
        self.desc_printer(found_match, "duplex         :", 'duplexMode', logger)


        return dev_id,found_match


    def vlan (self,vlan_id,dev_vlan_interfaces,dev_ip_interfaces,logger):
        dev_vlan = self.list_parse_exact(int(vlan_id), 'vlanId', dev_vlan_interfaces, logger)
        dev_vlan = self.list_parse_exact(("Vlan" + vlan_id), 'name', dev_ip_interfaces, logger)
        ####Create a function to run through a list of dict [title:name]. then iterate through the
        #### list to print out the required things, so the 'if name in dev_int' is not required each time?
        self.desc_printer(dev_vlan, "Vlan ID            :", 'name', logger)
        self.desc_printer(dev_vlan, "Admin Status       :", 'adminStatus', logger)
        self.desc_printer(dev_vlan, "Operational Status :", 'operationalStatus', logger)
        self.desc_printer(dev_vlan, "ip address         :", 'ipAddress', logger)
        return
    def list_parse_exact(self,find_match,find_str, dev_result,logger):
        for dev_item in dev_result:
            if dev_item[find_str] == find_match:
                found_match = dev_item
        return found_match

    def list_parse_ends(self,find_match,find_str, dev_result,logger):
        for dev_item in dev_result:
            if dev_item[find_str].endswith(find_match):
                found_match = dev_item
        return found_match

    def vlan_parse(self, vlan_id, dev_vlan_interfaces, dev_ip_interfaces, logger):
        #iterate through vlan interfaces (relevant if no L3 IP)
        if "/" not in vlan_id:  # if this is not an interface (routed link) -- Not functional yet as not all routed interfaces show up
            for dev_vlan in dev_vlan_interfaces:
                if dev_vlan['vlanId'] == int(vlan_id):
                    found_vlan = dev_vlan
        # iterate through ip interfaces (will overwrite found_vlan if L3 IP)
        for dev_vlan in dev_ip_interfaces:
                if dev_vlan['name'].endswith(vlan_id):
                    found_vlan = dev_vlan

        return found_vlan


    def desc_printer(self, dev_int,log_str,key_val, logger):
        if key_val in dev_int:
            logger.info("{}{}".format(log_str,dev_int[key_val]))
        else:
            logger.info("{} N/A".format(log_str))
        return