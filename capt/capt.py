#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

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
from function.push import Push
from function.poke import Poke
from function.tools import Tools
from function.test_api import TestApi
from cli_crafter import CliCrafter
from cli_parser import CliParser


class Capt:

    def __init__(self):

        # create CLICrafter object to parse CLI input. sub parsers may be added to this
        craft = CliCrafter()

        # ----- base sub-commands
        find_sp = craft.find_subparser(craft.subparsers)
        mock_sp = craft.mock_subparser(craft.subparsers)
        change_sp = craft.change_subparser(craft.subparsers)
        poke_sp = craft.poke_subparser(craft.subparsers)
        push_sp = craft.push_subparser(craft.subparsers)
        tools_sp = craft.tools_subparser(craft.subparsers)
        # ----- capt find ip x.x.x.x
        find_ip = craft.ip_parser(find_sp)
        craft.addr_arg(find_ip)
        find_ip.set_defaults(func=CliParser.find_ip)
        # ----- capt find ip x.x.x.x --ap
        craft.ap_arg(find_ip)
        # ----- capt find ip x.x.x.x --phone
        craft.phone_arg(find_ip)
        # ----- capt find mac xx:xx:xx:xx:xx:xx
        find_mac = craft.mac_parser(find_sp)
        craft.addr_arg(find_mac)
        find_mac.set_defaults(func=CliParser.find_mac)
        # ----- capt find mac xx:xx:xx:xx:xx:xx --ap
        craft.ap_arg(find_mac)
        # ----- capt find mac xx:xx:xx:xx:xx:xx --phone
        craft.phone_arg(find_mac)
        # ----- capt find desc xxxxxx
        find_desc = craft.desc_parser(find_sp)
        craft.desc_arg(find_desc)
        craft.device_name_arg(find_desc)
        find_desc.set_defaults(func=CliParser.find_desc)
        # ----- capt find desc xxxxxx --active
        craft.active_arg(find_desc)
        # ----- capt find core -vlan
        find_core = craft.core_parser(find_sp)
        craft.addr_arg(find_core)  # adds address field
        craft.core_search_arg(find_core)
        find_core.set_defaults(func=CliParser.find_core)
        # ----- capt poke port XXX.XXX.XXX.XXX Y/Y/Y
        poke_port = craft.port_parser(poke_sp)
        craft.addr_arg(poke_port)  # adds address field
        craft.int_arg(poke_port)  # adds interface field
        poke_port.set_defaults(func=CliParser.poke_port)
        # ----- capt upgrade x.x.x.x
        upgrade = craft.upgrade_parser(craft.subparsers)
        craft.addr_arg(upgrade)
        upgrade.set_defaults(func=CliParser.upgrade)
        # ----- capt mock upgrade x.x.x.x
        mock_upgrade = craft.upgrade_parser(mock_sp)
        craft.addr_arg(mock_upgrade)
        mock_upgrade.set_defaults(func=CliParser.mock_upgrade)
        # ----- capt change mac xx:xx:xx:xx:xx:xx --vlan yyyy
        change_mac = craft.mac_parser(change_sp)
        craft.addr_arg(change_mac)
        craft.vlan_arg(change_mac)
        change_mac.set_defaults(func=CliParser.change_mac)
        # ----- capt push bas -a W.W.W.W -p X/X/X -v YYYY -d "ZZZZZZ"
        push_bas = craft.bas_parser(push_sp)
        craft.addr_arg(push_bas)
        craft.int_arg(push_bas)
        craft.vlan_arg(push_bas)
        craft.desc_flag_arg(push_bas)
        push_bas.set_defaults(func=CliParser.push_bas)

        # ----- capt tools apcheck alarms
        tools_ap = craft.apcheck_subparser(tools_sp)
        ap_alarms = craft.alarms_parser(tools_ap)
        craft.days_arg(ap_alarms)
        craft.toggle_arg(ap_alarms)
        ap_alarms.set_defaults(func=CliParser.ap_alarms)

        # ----- capt tools apcheck slowports

        # ----- capt test_api
        test_api_sp = craft.test_api_subparser(craft.subparsers)
        test_api_mac = craft.mac_parser(test_api_sp)
        craft.addr_arg(test_api_mac)
        test_api_mac.set_defaults(func=CliParser.test_api_mac)



        argcomplete.autocomplete(craft.parser)
        args = craft.parser.parse_args()

        cli_parse = CliParser(args)

        # if sub commands
        if cli_parse.sub_cmd_exists():
            command, values_dict = args.func(cli_parse) # execute argument_parser function

            config.load_base_conf()
            subber = cli_parse.first_sub_cmd()
            if subber == 'find' or subber == 'change' or subber == 'tools' or subber == 'poke' or subber == 'push':
                log_file = False
            elif subber == 'upgrade' or subber == 'mock':
                log_file = True
            else:
                log_file = True

            #Revisit this line of code
            try:
                logger = self.set_logger(args.address, logging.INFO, log_file)
            except AttributeError:
                #address does not exist
                try:
                    logger = self.set_logger(args.description, logging.INFO, log_file)
                except AttributeError:
                    try:
                        logger = self.set_logger(args.tools, logging.INFO, log_file)
                    except AttributeError:
                        #do something here
                        sys_logger.critical("Address and description not found.")
                        sys.exit(1)
            find = Find()
            change = Change()
            push = Push()
            poke = Poke()
            tools = Tools()

            if command == 'find_ip':
                find.ip_client(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_ip--ap':
                find.ip_ap(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_ip--phone':
                find.ip_phone(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_mac':
                find.mac_client(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_mac--ap':
                find.mac_ap(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_mac--phone':
                find.mac_phone(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'change_mac--vlan':
                change.mac_vlan(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'push_bas':
                push.bas(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'poke_port':
                poke.port(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_desc':
                find.desc(values_dict, config.username, config.password, config.cpi_ipv4_address, cli_parse.args.name, logger)
            if command == 'find_desc--active': # currently does not take into account the -n flag
                find.desc_active(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'find_core':
                find.core(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'upgrade':
                UpgradeCode(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'mock_upgrade':
                MockUpgradeCode(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
            if command == 'ap_alarms':
                tools.checkAlarms(values_dict, config.username, config.password,config.cpi_ipv4_address, logger)
            if command == 'test_api_mac':
                TestApi.test_method(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
        else: # no sub commands
            config.load_full_conf()
            self.main(args.debug)

    def main(self, debug):

        # instantiate system logger (separate from per device loggers)
        if debug:
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
            alive_threads = [t for t in threads if t.is_alive()]
            threads = alive_threads
            t_count = len(threads)
            sys_logger.debug("Thread count before: {}".format(t_count))

            if t_count < max_threads:

                # instantiate per-thread/device logger (separate from system logger)
                if debug:
                    logger = self.set_logger(switch_ipv4_address_list[0], logging.DEBUG)
                else:
                    logger = self.set_logger(switch_ipv4_address_list[0], logging.INFO)

                try:
                    if 'code_upgrade' in proc_dict:
                        t = threading.Thread(target=UpgradeCode,
                                             args=({'address': switch_ipv4_address_list[0]}, config.username,
                                                   config.password, config.cpi_ipv4_address, logger)
                                             )
                    elif 'test_code_upgrade' in proc_dict:
                        t = threading.Thread(target=MockUpgradeCode,
                                             args=({'address': switch_ipv4_address_list[0]}, config.username,
                                                   config.password, config.cpi_ipv4_address, logger)
                                             )
                    elif 'push_command' in proc_dict:
                        t = threading.Thread(target=self.push_command({'address': switch_ipv4_address_list[0]},
                                                                      config.config_command, logger))
                    elif 'push_configuration' in proc_dict:
                        t = threading.Thread(target=self.push_configuration({'address': switch_ipv4_address_list[0]},
                                                                            config.config_configuration, logger))
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
                    time.sleep(30) # delay before creating next thread.
            else:
                time.sleep(5) # delay before checking thread count

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
            sys_logger.error("{} is selected.".format(proc_dict))
            sys_logger.error("This will NOT reload switches: {}".format(devices))
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
