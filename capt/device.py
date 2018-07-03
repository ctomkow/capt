#!/usr/bin/env python3

# system imports
import ipaddress
import json

# local imports
try:
    from .connector import Connector
except (ImportError, SystemError):
    from connector import Connector


class Device:


    def __init__(self, dev_addr, cpi_username, cpi_password, cpi_ipv4_address, logger):

        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address, logger)
        self.device(api_call, dev_addr, logger)

    def device(self, api_call, dev_addr, logger):

        result = self.get_device_info(api_call, dev_addr, logger).json()
        print("Switch      :{}".format(result['queryResponse']['entity'][0]['clientDetailsDTO']['deviceName']))
        print("Interface   :{}".format(result['queryResponse']['entity'][0]['clientDetailsDTO']['clientInterface']))
        print("Description :{}".format(result['queryResponse']['entity'][0]['clientDetailsDTO']['ifDescr']))
        print("mac addr    :{}".format(result['queryResponse']['entity'][0]['clientDetailsDTO']['macAddress']))

    def get_device_info(self, api_call, dev_addr, logger):

        dev_id = api_call.get_dev_id(dev_addr)
        return api_call.get_dev_details(dev_id)
