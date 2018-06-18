#!/usr/bin/env python3

# Craig Tomkow
# May 22, 2018
#
# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
import argparse
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import threading
import json
import time
import os
import sys
import platform
import logging
import datetime

# local imports
import config
import connector
from connector import connector
import switch
from switch import switch


class capt:


    def __init__(self):

        # arg parsing
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, add_help=True,
                                description="""Cisco APi Tool: a nettool built on Cisco Prime's API""")
        subparsers = parser.add_subparsers(dest="sub_command")

        #
        test = subparsers.add_parser('test_api', help="API testing")

        # upgrade.add_argument('ip_address', help="specify the IPv4 address of switch")
        # upgrade.set_defaults(func=self.test)

        #  -----
        # capt push
        push = subparsers.add_parser('push', help="send configuration to switch")
        # capt push "show int status"
        push.add_argument('cisco_config', help="specify the cisco IOS command to push")
        push_subparsers = push.add_subparsers()
        # capt push "show int status" to
        push_to = push_subparsers.add_parser('to', help="specify the IPv4 address of switch")
        # capt push "show int status" to 10.10.10.10
        push_to.add_argument('ip_address', help="specify the IPv4 address of switch")
        push_to.set_defaults(func=self.push_command)
        #  -----
        # capt push "no logging" config
        push_config = push_subparsers.add_parser('config', help="config_t configuration given")
        push_config_subparsers = push_config.add_subparsers()
        # capt push "no logging" config to
        push_config_to = push_config_subparsers.add_parser('to', help="specify the IPv4 address of switch")
        # capt push "no logging" config to 10.10.10.10
        push_config_to.add_argument('ip_address', help="specify the IPv4 address of switch")
        push_config_to.set_defaults(func=self.push_configuration)
        #  -----


        # capt upgrade
        upgrade = subparsers.add_parser('upgrade', help="initiate code upgrade and verify")
        # capt upgrade 10.10.10.10

        args = parser.parse_args()

        if args.sub_command:
            args.func(vars(args))
        else:
            config.load_configuration()
            self.main()


    def main(self):


        switch_ipv4_address_list = config.dev_ipv4_address
        max_threads = int(config.dev_concurrent_threads)

        proc_dict = {}
        proc_dict[config.proc_code_upgrade]   = 'code_upgrade'
        proc_dict[config.proc_push_config]    = 'push_config'
        proc_dict[config.proc_test_api_calls] = 'test_api_calls'
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
                        t = threading.Thread(target=self.upgrade_code, args=(switch_ipv4_address_list[0], config.username,
                                                                config.password, config.cpi_ipv4_address, logger))
                    elif proc_dict['true'] == 'push_config':
                        logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)
                        t = threading.Thread(target=self.push_config(switch_ipv4_address_list[0], config.config_user_exec,
                                                                config.config_priv_exec, config.config_global_config, logger))
                    elif proc_dict['true'] == 'test_api_calls':
                        logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)
                        t = threading.Thread(target=self.test_api_calls, args=(switch_ipv4_address_list[0], config.username,
                                                                config.password, config.cpi_ipv4_address, logger))
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
        api_call = connector(cpi_username, cpi_password, cpi_ipv4_address)

        sw = switch()
        sw.ipv4_address = switch_ipv4_address

        sw.id = api_call.get_dev_id(sw.ipv4_address)

        ####################
        ###### BEFORE ######
        ####################

        ###### 1. check for reachability

        print("{}: TESTING REACHABILITY".format(sw.ipv4_address))

        timeout = time.time() + 60*5 # 5 minute timeout starting now (this is before the code upgrade, so short timeout)
        while not self.reachable(sw, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 5 minutes and switch hasn't responded. Exiting script.".format(sw.ipv4_address))
                sys.exit(1)

        print("")
        print("{}: {}".format(sw.ipv4_address, sw.reachability))


        ##### 2. force sync of switch state

        print("{}: SYNCHRONIZE DEVICE".format(sw.ipv4_address))
        old_sync_time = api_call.get_sync_time(sw.id)
        api_call.sync(sw.ipv4_address) # force a sync!
        time.sleep(5) # don't test for sync status too soon (CPI delay and all that)

        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        while not self.synchronized(sw, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 10 minutes and switch hasn't synced. Exiting script.".format(sw.ipv4_address))
                sys.exit(1)

        print("")
        print("{}: {}".format(sw.ipv4_address, sw.sync_state))

        new_sync_time = api_call.get_sync_time(sw.id)
        if old_sync_time == new_sync_time: # KEEP CODE! needed for corner case issue where force sync fails (e.g. code 03.03.03)
            print("{}: ERROR - sync failed. Cancelling script. Proceed with upgrade manually ***".format(sw.ipv4_address))
            sys.exit(1)

        ###### 3. get current software version

        sw.pre_software_version = api_call.get_software_version(sw.id)
        print("{}: INFO - current version is {}".format(sw.ipv4_address, sw.pre_software_version))


        ###### 4. get stack members

        sw.pre_stack_member = api_call.get_stack_members(sw.id)
        sw.pre_stack_member = sorted(sw.pre_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.

        sw.pre_stack_member_name = [x['name'] for x in sw.pre_stack_member]  # extract name values
        sw.pre_stack_member_desc = [x['description'] for x in sw.pre_stack_member]  # extract description values
        print("{}: STACK MEMBERS - {}".format(sw.ipv4_address, sw.pre_stack_member_name))
        print("{}: STACK MEMBERS - {}".format(sw.ipv4_address, sw.pre_stack_member_desc))

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state

        sw.pre_cdp_neighbour = api_call.get_cdp_neighbours(sw.id)
        sw.pre_cdp_neighbour = sorted(sw.pre_cdp_neighbour, key=lambda k: k['nearEndInterface']) # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions

        sw.pre_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.pre_cdp_neighbour] # extract nearEnd values
        print("{}: CDP NEIGHOURS - {}".format(sw.ipv4_address, sw.pre_cdp_neighbour_nearend))

        print("")
        print("{}: PRE-PROCESSING COMPLETE".format(sw.ipv4_address))

        ####################
        ###### RELOAD ######
        ####################

        print("{}: REBOOTING".format(sw.ipv4_address))
        api_call.reload_switch(sw.id, "1")
        time.sleep(10)

        ###################
        ###### AFTER ######
        ###################

        ###### 1. check for reachability

        print("{}: TESTING REACHABILITY".format(sw.ipv4_address))

        timeout = time.time() + 60*45 # 45 minute timeout starting now
        while not self.reachable(sw, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: CRITICAL - 45 minutes and switch hasn't responded. Exiting script.".format(sw.ipv4_address))
                sys.exit(1)

        print("\n")
        print("{}: {}".format(sw.ipv4_address, sw.reachability))

        ##### 2. force sync of switch state

        print("{}: SYNCHRONIZE DEVICE".format(sw.ipv4_address))
        old_sync_time = api_call.get_sync_time(sw.id)
        api_call.sync(sw.ipv4_address)  # force a sync!
        time.sleep(5)  # don't test for sync status too soon (CPI delay and all that)

        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        while not self.synchronized(sw, api_call):
            print('.', end='', flush=True)
            time.sleep(5)
            if time.time() > timeout:
                print("")
                print("{}: ERROR - 10 minutes and switch hasn't synced. Exiting script.".format(sw.ipv4_address))
                sys.exit(1)

        print("")
        print("{}: {}".format(sw.ipv4_address, sw.sync_state))

        new_sync_time = api_call.get_sync_time(sw.id)
        if old_sync_time == new_sync_time:  # needed for corner case issue where force sync fails (e.g. code 03.03.03)
            print("{}: *** ERROR - sync failed. Cancelling script. Proceed with upgrade manually ***".format(
                sw.ipv4_address))
            sys.exit(1)

        ###### 3. get software version

        sw.post_software_version = api_call.get_software_version(sw.id)
        print("{}: INFO - new version is {}".format(sw.ipv4_address, sw.pre_software_version))

        # compare
        if sw.pre_software_version == sw.post_software_version:
            print("{}: ERROR - software version before and after is the same, {}".format(sw.ipv4_address, sw.post_software_version))
        else:
            print("{}: INFO - old:{} new:{}".format(sw.ipv4_address, sw.pre_software_version, sw.post_software_version))

        ###### 4. get stack members

        sw.post_stack_member = api_call.get_stack_members(sw.id)
        sw.post_stack_member = sorted(sw.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.

        sw.post_stack_member_name = [x['name'] for x in sw.post_stack_member]  # extract name values
        sw.post_stack_member_desc = [x['description'] for x in sw.post_stack_member]  # extract description values
        print("{}: STACK MEMBERS - {}".format(sw.ipv4_address, sw.post_stack_member_name))
        print("{}: STACK MEMBERS - {}".format(sw.ipv4_address, sw.post_stack_member_desc))

        # compare states
        pre_name_diff, post_name_diff = self.compare_list(sw.pre_stack_member_name, sw.post_stack_member_name)
        pre_desc_diff, post_desc_diff = self.compare_list(sw.pre_stack_member_desc, sw.post_stack_member_desc)

        if not pre_name_diff and not post_name_diff and not pre_desc_diff and not post_desc_diff:
            print("INFO: {} stack members are the same before as after".format(sw.ipv4_address))
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
                        print("CRITICAL {} - OS-mismatch or V-mismatch".format(sw.ipv4_address))

        ###### 5. get VLANs
        ### TO-DO
        ##
        #

        ###### 6. get CDP neighbour state

        sw.post_cdp_neighbour = api_call.get_cdp_neighbours(sw.id)
        sw.post_cdp_neighbour = sorted(sw.post_cdp_neighbour, key=lambda k: k['nearEndInterface'])  # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions

        sw.post_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.post_cdp_neighbour]  # extract nearEnd values
        print("{}: CDP NEIGHOURS - {}".format(sw.ipv4_address, sw.post_cdp_neighbour_nearend))

        # compare states
        pre_cdp_diff, post_cdp_diff = self.compare_list(sw.pre_cdp_neighbour_nearend, sw.post_cdp_neighbour_nearend)

        if not pre_cdp_diff and not post_cdp_diff:
            print("INFO: {} CDP neighbours are the same before as after".format(sw.ipv4_address))
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_cdp_diff:
                print("Neighbour(s) no longer exist! {}".format(pre_cdp_diff))
            # if the name difference exists after but not before ... switch was found???
            if post_cdp_diff:
                print("Neighbour(s) detected AFTER code upgrade! {}".format(post_cdp_diff))

        print("")
        print("{}: POST-PROCESSING COMPLETE".format(sw.ipv4_address))
        return True

    def push_command(self, *args):

        os.system("swITch -ea auth.txt -c \"{}\" -i \"{},cisco_ios\"".format(args[0]['cisco_config'], args[0]['ip_address']))


    def push_configuration(self, *args):

        print("Need to update swITch.py to work with new netmiko config parameter to push configuration code")

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

    def reachable(self, sw, api_call):

        if not self.ping(sw.ipv4_address):
            sw.reachability = "UNREACHABLE"
            return False
        elif self.ping(sw.ipv4_address) and api_call.get_reachability(sw.id) == "REACHABLE":
            sw.reachability = "REACHABLE"
            return True
        else: # in-between condition where switch is pingable, but CPI device hasn't moved to REACHABLE
            sw.reachability = api_call.get_reachability(sw.id)
            return False

    def synchronized(self, sw, api_call):

        if api_call.get_sync_status(sw.id) == "COMPLETED":
            sw.sync_state = "COMPLETED"
            return True
        elif api_call.get_sync_status(sw.id) == "SYNCHRONIZING":
            sw.sync_state = "SYNCHRONIZING"
            return False
        else:
            sw.sync_state = api_call.get_sync_status(sw.id)
            print("unexpected sync state: {}".format(sw.sync_state))
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

        api_call = connector(cpi_username, cpi_password, cpi_ipv4_address)

        sw = switch()
        sw.ipv4_address = switch_ipv4_address
        sw.id = api_call.get_dev_id(sw.ipv4_address)

        # # force sync device,need NBI_WRITE access
        # api_call.sync(switch_ipv4_address)
        #
        # # get reachability status
        # dev_reachability = api_call.get_reachability(sw.id)
        # print(json.dumps(dev_reachability, indent=4))
        #
        # # get software version
        # dev_software_version = api_call.get_software_version(sw.id)
        # print(json.dumps(dev_software_version, indent=4))
        #
        # # get switch stack info
        #dev_stack_info = api_call.get_stack_members(sw.id)
        #print(json.dumps(dev_stack_info, indent=4))
        # sw.pre_stack_member = api_call.get_stack_members(sw.id)
        # sw.pre_stack_member = sorted(sw.pre_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        #
        # sw.pre_stack_member_name = [x['name'] for x in sw.pre_stack_member]  # extract name values
        # sw.pre_stack_member_desc = [x['description'] for x in sw.pre_stack_member]  # extract description values
        # logger.info("stack member(s): {}".format(sw.pre_stack_member_name))
        # logger.info("stack member(s): {}".format(sw.pre_stack_member_desc))
        # logger.debug("ALJSFL:KSJDL:KSJDFL:")

        # sys.exit(1)
        #
        # input("Press enter to sync ...")
        #
        # #api_call.sync(sw.ipv4_address)
        # #time.sleep(5)
        # timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        # while not self.synchronized(sw, api_call):
        #     print('.', end='', flush=True)
        #     time.sleep(5)
        #     if time.time() > timeout:
        #         print("")
        #         print("{}: ERROR - 10 minutes and switch hasn't synced. Exiting script.".format(sw.ipv4_address))
        #         sys.exit(1)
        # print("")
        #
        # sw.post_stack_member = api_call.get_stack_members(sw.id)
        # sw.post_stack_member = sorted(sw.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        #
        # sw.post_stack_member_name = [x['name'] for x in sw.post_stack_member]  # extract name values
        # sw.post_stack_member_desc = [x['description'] for x in sw.post_stack_member]  # extract description values
        # print("{}: STACK MEMBERS - {}".format(sw.ipv4_address, sw.post_stack_member_name))
        # print("{}: STACK MEMBERS - {}".format(sw.ipv4_address, sw.post_stack_member_desc))
        #
        # ##### compare states
        # # the switch 'name' (e.g. 'Switch 1') is used to test switch
        #
        # pre_name_diff, post_name_diff = self.compare_list(sw.pre_stack_member_name, sw.post_stack_member_name)
        # pre_desc_diff, post_desc_diff = self.compare_list(sw.pre_stack_member_desc, sw.post_stack_member_desc)
        #
        # # if the name difference exists before but not after ... switch is missing!
        # if pre_name_diff:
        #     print("Switch(es) no longer exists in stack! {}".format(pre_name_diff))
        # # if the name difference exists after but not before ... switch was found???
        # if post_name_diff:
        #     print("New switch(es) detected AFTER code upgrade! {}".format(post_name_diff))
        # # if the description diff exists before and after, then "Provisioned" was tacked on or removed
        # if pre_desc_diff and post_desc_diff:
        #     for d in post_desc_diff:
        #         if "Provisioned" in d:
        #             print("CRITICAL {} - OS-mismatch or V-mismatch".format(sw.ipv4_address))
        #
        # if not pre_name_diff and not post_name_diff and not pre_desc_diff and not post_desc_diff:
        #     print("INFO: {} stack members are the same before as after".format(sw.ipv4_address))
        #
        # # CDP neighbour call
        #dev_cdp_neighbours = api_call.get_cdp_neighbours(sw.id)
        #cdp_neighbours_list = dev_cdp_neighbours
        #print(json.dumps(dev_cdp_neighbours, indent=4))
        # sorted_list = sorted(cdp_neighbours_list, key=lambda k: k['interfaceIndex']) # sort the list of dicts
        # sorted_interfaceIndex = [x['interfaceIndex'] for x in sorted_list] # extract interfaceIndex values
        #
        # data = next((item for item in dev_cdp_neighbours if item["neighborDeviceName"] == "SEPC0626BD2690F"))
        # print(data)
        #
        # print basic switch information
        #api_call.print_info(sw.id)
        #
        # #print detailed switch information
        #api_call.print_detailed_info(sw.id)
        #
        # # print client summary
        # api_call.print_client_summary(sw.id)

        # get switch ports
        # tmp = api_call.get_switch_ports(sw.id)
        # #sorted_list = sorted(tmp, key=lambda k: k['ethernetInterface'])  # sort the list of dicts
        # #key = [x['accessVlan'] for x in sorted_list]  # extract interfaceIndex values
        # print(json.dumps(tmp, indent=4))
        #
        # reboot switch
        api_call.reload_switch(sw.id, "1")

    def test(self, input):
        print('huzzah')
        print(input)

if __name__ == '__main__':

    capt()
