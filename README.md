[![Build Status](https://travis-ci.org/ctomkow/capt.svg?branch=master)](https://travis-ci.org/ctomkow/capt)

# Installation and Usage 

## Cisco APi Tool (capt): a nettool built on Cisco Prime's API

Aye Aye Capt.

I can't hear yoooouu!

The tool currently (as of v0.1.0) only verifies that code upgrades on Cisco switches were successful. This is mainly done through Cisco Prime Infrastructure's REST API. The code_upgrade method pulls the 'before' state of a switch, reloads the switch to initiate the code upgrade, then pulls the 'after' state of the switch. Comparison of the two states is done to ensure nothing is broken. This upgrade procedure can be scaled up by having concurrent threads.

Other functions are a work in progress, such as pushing configuration to switches.

Note: the program does not push new code to the device. The code needs to be uploaded ahead of time so that a reboot is all that is necessary.


### DEVICE SUPPORT

* Cisco switches

### PROCEDURE SUPPORT

* code_upgrade

### FUTURE DEVELOPMENT

* Implement more procedures
* (see bug tracking for other enhancements)

### DEPENDENCIES

* Cisco Prime Infrastructure 3.3+
* Python 3.5+
* Requests 2.9.1+

### USAGE

cli subcommands are a work in progress (think, `ip addr show`).

If cli commands are not given, the configuration is done through a configuration file; `config.text`

Then simply run the program, `python capt.py`
For debug output, `python capt.py -v`

```
[DEFAULT]
username=user
password=secret

[CPI]
version=3.3
ipv4_address=10.10.10.10

[DEVICE]
type=switch
concurrent=1
ipv4_address:
    20.20.20.20
    20.20.20.21
    20.20.20.22

# specify one procedure (yes)
[PROCEDURE]
code_upgrade:yes
test_code_upgrade:
push_command:
push_configuration:

[CONF]
command:
configuration:

```
