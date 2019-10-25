
# system imports
import sys


class CliParser:

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

        tmp = address.replace(':', '')
        tmp1 = tmp.replace('-', '')
        tmp2 = tmp1.replace(' ', '')
        tmp3 = tmp2.replace('.', '')
        return ':'.join(a + b for a, b in zip(tmp3[::2], tmp3[1::2]))  # insert colon every two chars

    def find_ip(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address}
        if self.args.ap:
            return 'find_ip--ap', dict_of_values
        elif self.args.phone:
            return 'find_ip--phone', dict_of_values
        else:
            return 'find_ip', dict_of_values

    def find_mac(self): # determine any flags and return all required values

        dict_of_values = {'address': self.normalize_mac(self.args.address)}
        if self.args.ap:
            return 'find_mac--ap', dict_of_values
        elif self.args.phone:
            return 'find_mac--phone', dict_of_values
        else:
            return 'find_mac', dict_of_values

    def change_mac(self): # determine any flags and return all required values

        dict_of_values = {'address': self.normalize_mac(self.args.address)}
        if self.args.vlan:
            dict_of_values['vlan'] = self.args.vlan # add vlan to dict
            return 'change_mac--vlan', dict_of_values
        else:
            print('missing flags are required')
            sys.exit(1)

    def push_bas(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address,'interface':self.args.interface,'vlan':self.args.vlan,'desc':self.args.description}
        if self.args.vlan:
            return 'push_bas', dict_of_values
        else:
           # print('missing flags are required: syntax example-> capt push bas X.X.X.X -i S/0/P -v VVV -d \“DESCRIPTION\” ')
            print('missing flags are required: syntax example-> capt push bas X.X.X.X  S/0/P -v VVV -d "DESCRIPTION" ')
            sys.exit(1)

    def ap_alarms(self): # determine any flags and return all required values
        if 'days' in self.args and self.args.days is not None:
            dict_of_values = {'days':self.args.days}
        else:
            dict_of_values = {'days': "all"}

        dict_of_values['toggle'] = self.args.toggle


        return 'ap_alarms', dict_of_values



    def find_desc(self):  # determine any flags and return all required values

        dict_of_values = {'description': self.args.description}
        if self.args.active:
            return 'find_desc--active', dict_of_values
        #elif self.args.phone:
            #return 'find_desc--phone', dict_of_values
        else:
            return 'find_desc', dict_of_values
    def find_core(self):  # determine any flags and return all required values

        dict_of_values = {'address':self.args.address, 'search_crit': self.args.search_crit}
      #  if self.args.port:
      #      return 'find_core--port', dict_of_values
      #  elif self.args.vlan:
      #      return 'find_core--vlan', dict_of_values
      #  else:
      #      return 'find_core', dict_of_values
        return 'find_core', dict_of_values

    def poke_port(self):  # determine any flags and return all required values

        if self.args.address and self.args.interface :
            dict_of_values = {'address': self.args.address, 'interface': self.args.interface}
        else:
            print('proper syntax: capt poke port <address/hostname> <interface X/Y/Z> ')
            sys.exit(1)

        return 'poke_port', dict_of_values

    def upgrade(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address}
        return 'upgrade', dict_of_values

    def mock_upgrade(self): # determine any flags and return all required values

        dict_of_values = {'address': self.args.address}
        return 'mock_upgrade', dict_of_values

    def test_api_mac(self): # determine any flags and return all required values

        dict_of_values = {'address': self.normalize_mac(self.args.address)}
        return 'test_api_mac', dict_of_values



