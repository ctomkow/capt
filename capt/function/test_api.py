
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

    def test_method(self, args, addr, addr_type, cpi_username, cpi_password, cpi_ipv4_address, logger):

        print(addr)

        api_call = Client(cpi_username, cpi_password, cpi_ipv4_address, logger)
        dev_id = api_call.get_id_by_mac(addr)
        print(dev_id)
        result = api_call.get_json_session(dev_id)

        print(json.dumps(result, indent=4))


