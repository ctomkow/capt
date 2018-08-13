
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

    def desc(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Device(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id_list = api_call.ids_by_desc(values_dict['description'].strip())

        logger.info("Occurrences of \"{}\" found: {}  ".format(values_dict['description'], len(dev_id_list)))
        # exit out of loop if no matches
        if len(dev_id_list) < 1:
            sys.exit(1)
        for curr_id in dev_id_list:
            dev_result = api_call.json_basic(curr_id)  # Modify this to go through multiple
            result = api_call.json_detailed(curr_id)  # Modify this to go through multiple
            logger.info("------- Occurrence #{}--------\n".format(dev_id_list.index(curr_id) + 1))

            key_list = ['queryResponse', 'entity', 0, 'devicesDTO', 'deviceName']
            neigh_name = self.parse_json.value(dev_result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'InventoryDetailsDTO', 'deviceIpAddress', 'address']
            tmp = self.parse_json.value(result, key_list, logger)
            neigh_ip = socket.gethostbyname(tmp)  # resolve fqdn to IP. Prime resolves IP if possible
            key_list = ['queryResponse', 'entity', 0, 'InventoryDetailsDTO', 'clientInterface']
            interface = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'InventoryDetailsDTO', 'ifDescr']
            description = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'InventoryDetailsDTO', 'vlan']
            vlan = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'InventoryDetailsDTO', 'vlanName']
            vlan_name = self.parse_json.value(result, key_list, logger)
            key_list = ['queryResponse', 'entity', 0, 'InventoryDetailsDTO', 'macAddress']
            mac_addr = self.parse_json.value(result, key_list, logger)

            logger.info("switch name :{}".format(neigh_name))
            logger.info("switch ip   :{}".format(neigh_ip))
            logger.info("interface   :{}".format(interface))
            logger.info("description :{}".format(description))
            logger.info("vlan        :{};{}".format(vlan, vlan_name))
            logger.info("mac addr    :{}".format(mac_addr))
        return neigh_name, neigh_ip, interface, description, vlan, vlan_name, mac_addr

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