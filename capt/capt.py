#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# system imports
import os #for logging file
import smtplib
import threading
import time
import sys
import logging
from logging.handlers import SMTPHandler
import datetime


# local imports
import config
from procedure.upgrade_code import UpgradeCode
from procedure.mock_upgrade_code import MockUpgradeCode
from function.find import Find
from function.change import Change
from function.push import Push
from function.poke import Poke
from function.tools import Tools
from function.reports import Reports
from function.test_api import TestApi
from cli_crafter import CliCrafter
from cli_parser import CliParser


class Capt:

    def __init__(self):

        # create CLICrafter object to parse CLI input
        craft = CliCrafter()

        #argcomplete.autocomplete(craft.parser)

        # create a namespace object of the arguments. If using a -h, the code will exit here
        # after this point the program has all of the chosen command line arguments
        args = craft.parser.parse_args()

        #arg_dict = vars(args);# this could turn the args into a dictionary to pass, is it necessary though?
        cli_parse = CliParser(args)

        if args.sub_cmd is not None:

            config.load_base_conf()  # should config use globals?

            # subber = cli_parse.first_sub_cmd()
            # if subber == 'find' or subber == 'change' or subber == 'tools' or subber == 'poke' or subber == 'push':
            #     log_file = False
            # elif subber == 'upgrade' or subber == 'mock':
            #     log_file = True
            # else:
            #     log_file = True

            #Revisit logging code
            log_file = True;



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
                        try:
                            logger = self.set_logger(args.reports, logging.INFO, log_file)
                        except AttributeError:
                            sys_logger.critical("Address and description not found.")
                            sys.exit(1)
            # if'email' in args and args.email is not None:
            #     self.set_logger_email(config, args.email,logger)


            if cli_parse.args.sub_cmd == 'find':
                find = Find()
                if cli_parse.args.find == 'ip':
                    if not (cli_parse.args.ap or cli_parse.args.phone):
                        find.ip_client(args, config, logger)
                    elif cli_parse.args.ap and not cli_parse.args.phone:
                        find.ip_ap(args, config, logger)
                    elif cli_parse.args.phone and not cli_parse.args.ap:
                        find.ip_phone(args, config, logger)
                elif cli_parse.args.find == 'mac':
                    args.address = CliParser.normalize_mac(args.address)
                    if not (cli_parse.args.ap or cli_parse.args.phone):
                        find.mac_client(args, config, logger)
                        #find.old_mac_client(values_dict, config.username, config.password, config.cpi_ipv4_address, logger)
                    elif cli_parse.args.ap and not cli_parse.args.phone:
                        find.mac_ap(args, config, logger)
                    elif cli_parse.args.phone and not cli_parse.args.ap:
                        find.mac_phone(args, config, logger)
                elif cli_parse.args.find == 'desc':
                    if not args.active:
                        find.desc(args, config, logger)
                    else:
                        find.desc_active(args, config, logger)
                elif cli_parse.args.find == 'core':
                    find.core(args, config, logger)
            elif cli_parse.args.sub_cmd == 'change':
                change = Change()
                change.mac_vlan(args, config, logger)
            elif cli_parse.args.sub_cmd == 'push':
                push = Push()
                if cli_parse.args.push == 'bas' :
                    push.bas(args, config, logger)
            elif cli_parse.args.sub_cmd == 'poke':
                poke = Poke()
                if cli_parse.args.poke == 'port':
                    poke.port(args,config,logger)
            elif cli_parse.args.sub_cmd == 'reports':
                reports = Reports()
                if cli_parse.args.reports == 'portcount':
                    reports.port_count(args, config, logger)
                elif cli_parse.args.reports == 'devcount':
                    reports.dev_count(args, config, logger)
                elif cli_parse.args.reports == 'vlanmap':
                    reports.vlanmap(args, config, logger)
            elif cli_parse.args.sub_cmd == 'mock':
                if cli_parse.args.mock =='upgrade':
                    MockUpgradeCode(args, config, logger)
            elif cli_parse.args.sub_cmd == 'upgrade':
                UpgradeCode(args, config, logger)
            elif cli_parse.args.sub_cmd == 'tools':
                tools = Tools()
                if cli_parse.args.tools == 'apcheck':
                    if cli_parse.args.apcheck == "alarms":
                        tools.checkAlarms(args, config, logger)
                    elif cli_parse.args.apcheck == "slow_ports":
                        tools.slow_aps(args,config,logger)
                    elif cli_parse.args.apcheck == "unack":
                        tools.un_ack_alarms(args,config,logger)

                    # if 'days' in self.args and self.args.days is not None:
                    #     dict_of_values = {'days': self.args.days}
                    # else:
                    #     dict_of_values = {'days': "all"}

            elif cli_parse.args.sub_cmd == 'test_api':
                TestApi.test_method(args, config, logger)

            if 'email' in args and args.email is not None:

                with open(config.logpath, 'r') as file:
                    #data = file.read().replace('\n', '')
                    data = file.read()

                try:
                    smtpObj = smtplib.SMTP(config.email_host)
                    smtpObj.sendmail(config.email_from, [args.email], data)
                    #smtpObj.sendmail(config.email_from, [args.email], email_string )
                    logger.info("successfully sent Email")
                except smtplib.SMTPException:
                    logger.info("Failed to send Email")
                except Exception as e:
                    logger.info(e)




    def set_logger(self, nm, level, log_file=True):

        # remove colons from name if exists (e.g. mac address)
        name = nm.replace(":","")
        formatter = logging.Formatter(
            fmt='%(asctime)s : {} : %(levelname)-8s : %(message)s'.format(name),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        if log_file:

            config.logpath = os.path.abspath(os.path.join(os.sep, 'var', 'log', 'capt',"{}-{}".format(datetime.datetime.now().strftime("%Y%m%d"), name)))
            handler = logging.FileHandler(config.logpath,mode='a')
                #"{}-{}".format(datetime.datetime.now().strftime("%Y%m%d"), name),
                #mode='a')
            #os.path.abspath(os.path.join(os.sep, 'usr', 'lib', 'capt'))
            # handler = logging.FileHandler(
            #     "{}-{}".format(datetime.datetime.now().strftime("%Y%m%d"), name),
            #     mode='a')
            handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if log_file:
            logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger


    def set_logger_email(self,config, email,logger):

        formatter = logging.Formatter(
            fmt='%(asctime)s  : %(levelname)-8s : %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


        handler = SMTPHandler(config.email_host,config.email_from,email,"test-subject")
        handler.setFormatter(formatter)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        return logger

if __name__ == '__main__':

    Capt()
