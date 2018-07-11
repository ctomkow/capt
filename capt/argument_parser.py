
# system imports
import sys

class ArgumentParser:

    def __init__(self, args):

        self.args = args

    def sub_cmd_exists(self):

        if self.args.sub_cmd is None:
            return False
        else:
            return True

    def first_sub_cmd(self):

        return self.args.sub_cmd

    def normalize_mac(self, address):

        tmp = address.replace(':', '')  # remove all colons
        tmp1 = tmp.replace('-', '')  # remove all dashes
        tmp2 = tmp1.replace(' ', '')  # remove all blanks
        tmp3 = tmp2.replace('.', '')  # remove all dots
        return ':'.join(a + b for a, b in zip(tmp3[::2], tmp3[1::2]))  # insert colon every two chars


    def find_ip(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address}

        if self.args.ap:
            return 'find_ip--ap', dict_of_values
        elif self.args.phone:
            return 'find_ip--phone', dict_of_values
        else: # no flags
            return 'find_ip', dict_of_values

    def find_mac(self): # determine any flags and return all required values

        dict_of_values = {'address': self.normalize_mac(self.args.address)}

        if self.args.ap:
            return 'find_mac--ap', dict_of_values
        elif self.args.phone:
            return 'find_mac--phone', dict_of_values
        else:  # no flags
            return 'find_mac', dict_of_values

    def change_mac(self): # determine any flags and return all required values

        dict_of_values = {'address': self.normalize_mac(self.args.address)}

        if self.args.vlan:
            dict_of_values['vlan'] = self.args.vlan # add vlan to dict
            return 'change_mac--vlan', dict_of_values
        else:  # no flags (flags are required)
            print('missing flags are required')
            sys.exit(1)

    def upgrade(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address}
        return 'upgrade', dict_of_values

    def mock_upgrade(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address}
        return 'mock_upgrade', dict_of_values

    def test_api_mac(self): # determine any flags and return all required values

        dict_of_values = {'address': self.normalize_mac(self.args.address)}
        return 'test_api_mac', dict_of_values



