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
import json

class Verify:


    def __init__(self):

        # argument parsing will go here

        Config.load_configuration()

        self.main()


    def main(self):

        ### within a thread... ###

        # get reachability status
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_reachability = api_call.get_reachability(api_call.get_dev_id(Config.device()))
        #print(json.dumps(dev_reachability, indent=4))

        # CDP neighbour call
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_cdp_neighbours = api_call.get_cdp_neighbours(api_call.get_dev_id(Config.device()))
        #dev_cdp_neighbours = dev_cdp_neighbours['cdpNeighbor']
        #print(json.dumps(dev_cdp_neighbours, indent=4))
        #data = next((item for item in dev_cdp_neighbours if item["neighborDeviceName"] == "SEPC0626BD2690F"))
        #print(data)

        # force sync device,need NBI_WRITE access
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #api_call.sync(Config.device())

        # get switch stack info
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_stack_info = api_call.get_stack_members(api_call.get_dev_id(Config.device()))
        #print(json.dumps(dev_stack_info, indent=4))

        # print basic switch information
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #api_call.print_info(api_call.get_dev_id(Config.device()))


        # print detailed switch information
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #api_call.print_detailed_info(api_call.get_dev_id(Config.device()))



if __name__ == '__main__':

    Verify()