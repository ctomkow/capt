# Craig Tomkow
# May 22, 2018
#
# Config handler module (singleton)


# system imports
import configparser


def load_configuration():

    config = configparser.ConfigParser()
    config.read("config.text")

    # define global variables
    global username
    global password

    global cpi_version
    global cpi_ipv4_address

    global dev_type
    global dev_concurrent_threads
    global dev_ipv4_address

    global proc_code_upgrade
    global proc_push_config
    global proc_test_api_calls

    global config_user_exec
    global config_priv_exec
    global config_global_config

    username               = config['DEFAULT']['username']
    password               = config['DEFAULT']['password']

    cpi_version            = config['CPI']['version']
    cpi_ipv4_address       = config['CPI']['ipv4_address']

    dev_type               = config['DEVICE']['type']
    dev_concurrent_threads = config['DEVICE']['concurrent']
    dev_ipv4_address       = config['DEVICE']['ipv4_address']

    proc_code_upgrade      = config['PROCEDURE']['code_upgrade']
    proc_push_config       = config['PROCEDURE']['push_config']
    proc_test_api_calls    = config['PROCEDURE']['test_api_calls']

    config_user_exec       = config['CONFIG']['user_exec']
    config_priv_exec       = config['CONFIG']['priv_exec']
    config_global_config   = config['CONFIG']['global_config']

    # strip out newlines
    dev_ipv4_address = dev_ipv4_address.split('\n')
    config_user_exec = config_user_exec.split('\n')
    config_priv_exec = config_priv_exec.split('\n')
    config_global_config = config_global_config.split('\n')

    # remove the empty string at beginning
    dev_ipv4_address.pop(0)
    config_user_exec.pop(0)
    config_priv_exec.pop(0)
    config_global_config.pop(0)
