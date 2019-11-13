
# system imports

# 3rd part imports
import requests

# local imports
from connector.connector import Connector


class AccessPoint(Connector):

    def id_by_name(self, name):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?name=\"{}\"".format(self.cpi_ipv4_address, name)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def ip_by_id(self, dev_id):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints/{}.json".format(self.cpi_ipv4_address, dev_id)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entity', 0, 'accessPointsDTO', 'ipAddress']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def id_by_mac(self, mac):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?ethernetMac=\"{}\"".format(self.cpi_ipv4_address, mac)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    # Can't seem to filter API call on ipAddress (I tried AccessPoints and AccessPointDetail)
    def id_by_ip(self, ip):

        # API v3 call is deprecated, need to change when Cisco Prime is upgraded
        url = "https://{}/webacs/api/v3/data/AccessPoints.json?ipAddress=\"{}\"".format(self.cpi_ipv4_address, ip)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)

    def id_by_alarm_mac_detailed(self,mac):
        url = "https://{}/webacs/api/v3/data/AccessPointDetails.json?macAddress=\"{}\"".format(self.cpi_ipv4_address, mac)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        key_list = ['queryResponse', 'entityId', 0, '$']
        return self.parse_json.value(result.json(), key_list, self.logger)
        #apmac = self.parse_json.value(result.json(), key_list, self.logger)[:16]
        #return apmac

    def get_slow_ports(self):
        url = "https://{}/webacs/api/v4/data/AccessPointDetails.json?.and_filter=true&cdpNeighbor.interfaceSpeed=100Mbps&cdpNeighbor.neighborPort=contains(GigabitEthernet)".format(
            self.cpi_ipv4_address)
        result = self.error_handling(requests.get, 5, url, False, self.username, self.password)
        #key_list = ['queryResponse', 'entityId', 0, '$']
        list_json = self.parse_json.value(result.json(), ['queryResponse', 'entityId'], self.logger)
        id_list = self.parse_json.ids_list(list_json)
        return id_list
        # return self.parse_json.value(result.json(), key_list, self.logger)



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