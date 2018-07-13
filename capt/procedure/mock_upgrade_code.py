#!/usr/bin/env python3

# the test api procedure

# system imports
import time
import sys

# local imports
from procedure.upgrade_code import UpgradeCode


class MockUpgradeCode(UpgradeCode):

    # override parent method
    def upgrade_code(self, api_call, sw_api_call, ap_api_call, sw, logger):

        logger.info("Initiate TEST code upgrade.")

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

        logger.info("NO Reloading ...")

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