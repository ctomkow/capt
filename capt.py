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

        parser.add_argument('-v', '--verbose', action='store_true', required=False, help="debug output")

        subparsers = parser.add_subparsers(dest="sub_command")

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

        # test api calls
        test = subparsers.add_parser('test_api', help="API testing")

        args = parser.parse_args()

        if args.sub_command:
            logger = self.set_logger(args.ip_address, logging.INFO)
            args.func(args, logger)
        else:
            config.load_configuration()
            self.main(args.verbose)

    def main(self, verbose):

        # instantiate system logger (separate from device loggers)
        if verbose:
            sys_logger = self.set_logger("system_log", logging.DEBUG)
        else:
            sys_logger = self.set_logger("system_log", logging.INFO)

        switch_ipv4_address_list = config.dev_ipv4_address
        max_threads = int(config.dev_concurrent_threads)

        proc_dict = {}

        # only add procedures that are selected
        if config.proc_code_upgrade:
            proc_dict['code_upgrade'] = config.proc_code_upgrade
        if config.proc_push_command:
            proc_dict['push_command'] = config.proc_push_command
        if config.proc_push_configuration:
            proc_dict['push_configuration'] = config.proc_push_configuration
        if config.proc_test_api_calls:
            proc_dict['test_api_calls'] = config.proc_test_api_calls

        if len(proc_dict) > 1 or len(proc_dict) < 1:
            sys_logger.error("Too many or too few procedures selected.")
            sys.exit(1)

        threads = []

        while len(switch_ipv4_address_list) > 0:

            # check if thread is alive, if not, remove from list
            threads = [t for t in threads if t.is_alive()]
            t_count = len(threads)

            # spawn thread if max concurrent number is not reached
            if t_count < max_threads:

                # instantiate per-thread/device logger (separate from system logger)
                if verbose:
                    logger = self.set_logger(switch_ipv4_address_list[0], logging.DEBUG)
                else:
                    logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)

                try:
                    if 'code_upgrade' in proc_dict:
                        t = threading.Thread(target=self.upgrade_code, args=(switch_ipv4_address_list[0], config.username,
                                                                config.password, config.cpi_ipv4_address, logger))
                    elif 'push_command' in proc_dict:
                        t = threading.Thread(target=self.push_command(switch_ipv4_address_list[0], config.config_command, logger))
                    elif 'push_configuration' in proc_dict:
                        t = threading.Thread(target=self.push_configuration(switch_ipv4_address_list[0], config.config_configuration, logger))
                    elif 'test_api_calls' in proc_dict:
                        t = threading.Thread(target=self.test_api_calls, args=(switch_ipv4_address_list[0], config.username,
                                                                config.password, config.cpi_ipv4_address, logger))
                except KeyError:
                    sys_logger.critical("Thread failed to execute function.")
                    sys.exit(1)

                threads.append(t)
                t.start()
                t_count += 1

                sys_logger.debug("Thread count: {}".format(t_count))

                switch_ipv4_address_list.pop()  # remove referenced switch

                # when last device is popped off list, wait for ALL threads to finish
                if len(switch_ipv4_address_list) == 0:
                    for t in threads:
                        t.join()

    def upgrade_code(self, switch_ipv4_address, cpi_username, cpi_password, cpi_ipv4_address, logger):

        logger.info("Initiate code upgrade.")

        #--------------------------#
        #      PRE_PROCESSING      #
        #--------------------------#
        api_call = connector(cpi_username, cpi_password, cpi_ipv4_address)

        sw = switch()
        sw.ipv4_address = switch_ipv4_address

        sw.id = api_call.get_dev_id(sw.ipv4_address)

        #--------------------------#
        #   PRE_STATE_COLLECTION   #
        #--------------------------#

        # 1. check for reachability
        logger.info("Testing reachability ...")
        timeout = time.time() + 60*5 # 5 minute timeout starting now (this is before the code upgrade, so short timeout)
        logger.info("Timeout set to {} minutes.".format(5))

        while not self.reachable(sw, api_call, logger):
            time.sleep(5)
            logger.debug("Switch reachability state: {}".format(sw.reachability))
            if time.time() > timeout:
                logger.critical("Timed out. Not reachable.")
                sys.exit(1)

        logger.debug("Switch reachability state: {}".format(sw.reachability))
        logger.info("Reachable!")

        # 2. force sync of switch state
        logger.info("Synchronizing ...")
        old_sync_time = api_call.get_sync_time(sw.id)
        api_call.sync(sw.ipv4_address) # force a sync!
        time.sleep(5) # don't test for sync status too soon (CPI delay and all that)
        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        logger.info("Timeout set to {} minutes.".format(10))

        while not self.synchronized(sw, api_call, logger):
            time.sleep(5)
            logger.debug("Switch sync state: {}".format(sw.sync_state))
            if time.time() > timeout:
                logger.critical("Timed out. Sync failed.")
                sys.exit(1)

        new_sync_time = api_call.get_sync_time(sw.id)
        if old_sync_time == new_sync_time: # KEEP CODE! needed for corner case issue where force sync fails (e.g. code 03.03.03)
            logger.critical("Before and after sync time is the same. Sync failed.")
            sys.exit(1)

        logger.debug("switch sync state: {}".format(sw.sync_state))
        logger.info("Synchronized!")

        # 3. get current software version
        sw.pre_software_version = api_call.get_software_version(sw.id)
        logger.info("Software version: {}".format(sw.pre_software_version))

        # 4. get stack members
        logger.info("Getting stack members ...")
        sw.pre_stack_member = api_call.get_stack_members(sw.id)
        sw.pre_stack_member = sorted(sw.pre_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.

        sw.pre_stack_member_name = [x['name'] for x in sw.pre_stack_member]  # extract name values
        sw.pre_stack_member_desc = [x['description'] for x in sw.pre_stack_member]  # extract description values

        logger.debug("Stack member names: {}".format(sw.pre_stack_member_name))
        logger.debug("Stack member descriptions: {}".format(sw.pre_stack_member_desc))
        logger.info("Stack members stored!")

        # 5. get VLANs
        # TO-DO
        #
        #

        # 6. get CDP neighbour state
        logger.info("Getting CDP neighbours ...")
        sw.pre_cdp_neighbour = api_call.get_cdp_neighbours(sw.id)
        sw.pre_cdp_neighbour = sorted(sw.pre_cdp_neighbour, key=lambda k: k['nearEndInterface']) # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions
        sw.pre_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.pre_cdp_neighbour] # extract nearEnd values

        #logger.debug("CDP neighbours: {}".format(sw.pre_cdp_neighbour))
        logger.debug("CDP neighbours near-end: {}".format(sw.pre_cdp_neighbour_nearend))
        logger.info("CDP neighbours stored!")

        # 7. test VoIP reachability
        logger.info("Testing phone reachability ...")
        sw.phones = []
        for c in sw.pre_cdp_neighbour:
            if "IP Phone" in c['neighborDevicePlatformType']:
                sw.phones.append(c['neighborDeviceName'])

        # test phone connectivity
        for p in sw.phones:
            logger.debug("phone: {}".format(p))
            if not self.ping("{}.voip.ualberta.ca".format(p), logger):
                logger.info("{} phone is not pingable, removing from list")
                sw.phones.remove(p)

        logger.debug("CDP neighbour phones: {}".format(sw.phones))
        logger.info("Phone reachability tested.")

        logger.info("State collection complete!")

        #--------------------------#
        #          RELOAD          #
        #--------------------------#

        logger.info("Reloading ...")
        job_id = api_call.reload_switch(sw.id, "1")
        logger.debug("Reload job_id: {}".format(job_id))
        timeout = time.time() + 60 * 5  # 5 minute timeout starting now
        time.sleep(90)  # Prime template needs a 1 minute delay before rebooting, so wait 90 seconds so reachability test doesn't false-positive
        while not api_call.job_complete(job_id): # while not completed ... wait...
            time.sleep(5)
            if time.time() > timeout:
                logger.critical("Timed out. CPI job failed.")
                sys.exit(1)

        logger.debug("Finished job_id: {}".format(job_id))

        # DON'T CHECK IF JOB WAS SUCCESSFUL, IT FAILS CAUSE SWITCH DROPS CONNECTIVITY WHEN REBOOTING
        # if api_call.job_successful(job_id):
        #     print("reload job successful")
        # else:
        #     print("reload job failed! exiting!")
        #     sys.exit(1)

        #--------------------------#
        #   POST_STATE_COLLECTION  #
        #--------------------------#

        # 1. check for reachability
        logger.info("Testing reachability ...")
        timeout = time.time() + 60*45 # 45 minute timeout starting now
        logger.info("Timeout set to {} minutes.".format(45))
        while not self.reachable(sw, api_call, logger):
            time.sleep(5)
            logger.debug("Switch reachability state: {}".format(sw.reachability))
            if time.time() > timeout:
                logger.critical("Timed out. Not reachable.")
                sys.exit(1)

        logger.debug("Switch reachability state: {}".format(sw.reachability))
        logger.info("Reachable!")

        # 2. force sync of switch state
        logger.info("Synchronizing ...")
        old_sync_time = api_call.get_sync_time(sw.id)
        api_call.sync(sw.ipv4_address)  # force a sync!
        time.sleep(20)  # don't test for sync status too soon (CPI delay and all that)
        timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        logger.info("Timeout set to {} minutes.".format(10))

        while not self.synchronized(sw, api_call, logger):
            time.sleep(5)
            logger.debug("Switch sync state: {}".format(sw.sync_state))
            if time.time() > timeout:
                logger.critical("Timed out. Sync failed.")
                sys.exit(1)

        new_sync_time = api_call.get_sync_time(sw.id)
        if old_sync_time == new_sync_time:  # KEEP CODE! needed for corner case issue where force sync fails (e.g. code 03.03.03)
            logger.critical("Before and after sync time is the same. Sync failed.")
            sys.exit(1)

        logger.debug("switch sync state: {}".format(sw.sync_state))
        logger.info("Synchronized!")

        # 3. get software version
        sw.post_software_version = api_call.get_software_version(sw.id)
        logger.info("Software version: {}".format(sw.post_software_version))

        # compare
        logger.info("Comparing software version states ...")
        if sw.pre_software_version == sw.post_software_version:
            logger.debug("Pre-software: {}".format(sw.pre_software_version))
            logger.debug("Post-software: {}".format(sw.post_software_version))
            logger.error("Upgrade failed. Software is same as before.")
        else:
            logger.info("Software is different (whew).")

        # 4. get stack members
        logger.info("Getting stack members ...")
        sw.post_stack_member = api_call.get_stack_members(sw.id)
        sw.post_stack_member = sorted(sw.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts

        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.

        sw.post_stack_member_name = [x['name'] for x in sw.post_stack_member]  # extract name values
        sw.post_stack_member_desc = [x['description'] for x in sw.post_stack_member]  # extract description values

        logger.debug("Stack member names: {}".format(sw.post_stack_member_name))
        logger.debug("Stack member descriptions: {}".format(sw.post_stack_member_desc))
        logger.info("Stack members stored!")

        # compare states
        logger.info("Comparing stack member states ...")
        pre_name_diff, post_name_diff = self.compare_list(sw.pre_stack_member_name, sw.post_stack_member_name, logger)
        pre_desc_diff, post_desc_diff = self.compare_list(sw.pre_stack_member_desc, sw.post_stack_member_desc, logger)

        if not pre_name_diff and not post_name_diff and not pre_desc_diff and not post_desc_diff:
            logger.info("Stack members are the same pre/post (noice).")
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_name_diff:
                logger.error("Stack member(s) no longer part of stack!")
                logger.error(pre_name_diff)
            # if the name difference exists after but not before ... switch was found???
            if post_name_diff:
                logger.error("New stack member(s) found!? after upgrade.")
                logger.error(post_name_diff)
            # if the description diff exists before and after, then "Provisioned" was tacked on or removed
            if pre_desc_diff and post_desc_diff:
                for d in post_desc_diff:
                    if "Provisioned" in d:
                        logger.error("Stack member has OS-mismatch or V-mismatch!")

        # 5. get VLANs
        # TO-DO
        #
        #

        # 6. get CDP neighbour state
        logger.info("Getting CDP neighbours ...")
        sw.post_cdp_neighbour = api_call.get_cdp_neighbours(sw.id)
        sw.post_cdp_neighbour = sorted(sw.post_cdp_neighbour, key=lambda k: k['nearEndInterface'])  # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions
        sw.post_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.post_cdp_neighbour]  # extract nearEnd values

        #logger.debug("CDP neighbours: {}".format(sw.post_cdp_neighbour))
        logger.debug("CDP neighbours near-end: {}".format(sw.post_cdp_neighbour_nearend))
        logger.info("CDP neighbours stored!")

        # compare states
        logger.info("Comparing CDP neighbour states ...")
        pre_cdp_diff, post_cdp_diff = self.compare_list(sw.pre_cdp_neighbour_nearend, sw.post_cdp_neighbour_nearend, logger)

        if not pre_cdp_diff and not post_cdp_diff:
            logger.info("CDP neighour(s) are the same pre/post (noice).")
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_cdp_diff:
                logger.error("CDP neighbour(s) no longer exist!")
                logger.error(pre_cdp_diff)
            # if the name difference exists after but not before ... switch was found???
            if post_cdp_diff:
                logger.warning("CDP neighbour(s) found?! after upgrade.")
                logger.warning(post_cdp_diff)

        # 7. test VoIP reachability
        logger.info("Testing phone reachability ...")

        # test phone connectivity
        for p in sw.phones:
            logger.debug("phone: {}".format(p))
            if not self.ping("{}.voip.ualberta.ca".format(p), logger):
                logger.error("{}.voip.ualberta.ca is not pingable")

        logger.debug("CDP neighbour phones: {}".format(sw.phones))
        logger.info("Phone reachability testing complete.")

        logger.info("State comparision and upgrade complete!")
        return True

    def push_command(self, *args):

        args[2].info("push command: {}".format(args[1][0]))
        os.system("swITch -ea auth.txt -c \"{}\" -i \"{},cisco_ios\"".format(args[1][0], args[0]))

    def push_configuration(self, *args):

        args[2].info("push configuration: {}".format(args[1][0]))
        print("Need to update swITch.py to work with new netmiko config parameter to push configuration code")

    # needed because Prime is slow to detect connectivity or not
    def ping(self, switch_ipv4_address, logger):

        if platform.system() == "Linux":
            response = os.system("ping -c 1 -W 1 {}>nul".format(switch_ipv4_address))
        elif platform.system() == "Windows":
            response = os.system("ping -n 1 -w 1000 {}>nul".format(switch_ipv4_address))
        else:
            logger.critical("Could not detect system for ping.")
            sys.exit(1)

        # ping program returns 0 on successful ICMP request, >0 on other values (inconsistent other values, can't rely on them)
        if response == 0:
            logger.debug("Ping success")
            return True
        else:
            logger.debug("Ping failed")
            return False

    def reachable(self, sw, api_call, logger):

        if not self.ping(sw.ipv4_address, logger):
            sw.reachability = "UNREACHABLE"
            return False
        elif self.ping(sw.ipv4_address, logger) and api_call.get_reachability(sw.id) == "REACHABLE":
            sw.reachability = "REACHABLE"
            return True
        else: # in-between condition where switch is pingable, but CPI device hasn't moved to REACHABLE
            sw.reachability = api_call.get_reachability(sw.id)
            return False

    def synchronized(self, sw, api_call, logger):

        if api_call.get_sync_status(sw.id) == "COMPLETED":
            sw.sync_state = "COMPLETED"
            return True
        elif api_call.get_sync_status(sw.id) == "SYNCHRONIZING":
            sw.sync_state = "SYNCHRONIZING"
            return False
        else:
            sw.sync_state = api_call.get_sync_status(sw.id)
            logger.warning("Unexpected sync state: {}".format(sw.sync_state))
            return False

    def compare_list(self, list1, list2, logger):

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

        # TESTING METHOD CALLS #

        api_call = connector(cpi_username, cpi_password, cpi_ipv4_address)

        sw = switch()
        sw.ipv4_address = switch_ipv4_address
        sw.id = api_call.get_dev_id(sw.ipv4_address)

        # print("sync")
        # api_call.sync(sw.ipv4_address)  # force a sync!
        # time.sleep(5)  # don't test for sync status too soon (CPI delay and all that)
        # timeout = time.time() + 60 * 10  # 10 minute timeout starting now
        # while not self.synchronized(sw, api_call, logger):
        #     time.sleep(5)
        #     if time.time() > timeout:
        #         logger.critical("Timed out. Sync failed.")
        #         sys.exit(1)

        # cdp_neighbours = api_call.get_cdp_neighbours(sw.id)
        # print(cdp_neighbours)
        phone_list = []
        # for c in cdp_neighbours:
        #     if "IP Phone" in c['neighborDevicePlatformType']:
        #         phone_list.append(c['neighborDeviceName'])
        #     else:
        #         pass
        #
        # print(phone_list)
        #
        # if self.ping("{}.voip.ualberta.ca".format(phone_list.pop()), logger):
        #     print('phone is alive')

if __name__ == '__main__':

    capt()
