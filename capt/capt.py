#!/usr/bin/env python3

# Craig Tomkow
# May 22, 2018
#
# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import threading
import time
import sys
import logging
import datetime

# local imports
# for unit testing, need the relative imports
try:
    from . import config # needed vs. 'import config' for unit testing
    from .upgrade_code import UpgradeCode
    from .mock_upgrade_code import MockUpgradeCode
except (ImportError, SystemError):
    import config
    from upgrade_code import UpgradeCode
    from mock_upgrade_code import MockUpgradeCode


class Capt:


    def __init__(self):

        # arg parsing
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, add_help=True,
                                description="""Cisco APi Tool: a nettool built on Cisco Prime's API""")

        parser.add_argument('-v', '--verbose', action='store_true', required=False, help="debug output")

        subparsers = parser.add_subparsers(dest="sub_command")

        # #  -----
        # # capt push
        # push = subparsers.add_parser('push', help="send configuration to switch")
        # # capt push "show int status"
        # push.add_argument('cisco_config', help="specify the cisco IOS command to push")
        # push_subparsers = push.add_subparsers()
        # # capt push "show int status" to
        # push_to = push_subparsers.add_parser('to', help="specify the IPv4 address of switch")
        # # capt push "show int status" to 10.10.10.10
        # push_to.add_argument('ip_address', help="specify the IPv4 address of switch")
        # push_to.set_defaults(func=self.push_command)
        # #  -----
        # # capt push "no logging" config
        # push_config = push_subparsers.add_parser('config', help="config_t configuration given")
        # push_config_subparsers = push_config.add_subparsers()
        # # capt push "no logging" config to
        # push_config_to = push_config_subparsers.add_parser('to', help="specify the IPv4 address of switch")
        # # capt push "no logging" config to 10.10.10.10
        # push_config_to.add_argument('ip_address', help="specify the IPv4 address of switch")
        # push_config_to.set_defaults(func=self.push_configuration)
        # #  -----
        #
        # # capt upgrade
        # upgrade = subparsers.add_parser('upgrade', help="initiate code upgrade and verify")
        # # capt upgrade 10.10.10.10
        #
        # # test api calls
        # test = subparsers.add_parser('test_api', help="API testing")

        args = parser.parse_args()

        if args.sub_command:
            logger = self.set_logger(args.ip_address, logging.INFO)
            args.func(args, logger)
        else:
            config.load_configuration()
            self.main(args.verbose)

    def main(self, verbose):

        # instantiate system logger (separate from device loggers)
        if verbose:
            sys_logger = self.set_logger("system_log", logging.DEBUG)
        else:
            sys_logger = self.set_logger("system_log", logging.INFO)

        switch_ipv4_address_list = config.dev_ipv4_address
        max_threads = int(config.dev_concurrent_threads)

        proc_dict = {}
        # only add procedures that are selected
        if config.proc_code_upgrade:
            proc_dict['code_upgrade'] = config.proc_code_upgrade
        if config.proc_test_code_upgrade:
            proc_dict['test_code_upgrade'] = config.proc_test_code_upgrade
        if config.proc_push_command:
            proc_dict['push_command'] = config.proc_push_command
        if config.proc_push_configuration:
            proc_dict['push_configuration'] = config.proc_push_configuration

        # Validate user's configuration file
        if not self.valid_proc_num(proc_dict, sys_logger):
            sys_logger.critical("procedure selection failed")
            sys_logger.critical("config.text validation failed")
            sys.exit(1)
        if not self.valid_concurrent_num(max_threads, sys_logger):
            sys_logger.critical("concurrent threads can only be between 1 and 5 (inclusive)")
            sys_logger.critical("config.text validation failed")
            sys.exit(1)
        if not self.valid_proc_type(proc_dict, switch_ipv4_address_list, sys_logger):
            sys_logger.critical("procedure type selection failed")
            sys_logger.critical("config.text validation failed")
            sys.exit(1)

        threads = []
        while len(switch_ipv4_address_list) > 0:

            # check if thread is alive, if not, remove from list
            alive_threads = [t for t in threads if t.is_alive()] # DON'T MODIFY THE LIST YOUR ITERATING OVER!
            threads = alive_threads
            t_count = len(threads)
            sys_logger.debug("Thread count before: {}".format(t_count))

            # spawn thread if max concurrent number is not reached
            if t_count < max_threads:

                # instantiate per-thread/device logger (separate from system logger)
                if verbose:
                    logger = self.set_logger(switch_ipv4_address_list[0], logging.DEBUG)
                else:
                    logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)

                try:
                    if 'code_upgrade' in proc_dict:
                        t = threading.Thread(target=UpgradeCode, args=(switch_ipv4_address_list[0], config.username,
                                                                       config.password, config.cpi_ipv4_address, logger))
                    elif 'test_code_upgrade' in proc_dict:
                        t = threading.Thread(target=MockUpgradeCode, args=(switch_ipv4_address_list[0], config.username,
                                                                           config.password, config.cpi_ipv4_address, logger))
                    elif 'push_command' in proc_dict:
                        t = threading.Thread(target=self.push_command(switch_ipv4_address_list[0], config.config_command, logger))
                    elif 'push_configuration' in proc_dict:
                        t = threading.Thread(target=self.push_configuration(switch_ipv4_address_list[0], config.config_configuration, logger))
                except KeyError:
                    sys_logger.critical("Thread failed to execute function.")
                    sys.exit(1)

                threads.append(t)
                t.start()

                sys_logger.debug("Thread count after: {}".format(len(threads)))
                sys_logger.debug("Threads: {}".format(threads))
                switch_ipv4_address_list.pop(0)  # remove referenced switch
                sys_logger.debug("IP list: {}".format(switch_ipv4_address_list))

                # when last device is popped off list, wait for ALL threads to finish
                if len(switch_ipv4_address_list) == 0:
                    for t in threads:
                        t.join()
                else:
                    time.sleep(30) # give delay before creating the next thread.
            else:
                time.sleep(5) # give delay before trying again

    def set_logger(self, name, level):

        formatter = logging.Formatter(
            fmt='%(asctime)s : {} : %(levelname)-8s : %(message)s'.format(name),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler = logging.FileHandler(
            "{}-{}".format(datetime.datetime.now().strftime("%Y%m%d"), name),
            mode='a'
        )
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger

    def valid_proc_num(self, proc_dict, sys_logger):
        if len(proc_dict) > 1 or len(proc_dict) < 1:
            sys_logger.debug("Procedures selected:{}".format(proc_dict))
            return False
        else:
            return True

    def valid_concurrent_num(self, max_concurrent, sys_logger):

        if max_concurrent > 5 or max_concurrent < 1:
            sys_logger.debug("Max concurrent selected:{}".format(max_concurrent))
            return False
        else:
            return True

    def valid_proc_type(self, proc_dict, devices, sys_logger):

        if 'code_upgrade' in proc_dict:
            sys_logger.info("{} is selected.".format(proc_dict))
            sys_logger.info("This will RELOAD switches: {}".format(devices))
            time.sleep(3)
            user_choice = input("Continue (yes/no)? ")
            if user_choice == "yes":
                return True
            else:
                return False
        elif 'test_code_upgrade' in proc_dict:
            sys_logger.error("{} is selected. This procedure will test code upgrade procedure without a reload.".format(proc_dict))
            time.sleep(3)
            user_choice = input("Continue (yes/no)? ")
            if user_choice == "yes":
                return True
            else:
                return False
        elif 'push_command' in proc_dict:
            sys_logger.error("{} is selected. This procedure is not implemented yet.".format(proc_dict))
            return False
        elif 'push_configuration' in proc_dict:
            sys_logger.error("{} is selected. This procedure is not implemented yet.".format(proc_dict))
            return False
        else:
            sys_logger.debug("procedure types:{}".format(proc_dict))
            return False


if __name__ == '__main__':

    Capt()
