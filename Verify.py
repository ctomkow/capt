# Craig Tomkow
# May 22, 2018
#
# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
import argparse
import _thread

# local imports
import Config

class Verify:


    def __init__(self):

        # argument parsing

        #config loading
        Config.load_configuration()

        self.main()


    def main(self):

        ### within a thread... ###
        print(Config.get_a_device())
        # call connector...
        # do stuff
        # compare
        # yadda yadda yadda


if __name__ == '__main__':

    Verify()