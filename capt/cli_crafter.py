# 3rd party imports
import argcomplete

# system imports
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

########################################
# Class: CliCrafter
# Description: Class creates the structure of command line arguments
#               all possible command options are defined in this file
########################################

class CliCrafter:

    def __init__(self):
        #############################################################################
        # Create parsers and assign arguments
        #############################################################################

        # arg parsing
        self.parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                     add_help=True,
                                     description="""Cisco APi Tool: a nettool built on Cisco Prime's API""")
        self.parser.add_argument('-d', '--debug', action='store_true', required=False, help="debug output")
        self.parser.add_argument('-e', '--email', required=False, help="email to log to")
        self.subparsers = self.parser.add_subparsers(dest="sub_cmd")


        # ----- Create base sub-commands
        find_sp = self.subparsers.add_parser('find', help="get client device information").add_subparsers(dest="find")
        mock_sp = self.mock_subparser(self.subparsers)
        change_sp = self.change_subparser(self.subparsers)
        poke_sp = self.poke_subparser(self.subparsers)
        push_sp = self.push_subparser(self.subparsers)
        tools_sp = self.tools_subparser(self.subparsers)
        reports_sp = self.reports_subparser(self.subparsers)
        # ----- Completed create base sub-commands

        # ----- capt find sub-commands -----
        # ----- capt find ip x.x.x.x
        find_ip = find_sp.add_parser('ip', help="IPv4 address of client device")
        self.addr_arg(find_ip)
        # defaults are used to determine which function should be called, allows interactive style prompt with
        #find_ip.set_defaults(func=CliParser.find_ip)
        # ----- capt find ip x.x.x.x --ap
        self.ap_arg(find_ip)
        # ----- capt find ip x.x.x.x --phone
        self.phone_arg(find_ip)
        # ----- capt find mac xx:xx:xx:xx:xx:xx
        find_mac = self.mac_parser(find_sp)
        self.addr_arg(find_mac)
        #find_mac.set_defaults(func=CliParser.find_mac)
        # ----- capt find mac xx:xx:xx:xx:xx:xx --ap
        self.ap_arg(find_mac)
        # ----- capt find mac xx:xx:xx:xx:xx:xx --phone
        self.phone_arg(find_mac)
        # ----- capt find desc xxxxxx
        find_desc = self.desc_parser(find_sp)
        self.desc_arg(find_desc)
        self.device_name_arg(find_desc)
        #find_desc.set_defaults(func=CliParser.find_desc)
        # ----- capt find desc xxxxxx --active
        self.active_arg(find_desc)
        # ----- capt find core -vlan
        find_core = self.core_parser(find_sp)
        self.addr_arg(find_core)  # adds address field
        self.core_search_arg(find_core)
      #  find_core.set_defaults(func=CliParser.find_core)
        # ----- Completed capt find sub-commands -----

        # ----- capt poke sub-commands -----
        # ----- capt poke port XXX.XXX.XXX.XXX Y/Y/Y
        poke_port = self.port_parser(poke_sp)
        self.addr_arg(poke_port)  # adds address field
        self.int_arg(poke_port)  # adds interface field
        #self.sync_arg(poke_port) <TODO implement sync functionality>
       # poke_port.set_defaults(func=CliParser.poke_port)

        # ----- capt upgrade sub-commands (deprecated?) -----
        # ----- capt upgrade x.x.x.x
        upgrade = self.upgrade_parser(self.subparsers)
        self.addr_arg(upgrade)
       # upgrade.set_defaults(func=CliParser.upgrade)
        # ----- capt mock upgrade x.x.x.x
        mock_upgrade = self.upgrade_parser(mock_sp)
        self.addr_arg(mock_upgrade)
       # mock_upgrade.set_defaults(func=CliParser.mock_upgrade)

        # ----- capt change sub-commands -----
        # ----- capt change mac xx:xx:xx:xx:xx:xx --vlan yyyy
        change_mac = self.mac_parser(change_sp)
        self.addr_arg(change_mac)
        self.vlan_arg(change_mac)
     #   change_mac.set_defaults(func=CliParser.change_mac)

        # ----- capt push sub-commands -----
        # ----- capt push bas -a W.W.W.W -p X/X/X -v YYYY -d "ZZZZZZ"
        push_bas = self.bas_parser(push_sp)
        self.addr_arg(push_bas)
        self.int_arg(push_bas)
        self.vlan_arg(push_bas)
        self.desc_flag_arg(push_bas)
      #  push_bas.set_defaults(func=CliParser.push_bas)

        # ----- capt tools sub-commands -----
        # ----- capt tools apcheck
        tools_ap = self.apcheck_subparser(tools_sp)

        # ----- capt tools apcheck slowports
        ap_slow_ports = self.slow_ports_parser(tools_ap)
        self.toggle_arg(ap_slow_ports)
        self.batch_arg(ap_slow_ports)
        # ----- capt tools apcheck unack
        ap_unack = self.unack_parser(tools_ap)

        # ----- capt tools apcheck alarms
        ap_alarms = self.alarms_parser(tools_ap)
        self.days_arg(ap_alarms)
        self.toggle_arg(ap_alarms)
        self.batch_arg(ap_alarms)
     #   ap_alarms.set_defaults(func=CliParser.ap_alarms)

        # ----- capt tools apcheck slowports


        # ----- capt test sub-commands -----
        # ----- capt test_api
        test_api_sp = self.test_api_subparser(self.subparsers)
        test_api_mac = self.mac_parser(test_api_sp)
        self.addr_arg(test_api_mac)
      #  test_api_mac.set_defaults(func=CliParser.test_api_mac)

        argcomplete.autocomplete(self.parser)
        ################NEW DONE

        # -- reports_portcount ----
        port_count = self.port_count_parser(reports_sp)
        self.building_filter_arg(port_count)
        self.verbose_arg(port_count)
        self.csv_arg(port_count)

        # -- reports devcount ---
        dev_count = self.dev_count_parser(reports_sp)
        self.building_filter_arg(dev_count)
        self.verbose_arg(dev_count)
        self.csv_arg(dev_count)

        # -- reports vlan_mapper ---
        vlan_map = self.vlan_map_parser(reports_sp)
        self.building_filter_arg(vlan_map)
        self.verbose_arg(vlan_map)
        self.csv_arg(vlan_map)

