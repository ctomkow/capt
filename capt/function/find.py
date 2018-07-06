
# system imports
import socket
import json
import sys

# local imports
from connector.client import Client
from connector.access_point import AccessPoint
from json_parser import JsonParser


class Find:

    def __init__(self, args, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        if args.find == 'mac' and args.ap:
            self.find_ap(dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)
        elif args.find == 'mac' and args.phone:
            self.find_phone(dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)
        elif args.find == 'mac':
            self.find_client(dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)
        elif args.find == 'ip' and args.phone:
            self.find_phone(dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)
        elif args.find == 'ip' and args.ap:
            self.find_ap(dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)
        elif args.find == 'ip':
            self.find_client(dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)
        else:
            logger.critical('failed to execute function')
            sys.exit(1)

    def find_client(self, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)

        if addr_type == 'ipv4':
            dev_id = api_call.get_id_by_ip(dev_addr)
        elif addr_type == 'mac':
            dev_id = api_call.get_id_by_mac(dev_addr)
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

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
        if addr_type == 'mac':
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ipAddress', 'address']
            ip_addr = JsonParser.get_value(JsonParser, result, key_list, logger)
        elif addr_type == 'ipv4':
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
            mac_addr = JsonParser.get_value(JsonParser, result, key_list, logger)
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

        print("switch name :{}".format(neigh_name))
        print("switch ip   :{}".format(neigh_ip))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("vlan        :{};{}".format(vlan, vlan_name))
        if addr_type == 'mac':
            print("ip addr     :{}".format(ip_addr))
        elif addr_type == 'ipv4':
            print("mac addr    :{}".format(mac_addr))
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

    def find_ap(self, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        ap_api_call = AccessPoint(cpi_username, cpi_password, cpi_ipv4_address, logger)
        client_api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)

        if addr_type == 'ipv4':
            client_id = client_api_call.get_id_by_ip(dev_addr)
            ap_id = ap_api_call.get_id_by_ip(dev_addr)
        elif addr_type == 'mac':
            client_id = client_api_call.get_id_by_mac(dev_addr)
            ap_id = ap_api_call.get_id_by_mac(dev_addr)
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

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
        if addr_type == 'mac':
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'ipAddress']
            ip_addr = JsonParser.get_value(JsonParser, ap_result, key_list, logger)
        elif addr_type == 'ipv4':
            key_list = ['queryResponse', 'entity', 0, 'accessPointDetailsDTO', 'ethernetMac']
            mac_addr = JsonParser.get_value(JsonParser, ap_result, key_list, logger)
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

        print("switch name :{}".format(neigh_name))
        print("switch ip   :{}".format(neigh_ip))
        print("interface   :{}".format(interface))
        print("vlan        :{};{}".format(vlan, vlan_name))
        if addr_type == 'mac':
            print("ap ip addr  :{}".format(ip_addr))
        elif addr_type == 'ipv4':
            print("ap mac addr :{}".format(mac_addr))
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

    def find_phone(self, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)

        if addr_type == 'ipv4':
            dev_id = api_call.get_id_by_ip(dev_addr)
        elif addr_type == 'mac':
            dev_id = api_call.get_id_by_mac(dev_addr)
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

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
        if addr_type == 'mac':
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ipAddress', 'address']
            ip_addr = JsonParser.get_value(JsonParser, result, key_list, logger)
        elif addr_type == 'ipv4':
            key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
            mac_addr = JsonParser.get_value(JsonParser, result, key_list, logger)
        else:
            logger.critical('incorrect address type')
            sys.exit(1)

        print("switch name :{}".format(neigh_name))
        print("switch ip   :{}".format(neigh_ip))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("vlan        :{};{}".format(vlan, vlan_name))
        if addr_type == 'mac':
            print("ip addr     :{}".format(ip_addr))
        elif addr_type == 'ipv4':
            print("mac addr    :{}".format(mac_addr))
        else:
            logger.critical('incorrect address type')
            sys.exit(1)
