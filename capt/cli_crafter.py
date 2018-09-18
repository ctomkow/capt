
# system imports
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


class CliCrafter:

    def __init__(self):

        # arg parsing
        self.parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                     add_help=True,
                                     description="""Cisco APi Tool: a nettool built on Cisco Prime's API""")
        self.parser.add_argument('-d', '--debug', action='store_true', required=False, help="debug output")
        self.subparsers = self.parser.add_subparsers(dest="sub_cmd")

    def find_subparser(self, sp):

        find = sp.add_parser('find', help="get client device information")
        return find.add_subparsers(dest="find")

    def find_parser(self, sp):

        return sp.add_parser('find', help="get client device information")

    def upgrade_subparser(self, sp):

        upgrade = sp.add_parser('upgrade', help="initiate code upgrade on switch")
        return upgrade.add_subparsers(dest="upgrade")

    def upgrade_parser(self, sp):

        return sp.add_parser('upgrade', help="initiate code upgrade on switch")

    def mock_subparser(self, sp):

        mock = sp.add_parser('mock', help="initiate test procedure (non prod impacting)")
        return mock.add_subparsers(dest="mock")

    def mock_parser(self, sp):

        return sp.add_parser('mock', help="initiate test procedure (non prod impacting)")

    def ip_subparser(self, sp):

        ip = sp.add_parser('ip', help="IPv4 address of client device")
        return ip.add_subparsers(dest="ip")

    def ip_parser(self, sp):

        return sp.add_parser('ip', help="IPv4 address of client device")

    def mac_subparser(self, sp):

        mac = sp.add_parser('mac', help="mac address of client device")
        return mac.add_subparsers(dest="mac")

    def mac_parser(self, sp):

        return sp.add_parser('mac', help="mac address of client device")
    def bas_parser(self, sp):

        return sp.add_parser('bas', help="Enable a BAS port")

    def desc_parser(self, sp):
        return sp.add_parser('desc', help="port description / label on wall port")

    def core_parser(self, sp):
        return sp.add_parser('core', help="find info on core devices")



    def core_vlan_parser(self, sp):
        return sp.add_parser('vlan', help="find vlan info on core devices")

    def core_port_parser(self, sp):
        return sp.add_parser('port', help="find port info on core devices")

    def port_parser(self, sp):
        return sp.add_parser('port', help="find individual port info ")

    def vlan_subparser(self, sp):

        vlan = sp.add_parser('vlan', help="new vlan for client device")
        return vlan.add_subparsers(dest="vlan")

    def vlan_parser(self, sp):

        return sp.add_parser('vlan', help="new vlan for client device")

    def change_subparser(self, sp):

        change = sp.add_parser('change', help="change switch configuration")
        return change.add_subparsers(dest="change")

    def poke_subparser(self, sp):
        poke = sp.add_parser('poke', help="get specific device information")
        return poke.add_subparsers(dest="poke")

    def push_subparser(self, sp):
        push = sp.add_parser('push', help="push edge templates")
        return push.add_subparsers(dest="push")

    def change_parser(self, sp):

        return sp.add_parser('change', help="change switch configuration")

    def test_api_subparser(self, sp):

        test_api = sp.add_parser('test_api', help="test api calls")
        return test_api.add_subparsers(dest="test_api")

    def test_api_parser(self, sp):

        return sp.add_parser('test_api', help="test api calls")

    def addr_arg(self, p):

        p.add_argument('address', help="specify the device address")

    def int_arg(self, p):
        p.add_argument('interface', help="specify the device interface")

    def vlan_arg(self, p):

        p.add_argument('-v', '--vlan', help="specify the new client VLAN ID")
    def desc_flag_arg(self, p):
        p.add_argument('-d','--description', help="specify the description to search. \n "
           "Enclose in brackets if including spaces and seperate multiple criteria with commas")

    def ap_arg(self, p):

        p.add_argument('-a', '--ap', help="access point", action="store_true")

    def phone_arg(self, p):

        p.add_argument('-p', '--phone', help="VoIP phone", action="store_true")

    def desc_arg(self, p):
        p.add_argument('description', help="specify the description to search. \n "
           "Enclose in brackets if including spaces and seperate multiple criteria with commas")

    def active_arg(self, p):
        p.add_argument('-a','--active', help="connection is active / has something connected", action="store_true")

    def device_name_arg(self, p):
        p.add_argument('-n','--name', help="name of switch to search (can be partial) ")

    def core_search_arg(self, p):
        p.add_argument('search_crit', help="port/vlan to find info on" )