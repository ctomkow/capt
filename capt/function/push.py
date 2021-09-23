
# system imports
import sys
import time

# local imports
from function.find import Find
from connector.switch import Switch



class Push:

    def __init__(self):

        self.find = Find()



    def bas(self, args, config, logger):
        # find and display (update this call to work)
        dev_id, found_int, dev_ip = self.find.int(args, config, args.interface, logger)

        # require 'yes' input to proceed
        logger.info('Activate BAS on switch  INTERFACE {} using VLAN: {}'.format(found_int['name'], args.vlan))
        response = input("Confirm action of changing VLAN ('yes'):")
        if not response == 'yes':
            logger.info('Did not proceed with change.')
            sys.exit(1)

        # invoke API call to change VLAN
        sw_api_call = Switch(config.username, config.password, config.cpi_ipv4_address, logger) # create API switch call object

        # push API_CALL_conf_if_bas template out. Update this to use a shared template, the same as change vlan?
        job_id = sw_api_call.conf_if_bas(dev_id, found_int['name'], args.description, args.vlan)

        timeout = time.time() + 30  # 30 second timeout starting now
        time.sleep(1) # without the sleep the job_complete can balk, not finding the job_id yet
        while not sw_api_call.job_complete(job_id):
            time.sleep(5)
            if time.time() > timeout:
                logger.critical("Change VLAN failed. Prime job not completed")
                sys.exit(1)
        if not sw_api_call.job_successful(job_id):
            logger.critical("Change VLAN failed. Prime job not successful")
            sys.exit(1)

        logger.info('Change VLAN complete.')

        ########################################################
        #add a verification flag to sync and display after, instead of default?
        ########################################################
        logger.info("Synchronizing ...")

        self.force_sync(dev_id,dev_ip, sw_api_call, 20, logger)  # 20 minute timeout
        logger.info("Synchronized!")
        dev_id, found_int, dev_ip = self.find.int(args, config, args.interface, logger)

        return args

    # Copies of synchronized and force_sync from upgrade_code.py That uses a constant to hold values though
    def force_sync(self, sw_id,sw_ip, sw_api_call, timeout, logger):
        old_sync_time = sw_api_call.sync_time(sw_id)
        sw_api_call.sync(sw_ip)  # force a sync!
        end_time = time.time() + 60 * timeout
        logger.info("Timeout set to {} minutes.".format(timeout))
        time.sleep(20)  # don't test for sync status too soon (CPI delay and all that)
        while not self.synchronized(sw_id, sw_api_call, logger):
            time.sleep(10)
            if time.time() > end_time:
                logger.critical("Timed out. Sync failed.")
                sys.exit(1)
        new_sync_time = sw_api_call.sync_time(sw_id)
        if old_sync_time == new_sync_time:  # KEEP CODE! needed for corner case where force sync fails (code 03.03.03)
            logger.critical("Before and after sync time is the same. Sync failed.")
            sys.exit(1)

    def synchronized(self, sw_id, sw_api_call, logger):
        if sw_api_call.sync_status(sw_id) == "COMPLETED":
            logger.info("Synchronization Complete!")
            return True
        elif sw_api_call.sync_status(sw_id) == "SYNCHRONIZING":
            return False
        else:
            #sw.sync_state = sw_api_call.sync_status(sw_id)
            logger.warning("Unexpected sync state:")
            return False