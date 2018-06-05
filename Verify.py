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

            time.sleep(0.1)

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

        print("END OF MAIN --- ALL THREADS FINISHED")

    def test_method(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        ### TESTING METHOD CALLS ###

        # # force sync device,need NBI_WRITE access
        # api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        # api_call.sync(Config.device())
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
        # api_call = Connector(Config.username, Config.password, Config.cpi_ipv4_address)
        # api_call.print_info(api_call.get_dev_id(Config.device()))
        #
        # print detailed switch information
        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)
        api_call.print_detailed_info(api_call.get_dev_id(switch_ipv4_address))


    def upgrade_code(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address):

        print('START: UPGRADE_CODE')

        ############################
        ###### PRE_PROCESSING ######
        ############################
        api_call = Connector(cpi_username, cpi_password, cpi_ipv4_address)

        switch = Switch()
        switch.ipv4_address = switch_ipv4_address
        print(f"SWITCH IP: {switch.ipv4_address}")

        time.sleep(0.5)
        switch.id = api_call.get_dev_id(switch.ipv4_address)

        ####################
        ###### BEFORE ######
        ####################

        ###### 1. check for reachability
        #print("PRE REACHABILITY TESTING")
        time.sleep(0.5)
        switch.pre_reachability = api_call.get_reachability(switch.id)
        if switch.pre_reachability != "REACHABLE":
            print(f"ERROR: {switch.ipv4_address} is {switch.pre_reachability}")
            print("Cancelling process. Proceed with upgrade manually")
            return False

        print(f"{switch.ipv4_address} is {switch.pre_reachability}")

        ##### 2. force sync of switch state
        #print("SYNC SWITCH")
        time.sleep(0.5)
        old_sync_time = api_call.get_sync_time(switch.id)

        time.sleep(0.5)
        api_call.sync(switch.ipv4_address)
        time.sleep(5)
        switch.pre_sync_state = api_call.get_sync_status(switch.id)
        print(switch.pre_sync_state)
        while switch.pre_sync_state != "COMPLETED":
            time.sleep(5)
            switch.pre_sync_state = api_call.get_sync_status(switch.id)
            print('.', end='', flush=True)
        print(switch.pre_sync_state)

        time.sleep(0.5)
        new_sync_time = api_call.get_sync_time(switch.id)
        # compare sync times
        if old_sync_time != new_sync_time:
            pass
        else:
            print("*** ERROR: sync failed. Cancelling process. Proceed with upgrade manually ***")
            return False

        ###### 3. get current software version
        print("GLEANING SOFTWARE VERSION")
        time.sleep(0.5)
        switch.pre_software_version = api_call.get_software_version(switch.id)
        print(switch.pre_software_version)

        ###### 4. get stack members
        ###### (using 'description' key. It appends the word 'Provisioned' if OS-mismatch or V-mismatch
        print("GLEANING STACK MEMBER STATE")
        time.sleep(0.5)
        switch.pre_stack_member = api_call.get_stack_members(switch.id)
        sorted_list = sorted(switch.pre_stack_member, key=lambda k: k['name']) # sort the list of dicts
        switch.pre_stack_member_key = [x['description'] for x in sorted_list] # extract entPhysicalIndex values
        print(switch.pre_stack_member_key)

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state
        ###### Using 'nearEndInterface' key. The phyInterface number changes between code upgrade versions
        print("GLEANING CDP NEIGHBOUR STATE")
        time.sleep(0.5)
        switch.pre_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        sorted_list = sorted(switch.pre_cdp_neighbour, key=lambda k: k['nearEndInterface']) # sort the list of dicts
        switch.pre_cdp_neighbour_key = [x['nearEndInterface'] for x in sorted_list] # extract interfaceIndex values
        print(switch.pre_cdp_neighbour_key)

        print("")
        print("PRE-PROCESSING COMPLETE")

        ####################
        ###### RELOAD ######
        ####################

        print("")
        print(f"Reload switch {switch.ipv4_address} manually now.")
        print("")
        for x in range(0, 3):
            time.sleep(1)
            print(".")
        print("")
        input("Press Enter to continue after the reload command has been issued ...")
        print("")
        # wait five minutes for Prime to update reachability status. I tested with 3 minutes, too short.
        print("REBOOTING (wait 5 minutes before testing reachability)")
        time.sleep(300)

        ###################
        ###### AFTER ######
        ###################

        ###### 1. check for reachability
        #print("POST REACHABILITY TESTING")
        switch.post_reachability = api_call.get_reachability(switch.id)
        print(switch.post_reachability)
        while switch.post_reachability != "REACHABLE":
            time.sleep(5)
            switch.post_reachability = api_call.get_reachability(switch.id)
            print('.', end='', flush=True)

        print(f"{switch.ipv4_address} is {switch.post_reachability}")

        ##### 2. force sync of switch state
        #print("SYNC SWITCH")
        time.sleep(0.5)
        old_sync_time = api_call.get_sync_time(switch.id)

        time.sleep(0.5)
        api_call.sync(switch.ipv4_address)
        time.sleep(5)
        switch.post_sync_state = api_call.get_sync_status(switch.id)
        print(switch.post_sync_state)
        while switch.post_sync_state != "COMPLETED":
            time.sleep(5)
            switch.post_sync_state = api_call.get_sync_status(switch.id)
            print('.', end='', flush=True)
        print(switch.post_sync_state)

        time.sleep(0.5)
        new_sync_time = api_call.get_sync_time(switch.id)
        #compare sync times
        if old_sync_time != new_sync_time:
            print("Switch sync'd")
        else:
            print("*** ERROR: sync failed. Cancelling process. Proceed with verification manually ***")
            return False

        ###### 3. get software version
        #print("CHECKING SOFTWARE VERSION")
        time.sleep(0.5)
        switch.post_software_version = api_call.get_software_version(switch.id)

        # compare
        if switch.pre_software_version == switch.post_software_version:
            ### ERROR HANDLING
            print(f"ERROR: software version before and after is the same, {switch.post_software_version}")
        else:
            print(f"Code upgraded to {switch.post_software_version}")

        ###### 4. get stack members
        #print("TESTING FOR STACK MEMBERS")
        time.sleep(0.5)
        switch.post_stack_member = api_call.get_stack_members(switch.id)
        sorted_list = sorted(switch.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        switch.post_stack_member_key = [x['description'] for x in sorted_list]  # extract entPhysicalIndex values
        print(switch.post_stack_member_key)

        # test for stack member equality
        if switch.pre_stack_member_key != switch.post_stack_member_key:
            diff_keys = set(switch.pre_stack_member_key).symmetric_difference(set(switch.post_stack_member_key))
            for key in diff_keys:
                print("DISPLAYING DIFFERENCE IN SWITCH STACK STATE")
                # check which list it exists in pre list of dicts, otherwise search post list of dicts
                if (any(d["description"] == key for d in switch.pre_stack_member)) is True:
                    print("MISSING STACK MEMBER")
                    stack_member = next((item for item in switch.pre_stack_member if item["description"] == key))
                    print(json.dumps(stack_member, indent=4))
                elif (any(d["description"] == key for d in switch.post_stack_member)) is True:
                    print("NEW? STACK MEMBER (implies not properly joined to begin with)")
                    stack_member = next((item for item in switch.post_stack_member if item["description"] == key))
                    print(json.dumps(stack_member, indent=4))
                else:
                    print(f"ERROR: {key} key not found in either list!")
        else:
            print("STACK MEMBER STATE IS THE SAME BEFORE AS AFTER")


        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state
        #print("TESTING FOR CDP NEIGHBOURS")
        time.sleep(0.5)
        switch.post_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        sorted_list = sorted(switch.post_cdp_neighbour, key=lambda k: k['nearEndInterface'])  # sort the list of dicts
        switch.post_cdp_neighbour_key = [x['nearEndInterface'] for x in sorted_list]  # extract interfaceIndex values
        print(switch.post_cdp_neighbour_key)

        # test for CDP neighbour equality
        if switch.pre_cdp_neighbour_key != switch.post_cdp_neighbour_key:
            diff_keys = set(switch.pre_cdp_neighbour_key).symmetric_difference(set(switch.post_cdp_neighbour_key))
            for key in diff_keys:
                print("DISPLAYING DIFFERENCE IN CDP NEIGHBOUR STATE")
                # check which list it exists in pre list of dicts, otherwise search post list of dicts
                if (any(d["nearEndInterface"] == key for d in switch.pre_cdp_neighbour)) is True:
                    print("MISSING CDP NEIGHBOUR")
                    cdp_neighbour = next((item for item in switch.pre_cdp_neighbour if item["nearEndInterface"] == key))
                    print(json.dumps(cdp_neighbour, indent=4))
                elif (any(d["nearEndInterface"] == key for d in switch.post_cdp_neighbour)) is True:
                    print("NEW CDP NEIGHBOUR FOUND")
                    cdp_neighbour = next((item for item in switch.post_cdp_neighbour if item["nearEndInterface"] == key))
                    print(json.dumps(cdp_neighbour, indent=4))
                else:
                    print(f"ERROR: {key} key not found in either list!")
        else:
            print("ALL CDP NEIGHBOURS MATCH CORRECTLY")


        return True

if __name__ == '__main__':

    Verify()