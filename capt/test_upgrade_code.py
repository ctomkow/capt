#!/usr/bin/env python3

# Craig Tomkow
# June 28, 2018
#
# the test api procedure

# system imports
import time
import sys

# local imports
from upgrade_code import upgrade_code


class test_upgrade_code(upgrade_code):


    # override parent method
    def upgrade_code(self, api_call, sw, logger):
        logger.info("Initiate TEST.")

        # --------------------------#
        #      PRE_PROCESSING      #
        # --------------------------#

        sw.id = api_call.get_switch_id(sw.ipv4_address)

        # --------------------------#
        #   PRE_STATE_COLLECTION   #
        # --------------------------#

        # 1. check for reachability
        logger.info("Testing reachability ...")
        timeout = time.time() + 60 * 5  # 5 minute timeout starting now (this is before the code upgrade, so short timeout)
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
        api_call.sync(sw.ipv4_address)  # force a sync!
        timeout = time.time() + 60 * 20  # 20 minute timeout starting now
        logger.info("Timeout set to {} minutes.".format(20))
        time.sleep(20)  # don't test for sync status too soon (CPI delay and all that)

        while not self.synchronized(sw, api_call, logger):
            time.sleep(10)
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

        # 6. get CDP neighbour state
        logger.info("Getting CDP neighbours ...")
        sw.pre_cdp_neighbour = api_call.get_cdp_neighbours(sw.id)
        sw.pre_cdp_neighbour = sorted(sw.pre_cdp_neighbour,
                                      key=lambda k: k['nearEndInterface'])  # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions
        sw.pre_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.pre_cdp_neighbour]  # extract nearEnd values

        # logger.debug("CDP neighbours: {}".format(sw.pre_cdp_neighbour))
        logger.debug("CDP neighbours near-end: {}".format(sw.pre_cdp_neighbour_nearend))
        logger.info("CDP neighbours stored!")

        # 7. test VoIP reachability
        logger.info("Testing phone reachability ...")
        sw.phones = []
        for c in sw.pre_cdp_neighbour:
            if "IP Phone" in c['neighborDevicePlatformType']:
                sw.phones.append(c['neighborDeviceName'])

        # test phone connectivity
        tmp_phone_list = []  # DON'T MODIFY A LIST YOUR LOOPING THROUGH!
        for p in sw.phones:
            logger.debug("phone: {}".format(p))
            if self.ping("{}.voip.ualberta.ca".format(p), logger):
                tmp_phone_list.append(p)
            else:
                logger.info("{}.voip.ualberta.ca is not pingable".format(p))
        sw.phones = tmp_phone_list

        logger.debug("CDP neighbour phones tested: {}".format(sw.phones))
        logger.info("Phone reachability tested.")

        # 8. test access point reachability
        logger.info("Testing access point reachability ...")
        sw.access_points = []
        for c in sw.pre_cdp_neighbour:
            if "AIR-" in c['neighborDevicePlatformType']:
                sw.access_points.append(c['neighborDeviceName'])

        # test access point connectivity
        sw.test_ap = []
        for a in sw.access_points:
            a = a.split('.')[0]  # Prime returns either "xxxx" or "xxxx.subdomain.domain.tld" for name
            logger.debug("access point: {}".format(a))
            if self.ping(api_call.get_access_point_ip(api_call.get_access_point_id(a)), logger):
                sw.test_ap.append(a)
                break  # access point is pingable, so only keep this one in the list
            else:
                logger.info("{} is not pingable".format(a))

        logger.debug("CDP neighbour access points: {}".format(sw.test_ap))
        logger.info("Access point reachability tested.")

        logger.info("State collection complete!")

        # --------------------------#
        #          RELOAD          #
        # --------------------------#

        logger.info("FAKE RELOAD!")

        # DON'T CHECK IF JOB WAS SUCCESSFUL, IT FAILS CAUSE SWITCH DROPS CONNECTIVITY WHEN REBOOTING
        # if api_call.job_successful(job_id):
        #     print("reload job successful")
        # else:
        #     print("reload job failed! exiting!")
        #     sys.exit(1)

        # --------------------------#
        #   POST_STATE_COLLECTION  #
        # --------------------------#

        # 1. check for reachability
        logger.info("Testing reachability ...")
        timeout = time.time() + 60 * 60  # 60 minute timeout starting now
        logger.info("Timeout set to {} minutes.".format(60))
        count = 0
        while not self.reachable(sw, api_call, logger):
            time.sleep(5)
            if count > 8:  # how often informational logging is displayed
                logger.info("Switch reachability state: {}".format(sw.reachability))
                count = 0
            else:
                count += 1

            if time.time() > timeout:
                logger.critical("Timed out. Not reachable.")
                sys.exit(1)

        logger.debug("Switch reachability state: {}".format(sw.reachability))
        logger.info("Reachable!")

        # 2. force sync of switch state
        logger.info("Synchronizing ...")
        old_sync_time = api_call.get_sync_time(sw.id)
        api_call.sync(sw.ipv4_address)  # force a sync!
        timeout = time.time() + 60 * 20  # 20 minute timeout starting now
        logger.info("Timeout set to {} minutes.".format(20))
        time.sleep(20)  # don't test for sync status too soon (CPI delay and all that)

        while not self.synchronized(sw, api_call, logger):
            time.sleep(10)
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
            logger.warning("Upgrade failed. Software is same as before.")
        else:
            logger.info("Software is different.")

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
            logger.info("Stack members are the same pre/post.")
        else:
            # if the name difference exists before but not after ... switch is missing!
            if pre_name_diff:
                logger.error("Stack member(s) no longer part of stack!")
                logger.error(pre_name_diff)
            # if the name difference exists after but not before ... switch was found? sw powered off, then powered up ... boom, discovered.
            if post_name_diff:
                logger.error("New stack member(s) detected! Could be an issue with a stack member.")
                logger.error(post_name_diff)
            # if the description diff exists before and after, then "Provisioned" was tacked on or removed
            if pre_desc_diff and post_desc_diff:
                for d in post_desc_diff:
                    if "Provisioned" in d:
                        logger.error("Stack member has OS-mismatch or V-mismatch! (or some other issue)")

        # 6. get CDP neighbour state
        logger.info("Getting CDP neighbours ...")
        sw.post_cdp_neighbour = api_call.get_cdp_neighbours(sw.id)
        sw.post_cdp_neighbour = sorted(sw.post_cdp_neighbour,
                                       key=lambda k: k['nearEndInterface'])  # sort the list of dicts

        # Using 'nearEndInterface' key. The 'phyInterface' number changes between code upgrade versions
        sw.post_cdp_neighbour_nearend = [x['nearEndInterface'] for x in sw.post_cdp_neighbour]  # extract nearEnd values

        # logger.debug("CDP neighbours: {}".format(sw.post_cdp_neighbour))
        logger.debug("CDP neighbours near-end: {}".format(sw.post_cdp_neighbour_nearend))
        logger.info("CDP neighbours stored!")

        # compare states
        logger.info("Comparing CDP neighbour states ...")
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

        # 7. test VoIP reachability
        logger.info("Testing phone reachability ...")

        # test phone connectivity
        for p in sw.phones:
            logger.debug("phone: {}".format(p))
            if not self.ping("{}.voip.ualberta.ca".format(p), logger):
                logger.error("{}.voip.ualberta.ca is not pingable".format(p))

        logger.debug("CDP neighbour phones: {}".format(sw.phones))
        logger.info("Phone reachability testing complete.")

        # 8. test access point reachability
        logger.info("Testing access point reachability ...")

        # test access point connectivity
        for a in sw.test_ap:
            logger.debug("access point: {}".format(a))
            if not self.ping(api_call.get_access_point_ip(api_call.get_access_point_id(a)), logger):
                logger.error("{} is not pingable".format(a))

        logger.debug("CDP neighbour access points: {}".format(sw.test_ap))
        logger.info("Access point reachability testing complete.")

        logger.info("State comparision complete. Check all 'error', and 'critical' messages.")
        return True


