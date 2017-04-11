Netbox external inventory script
================================

[![Build Status](https://travis-ci.org/AAbouZaid/netbox-as-ansible-inventory.svg?branch=master)](https://travis-ci.org/AAbouZaid/netbox-as-ansible-inventory) [![Coverage Status](https://coveralls.io/repos/github/AAbouZaid/netbox-as-ansible-inventory/badge.svg?branch=master)](https://coveralls.io/github/AAbouZaid/netbox-as-ansible-inventory?branch=master)

ToC
---
  * [Intro](#intro)
  * [Requirements](#requirements)
  * [Inventory groups](#inventory-groups)
  * [Hosts variables](#hosts-variables)
  * [Usage](#usage)


Intro
-----
This script uses NetBox as a dynamic inventory for Ansible. [Netbox](https://github.com/digitalocean/netbox/) is an IP address management (IPAM) and data center infrastructure management (DCIM) tool. It's nice, modern, and has good APIs ... so it's a pretty nice option to serve as a "Source of Truth".

You can group servers as you want and based on what you have in Netbox, you can select fields as groups or as vars for hosts. And you can use default fields or custom fields.


Requirements
---------
```
netbox>=1.6
pyyaml>=3.11
```


Inventory groups
----------------
Server could be grouped by any section in Netbox, e.g. you can group hosts by "site, "rack", "role", "platform", or any other section in Netbox (please remember, right now you need to use the names as in API not in UI).

So if you have a "site" called "US-East", in Ansible you will get a group is called "US-East" has all hosts in that site.

If that section is a default section you need to put it under `group_by.default` if it is a custom section put it under `group_by.custom`.

Here the servers will be grouped based on `platform`. So if you have "Ubuntu" and "CentOS" as platforms in Netbox, you will have 2 groups of servers that using that systems.
```
group_by:
    default:
        - platform
```

Hosts variables
---------------
Netbox sections could be used as variables for hosts! e.g. you could use the IP of the host in Netbox as `ansible_ssh_host`, or use a custom field as well.

There are 3 sections here, first type is `IP`, second one is `General`, and finally `Custom`. 

Variables are defined as `Key: Value`. The key is what will be in Ansible and value comes from Netbox.

Here `primary_ip` will be used as value for `ansible_ssh_host`.
```
hosts_vars:
    ip:
        ansible_ssh_host: primary_ip
```


Usage
-----
```
usage: netbox-inventory.py [-h] [-c CONFIG_FILE] [--list] [--host HOST]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Path for configuration of the script. (default:
                        netbox-inventory.yml)
  --list                Print all hosts with vars as Ansible dynamic inventory
                        syntax. (default: False)
  --host HOST           Print specific host vars as Ansible dynamic inventory
                        syntax. (default: None)
```

In Ansible:
```
ansible all -i netbox-inventory.py -m ping
```
