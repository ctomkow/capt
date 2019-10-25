
# system imports

# 3rd part imports
import requests

# local imports
from connector.connector import Connector


class Alarms(Connector):


    def get_critical_alarm_ids(self):
        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/Alarms.json?.and_filter=true&condition.value=AP_DISASSOCIATED&severity=eq(CRITICAL)".format(
            self.cpi_ipv4_address)

        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        list_json = self.parse_json.value(result.json(), ['queryResponse', 'entityId'], self.logger)
        id_list = self.parse_json.ids_list(list_json)
        return id_list
        #key_list = ['queryResponse', 'entityId', 0, '$']
        #return self.parse_json.value(result.json(), key_list, self.logger)

    def devname_by_alarm_id(self,alarm_id):
        url = "https://{}/webacs/api/v3/data/Alarms/{}.json".format(self.cpi_ipv4_address,alarm_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'alarmsDTO', 'deviceName']
        apmac = self.parse_json.value(result.json(), key_list, self.logger)[:17]

        return apmac

    #grab severity, alarmId,category.value, condition.value,device name


    def json_basic(self, dev_id):
        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()

    def json_detailed(self, dev_id):
        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPointDetails/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        return result.json()