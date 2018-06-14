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
import logging
import datetime

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
                        logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)
                        t = threading.Thread(target=self.upgrade_code, args=(switch_ipv4_address_list[0], Config.username,
                                                                Config.password, Config.cpi_ipv4_address, logger))
                    elif proc_dict['true'] == 'push_config':
                        logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)
                        t = threading.Thread(target=self.push_config(switch_ipv4_address_list[0], Config.config_user_exec,
                                                                Config.config_priv_exec, Config.config_global_config, logger))
                    elif proc_dict['true'] == 'test_api_calls':
                        logger = self.set_logger(switch_ipv4_address_list[0], logging.DEBUG)
                        t = threading.Thread(target=self.test_api_calls, args=(switch_ipv4_address_list[0], Config.username,
                                                                Config.password, Config.cpi_ipv4_address, logger))
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

    def upgrade_code(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address, logger):

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

        timeout = time.time() + 60*5 # 5 minute timeout starting now (this is before the code upgrade, so short timeout)
        while not self.reachable(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 5 minutes and switch hasn't responded. Exiting script.".format(switch.ipv4_address))
                sys.exit(1)

        print("")
        print("{}: {}".format(switch.ipv4_address, switch.reachability))


        ##### 2. force sync of switch state

        print("{}: SYNCHRONIZE DEVICE".format(switch.ipv4_address))
        old_sync_time = api_call.get_sync_time(switch.id)
        api_call.sync(switch.ipv4_address) # force a sync!
        time.sleep(5) # don't test for sync status too soon (CPI delay and all that)

        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        while not self.synchronized(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 10 minutes and switch hasn't synced. Exiting script.".format(switch.ipv4_address))
                sys.exit(1)

        print("")
        print("{}: {}".format(switch.ipv4_address, switch.sync_state))

        new_sync_time = api_call.get_sync_time(switch.id)
        if old_sync_time == new_sync_time: # KEEP CODE! needed for corner case issue where force sync fails (e.g. code 03.03.03)
            print("{}: ERROR - sync failed. Cancelling script. Proceed with upgrade manually ***".format(switch.ipv4_address))
            sys.exit(1)

        ###### 3. get current software version

        switch.pre_software_version = api_call.get_software_version(switch.id)
        print("{}: INFO - current version is {}".format(switch.ipv4_address, switch.pre_software_version))


        ###### 4. get stack members

        switch.pre_stack_member = api_call.get_stack_members(switch.id)
        switch.pre_stack_member = sorted(switch.pre_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.

        switch.pre_stack_member_name = [x['name'] for x in switch.pre_stack_member]  # extract name values
        switch.pre_stack_member_desc = [x['description'] for x in switch.pre_stack_member]  # extract description values
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.pre_stack_member_name))
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.pre_stack_member_desc))

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state

        switch.pre_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        switch.pre_cdp_neighbour = sorted(switch.pre_cdp_neighbour, key=lambda k: k['nearEndInterface']) # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions

        switch.pre_cdp_neighbour_nearend = [x['nearEndInterface'] for x in switch.pre_cdp_neighbour] # extract nearEnd values
        print("{}: CDP NEIGHOURS - {}".format(switch.ipv4_address, switch.pre_cdp_neighbour_nearend))

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

        timeout = time.time() + 60*45 # 45 minute timeout starting now
        while not self.reachable(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: CRITICAL - 45 minutes and switch hasn't responded. Exiting script.".format(switch.ipv4_address))
                sys.exit(1)

        print("\n")
        print("{}: {}".format(switch.ipv4_address, switch.reachability))

        ##### 2. force sync of switch state

        print("{}: SYNCHRONIZE DEVICE".format(switch.ipv4_address))
        old_sync_time = api_call.get_sync_time(switch.id)
        api_call.sync(switch.ipv4_address)  # force a sync!
        time.sleep(5)  # don't test for sync status too soon (CPI delay and all that)

        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        while not self.synchronized(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 10 minutes and switch hasn't synced. Exiting script.".format(switch.ipv4_address))
                sys.exit(1)

        print("")
        print("{}: {}".format(switch.ipv4_address, switch.sync_state))

        new_sync_time = api_call.get_sync_time(switch.id)
        if old_sync_time == new_sync_time:  # needed for corner case issue where force sync fails (e.g. code 03.03.03)
            print("{}: *** ERROR - sync failed. Cancelling script. Proceed with upgrade manually ***".format(
                switch.ipv4_address))
            sys.exit(1)

        ###### 3. get software version

        switch.post_software_version = api_call.get_software_version(switch.id)
        print("{}: INFO - new version is {}".format(switch.ipv4_address, switch.pre_software_version))

        # compare
        if switch.pre_software_version == switch.post_software_version:
            print("{}: ERROR - software version before and after is the same, {}".format(switch.ipv4_address, switch.post_software_version))
        else:
            print("{}: INFO - old:{} new:{}".format(switch.ipv4_address, switch.pre_software_version, switch.post_software_version))

        ###### 4. get stack members

        switch.post_stack_member = api_call.get_stack_members(switch.id)
        switch.post_stack_member = sorted(switch.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.

        switch.post_stack_member_name = [x['name'] for x in switch.post_stack_member]  # extract name values
        switch.post_stack_member_desc = [x['description'] for x in switch.post_stack_member]  # extract description values
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.post_stack_member_name))
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.post_stack_member_desc))

        # compare states
        pre_name_diff, post_name_diff = self.compare_list(switch.pre_stack_member_name, switch.post_stack_member_name)
        pre_desc_diff, post_desc_diff = self.compare_list(switch.pre_stack_member_desc, switch.post_stack_member_desc)

        if not pre_name_diff and not post_name_diff and not pre_desc_diff and not post_desc_diff:
            print("INFO: {} stack members are the same before as after".format(switch.ipv4_address))
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_name_diff:
                print("Switch(es) no longer exists in stack! {}".format(pre_name_diff))
            # if the name difference exists after but not before ... switch was found???
            if post_name_diff:
                print("New switch(es) detected AFTER code upgrade! {}".format(post_name_diff))
            # if the description diff exists before and after, then "Provisioned" was tacked on or removed
            if pre_desc_diff and post_desc_diff:
                for d in post_desc_diff:
                    if "Provisioned" in d:
                        print("CRITICAL {} - OS-mismatch or V-mismatch".format(switch.ipv4_address))

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state

        switch.post_cdp_neighbour = api_call.get_cdp_neighbours(switch.id)
        switch.post_cdp_neighbour = sorted(switch.post_cdp_neighbour, key=lambda k: k['nearEndInterface'])  # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions

        switch.post_cdp_neighbour_nearend = [x['nearEndInterface'] for x in switch.post_cdp_neighbour]  # extract nearEnd values
        print("{}: CDP NEIGHOURS - {}".format(switch.ipv4_address, switch.post_cdp_neighbour_nearend))

        # compare states
        pre_cdp_diff, post_cdp_diff = self.compare_list(switch.pre_cdp_neighbour_nearend, switch.post_cdp_neighbour_nearend)

        if not pre_cdp_diff and not post_cdp_diff:
            print("INFO: {} CDP neighbours are the same before as after".format(switch.ipv4_address))
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_cdp_diff:
                print("Neighbour(s) no longer exist! {}".format(pre_cdp_diff))
            # if the name difference exists after but not before ... switch was found???
            if post_cdp_diff:
                print("Neighbour(s) detected AFTER code upgrade! {}".format(post_cdp_diff))

        print("")
        print("{}: POST-PROCESSING COMPLETE".format(switch.ipv4_address))
        return True

    def push_config(self, switch_ipv4_address, config_user_exec, config_priv_exec, config_global_config, logger):

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
        else: # in-between condition where switch is pingable, but CPI device hasn't moved to REACHABLE
            switch.reachability = api_call.get_reachability(switch.id)
            return False

    def synchronized(self, switch, api_call):

        if api_call.get_sync_status(switch.id) == "COMPLETED":
            switch.sync_state = "COMPLETED"
            return True
        elif api_call.get_sync_status(switch.id) == "SYNCHRONIZING":
            switch.sync_state = "SYNCHRONIZING"
            return False
        else:
            switch.sync_state = api_call.get_sync_status(switch.id)
            print("unexpected sync state: {}".format(switch.sync_state))
            return False

    def compare_list(self, list1, list2):

        diff_list1 = []
        diff_list2 = []

        if list1 == list2:
            return diff_list1, diff_list2 # empty list evaluates to boolean False

        diff = sorted(list(set(list1).symmetric_difference(set(list2))))

        # determine which list contains the difference
        for d in diff:
            if d in list1:
                diff_list1.append(d)
            if d in list2:
                diff_list2.append(d)

        return diff_list1, diff_list2

    def set_logger(self, name, level):

        formatter = logging.Formatter(
            fmt='%(asctime)s : {} : %(levelname)-8s : %(message)s'.format(name),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler = logging.FileHandler(
            "{}-{}".format(datetime.datetime.now().strftime("%Y%m%d"), name),
            mode='a'
        )
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger

    def test_api_calls(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address, logger):

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
        #dev_stack_info = api_call.get_stack_members(switch.id)
        #print(json.dumps(dev_stack_info, indent=4))
        switch.pre_stack_member = api_call.get_stack_members(switch.id)
        switch.pre_stack_member = sorted(switch.pre_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        switch.pre_stack_member_name = [x['name'] for x in switch.pre_stack_member]  # extract name values
        switch.pre_stack_member_desc = [x['description'] for x in switch.pre_stack_member]  # extract description values
        logger.info("stack member(s): {}".format(switch.pre_stack_member_name))
        logger.info("stack member(s): {}".format(switch.pre_stack_member_desc))
        logger.debug("ALJSFL:KSJDL:KSJDFL:")

        sys.exit(1)

        input("Press enter to sync ...")

        #api_call.sync(switch.ipv4_address)
        #time.sleep(5)
        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        while not self.synchronized(switch, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 10 minutes and switch hasn't synced. Exiting script.".format(switch.ipv4_address))
                sys.exit(1)
        print("")

        switch.post_stack_member = api_call.get_stack_members(switch.id)
        switch.post_stack_member = sorted(switch.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        switch.post_stack_member_name = [x['name'] for x in switch.post_stack_member]  # extract name values
        switch.post_stack_member_desc = [x['description'] for x in switch.post_stack_member]  # extract description values
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.post_stack_member_name))
        print("{}: STACK MEMBERS - {}".format(switch.ipv4_address, switch.post_stack_member_desc))

        ##### compare states
        # the switch 'name' (e.g. 'Switch 1') is used to test switch

        pre_name_diff, post_name_diff = self.compare_list(switch.pre_stack_member_name, switch.post_stack_member_name)
        pre_desc_diff, post_desc_diff = self.compare_list(switch.pre_stack_member_desc, switch.post_stack_member_desc)

        # if the name difference exists before but not after ... switch is missing!
        if pre_name_diff:
            print("Switch(es) no longer exists in stack! {}".format(pre_name_diff))
        # if the name difference exists after but not before ... switch was found???
        if post_name_diff:
            print("New switch(es) detected AFTER code upgrade! {}".format(post_name_diff))
        # if the description diff exists before and after, then "Provisioned" was tacked on or removed
        if pre_desc_diff and post_desc_diff:
            for d in post_desc_diff:
                if "Provisioned" in d:
                    print("CRITICAL {} - OS-mismatch or V-mismatch".format(switch.ipv4_address))

        if not pre_name_diff and not post_name_diff and not pre_desc_diff and not post_desc_diff:
            print("INFO: {} stack members are the same before as after".format(switch.ipv4_address))
        #
        # # CDP neighbour call
        #dev_cdp_neighbours = api_call.get_cdp_neighbours(switch.id)
        #cdp_neighbours_list = dev_cdp_neighbours
        #print(json.dumps(dev_cdp_neighbours, indent=4))
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