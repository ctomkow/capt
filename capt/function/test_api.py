
# system imports
import json

# local imports
from connector.switch import Switch
from connector.client import Client
from json_parser import JsonParser


class TestApi:

    def __init__(self):

        self.parse_json = JsonParser()

    def test_method(self, args, config, logger):

        api_call = Client(config, logger)
        sw_api_call = Switch(config, logger)

        dev_id = sw_api_call.id_by_ip("172.30.28.246")
        result = sw_api_call.json_detailed(dev_id)

        key_list = ['queryResponse', 'entity', 0, 'inventoryDetailsDTO', 'ethernetInterfaces', 'ethernetInterface']
        interface_list_of_dicts = self.parse_json.value(result, key_list, logger)

        for interface_dict in interface_list_of_dicts:
            for key in interface_dict: # iterating over dict's return keys only
                if interface_dict[key] == 'GigabitEthernet1/0/1':
                    print(json.dumps(interface_dict, indent=4))
