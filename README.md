Netbox external inventory script
================================

ToC
---
  * [Intro](#intro)
  * [Requirements](#requirements)
  * [Inventory groups](#inventory-groups)
  * [Hosts variables](#hosts-variables)
  * [Usage](#usage)
  * [Output example](#output-example)


Intro
-----
This script uses NetBox as a dynamic inventory for Ansible. [Netbox](https://github.com/digitalocean/netbox/) is an IP address management (IPAM) and data center infrastructure management (DCIM) tool. It's nice, modern, and has good APIs ... so it's a pretty nice option to serve as a "Source of Truth".

You can group servers as you want and based on what you have in Netbox, you can select fields as groups or as vars for hosts. And you can use default fields or custom fields.


Requirements
------------
-


Inventory groups
----------------
Server could be grouped by any section in Netbox, e.g. you can group hosts by "site, "rack", "role", "platform", or any other section in Netbox (please remember, right now you need to use the names as in API not in UI).

So if you have a "site" called "US-East", in Ansible you will get a group is called "US-East" has all hosts in that site.

If that section is a default section you need to put it under `group_by.default` if it is a custom section put it under `group_by.custom`.


Hosts variables
---------------
Netbox sections could be used as variables for hosts! e.g. you could use the IP of the host in Netbox as `ansible_ssh_host`, or use a custom field as well.

There are 3 sections here, first type is `IP`, second one is `General`, and finally `Custom`. 

Variables are defined as `Key: Value`. The key is what will be in Ansible and value comes from Netbox.

e.g.
```
hosts_vars:
    ip:
        ansible_ssh_host: primary_ip
```
Here `primary_ip` will be used as value of `ansible_ssh_host`.


Usage
-----
-


Output example
--------------
-
