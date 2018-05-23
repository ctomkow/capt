# Craig Tomkow
# May 22, 2018
#
# Config handler module (singleton)


# system imports
import configparser


def load_configuration():

    config = configparser.ConfigParser()
    config.read("config.text")

    username           = config['DEFAULT']['username']
    password           = config['DEFAULT']['password']
    glean_state        = config['DEFAULT']['glean_state']
    push_config        = config['DEFAULT']['push_config']

    cpi_version        = config['CPI']['version']
    cpi_ipv4_address   = config['CPI']['ipv4_address']

    dev_type           = config['DEVICE']['type']
    dev_model          = config['DEVICE']['model']
    dev_ipv4_address   = config['DEVICE']['ipv4_address']

    attr_reachability  = config['TEST_ATTRIBUTE']['reachability']
    attr_software      = config['TEST_ATTRIBUTE']['software']
    attr_stack_member  = config['TEST_ATTRIBUTE']['stack_member']
    attr_active_port   = config['TEST_ATTRIBUTE']['active_port']
    attr_active_uplink = config['TEST_ATTRIBUTE']['active_uplink']
    attr_vlan          = config['TEST_ATTRIBUTE']['vlan']