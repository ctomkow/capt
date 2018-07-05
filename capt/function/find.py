
# system imports
import socket
import json

# local imports
from connector.client import Client
from connector.access_point import AccessPoint
from connector.switch import Switch
from json_parser import JsonParser


class Find:

    def find_client_ip(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.get_id_by_ip(dev_addr)
        result = api_call.get_json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = JsonParser.get_value(JsonParser, result, key_list, logger)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
        tmp = JsonParser.get_value(JsonParser, result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp) # resolve fqdn to IP. Prime resolves IP if possible

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
        mac_addr = JsonParser.get_value(JsonParser, result, key_list, logger)

        print("switch name :{}".format(neigh_name))
        print("switch ip   :{}".format(neigh_ip))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("vlan        :{};{}".format(vlan, vlan_name))
        print("mac addr    :{}".format(mac_addr))

    def find_client_mac(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        # address manipulation
        dev_addr = self.format_mac(self, dev_addr)

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.get_id_by_mac(dev_addr)
        result = api_call.get_json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = JsonParser.get_value(JsonParser, result, key_list, logger)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceIpAddress', 'address']
        tmp = JsonParser.get_value(JsonParser, result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp) # resolve fqdn to IP. Prime resolves IP if possible

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ipAddress', 'address']
        ip_addr = JsonParser.get_value(JsonParser, result, key_list, logger)

        print("switch name :{}".format(neigh_name))
        print("switch ip   :{}".format(neigh_ip))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("vlan        :{};{}".format(vlan, vlan_name))
        print("ip addr     :{}".format(ip_addr))

    def find_ap_mac(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        # address manipulation
        dev_addr = self.format_mac(self, dev_addr)
        ap_api_call = AccessPoint(cpi_username, cpi_password, cpi_ipv4_address, logger)
        client_api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)

        client_id = client_api_call.get_id_by_mac(dev_addr)
        ap_id = ap_api_call.get_id_by_mac(dev_addr)

        ap_result = ap_api_call.get_json_detailed(ap_id)
        client_result = client_api_call.get_json_detailed(client_id)

        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborName']
        neigh_name = JsonParser.get_value(JsonParser, ap_result, key_list, logger)

        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborIpAddress']
        tmp = JsonParser.get_value(JsonParser, ap_result, key_list, logger)
        neigh_ip = socket.gethostbyname(tmp) # resolve fqdn to IP. Prime resolves IP if possible

        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'cdpNeighbors', 'cdpNeighbor', 0, 'neighborPort']
        interface = JsonParser.get_value(JsonParser, ap_result, key_list, logger)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlan']
        vlan = JsonParser.get_value(JsonParser, client_result, key_list, logger)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'vlanName']
        vlan_name = JsonParser.get_value(JsonParser, client_result, key_list, logger)

        key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'ipAddress']
        ip_addr = JsonParser.get_value(JsonParser, ap_result, key_list, logger)

        print("switch name :{}".format(neigh_name))
        print("switch ip   :{}".format(neigh_ip))
        print("interface   :{}".format(interface))
        print("vlan        :{};{}".format(vlan, vlan_name))
        print("ap ip addr  :{}".format(ip_addr))

    def format_mac(self, address):

        tmp = address.replace(':', '') # remove all colons
        address = tmp.replace('-', '') # remove all dashes
        tmp = address.replace(' ', '') # remove all blanks
        address = tmp.replace('.', '') # remove all dots
        return ':'.join(a+b for a,b in zip(address[::2], address[1::2])) # insert colon every two chars