#############################################################################
    # Define possible CLI Options below
    # (subcategoried and Alphanumeric for viewing pleasure)
#############################################################################
        # Define parsers to add
        # (parsers have arguments applied to them)
#############################################################################
    def alarms_parser(self, sp):
        return sp.add_parser('alarms', help="go through ap alarms")

    def bas_parser(self, sp):
        return sp.add_parser('bas', help="Enable a BAS port")

    def change_parser(self, sp):
        return sp.add_parser('change', help="change switch configuration")

    def core_parser(self, sp):
        return sp.add_parser('core', help="find info on core devices")

    def core_port_parser(self, sp):
        return sp.add_parser('port', help="find port info on core devices")

    def core_vlan_parser(self, sp):
        return sp.add_parser('vlan', help="find vlan info on core devices")

    def desc_parser(self, sp):
        return sp.add_parser('desc', help="port description / label on wall port")

    def find_parser(self, sp):
        return sp.add_parser('find', help="get client device information")

    def ip_parser(self, sp):
        return sp.add_parser('ip', help="IPv4 address of client device")

    def mac_parser(self, sp):
        return sp.add_parser('mac', help="mac address of client device")

    def mock_parser(self, sp):
        return sp.add_parser('mock', help="initiate test procedure (non prod impacting)")

    def port_parser(self, sp):
        return sp.add_parser('port', help="find individual port info ")

    def slow_ports_parser(self, sp):
        return sp.add_parser('slow_ports', help="get list of gig ports negotiating to 100Mbps")

    def test_api_parser(self, sp):
        return sp.add_parser('test_api', help="test api calls")

    def unack_parser(self, sp):
        return sp.add_parser('unack', help="unacknowledge AP alarms")

    def upgrade_parser(self, sp):
        return sp.add_parser('upgrade', help="initiate code upgrade on switch")

    def vlan_parser(self, sp):
        return sp.add_parser('vlan', help="new vlan for client device")

    def port_count_parser(self, sp):
        return sp.add_parser('portcount', help="Count Connected and Notconnect for physical interfaces")

    def dev_count_parser(self, sp):
        return sp.add_parser('devcount', help="Count APs and VoIP phones")

    def vlan_map_parser(self, sp):
        return sp.add_parser('vlanmap', help="VLAN summary of switch")

