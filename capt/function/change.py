
# system imports
import sys
import time

# local imports
from function.find import Find
from connector.switch import Switch


class Change:


    def __init__(self, args, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        if args.change == 'mac' and args.vlan:
            self.if_vlan_and_find(dev_addr, addr_type, args.vlan, cpi_username, cpi_password, cpi_ipv4_address, logger)
        else:
            logger.critical('failed to execute function. Possibly missing arguments')
            sys.exit(1)

    def if_vlan_and_find(self, dev_addr, addr_type, vlan, cpi_username, cpi_password, cpi_ipv4_address, logger):

        # find and display
        neigh_name, neigh_ip, interface, description, old_vlan, old_vlan_name, addr = \
            Find.find_client(self, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger)

        # require 'yes' input to proceed
        logger.info('Change VLAN to: {}'.format(vlan))
        response = input("Confirm action of changing VLAN ('yes'):")
        if not response == 'yes':
            logger.info('Did not proceed with change.')
            sys.exit(1)

        # invoke API call to change VLAN
        sw_api_call = Switch(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = sw_api_call.get_id_by_ip(neigh_ip)
        job_id = sw_api_call.conf_if_vlan(dev_id, interface, "Access", vlan)

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
