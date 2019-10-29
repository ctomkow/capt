#!/usr/bin/env python3

# the upgrade code procedure

# system imports
import time
import os
import sys
import platform

# local imports
from connector.connector import Connector
from connector.switch import Switch as ConnSwitch
from connector.access_point import AccessPoint
from switch import Switch


class UpgradeCode:

    def __init__(self, args, config, logger):

        api_call    = Connector(config, logger)
        sw_api_call = ConnSwitch(config, logger)
        ap_api_call = AccessPoint(config, logger)

        sw = Switch()
        sw.ipv4_address = args.address
        self.upgrade_code(api_call, sw_api_call, ap_api_call, sw, logger)

    def upgrade_code(self, api_call, sw_api_call, ap_api_call, sw, logger):

        logger.info("Initiate code upgrade.")

        # --------------------------#
        #      PRE_PROCESSING      #
        # --------------------------#

        sw.id = sw_api_call.id_by_ip(sw.ipv4_address)

        # --------------------------#
        #   PRE_STATE_COLLECTION   #
        # --------------------------#

        # 1. check for reachability
        logger.info("Testing reachability ...")
        self.check_reachability(sw, sw_api_call, 5, logger)  # 5 minute timeout (before code upgrade, so short timeout)
        logger.debug("Switch reachability state: {}".format(sw.reachability))
        logger.info("Reachable!")

        # 2. force sync of switch state
        logger.info("Synchronizing ...")
        self.force_sync(sw, sw_api_call, 20, logger)  # 20 minute timeout
        logger.debug("switch sync state: {}".format(sw.sync_state))
        logger.info("Synchronized!")

        # 3. get current software version
        logger.info("Getting software version ...")
        self.pre_software_version(sw, sw_api_call, logger)
        logger.info("Software version: {}".format(sw.pre_software_version))

        # 4. get stack members
        logger.info("Getting stack members ...")
        self.pre_stack_member(sw, sw_api_call, logger)
        logger.debug("Stack member names: {}".format(sw.pre_stack_member_name))
        logger.debug("Stack member descriptions: {}".format(sw.pre_stack_member_desc))
        logger.info("Stack members stored!")

        # 5. get CDP neighbour state
        logger.info("Getting CDP neighbours ...")
        self.pre_cdp_neighbour(sw, sw_api_call, logger)
        # logger.debug("CDP neighbours: {}".format(sw.pre_cdp_neighbour))
        logger.debug("CDP neighbours near-end: {}".format(sw.pre_cdp_neighbour_nearend))
        logger.info("CDP neighbours stored!")

        # 6. test VoIP reachability
        logger.info("Getting VoIP phones ...")
        self.voip_phones(sw, sw_api_call, logger)
        logger.info("Testing phone reachability ...")
        self.pre_voip_reachability(sw, sw_api_call, logger)
        logger.debug("CDP neighbour phones tested: {}".format(sw.phones))
        logger.info("Phone reachability tested.")

        # 7. test access point reachability
        logger.info("Getting access points ...")
        self.access_points(sw, ap_api_call, logger)
        logger.info("Testing access point reachability ...")
        self.pre_ap_reachability(sw, ap_api_call, logger)
        logger.debug("CDP neighbour access points: {}".format(sw.test_ap))
        logger.info("Access point reachability tested.")

        # End of Collection
        logger.info("State collection complete!")

        # --------------------------#
        #          RELOAD           #
        # --------------------------#

        logger.info("Reloading ...")
        self.switch_reload(sw, api_call, sw_api_call, 5, logger) # 5 minute timeout

        # --------------------------#
        #   POST_STATE_COLLECTION  #
        # --------------------------#

        # 1. check for reachability
        logger.info("Testing reachability ...")
        self.check_reachability(sw, sw_api_call, 60, logger)  # 60 minute timeout
        logger.debug("Switch reachability state: {}".format(sw.reachability))
        logger.info("Reachable!")

        # 2. force sync of switch state
        logger.info("Synchronizing ...")
        self.force_sync(sw, sw_api_call, 20, logger)  # 20 minute timeout
        logger.debug("switch sync state: {}".format(sw.sync_state))
        logger.info("Synchronized!")

        # 3. get software version
        self.post_software_version(sw, sw_api_call, logger)
        logger.info("Software version: {}".format(sw.post_software_version))

        logger.info("Comparing software version states ...")
        self.software_comparision(sw, logger)

        # 4. get stack members
        logger.info("Getting stack members ...")
        self.post_stack_member(sw, sw_api_call, logger)
        logger.debug("Stack member names: {}".format(sw.post_stack_member_name))
        logger.debug("Stack member descriptions: {}".format(sw.post_stack_member_desc))
        logger.info("Stack members stored!")

        logger.info("Comparing stack member states ...")
        self.stack_member_comparision(sw, logger)

        # 5. get CDP neighbour state
        logger.info("Getting CDP neighbours ...")
        self.post_cdp_neighbour(sw, sw_api_call, logger)
        # logger.debug("CDP neighbours: {}".format(sw.post_cdp_neighbour))
        logger.debug("CDP neighbours near-end: {}".format(sw.post_cdp_neighbour_nearend))
        logger.info("CDP neighbours stored!")

        logger.info("Comparing CDP neighbour states ...")
        self.cdp_comparision(sw, logger)

        # 6. test VoIP reachability
        logger.info("Testing phone reachability ...")
        self.post_voip_reachability(sw, sw_api_call, logger)
        logger.debug("CDP neighbour phones tested: {}".format(sw.phones))
        logger.info("Phone reachability tested.")

        # 7. test access point reachability
        logger.info("Testing access point reachability ...")
        self.post_ap_reachability(sw, ap_api_call, logger)
        logger.debug("CDP neighbour access points: {}".format(sw.test_ap))
        logger.info("Access point reachability tested.")

        # End of Testing
        logger.info("Complete. Check all 'error', and 'critical' messages.")
        return True

    # Step 1
    def check_reachability(self, sw, sw_api_call, timeout, logger):

        logger.info("Timeout set to {} minutes.".format(timeout))
        end_time = time.time() + 60 * timeout
        count = 0
        while not self.reachable(sw, sw_api_call, logger):
            time.sleep(5)
            logger.debug("Switch reachability state: {}".format(sw.reachability))

            if count > 8:  # how often informational logging is displayed
                logger.info("Switch reachability state: {}".format(sw.reachability))
                count = 0
            else:
                count += 1

            if time.time() > end_time:
                logger.critical("Timed out. Not reachable.")
                sys.exit(1)

    # Step 2
    def force_sync(self, sw, sw_api_call, timeout, logger):

        old_sync_time = sw_api_call.sync_time(sw.id)
        sw_api_call.sync(sw.ipv4_address)  # force a sync!
        end_time = time.time() + 60 * timeout
        logger.info("Timeout set to {} minutes.".format(timeout))
        time.sleep(20)  # don't test for sync status too soon (CPI delay and all that)
        while not self.synchronized(sw, sw_api_call, logger):
            time.sleep(10)
            logger.debug("Switch sync state: {}".format(sw.sync_state))
            if time.time() > end_time:
                logger.critical("Timed out. Sync failed.")
                sys.exit(1)
        new_sync_time = sw_api_call.sync_time(sw.id)
        if old_sync_time == new_sync_time:  # KEEP CODE! needed for corner case where force sync fails (code 03.03.03)
            logger.critical("Before and after sync time is the same. Sync failed.")
            sys.exit(1)

    # Step 3
    def pre_software_version(self, sw, sw_api_call, logger):

        sw.pre_software_version = sw_api_call.software_version(sw.id)

    def post_software_version(self, sw, sw_api_call, logger):

        sw.post_software_version = sw_api_call.software_version(sw.id)

    def software_comparision(self, sw, logger):

        if sw.pre_software_version == sw.post_software_version:
            logger.debug("Pre-software: {}".format(sw.pre_software_version))
            logger.debug("Post-software: {}".format(sw.post_software_version))
            logger.warning("Upgrade failed. Software is same as before.")
        else:
            logger.info("Software is different.")

    # Step 4
    def pre_stack_member(self, sw, sw_api_call, logger):

        sw.pre_stack_member = sw_api_call.stack_members(sw.id)
        sw.pre_stack_member = sorted(sw.pre_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.
        sw.pre_stack_member_name = [x['name'] for x in sw.pre_stack_member]  # extract name values
        sw.pre_stack_member_desc = [x['description'] for x in sw.pre_stack_member]  # extract description values

    def post_stack_member(self, sw, sw_api_call, logger):

        sw.post_stack_member = sw_api_call.stack_members(sw.id)
        sw.post_stack_member = sorted(sw.post_stack_member, key=lambda k: k['name'])  # sort the list of dicts
        # the switch 'name' (e.g. 'Switch 1') is used to test switch existence (e.g. powered off, not detected at all)
        # the switch 'description' (e.g. 'WS-3650-PD-L') is used to detect OS-mismatch or V-mismatch
        #     CPI appends the "Provisioned" word onto the description ... that's how I know there is a mismatch, sigh.
        sw.post_stack_member_name = [x['name'] for x in sw.post_stack_member]  # extract name values
        sw.post_stack_member_desc = [x['description'] for x in sw.post_stack_member]  # extract description values

    def stack_member_comparision(self, sw, logger):

        pre_name_diff, post_name_diff = self.compare_list(sw.pre_stack_member_name, sw.post_stack_member_name, logger)
        pre_desc_diff, post_desc_diff = self.compare_list(sw.pre_stack_member_desc, sw.post_stack_member_desc, logger)

        if not pre_name_diff and not post_name_diff and not pre_desc_diff and not post_desc_diff:
            logger.info("Stack members are the same pre/post.")
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_name_diff:
                logger.error("Stack member(s) no longer part of stack!")
                logger.error(pre_name_diff)
            # if the name difference exists after but not before ... switch was found? sw powered off, then powered up
            if post_name_diff:
                logger.error("New stack member(s) detected! Could be an issue with a stack member.")
                logger.error(post_name_diff)
            # if the description diff exists before and after, then "Provisioned" was tacked on or removed
            if pre_desc_diff and post_desc_diff:
                for d in post_desc_diff:
                    if "Provisioned" in d:
                        logger.error("Stack member has OS-mismatch or V-mismatch! (or some other issue)")

    # Step 5
    def pre_cdp_neighbour(self, sw, sw_api_call, logger):

        sw.pre_cdp_neighbour = sw_api_call.cdp_neighbours(sw.id)
        sw.pre_cdp_neighbour = sorted(sw.pre_cdp_neighbour,
                                      key=lambda k: k['nearEndInterface'])  # sort the list of dicts
        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions
        sw.pre_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.pre_cdp_neighbour]  # extract nearEnd values

    def post_cdp_neighbour(self, sw, sw_api_call, logger):

        sw.post_cdp_neighbour = sw_api_call.cdp_neighbours(sw.id)
        sw.post_cdp_neighbour = sorted(sw.post_cdp_neighbour,
                                       key=lambda k: k['nearEndInterface'])  # sort the list of dicts
        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions
        sw.post_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.post_cdp_neighbour]  # extract nearEnd values

    def cdp_comparision(self, sw, logger):

        pre_cdp_diff, post_cdp_diff = self.compare_list(sw.pre_cdp_neighbour_nearend, sw.post_cdp_neighbour_nearend,
                                                        logger)

        if not pre_cdp_diff and not post_cdp_diff:
            logger.info("CDP neighour(s) are the same pre/post.")
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_cdp_diff:
                logger.error("CDP neighbour(s) no longer exist!")
                logger.error(pre_cdp_diff)
            # if the name difference exists after but not before ... switch was found???
            if post_cdp_diff:
                logger.warning("CDP neighbour(s) found?! after upgrade.")
                logger.warning(post_cdp_diff)

    # Step 6
    def voip_phones(self, sw, sw_api_call, logger):

        sw.phones = []
        for c in sw.pre_cdp_neighbour:
            if "IP Phone" in c['neighborDevicePlatformType']:
                sw.phones.append(c['neighborDeviceName'])

    def pre_voip_reachability(self, sw, sw_api_call, logger):

        # test phone connectivity
        tmp_phone_list = []  # DON'T MODIFY A LIST YOUR LOOPING THROUGH!
        for p in sw.phones:
            logger.debug("phone: {}".format(p))
            if self.ping("{}.voip.ualberta.ca".format(p), logger):
                tmp_phone_list.append(p)
            else:
                logger.info("{}.voip.ualberta.ca is not pingable".format(p))
        sw.phones = tmp_phone_list

    def post_voip_reachability(self, sw, sw_api_call, logger):

        for p in sw.phones:
            logger.debug("phone: {}".format(p))
            if not self.ping("{}.voip.ualberta.ca".format(p), logger):
                logger.error("{}.voip.ualberta.ca is not pingable".format(p))

    # Step 7
    def access_points(self,sw, ap_api_call, logger):

        sw.access_points = []
        for c in sw.pre_cdp_neighbour:
            if "AIR-" in c['neighborDevicePlatformType']:
                sw.access_points.append(c['neighborDeviceName'])

    def pre_ap_reachability(self, sw, ap_api_call, logger):

        sw.test_ap = []
        for a in sw.access_points:
            a = a.split('.')[0]  # Prime returns either "xxxx" or "xxxx.subdomain.domain.tld" for name
            logger.debug("access point: {}".format(a))
            if self.ping(ap_api_call.ip_by_id(ap_api_call.id_by_ip(a)), logger):
                sw.test_ap.append(a)
                break  # access point is pingable, so only keep this one in the list
            else:
                logger.info("{} is not pingable".format(a))

    def post_ap_reachability(self, sw, ap_api_call, logger):

        for a in sw.test_ap:
            logger.debug("access point: {}".format(a))
            if not self.ping(ap_api_call.ip_by_id(ap_api_call.id_by_ip(a)), logger):
                logger.error("{} is not pingable".format(a))

    # (reload)Step 8
    def switch_reload(self, sw, api_call, sw_api_call, timeout, logger):

        job_id = sw_api_call.reload(sw.id, "1")
        logger.debug("Reload job_id: {}".format(job_id))
        end_time = time.time() + 60 * timeout
        time.sleep(90)  # Prime template needs a 1 minute delay before rebooting, so wait 90 seconds
        while not api_call.job_complete(job_id):
            time.sleep(5)
            if time.time() > end_time:
                logger.critical("Timed out. CPI job failed.")
                sys.exit(1)
        logger.debug("Finished job_id: {}".format(job_id))


    # --- Helper methods --- #

    # needed because Prime is slow to detect connectivity or not
    def ping(self, switch_ipv4_address, logger):
        if platform.system() == "Linux":
            response = os.system("ping -c 1 -W 1 {}>nul".format(switch_ipv4_address))
        elif platform.system() == "Windows":
            response = os.system("ping -n 1 -w 1000 {}>nul".format(switch_ipv4_address))
        else:
            logger.critical("Could not detect system for ping.")
            sys.exit(1)

        # ping program returns 0 on successful ICMP request, >0 on other values (inconsistent other values)
        if response == 0:
            logger.debug("Ping success")
            return True
        else:
            logger.debug("Ping failed")
            return False

    def reachable(self, sw, sw_api_call, logger):
        if not self.ping(sw.ipv4_address, logger):
            sw.reachability = "UNREACHABLE"
            return False
        elif self.ping(sw.ipv4_address, logger) and sw_api_call.reachability(sw.id) == "REACHABLE":
            sw.reachability = "REACHABLE"
            return True
        else:  # in-between condition where switch is pingable, but CPI device hasn't moved to REACHABLE
            sw.reachability = sw_api_call.reachability(sw.id)
            return False

    def synchronized(self, sw, sw_api_call, logger):
        if sw_api_call.sync_status(sw.id) == "COMPLETED":
            sw.sync_state = "COMPLETED"
            return True
        elif sw_api_call.sync_status(sw.id) == "SYNCHRONIZING":
            sw.sync_state = "SYNCHRONIZING"
            return False
        else:
            sw.sync_state = sw_api_call.sync_status(sw.id)
            logger.warning("Unexpected sync state: {}".format(sw.sync_state))
            return False

    def compare_list(self, list1, list2, logger):
        diff_list1 = []
        diff_list2 = []

        if list1 == list2:
            return diff_list1, diff_list2  # empty list evaluates to boolean False

        diff = sorted(list(set(list1).symmetric_difference(set(list2))))

        # determine which list contains the difference
        for d in diff:
            if d in list1:
                diff_list1.append(d)
            if d in list2:
                diff_list2.append(d)

        return diff_list1, diff_list2