#############################################################################
        # Define sub-parsers to add
        # (sub-parsers can have further pre defined options applied to them, not arguments)
#############################################################################
    def apcheck_subparser(self, sp):
        return sp.add_parser('apcheck', help="go through list of disassociated ap alarms").add_subparsers(
            dest="apcheck")

    def change_subparser(self, sp):
        change = sp.add_parser('change', help="change switch configuration")
        return change.add_subparsers(dest="change")

    def find_subparser(self, sp):
        find = sp.add_parser('find', help="get client device information")
        return find.add_subparsers(dest="find")

    def ip_subparser(self, sp):
        ip = sp.add_parser('ip', help="IPv4 address of client device")
        return ip.add_subparsers(dest="ip")

    def mac_subparser(self, sp):
        mac = sp.add_parser('mac', help="mac address of client device")
        return mac.add_subparsers(dest="mac")

    def mock_subparser(self, sp):
        mock = sp.add_parser('mock', help="initiate test procedure (non prod impacting)")
        return mock.add_subparsers(dest="mock")

    def poke_subparser(self, sp):
        poke = sp.add_parser('poke', help="get specific device information")
        return poke.add_subparsers(dest="poke")

    def push_subparser(self, sp):
        push = sp.add_parser('push', help="push edge templates")
        return push.add_subparsers(dest="push")

    def reports_subparser(self, sp):
        return sp.add_parser("reports", help="various reports").add_subparsers(dest="reports")

    def test_api_subparser(self, sp):
        test_api = sp.add_parser('test_api', help="test api calls")
        return test_api.add_subparsers(dest="test_api")

    def tools_subparser(self, sp):
        return sp.add_parser("tools", help="various tools without a subcategory").add_subparsers(dest="tools")

    def upgrade_subparser(self, sp):
        upgrade = sp.add_parser('upgrade', help="initiate code upgrade on switch")
        return upgrade.add_subparsers(dest="upgrade")

    def vlan_subparser(self, sp):
        vlan = sp.add_parser('vlan', help="new vlan for client device")
        return vlan.add_subparsers(dest="vlan")

#############################################################################
    # Define arguments to add
    # (arguments that take direct input)
#############################################################################

    def addr_arg(self, p):
        p.add_argument('address', help="specify the device address")

    def core_search_arg(self, p):
        p.add_argument('search_crit', help="port/vlan to find info on" )

    def days_arg(self, p):
        p.add_argument('-d', '--days', help="specify how many days ago to search")

    def desc_arg(self, p):
        p.add_argument('description', help="specify the description to search. \n "
           "Enclose in brackets if including spaces and seperate multiple criteria with commas")

    def desc_flag_arg(self, p):
        p.add_argument('-d','--description', help="specify the description to search. \n "
           "Enclose in brackets if including spaces and seperate multiple criteria with commas")

    def device_name_arg(self, p):
        p.add_argument('-n','--name', help="name of switch to search (can be partial) ")

    def email_arg(self, p):
        p.add_argument('-e', '--email', help="email to log to ")

    def int_arg(self, p):
        p.add_argument('interface', help="specify the device interface")

    def vlan_arg(self, p):
        p.add_argument('-v', '--vlan', help="specify the new client VLAN ID", required=True)

    def building_filter_arg(self, p):
        p.add_argument('building_filter', help="Specify building or all,")

#############################################################################
    # Define flags / arguments that take no additional info
    # ()
#############################################################################

    def active_arg(self, p):
        p.add_argument('-a','--active', help="connection is active / has something connected", action="store_true")

    def ap_arg(self, p):
        p.add_argument('-a', '--ap', help="access point", action="store_true")

    def batch_arg(self, p):
        p.add_argument('-b', '--batch', help="skip verification, for batch files", action="store_true")

    def phone_arg(self, p):
        p.add_argument('-p', '--phone', help="VoIP phone", action="store_true")

    def sync_arg(self, p):
        p.add_argument('-s', '--sync', help="Sync data first", action="store_true")

    def toggle_arg(self, p):
        p.add_argument('-t', '--toggle', help="toggle port up and down", action="store_true")

    def verbose_arg(self, p):
        p.add_argument('-v', '--verbose', help="print additional detail", action="store_true")

    def csv_arg(self, p):
        p.add_argument('-c', '--csv', help="output in CSV format", action="store_true")







