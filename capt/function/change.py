
# system imports
import sys
import time

# local imports
from function.find import Find
from connector.switch import Switch


class Change:

    def __init__(self):

        self.find = Find()

    def mac_vlan(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):

        # find and display
        neigh_name, neigh_ip, interface, description, old_vlan, old_vlan_name, addr = \
            self.find.mac_client(values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger)

        # require 'yes' input to proceed
        logger.info('Change VLAN to: {}'.format(values_dict['vlan']))
        response = input("Confirm action of changing VLAN ('yes'):")
        if not response == 'yes':
            logger.info('Did not proceed with change.')
            sys.exit(1)

        # invoke API call to change VLAN
        sw_api_call = Switch(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = sw_api_call.id_by_ip(neigh_ip)
        job_id = sw_api_call.conf_if_vlan(dev_id, interface, "Access", values_dict['vlan'])

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

