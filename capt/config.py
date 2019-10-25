
# Config handler module (singleton)

# system imports
import configparser
import os


def load_base_conf():
    config = configparser.ConfigParser()
    #config.read("config.text")
    config.read(os.path.join(os.path.expanduser('~'), "config.text"))

    global username
    global password

    global cpi_version
    global cpi_ipv4_address

    username = config['DEFAULT']['username']
    password = config['DEFAULT']['password']

    cpi_version = config['CPI']['version']
    cpi_ipv4_address = config['CPI']['ipv4_address']


def load_full_conf():

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), "config.text"))
    #config.read("config.text")

    global username
    global password

    global cpi_version
    global cpi_ipv4_address

    global dev_type
    global dev_concurrent_threads
    global dev_ipv4_address

    global proc_code_upgrade
    global proc_test_code_upgrade
    global proc_push_command
    global proc_push_configuration

    global config_command
    global config_configuration

    username                = config['DEFAULT']['username']
    password                = config['DEFAULT']['password']

    cpi_version             = config['CPI']['version']
    cpi_ipv4_address        = config['CPI']['ipv4_address']

    dev_type                = config['DEVICE']['type']
    dev_concurrent_threads  = config['DEVICE']['concurrent']
    dev_ipv4_address        = config['DEVICE']['ipv4_address']

    proc_code_upgrade       = config['PROCEDURE']['code_upgrade']
    proc_test_code_upgrade  = config['PROCEDURE']['test_code_upgrade']
    proc_push_command       = config['PROCEDURE']['push_command']
    proc_push_configuration = config['PROCEDURE']['push_configuration']

    config_command          = config['CONF']['command']
    config_configuration    = config['CONF']['configuration']

    # strip out newlines
    dev_ipv4_address     = dev_ipv4_address.split('\n')
    config_command       = config_command.split('\n')
    config_configuration = config_configuration.split('\n')

    # remove the empty string at beginning
    dev_ipv4_address.pop(0)
    config_command.pop(0)
    config_configuration.pop(0)
