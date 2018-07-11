#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# Used to compare switch state before and after code upgrades.
# Pulls state info from Cisco Prime Infrastructure

# system imports
import threading
import time
import sys
import logging
import datetime

# 3rd party imports
import argcomplete

# local imports
import config
from procedure.upgrade_code import UpgradeCode
from procedure.mock_upgrade_code import MockUpgradeCode
from function.find import Find
from function.change import Change
from function.test_api import TestApi
from cli_crafter import CliCrafter


class Capt:


    def __init__(self):

        craft = CliCrafter()
        subparsers = craft.subparsers

        #  -----
        # base sub-commands
        find_sp = craft.find_subparser(subparsers)
        mock_sp = craft.mock_subparser(subparsers)
        change_sp = craft.change_subparser(subparsers)
        #  -----
        #  -----
        # capt find ip x.x.x.x
        find_ip = craft.ip_parser(find_sp)
        craft.addr_arg(find_ip)
        find_ip.set_defaults(func=Find)
        #  -----
        # capt find ip x.x.x.x --ap
        craft.ap_arg(find_ip)
        #  -----
        # capt find ip x.x.x.x --phone
        craft.phone_arg(find_ip)
        #  -----
        # capt find mac xx:xx:xx:xx:xx:xx
        find_mac = craft.mac_parser(find_sp)
        craft.addr_arg(find_mac)
        find_mac.set_defaults(func=Find)
        #  -----
        # capt find mac xx:xx:xx:xx:xx:xx --ap
        craft.ap_arg(find_mac)
        #  -----
        # capt find mac xx:xx:xx:xx:xx:xx --phone
        craft.phone_arg(find_mac)
        #  -----
        # capt upgrade x.x.x.x
        upgrade = craft.upgrade_parser(subparsers)
        craft.addr_arg(upgrade)
        upgrade.set_defaults(func=UpgradeCode)
        #  -----
        # capt mock upgrade x.x.x.x
        mock_upgrade = craft.upgrade_parser(mock_sp)
        craft.addr_arg(mock_upgrade)
        mock_upgrade.set_defaults(func=MockUpgradeCode)
        #  -----
        # capt change mac xx:xx:xx:xx:xx:xx --vlan yyyy
        change_mac = craft.mac_parser(change_sp)
        craft.addr_arg(change_mac)
        craft.vlan_arg(change_mac)
        change_mac.set_defaults(func=Change)
        #  -----
        # capt test_api
        test_api_sp = craft.test_api_subparser(subparsers)
        test_api_mac = craft.mac_parser(test_api_sp)
        craft.addr_arg(test_api_mac)
        test_api_mac.set_defaults(func=TestApi.test_method)

        parser = craft.parser

        argcomplete.autocomplete(parser)
        args = parser.parse_args()

        #print(args)
        #print(sys.argv)

        # handle addressing for ip/mac selection
        if 'ip' in sys.argv or 'mac' in sys.argv:
            addr = craft.normalize_addr(args.address, sys.argv)
            addr_type = craft.detect_addr_type(sys.argv)

        if args.sub_cmd == 'find':
            if args.find == 'ip' or args.find == 'mac':
                config.load_base_conf()
                log_file = False
                logger = self.set_logger(args.address, logging.INFO, log_file)
                args.func(args, addr, addr_type, config.username, config.password, config.cpi_ipv4_address, logger)

        if args.sub_cmd == 'change':
            if args.change == 'ip' or args.change == 'mac':
                config.load_base_conf()
                log_file = False
                logger = self.set_logger(args.address, logging.INFO, log_file)
                args.func(args, addr, addr_type, config.username, config.password, config.cpi_ipv4_address, logger)

        if args.sub_cmd == 'upgrade':
            config.load_base_conf()
            logger = self.set_logger(args.address, logging.INFO)
            args.func(args.address, config.username, config.password, config.cpi_ipv4_address, logger)

        if args.sub_cmd == 'mock':
            if args.mock == 'upgrade':
                config.load_base_conf()
                logger = self.set_logger(args.address, logging.INFO)
                args.func(args.address, config.username, config.password, config.cpi_ipv4_address, logger)

        if args.sub_cmd == 'test_api':
            config.load_base_conf()
            logger = self.set_logger(args.address, logging.INFO)
            args.func(TestApi, args, addr, addr_type, config.username, config.password, config.cpi_ipv4_address, logger)

        # if not sub commands are selected, execute configuration file
        if not args.sub_cmd:
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

    def set_logger(self, nm, level, log_file=True):

        # remove colons from name if exists (e.g. mac address)
        name = nm.replace(":","")

        formatter = logging.Formatter(
            fmt='%(asctime)s : {} : %(levelname)-8s : %(message)s'.format(name),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        if log_file:
            handler = logging.FileHandler(
                "{}-{}".format(datetime.datetime.now().strftime("%Y%m%d"), name),
                mode='a'
            )
            handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        if log_file:
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
