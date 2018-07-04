#!/usr/bin/env python3

# system imports
import ipaddress
import json

# local imports
try:
    from .connector import Connector
    from .json_parser import JsonParser
except (ImportError, SystemError):
    from connector import Connector
    from json_parser import JsonParser


class Device:


    def __init__(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address, logger)
        self.device(api_call, dev_addr, logger)

    def device(self, api_call, dev_addr, logger):

        result = self.get_device_info(api_call, dev_addr, logger).json()

        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'deviceName']
        dev_name = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'clientInterface']
        interface = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'ifDescr']
        description = JsonParser.get_value(JsonParser, result, key_list, logger)
        key_list = ['queryResponse', 'entity', 0, 'clientDetailsDTO', 'macAddress']
        mac_addr = JsonParser.get_value(JsonParser, result, key_list, logger)

        print("switch      :{}".format(dev_name))
        print("interface   :{}".format(interface))
        print("description :{}".format(description))
        print("mac addr    :{}".format(mac_addr))

    def get_device_info(self, api_call, dev_addr, logger):

        dev_id = api_call.get_dev_id(dev_addr)
        return api_call.get_dev_details(dev_id)

