
# system imports
import socket
import sys

# local imports
from function.find import Find
from connector.switch import Switch


class Poke:

    def __init__(self):

        self.find = Find()

    def port(self, args, config, logger):
        # Currently working with IP. Change this to be similar to find core where it parses
        dev_id, found_int, dev_ip = self.find.int(args, config, args.interface, logger)

        return args

    def vlan(self, args, config, logger):
        # Currently working with IP. Change this to be similar to find core where it parses?
        dev_id, found_int, dev_ip = self.find.int(args, config, args.interface, logger)
        return args