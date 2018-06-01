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
import Switch
from Switch import Switch
import json


class Verify:


    def __init__(self):

        # argument parsing will go here

        Config.load_configuration()

        self.main()


    def main(self):

        ### within a thread... ###

        ### PRE_PROCESSING ###
        api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)

        switch = Switch()
        switch.ipv4_address = Config.device()
        switch.id = api_call.get_dev_id(switch.ipv4_address)


        ### BEFORE ###

        # set switch state information from Cisco Prime

        switch.reachability = api_call.get_reachability(switch.id)
        switch.software_version = api_call.get_software_version(switch.id)
        switch.stack_member = api_call.get_stack_members(switch.id)
        ########### Need to set VLAN information (don't have a method for this yet in Connector class) ###############



        print(switch.reachability)
        print(switch.software_version)
        print(json.dumps(switch.stack_member, indent=4))











        # if dev_reachability == 'REACHABLE':
        #     print(Config.device() + ' is ' + dev_reachability)
        # else:
        #     print(Config.device() + ' is ' + dev_reachability)


        # 2. force sync state
        # 3. get software version
        # 4. get stack members
        # 5. get vlans
        # 6. get CDP neighbour state

        ### RELOAD ###

        ### AFTER ###
        # 1. get reachability
        # 2. force sync state
        # 3. get software version
        # 4. get stack members
        # 5. get vlans
        # 6. get CDP neighbour state

        ### POST_PROCESSING ###
        Config.remove_device()







        ### TESTING METHOD CALLS ###

        # force sync device,need NBI_WRITE access
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #api_call.sync(Config.device())

        # get reachability status
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_reachability = api_call.get_reachability(api_call.get_dev_id(Config.device()))
        #print(json.dumps(dev_reachability, indent=4))

        # get software version
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_software_version = api_call.get_software_version(api_call.get_dev_id(Config.device()))
        #print(json.dumps(dev_software_version, indent=4))

        # get switch stack info
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_stack_info = api_call.get_stack_members(api_call.get_dev_id(Config.device()))
        #print(json.dumps(dev_stack_info, indent=4))

        # CDP neighbour call
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #dev_cdp_neighbours = api_call.get_cdp_neighbours(api_call.get_dev_id(Config.device()))
        #cdp_neighbours_list = dev_cdp_neighbours
        #sorted_list = sorted(cdp_neighbours_list, key=lambda k: k['interfaceIndex']) # sort the list of dicts
        #sorted_interfaceIndex = [x['interfaceIndex'] for x in sorted_list] # extract interfaceIndex values

        #data = next((item for item in dev_cdp_neighbours if item["neighborDeviceName"] == "SEPC0626BD2690F"))
        #print(data)

        # print basic switch information
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #api_call.print_info(api_call.get_dev_id(Config.device()))

        # print detailed switch information
        #api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        #api_call.print_detailed_info(api_call.get_dev_id(Config.device()))



if __name__ == '__main__':

    Verify()