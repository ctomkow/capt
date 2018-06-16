# Installation and Usage 

## Cisco APi Tool: a nettool built on Cisco Prime's API

The main goal of this tool is to verify that a code upgrade to Cisco switches was successful. This is mainly done through Cisco Prime Infrastructure's REST API. The code_upgrade method pulls the 'before' state of a switch, reloads the switch to initiate the code upgrade, then pulls the 'after' state of the switch. Comparison of the two states is done to ensure nothing is broken. This upgrade procedure can be scaled up by having concurrent processes.

Note: at this moment the program does not push new code to the device. The code needs to be uploaded ahead of time so that a reboot is all that is necessary.


### DEVICE SUPPORT

* Cisco switches.

### FUTURE DEVELOPMENT

* TBD

### DEPENDENCIES

* Cisco Prime Infrastructure 3.3+
* Python 3.5+
* swITch.py 0.1.2 (https://github.com/ctomkow/swITch)
* netmiko 2.1.1

### USAGE

Most of the configuration is done through a configuration file; `config.text`

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

# true/false; only one true at a time
[PROCEDURE]
code_upgrade:true
push_config:false
test_api_calls:false

# if no config, use 'false' as placeholder
[CONFIG]
user_exec:
    show int status
priv_exec:
    show runn
global_config:
    false
```


`$python ./Verify.py`
