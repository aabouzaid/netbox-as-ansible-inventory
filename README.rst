Netbox dynamic inventory script
===============================

|PyPI Version| |Python Version| |Build Status| |Codacy Badge| |Code Health| |Coverage Status|

ToC
---

-  `Intro <#intro>`__
-  `Compatibility <#compatibility>`__
-  `Grouping <#grouping>`__
-  `Hosts variables <#hosts-variables>`__
-  `Options <#options>`__
-  `Usage <#usage>`__


Intro
-----

This is a Netbox dynamic inventory script for Ansible.
`Netbox <https://github.com/digitalocean/netbox/>`__ is an IP address
management (IPAM) and data center infrastructure management (DCIM) tool.
It's nice, modern, and has good APIs ... so it's a pretty nice option to
serve as a "Source of Truth".

You can group servers as you want and based on what you have in Netbox,
you can select fields as groups or as vars for hosts. And you can use
default fields or custom fields.


Compatibility
-------------

The script tested with ``netbox = v1.6`` and ``netbox = v2.0.4``,
but most probably it will work with all netbox v1.0 and above.


Grouping
--------

Servers could be grouped by any section in Netbox.
e.g. you can group hosts by "site, "rack", "role", "platform",
or any other section in Netbox.
**Please remember**: For grouping, API names should be used not UI names.

So if you have a "site" called "US-East", in Ansible you will get a
hosts group is called "US-East" has all hosts in that site.

If that section is a `default` section you need to put it under
``group_by.default`` if it's a custom section (custom fields), then
put it under ``group_by.custom``.

Here is an example how servers will be grouped based on their ``platform``.

::

    group_by:
       default:
           - platform

So if you have "Ubuntu" and "CentOS" as platforms in Netbox,
you will have 2 groups of servers that using that systems.


Hosts variables
---------------

Netbox sections could be used as variables for hosts! e.g. you could use
the IP of the host in Netbox as ``ansible_ssh_host``, or use a custom
field as well.

There are 3 sections here, first type is ``IP``, second one is
``General``, and finally ``Custom``.

Variables are defined as ``Key: Value``. The key is what will be in
Ansible and value comes from Netbox.

::

    hosts_vars:
        ip:
            ansible_ssh_host: primary_ip

Here ``primary_ip`` will be used as value for ``ansible_ssh_host``.


Options
-------

::

    $ netbox.py -h
    usage: netbox.py [-h] [-c CONFIG_FILE] [--list] [--host HOST]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            Path for script's configuration. Also
                            "NETBOX_CONFIG_FILE" could be used as env var to set
                            conf file path. (default: netbox.yml)

      --list                Print all hosts with vars as Ansible dynamic inventory
                            syntax. (default: False)
      --host HOST           Print specific host vars as Ansible dynamic inventory
                            syntax. (default: None)

You can also set config file path through environment variable ``NETBOX_CONFIG_FILE``.


Usage
-----

::

    $ ansible all -i netbox.py -m ping


.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ansible-netbox-inventory.svg
   :target: https://pypi.python.org/pypi/ansible-netbox-inventory
.. |PyPI Version| image:: https://img.shields.io/pypi/v/ansible-netbox-inventory.svg
   :target: https://pypi.python.org/pypi/ansible-netbox-inventory
.. |Build Status| image:: https://travis-ci.org/AAbouZaid/netbox-as-ansible-inventory.svg?branch=master
   :target: https://travis-ci.org/AAbouZaid/netbox-as-ansible-inventory
.. |Codacy Badge| image:: https://img.shields.io/codacy/8deda33a029a45a8bc360df4dcbf8660.svg
   :target: https://www.codacy.com/app/AAbouZaid/netbox-as-ansible-inventory
.. |Code Health| image:: https://landscape.io/github/AAbouZaid/netbox-as-ansible-inventory/master/landscape.svg?style=flat
   :target: https://landscape.io/github/AAbouZaid/netbox-as-ansible-inventory/master
.. |Coverage Status| image:: https://coveralls.io/repos/github/AAbouZaid/netbox-as-ansible-inventory/badge.svg
   :target: https://coveralls.io/github/AAbouZaid/netbox-as-ansible-inventory
