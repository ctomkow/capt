
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

    @staticmethod
    def normalize_mac(address):

        tmp = address.replace(':', '')
        tmp1 = tmp.replace('-', '')
        tmp2 = tmp1.replace(' ', '')
        tmp3 = tmp2.replace('.', '')
        return ':'.join(a + b for a, b in zip(tmp3[::2], tmp3[1::2]))  # insert colon every two chars


    # def poke_port(self):  # determine any flags and return all required values <TODO: address required poke vars>
    #
    #     if self.args.address and self.args.interface :
    #         dict_of_values = {'address': self.args.address, 'interface': self.args.interface}
    #     else:
    #         print('proper syntax: capt poke port <address/hostname> <interface X/Y/Z> ')
    #         sys.exit(1)
    #
    #     return 'poke_port', dict_of_values


