#!/usr/bin/env python

# -*- encoding: utf-8 -*-
# Copyright 2017, Ahmed AbouZaid <http://aabouzaid.com/>
# setup.py file is part of Netbox dynamic inventory script.
# https://github.com/AAbouZaid/netbox-as-ansible-inventory

from setuptools.command.test import test as TestCommand
from setuptools import setup, Command
from codecs import open as openc
from os import path
import subprocess
import sys


def open_file(file_name, splitlines=False):
    here = path.abspath(path.dirname(__file__))
    with openc(path.join(here, file_name), encoding='utf-8') as opened_file:
        file_output = opened_file.read().strip()

    if splitlines:
        file_output = file_output.splitlines()

    return file_output


# Get vars from project files.
version = open_file('VERSION')
long_description = open_file('README.rst')
main_requirements = open_file('requirements.txt', splitlines=True)
tests_requirements = open_file('tests/requirements.txt', splitlines=True)


class PyTest(TestCommand):
    """ Run tests. """

    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class Release(Command):
    """ Tag, push, and upload to PyPI. """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Create Git tag.
        tag_name = 'v%s' % version
        cmd = ['git', 'tag', '-a', tag_name, '-m', 'version %s' % version]
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push Git tag to origin remote.
        cmd = ['git', 'push', 'origin', tag_name]
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push branch to origin remote.
        cmd = ['git', 'push', 'origin', 'master']
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Upload package to PyPI.
        cmd = ['python', 'setup.py', 'sdist', 'upload']
        print(' '.join(cmd))
        subprocess.check_call(cmd)


class Requirements(Command):
    """ Install requirements. """

    user_options = [('tests-requirement', 't', "Install requirements for unit test.")]

    def initialize_options(self):
        self.tests_requirement = False

    def finalize_options(self):
        pass

    def run(self):
        # Install requirements via pip.
        cmd = ['pip', 'install', '-r', 'requirements.txt']

        if self.tests_requirement:
            cmd += ['-r', 'tests/requirements.txt']

        print(' '.join(cmd))
        subprocess.check_call(cmd)

setup(
    name='ansible-netbox-inventory',
    version=version,
    description='Ansible dynamic inventory script for Netbox',
    long_description=long_description,
    url='https://github.com/AAbouZaid/netbox-as-ansible-inventory',
    author='Ahmed AbouZaid',
    author_email='@'.join(("ahmed.m", "aabouzaid.com")),  # To avoid spam.
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    keywords=['ansible', 'netbox', 'dynamic', 'inventory'],
    packages=['netbox'],
    package_data={
        'netbox': ['netbox.yml'],
    },
    install_requires=main_requirements,
    extras_require={
        'tests': tests_requirements,
    },
    cmdclass={
        'test': PyTest,
        'release': Release,
        'requirements': Requirements,
    },
    entry_points={
        'console_scripts': ['ansible-netbox-inventory=netbox.netbox:main']
    }
)
