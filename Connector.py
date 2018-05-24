# Craig Tomkow
# May 22, 2018
#
# Connector class to pull state from Cisco Prime Infrastructure


# 3rd part imports
import requests


class Connector:


    def __init__(self, username, password, cpi_ipv4_address):

        self.username = username
        self.password = password
        self.cpi_ipv4_address = cpi_ipv4_address

    def get_dev(self, dev_ipv4_address):

        pass
        #resource = 'https:///webacs/api/v4/data/Devices.json?ipAddress=f"{dev_ipv4_address}"'
        #print resource
        #dev = requests.get(resource, auth=(self.username, self.password))

        # error handling around this!
        #print(dev.status_code)

        #self.data = dev.json()

