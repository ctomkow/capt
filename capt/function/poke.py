
# system imports
import socket
import sys

# local imports
from function.find import Find
from connector.switch import Switch


class Poke:

    def __init__(self):

        self.find = Find()

    def port(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):
        # Currently working with IP. Change this to be similar to find core where it parses?
        dev_id, found_int, dev_ip = \
            self.find.int(values_dict, cpi_username, cpi_password, cpi_ipv4_address, values_dict['interface'],
                          logger)
        return values_dict

    def vlan(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):
        # Currently working with IP. Change this to be similar to find core where it parses?
        dev_id, found_int, dev_ip = \
            self.find.int(values_dict, cpi_username, cpi_password, cpi_ipv4_address, values_dict['interface'],
                          logger)
        return values_dict