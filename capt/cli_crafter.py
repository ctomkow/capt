
# system imports
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import sys

class CliCrafter:


    def __init__(self):

        # arg parsing
        self.parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, add_help=True,
                                description="""Cisco APi Tool: a nettool built on Cisco Prime's API""")

        self.parser.add_argument('-v', '--verbose', action='store_true', required=False, help="debug output")
        self.subparsers = self.parser.add_subparsers(dest="sub_cmd")


    def find_subparser(self, sp):

        find = sp.add_parser('find', help="get client device information")
        return find.add_subparsers(dest="find") # return a subparser

    def find_parser(self, sp):

        return sp.add_parser('find', help="get client device information") # return a parser

    def upgrade_subparser(self, sp):

        upgrade = sp.add_parser('upgrade', help="initiate code upgrade on switch")
        return upgrade.add_subparsers(dest="upgrade")  # return a subparser

    def upgrade_parser(self, sp):

        return sp.add_parser('upgrade', help="initiate code upgrade on switch") # return a parser

    def mock_subparser(self, sp):

        mock = sp.add_parser('mock', help="initiate test procedure (non prod impacting)")
        return mock.add_subparsers(dest="mock") # return a subparser

    def mock_parser(self, sp):

        return sp.add_parser('mock', help="initiate test procedure (non prod impacting)") # return a parser

    def ip_subparser(self, sp):

        ip = sp.add_parser('ip', help="IPv4 address of client device")
        return ip.add_subparsers(dest="ip") # return a subparser

    def ip_parser(self, sp):

        return sp.add_parser('ip', help="IPv4 address of client device") # return a parser

    def mac_subparser(self, sp):

        mac = sp.add_parser('mac', help="mac address of client device")
        return mac.add_subparsers(dest="mac")  # return a subparser

    def mac_parser(self, sp):

        return sp.add_parser('mac', help="mac address of client device") # return a parser

    def test_api_subparser(self, sp):

        test_api = sp.add_parser('test_api', help="test api calls")
        return test_api.add_subparsers(dest="test_api")  # return a subparser

    def test_api_parser(self, sp):

        return sp.add_parser('test_api', help="test api calls")  # return a parser

    def addr_arg(self, p):

        p.add_argument('address', help="specify the device address")

    def ap_arg(self, p):

        p.add_argument('--ap', help="access point", action="store_true")

    def phone_arg(self, p):

        p.add_argument('--phone', help="VoIP phone", action="store_true")

    def normalize_addr(self, addr, args):

        if 'mac' in args:
            tmp = addr.replace(':', '')  # remove all colons
            tmp1 = tmp.replace('-', '')  # remove all dashes
            tmp2 = tmp1.replace(' ', '')  # remove all blanks
            tmp3 = tmp2.replace('.', '') # remove all dots
            return ':'.join(a + b for a, b in zip(tmp3[::2], tmp3[1::2]))  # insert colon every two chars
        elif 'ip' in args:
            tmp = addr.replace(':', '')  # remove all colons
            tmp1 = tmp.replace('-', '')  # remove all dashes
            tmp2 = tmp1.replace(' ', '')  # remove all blanks
            return tmp2
        else:
            print('failed to normalize address')
            sys.exit(1)

    def detect_addr_type(self, args):

        if 'mac' in args:
            return 'mac'
        elif 'ip' in args:
            return 'ipv4'
        else:
            print('failed to detect address type')
            sys.exit(1)
