#!/usr/bin/env python3

# system imports
import json

# local imports
try:
    from .device_connector import DeviceConnector
    from .json_parser import JsonParser
except (ImportError, SystemError):
    from device_connector import DeviceConnector
    from json_parser import JsonParser


class Device:


    def find_dev_ip(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = DeviceConnector(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.get_id_by_ip(dev_addr, logger)
        result = api_call.get_json_details(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = JsonParser.get_value(JsonParser, result, key_list, logger)
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

        print("switch      :{}".format(neigh_name))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("vlan        :{};{}".format(vlan, vlan_name))
        print("mac addr    :{}".format(mac_addr))

    def find_dev_mac(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = DeviceConnector(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.get_id_by_mac(dev_addr, logger)
        result = api_call.get_json_details(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        neigh_name = JsonParser.get_value(JsonParser, result, key_list, logger)
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

        print("switch      :{}".format(neigh_name))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("vlan        :{};{}".format(vlan, vlan_name))
        print("ip addr     :{}".format(ip_addr))
