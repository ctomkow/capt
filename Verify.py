# Craig Tomkow
# May 22, 2018
#
# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
import argparse
import _thread

# local imports
import Config

import Connector
from Connector import Connector

class Verify:


    def __init__(self):

        # argument parsing

        #config loading
        Config.load_configuration()

        self.main()


    def main(self):

        ### within a thread... ###

        # CDP neighbour call
        api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        dev_cdp_neighbours = api_call.get_cdp_neighbours(api_call.get_dev_id(Config.device()))

        print(dev_cdp_neighbours)

        # grab state for device


        # parse and store only the state specified from Connector module
        # compare old and new state files
        # yadda yadda yadda


if __name__ == '__main__':

    Verify()