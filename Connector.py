# Craig Tomkow
# May 22, 2018
#
# Connector class to pull state from Cisco Prime Infrastructure


# 3rd part imports
import requests


class Connector:


    def __init__(self, username, password):

        self.username = username
        self.password = password

    def reachability(self):

        pass