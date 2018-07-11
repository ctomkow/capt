
#system imports
import json

# local imports
from connector.switch import Switch
from connector.access_point import AccessPoint
from connector.client import Client
from json_parser import JsonParser

class TestApi:

    def __init__(self):

        pass

    def test_method(self, values_dict, cpi_username, cpi_password, cpi_ipv4_address, logger):



        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        sw_api_call = Switch(cpi_username, cpi_password, cpi_ipv4_address, logger)

        dev_id = sw_api_call.get_id_by_ip("172.30.28.246")
        result = sw_api_call.get_json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'ethernetInterfaces', 'ethernetInterface']
        interface_list_of_dicts = JsonParser.get_value(JsonParser, result, key_list, logger)

        for interface_dict in interface_list_of_dicts:
            for key in interface_dict: # iterating over dict's return keys only
                if interface_dict[key] == 'GigabitEthernet1/0/1':
                    print(json.dumps(interface_dict, indent=4))


