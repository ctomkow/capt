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
        max_threads = int(Config.concurrent_threads)

        threads = []

        while len(switch_ipv4_address_list) > 0:

            # don't make threads so quickly, you may just scare off Cisco Prime
            time.sleep(1)

            # check if thread is alive, if not, remove from list
            threads = [t for t in threads if t.is_alive()]
            t_count = len(threads)

            #print(t_count)

            # spawn thread if max concurrent number is not reached
            if t_count < max_threads:
                t = threading.Thread(target=self.upgrade_code, args=(switch_ipv4_address_list.pop(), Config.username,
                                                                         Config.password, Config.cpi_ipv4_address))
                threads.append(t)
                t.start()
                t_count += 1

            # when last device is popped off list, wait for ALL threads to finish
            if len(switch_ipv4_address_list) == 0:
                for t in threads:
                    t.join()


    def test_method(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        ### TESTING METHOD CALLS ###

        # # force sync device,need NBI_WRITE access
        #api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)
        #api_call.sync(switch_ipv4_address)
        #
        # # get reachability status
        # api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        # dev_reachability = api_call.get_reachability(api_call.get_dev_id(Config.device()))
        # print(json.dumps(dev_reachability, indent=4))
        #
        # # get software version
        # api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        # dev_software_version = api_call.get_software_version(api_call.get_dev_id(Config.device()))
        # print(json.dumps(dev_software_version, indent=4))
        #
        # # get switch stack info
        # api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        # dev_stack_info = api_call.get_stack_members(api_call.get_dev_id(Config.device()))
        # print(json.dumps(dev_stack_info, indent=4))
        #
        # # CDP neighbour call
        # api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        # dev_cdp_neighbours = api_call.get_cdp_neighbours(api_call.get_dev_id(Config.device()))
        # cdp_neighbours_list = dev_cdp_neighbours
        # sorted_list = sorted(cdp_neighbours_list, key=lambda k: k['interfaceIndex']) # sort the list of dicts
        # sorted_interfaceIndex = [x['interfaceIndex'] for x in sorted_list] # extract interfaceIndex values
        #
        # data = next((item for item in dev_cdp_neighbours if item["neighborDeviceName"] == "SEPC0626BD2690F"))
        # print(data)
        #
        # # print basic switch information
        #api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)
        #api_call.print_info(api_call.get_dev_id(switch_ipv4_address))
        #
        # print detailed switch information
        #api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)
        #api_call.print_detailed_info(api_call.get_dev_id(switch_ipv4_address))

        pass


    def upgrade_code(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        print(f"{switch_ipv4_address}: UPGRADE_CODE")

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

        switch.pre_reachability = None
        while switch.pre_reachability != "REACHABLE":
            time.sleep(5)
            switch.pre_reachability = api_call.get_reachability(switch.id)
            if self.ping(switch.ipv4_address) is False:
                switch.pre_reachability = "UNREACHABLE"
                print('.', end='', flush=True)
        print("")
        print(f"{switch.ipv4_address}: {switch.pre_reachability}")

        ##### 2. force sync of switch state

        old_sync_time = api_call.get_sync_time(switch.id)

        api_call.sync(switch.ipv4_address)
        print(f"{switch.ipv4_address}: BEGIN SYNC")
        switch.pre_sync_state = None
        while switch.pre_sync_state != "COMPLETED":
            time.sleep(5)
            switch.pre_sync_state = api_call.get_sync_status(switch.id)
            print('.', end='', flush=True)
        print("")
        print(f"{switch.ipv4_address}: {switch.pre_sync_state}")

        new_sync_time = api_call.get_sync_time(switch.id)
        # compare sync times
        if old_sync_time != new_sync_time:
            pass
        else:
            print(f"{switch.ipv4_address}: *** ERROR - sync failed. Cancelling process. Proceed with upgrade manually ***")
            return False

        ###### 3. get current software version

        switch.pre_software_version = api_call.get_software_version(switch.id)
        print(f"{switch.ipv4_address}: VERSION - {switch.pre_software_version}")

        ###### 4. get stack members
        ###### (using 'description' key. It appends the word 'Provisioned' if OS-mismatch or V-mismatch

        switch.pre_stack_member = api_call.get_stack_members(switch.id)
        sorted_list = sorted(switch.pre_stack_member, key=lambda k: k['name']) # sort the list of dicts
        switch.pre_stack_member_key = [x['description'] for x in sorted_list] # extract description values
        print(f"{switch.ipv4_address}: STACK MEMBERS - {switch.pre_stack_member_key}")

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state
        ###### Using 'nearEndInterface' key. The phyInterface number changes between code upgrade versions

        switch.pre_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        sorted_list = sorted(switch.pre_cdp_neighbour, key=lambda k: k['nearEndInterface']) # sort the list of dicts
        switch.pre_cdp_neighbour_key = [x['nearEndInterface'] for x in sorted_list] # extract interfaceIndex values
        print(f"{switch.ipv4_address}: CDP NEIGHOURS - {switch.pre_cdp_neighbour_key}")

        print("")
        print(f"{switch.ipv4_address}: PRE-PROCESSING COMPLETE")

        ####################
        ###### RELOAD ######
        ####################

        print(f"{switch.ipv4_address}: Reload switch manually now.")
        input("Press Enter to continue after the reload command has been issued ...")
        print(f"{switch.ipv4_address}: REBOOTING")

        ###################
        ###### AFTER ######
        ###################

        ###### 1. check for reachability

        switch.post_reachability = None
        while switch.post_reachability != "REACHABLE":
            time.sleep(10)
            switch.post_reachability = api_call.get_reachability(switch.id)
            if self.ping(switch.ipv4_address) is False:
                switch.post_reachability = "UNREACHABLE"
                print('.', end='', flush=True)
        print("")
        print(f"{switch.ipv4_address}: {switch.post_reachability}")

        ##### 2. force sync of switch state

        old_sync_time = api_call.get_sync_time(switch.id)

        api_call.sync(switch.ipv4_address)
        print(f"{switch.ipv4_address}: BEGIN SYNC")
        switch.post_sync_state = None
        while switch.post_sync_state != "COMPLETED":
            time.sleep(5)
            switch.post_sync_state = api_call.get_sync_status(switch.id)
            print('.', end='', flush=True)
        print("")
        print(f"{switch.ipv4_address}: {switch.post_sync_state}")

        new_sync_time = api_call.get_sync_time(switch.id)
        #compare sync times
        if old_sync_time != new_sync_time:
            print(f"{switch.ipv4_address}: SYNCHRONIZED")
        else:
            print(f"{switch.ipv4_address}: *** ERROR - sync failed. Cancelling process. Proceed with verification manually ***")
            return False

        ###### 3. get software version

        switch.post_software_version = api_call.get_software_version(switch.id)

        # compare
        if switch.pre_software_version == switch.post_software_version:
            print(f"{switch.ipv4_address}: ERROR - software version before and after is the same, {switch.post_software_version}")
        else:
            print(f"{switch.ipv4_address}: code upgraded to {switch.post_software_version}")

        ###### 4. get stack members

        switch.post_stack_member = api_call.get_stack_members(switch.id)
        sorted_list = sorted(switch.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        switch.post_stack_member_key = [x['description'] for x in sorted_list]  # extract entPhysicalIndex values
        print(f"{switch.ipv4_address}: {switch.post_stack_member_key}")

        # test for stack member equality
        if switch.pre_stack_member_key != switch.post_stack_member_key:
            diff_keys = set(switch.pre_stack_member_key).symmetric_difference(set(switch.post_stack_member_key))
            for key in diff_keys:
                # check which list it exists in pre list of dicts, otherwise search post list of dicts
                if (any(d["description"] == key for d in switch.pre_stack_member)) is True:
                    print(f"{switch.ipv4_address}: MISSING STACK MEMBER")
                    stack_member = next((item for item in switch.pre_stack_member if item["description"] == key))
                    print(json.dumps(stack_member, indent=4))
                elif (any(d["description"] == key for d in switch.post_stack_member)) is True:
                    print(f"{switch.ipv4_address}: NEW MEMBER (if member says \'Provisioned\' it likely is OS-Mismatch or V-Mismatch)")
                    stack_member = next((item for item in switch.post_stack_member if item["description"] == key))
                    print(json.dumps(stack_member, indent=4))
                else:
                    print(f"{switch.ipv4_address}: ERROR - {key} key not found in either list!")
        else:
            print(f"{switch.ipv4_address}: ALL STACK MEMBERS MATCH")


        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state

        switch.post_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        sorted_list = sorted(switch.post_cdp_neighbour, key=lambda k: k['nearEndInterface'])  # sort the list of dicts
        switch.post_cdp_neighbour_key = [x['nearEndInterface'] for x in sorted_list]  # extract interfaceIndex values
        print(f"{switch.ipv4_address}: {switch.post_cdp_neighbour_key}")

        # test for CDP neighbour equality
        if switch.pre_cdp_neighbour_key != switch.post_cdp_neighbour_key:
            diff_keys = set(switch.pre_cdp_neighbour_key).symmetric_difference(set(switch.post_cdp_neighbour_key))
            for key in diff_keys:
                # check which list it exists in pre list of dicts, otherwise search post list of dicts
                if (any(d["nearEndInterface"] == key for d in switch.pre_cdp_neighbour)) is True:
                    print(f"{switch.ipv4_address}: MISSING CDP NEIGHBOUR")
                    cdp_neighbour = next((item for item in switch.pre_cdp_neighbour if item["nearEndInterface"] == key))
                    print(json.dumps(cdp_neighbour, indent=4))
                elif (any(d["nearEndInterface"] == key for d in switch.post_cdp_neighbour)) is True:
                    print(f"{switch.ipv4_address}: NEW CDP NEIGHBOUR FOUND")
                    cdp_neighbour = next((item for item in switch.post_cdp_neighbour if item["nearEndInterface"] == key))
                    print(json.dumps(cdp_neighbour, indent=4))
                else:
                    print(f"{switch.ipv4_address}: ERROR - {key} key not found in either list!")
        else:
            print(f"{switch.ipv4_address}: ALL CDP NEIGHBOURS MATCH")


        return True

    # needed because Prime is slow to detect connectivity or not
    def ping(self, switch_ipv4_address):

        # use "ping -c 1 -W 1" for linux, -n for Windows
        response = os.system(f"ping -n 1 -w 1000 {switch_ipv4_address}>nul")

        if response == 0:
            return True
        else:
            return False

if __name__ == '__main__':

    Verify()