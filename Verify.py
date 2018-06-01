# Craig Tomkow
# May 22, 2018
#
# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
import argparse
import threading
import json

# local imports
import Config
import Connector
from Connector import Connector
import Switch
from Switch import Switch


class Verify:


    def __init__(self):

        # argument parsing will go here

        Config.load_configuration()

        self.main()


    def main(self):

        ### THREAD HANDLING ###
        switch_ipv4_address_list = Config.dev_ipv4_address
        threads = []
        for switch_ipv4_address in switch_ipv4_address_list:
            t = threading.Thread(target=self.upgrade_code, args=(switch_ipv4_address, Config.username,
                                                                 Config.password, Config.cpi_ipv4_address))
            threads.append(t)
            t.start()

        print('END MAIN PROGRAM, THREADS BE RUNNING STILL')
        print('WAIT FOR X NUMBER OF THREADS TO FINISH, OUTPUT RESULTS, GET USER INPUT ON ACTION TO PERFORM')

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

    def upgrade_code(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        ### PRE_PROCESSING ###
        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)

        switch = Switch()
        switch.ipv4_address = switch_ipv4_address
        print(switch.ipv4_address)
        switch.id = api_call.get_dev_id(switch.ipv4_address)
        print(switch.id)

        ### BEFORE ###

        # 1. check for reachability
        switch.reachability = api_call.get_reachability(switch.id)
        if switch.reachability != 'REACHABLE':
            print('ERROR: ' + switch.ipv4_address + ' is ' + switch.reachability)
            ### < ERROR HANDLING HERE > ###
            ### < LOGGING HERE > ###

        print(switch.ipv4_address + ' is ' + switch.reachability)

        # 2. force sync of switch state
        api_call.sync(switch.ipv4_address)

        switch.software_version = api_call.get_software_version(switch.id)
        switch.stack_member = api_call.get_stack_members(switch.id)
        ########### Need to set VLAN information (don't have a method for this yet in Connector class) ###############

        print(switch.reachability)
        print(switch.software_version)
        print(json.dumps(switch.stack_member, indent=4))

        # 1. check reachability
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

        return True

if __name__ == '__main__':

    Verify()