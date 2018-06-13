#!/usr/bin/env python3

# Craig Tomkow
# May 22, 2018
#
# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
import argparse
import threading
import json
import time
import os
import sys
import platform

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

        switch_ipv4_address_list = Config.dev_ipv4_address
        max_threads = int(Config.dev_concurrent_threads)

        proc_dict = {}
        proc_dict[Config.proc_code_upgrade]   = 'code_upgrade'
        proc_dict[Config.proc_push_config]    = 'push_config'
        proc_dict[Config.proc_test_api_calls] = 'test_api_calls'
        del proc_dict['false']  # remove procedures that should not be executed (there is only one 'true' key anyway cause its a dictionary)

        threads = []

        while len(switch_ipv4_address_list) > 0:

            # check if thread is alive, if not, remove from list
            threads = [t for t in threads if t.is_alive()]
            t_count = len(threads)



            # spawn thread if max concurrent number is not reached
            if t_count < max_threads:

                try:
                    if proc_dict['true'] == 'code_upgrade':
                        t = threading.Thread(target=self.upgrade_code, args=(switch_ipv4_address_list[0], Config.username,
                                                                                Config.password, Config.cpi_ipv4_address))
                    elif proc_dict['true'] == 'push_config':
                        t = threading.Thread(target=self.push_config(switch_ipv4_address_list[0], Config.config_user_exec,
                                                                                Config.config_priv_exec, Config.config_global_config))
                    elif proc_dict['true'] == 'test_api_calls':
                        t = threading.Thread(target=self.test_api_calls, args=(switch_ipv4_address_list[0], Config.username,
                                                                                Config.password, Config.cpi_ipv4_address))
                except KeyError:
                    print("No procedure selected as 'true' in config.text")
                    sys.exit(1)

                threads.append(t)
                t.start()
                t_count += 1

                switch_ipv4_address_list.pop()  # remove referenced switch

                # when last device is popped off list, wait for ALL threads to finish
                if len(switch_ipv4_address_list) == 0:
                    for t in threads:
                        t.join()

    def upgrade_code(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        print("{}: UPGRADE_CODE".format(switch_ipv4_address))

        ############################
        ###### PRE_PROCESSING ######
        ############################
        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)

        switch = Switch()
        switch.ipv4_address = switch_ipv4_address

        switch.id = api_call.get_dev_id(switch.ipv4_address)

        ####################
        ###### BEFORE ######
        ####################

        ###### 1. check for reachability

        print("{}: TESTING REACHABILITY".format(switch.ipv4_address))

        while not self.reachable(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)

        print("\n")
        print("{}: {}".format(switch.ipv4_address, switch.reachability))


        ##### 2. force sync of switch state

        old_sync_time = api_call.get_sync_time(switch.id)

        api_call.sync(switch.ipv4_address)
        print("{}: BEGIN SYNC".format(switch.ipv4_address))
        switch.pre_sync_state = None
        while switch.pre_sync_state != "COMPLETED":
            time.sleep(5)
            switch.pre_sync_state = api_call.get_sync_status(switch.id)
            print('.', end='', flush=True)
        print("")
        print("{}: {}".format(switch.ipv4_address, switch.pre_sync_state))

        new_sync_time = api_call.get_sync_time(switch.id)
        # compare sync times
        if old_sync_time != new_sync_time:
            pass
        else:
            print("{}: *** ERROR - sync failed. Cancelling process. Proceed with upgrade manually ***".format(switch.ipv4_address))
            return False

        ###### 3. get current software version

        switch.pre_software_version = api_call.get_software_version(switch.id)
        print("{}: VERSION - {}".format(switch.ipv4_address, switch.pre_software_version))

        ###### 4. get stack members
        ###### (using 'description' key. It appends the word 'Provisioned' if OS-mismatch or V-mismatch

        switch.pre_stack_member = api_call.get_stack_members(switch.id)
        sorted_list = sorted(switch.pre_stack_member, key=lambda k: k['name']) # sort the list of dicts
        switch.pre_stack_member_key = [x['description'] for x in sorted_list] # extract description values
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.pre_stack_member_key))

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state
        ###### Using 'nearEndInterface' key. The phyInterface number changes between code upgrade versions

        switch.pre_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        sorted_list = sorted(switch.pre_cdp_neighbour, key=lambda k: k['nearEndInterface']) # sort the list of dicts
        switch.pre_cdp_neighbour_key = [x['nearEndInterface'] for x in sorted_list] # extract interfaceIndex values
        print("{}: CDP NEIGHOURS - {}".format(switch.ipv4_address, switch.pre_cdp_neighbour_key))

        print("")
        print("{}: PRE-PROCESSING COMPLETE".format(switch.ipv4_address))

        ####################
        ###### RELOAD ######
        ####################

        print("{}: REBOOTING".format(switch.ipv4_address))
        os.system("swITch.py -ea auth.txt -c \"reload code_upgrade\" -i \"{},cisco_ios\"".format(switch.ipv4_address))
        time.sleep(10)

        ###################
        ###### AFTER ######
        ###################

        ###### 1. check for reachability

        print("{}: TESTING REACHABILITY".format(switch.ipv4_address))

        while not self.reachable(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)

        print("\n")
        print("{}: {}".format(switch.ipv4_address, switch.reachability))

        ##### 2. force sync of switch state

        old_sync_time = api_call.get_sync_time(switch.id)

        api_call.sync(switch.ipv4_address)
        print("{}: BEGIN SYNC".format(switch.ipv4_address))
        switch.post_sync_state = None
        while switch.post_sync_state != "COMPLETED":
            time.sleep(5)
            switch.post_sync_state = api_call.get_sync_status(switch.id)
            print('.', end='', flush=True)
        print("")
        print("{}: {}".format(switch.ipv4_address, switch.post_sync_state))

        new_sync_time = api_call.get_sync_time(switch.id)
        #compare sync times
        if old_sync_time != new_sync_time:
            print("{}: SYNCHRONIZED".format(switch.ipv4_address))
        else:
            print("{}: *** ERROR - sync failed. Cancelling process. Proceed with verification manually ***".format(switch.ipv4_address))
            return False

        ###### 3. get software version

        switch.post_software_version = api_call.get_software_version(switch.id)

        # compare
        if switch.pre_software_version == switch.post_software_version:
            print("{}: ERROR - software version before and after is the same, {}".format(switch.ipv4_address, switch.post_software_version))
        else:
            print("{}: VERSION - {}".format(switch.ipv4_address, switch.post_software_version))

        ###### 4. get stack members

        switch.post_stack_member = api_call.get_stack_members(switch.id)
        sorted_list = sorted(switch.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        switch.post_stack_member_key = [x['description'] for x in sorted_list]  # extract entPhysicalIndex values
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.post_stack_member_key))

        # test for stack member equality
        if switch.pre_stack_member_key != switch.post_stack_member_key:
            diff_keys = set(switch.pre_stack_member_key).symmetric_difference(set(switch.post_stack_member_key))
            for key in diff_keys:
                # check which list it exists in pre list of dicts, otherwise search post list of dicts
                if (any(d["description"] == key for d in switch.pre_stack_member)) is True:
                    print("{}: MISSING STACK MEMBER".format(switch.ipv4_address))
                    stack_member = next((item for item in switch.pre_stack_member if item["description"] == key))
                    print(json.dumps(stack_member, indent=4))
                elif (any(d["description"] == key for d in switch.post_stack_member)) is True:
                    print("{}: NEW MEMBER (if member says \'Provisioned\' it likely is OS-Mismatch or V-Mismatch)".format(switch.ipv4_address))
                    stack_member = next((item for item in switch.post_stack_member if item["description"] == key))
                    print(json.dumps(stack_member, indent=4))
                else:
                    print("{}: ERROR - {} key not found in either list!".format(switch.ipv4_address, key))
        else:
            print("{}: ALL STACK MEMBERS MATCH".format(switch.ipv4_address))


        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state

        switch.post_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        sorted_list = sorted(switch.post_cdp_neighbour, key=lambda k: k['nearEndInterface'])  # sort the list of dicts
        switch.post_cdp_neighbour_key = [x['nearEndInterface'] for x in sorted_list]  # extract interfaceIndex values
        print("{}: CDP NEIGHBOURS - {}".format(switch.ipv4_address, switch.post_cdp_neighbour_key))

        # test for CDP neighbour equality
        if switch.pre_cdp_neighbour_key != switch.post_cdp_neighbour_key:
            diff_keys = set(switch.pre_cdp_neighbour_key).symmetric_difference(set(switch.post_cdp_neighbour_key))
            for key in diff_keys:
                # check which list it exists in pre list of dicts, otherwise search post list of dicts
                if (any(d["nearEndInterface"] == key for d in switch.pre_cdp_neighbour)) is True:
                    print("{}: MISSING CDP NEIGHBOUR".format(switch.ipv4_address))
                    cdp_neighbour = next((item for item in switch.pre_cdp_neighbour if item["nearEndInterface"] == key))
                    print(json.dumps(cdp_neighbour, indent=4))
                elif (any(d["nearEndInterface"] == key for d in switch.post_cdp_neighbour)) is True:
                    print("{}: NEW CDP NEIGHBOUR FOUND".format(switch.ipv4_address))
                    cdp_neighbour = next((item for item in switch.post_cdp_neighbour if item["nearEndInterface"] == key))
                    print(json.dumps(cdp_neighbour, indent=4))
                else:
                    print("{}: ERROR - {} key not found in either list!".format(switch.ipv4_address, key))
        else:
            print("{}: ALL CDP NEIGHBOURS MATCH".format(switch.ipv4_address))


        return True

    def push_config(self, switch_ipv4_address, config_user_exec, config_priv_exec, config_global_config):

        if config_user_exec[0] != "false":
            os.system("swITch.py -a auth.txt -c \"{}\" -i \"{},cisco_ios\"".format(config_user_exec[0], switch_ipv4_address))
        if config_priv_exec[0] != "false":
            os.system("swITch.py -ea auth.txt -c \"{}\" -i \"{},cisco_ios\"".format(config_priv_exec[0], switch_ipv4_address))
        if config_global_config[0] != "false":
            print("Need to update swITch.py to work with new netmiko config parameter")

    # needed because Prime is slow to detect connectivity or not
    def ping(self, switch_ipv4_address):

        if platform.system() == "Linux":
            response = os.system("ping -c 1 -W 1 {}>nul".format(switch_ipv4_address))
        elif platform.system() == "Windows":
            response = os.system("ping -n 1 -w 1000 {}>nul".format(switch_ipv4_address))
        else:
            print("Ping failed, could not detect system")
            sys.exit(1)

        # ping program returns 0 on successful ICMP request, 1 on failed ICMP request
        if response == 0:
            return True
        elif response == 1:
            return False
        else:
            print("Ping failed to return 0 or 1. Exiting...")
            sys.exit(1)

    def reachable(self, switch, api_call):

        if not self.ping(switch.ipv4_address):
            switch.reachability = "UNREACHABLE"
            return False
        elif self.ping(switch.ipv4_address) and api_call.get_reachability(switch.id) == "REACHABLE":
            switch.reachability = "REACHABLE"
            return True
        else:
            switch.reachability = "UNREACHABLE"
            return False

    def test_api_calls(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        ### TESTING METHOD CALLS ###

        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)

        switch = Switch()
        switch.ipv4_address = switch_ipv4_address
        switch.id = api_call.get_dev_id(switch.ipv4_address)

        # # force sync device,need NBI_WRITE access
        # api_call.sync(switch_ipv4_address)
        #
        # # get reachability status
        # dev_reachability = api_call.get_reachability(switch.id)
        # print(json.dumps(dev_reachability, indent=4))
        #
        # # get software version
        # dev_software_version = api_call.get_software_version(switch.id)
        # print(json.dumps(dev_software_version, indent=4))
        #
        # # get switch stack info
        dev_stack_info = api_call.get_stack_members(switch.id)
        print(json.dumps(dev_stack_info, indent=4))
        #
        # # CDP neighbour call
        dev_cdp_neighbours = api_call.get_cdp_neighbours(switch.id)
        cdp_neighbours_list = dev_cdp_neighbours
        print(json.dumps(dev_cdp_neighbours, indent=4))
        # sorted_list = sorted(cdp_neighbours_list, key=lambda k: k['interfaceIndex']) # sort the list of dicts
        # sorted_interfaceIndex = [x['interfaceIndex'] for x in sorted_list] # extract interfaceIndex values
        #
        # data = next((item for item in dev_cdp_neighbours if item["neighborDeviceName"] == "SEPC0626BD2690F"))
        # print(data)
        #
        # print basic switch information
        #api_call.print_info(switch.id)
        #
        # #print detailed switch information
        # api_call.print_detailed_info(switch.id)
        #
        # # print client summary
        # api_call.print_client_summary(switch.id)

if __name__ == '__main__':

    Verify()