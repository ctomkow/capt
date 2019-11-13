# A container for reporting functions

from connector.switch import Switch
from connector.access_point import AccessPoint
from connector.alarms import Alarms
from json_parser import JsonParser

class Reports:

    def __init__(self):

        self.parse_json = JsonParser()