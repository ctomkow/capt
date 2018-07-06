
# Installation and Usage 

## Cisco APi Tool (capt): a nettool built on Cisco Prime's API

Aye Aye Capt.

I can't hear yoooouu!

A network tool based on Cisco Prime Infrastructure's REST API. Capt contains a collection of network tools for simplified network management.

The code_upgrade procedure pulls the 'before' state of a switch, reloads the switch to initiate the code upgrade, then pulls the 'after' state of the switch. Comparison of the two states is done to ensure nothing is broken. This upgrade procedure can be scaled up by having concurrent threads. Other cli commands exist as well as one-off executions.

Note: the program does not push new code to the device. The code needs to be uploaded ahead for the code_upgrade procedure to work (it reloads the switch).

### PROCEDURE SUPPORT

* code_upgrade

### FUNCTION SUPPORT

* find ip x.x.x.x [--phone | --ap]
* find mac xx:xx:xx:xx:xx:xx [--phone | --ap]
* upgrade x.x.x.x
* mock upgrade x.x.x.x (non-production impacting test)

### FUTURE DEVELOPMENT

* Implement more procedures and functions
* (see bug tracking for other enhancements)

### DEPENDENCIES

* Cisco Prime Infrastructure 3.3+
* Python 3.5+
* Requests 2.9.1+
* argcomplete 1.9.4+

### USAGE

The program can be configured with a conf file; `config.text`

Once the conf file is made, simply run the program, `$python capt.py`
For debug output, `$python capt.py -v`

<br><br>

capt can be executed through cli commands. Note: The `config.text` needs to still exist as the [DEFAULT] and [CPI] sections are required.

Some cli function commands.

`$python capt.py find ip x.x.x.x`

`$python capt.py find ip x.x.x.x --phone`

`$python capt.py find mac xx:xx:xx:xx:xx:xx`

cli procedure commands.

`$python capt.py upgrade x.x.x.x`

`$python capt.py mock upgrade x.x.x.x`

<br><br>

Sample `config.text`

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
