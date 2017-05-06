#!/usr/bin/env python

# -*- coding: utf-8 -*-
# Copyright 2017, Ahmed AbouZaid <http://aabouzaid.com/>
# setup.py file is part Netbox dynamic inventory script.
# https://github.com/AAbouZaid/netbox-as-ansible-inventory

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

# Get the requirements.
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as main_requirements_file:
    main_requirements = main_requirements_file.read().splitlines()
with open(path.join(here, 'tests/requirements.txt'), encoding='utf-8') as tests_requirements_file:
    tests_requirements = tests_requirements_file.read().splitlines()

setup(
    name='ansible-netbox-inventory',
    version='1.0.0',
    description='Ansible dynamic inventory script for Netbox',
    long_description=long_description,
    url='https://github.com/AAbouZaid/netbox-as-ansible-inventory',
    author='Ahmed AbouZaid',
    license='GPLv3',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    keywords=['ansible', 'netbox', 'inventory'],
    install_requires=main_requirements,
    extras_require={
        'test': tests_requirements,
    },
)
