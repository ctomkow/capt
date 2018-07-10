
# system imports
import sys

# local imports
from function.find import Find
from connector.switch import Switch


class Change:


    def __init__(self, args, dev_addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        print(args)
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
        job_id = sw_api_call.conf_if_vlan(sw_api_call.get_id(dev_addr), interface, "Access", vlan)
        if not sw_api_call.job_complete(job_id):
            logger.critical("Change VLAN failed. Prime job not completed")
            sys.exit(1)
        else:
            if not sw_api_call.job_successful(job_id):
                logger.critical("Change VLAN failed. Prime job not successful")
                sys.exit(1)

        logger.info('Change VLAN complete.')
