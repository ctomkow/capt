
# system imports
import sys
import time

# local imports
from function.find import Find
from connector.switch import Switch

class Push:

    def __init__(self):

        self.find = Find()

    def bas(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):
        # find and display (update this call to work)
        dev_id, found_int = \
            self.find.int(values_dict, cpi_username, cpi_password, cpi_ipv4_address, values_dict['interface'], logger)

        # require 'yes' input to proceed
        logger.info('Activate BAS on switch  INTERFACE {} using VLAN: {}'.format(found_int['name'], values_dict['vlan']))
        response = input("Confirm action of changing VLAN ('yes'):")
        if not response == 'yes':
            logger.info('Did not proceed with change.')
            sys.exit(1)

        # invoke API call to change VLAN
        sw_api_call = Switch(cpi_username, cpi_password, cpi_ipv4_address, logger)
        job_id = sw_api_call.conf_if_bas(dev_id, found_int['name'], values_dict['desc'], values_dict['vlan'])

        timeout = time.time() + 30  # 30 second timeout starting now
        while not sw_api_call.job_complete(job_id):
            time.sleep(5)
            if time.time() > timeout:
                logger.critical("Change VLAN failed. Prime job not completed")
                sys.exit(1)
        if not sw_api_call.job_successful(job_id):
            logger.critical("Change VLAN failed. Prime job not successful")
            sys.exit(1)

        logger.info('Change VLAN complete.')
        #logger.info('Showing new port info:')  # update this to account for sync time of prime DB
#       dev_id, found_int = \
#            self.find.int(values_dict, cpi_username, cpi_password, cpi_ipv4_address, values_dict['interface'], logger)

