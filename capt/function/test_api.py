
# local imports
from connector.switch import Switch
from connector.access_point import AccessPoint
from json_parser import JsonParser

class TestApi:

    def __init__(self):

        pass

    def conf_if_vlan(self, switch_ip, if_name, sw_port_type, vlan, cpi_username, cpi_password, cpi_ipv4_address, logger):

        print(switch_ip)
        print(if_name)
        print(vlan)


        sw_api_call = Switch(cpi_username, cpi_password, cpi_ipv4_address, logger)
        job_id = sw_api_call.conf_if_vlan(sw_api_call.get_id(switch_ip), if_name, sw_port_type, vlan)
        print(job_id)

