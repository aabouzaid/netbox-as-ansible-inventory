#! /usr/bin/python

import os
import sys
import json
import yaml
import urllib
import argparse


# Utils.
def get_value_by_path(source_dict, key_path, ignore_key_error=False):
    """Get key value from nested dict by path.

    Args:
        source_dict: The dict that we look into.
        key_path: The path of key in dot notion. e.g. "parent_dict.child_dict.key_name"
        ignore_key_error: Ignore KeyError if the key not found in provided path.

    Returns:
        If key found in provided path, it will be returned.
        If not, None will be returned.
    """

    try:
        key_output = reduce(lambda xdict, key: xdict[key], key_path.split('.'), source_dict)
    except KeyError, key_name:
        if ignore_key_error:
            key_output = None
        else:
            print "The key %s is not found. Please remember, Python is case sensitive." % key_name
            sys.exit(1)
    except TypeError:
        key_output = None
    return key_output


def get_full_path(file_name):
    """Get full path of file.

    Args:
        file_name: The file that will be looked for.

    Returns:
        Full path of the file.
    """

    full_path = os.path.dirname(os.path.realpath(__file__)) + "/" + file_name
    return full_path


class Script(object):
    """All stuff related to script itself.
    """

    def cli_arguments(self):
        """Script cli arguments.
        By default Ansible calls "--list" as argument.
        """

        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-c", "--config-file", default="netbox-inventory.yml",
                            help="Path for configuration of the script.")
        parser.add_argument("--list", help="Print all hosts with vars as Ansible dynamic inventory syntax.",
                            action="store_true")
        parser.add_argument("--host", help="Print specific host vars as Ansible dynamic inventory syntax.",
                            action="store")
        cli_arguments = parser.parse_args()
        return cli_arguments

    def open_yaml_file(self, yaml_file):
        """Open YAML file.

        Args:
            yaml_file: Relative or absolute path to YAML file.

        Returns:
            Content of YAML the file.
        """

        # Load content of YAML file.
        try:
            with open(yaml_file, 'r') as config_yaml_file:
                try:
                    yaml_file_content = yaml.load(config_yaml_file)
                except yaml.YAMLError as yaml_error:
                    print(yaml_error)
                    sys.exit(1)
        except IOError as io_error:
            print "Cannot open YAML file: %s\n%s" % (get_full_path(yaml_file), io_error)
            sys.exit(1)
        return yaml_file_content


class NetboxAsInventory(object):
    """Netbox as a dynamic inventory for Ansible.

    Retrieves hosts list from netbox API and returns Ansible dynamic inventory (JSON).

    Attributes:
        script_config_data: Content of its config which comes from YAML file.
    """

    def __init__(self, script_args, script_config_data):
        # Script arguments.
        self.config_file = script_args.config_file
        self.list = script_args.list
        self.host = script_args.host

        # Script configuration.
        script_config = script_config_data.get("netbox_inventory")
        if script_config:
            self.api_url = script_config["main"].get('api_url')
            self.group_by = script_config.setdefault("group_by", {})
            self.hosts_vars = script_config.setdefault("hosts_vars", {})
        else:
            print "The key 'netbox_inventory' is not found in config file."
            sys.exit(1)

        # Get value based on key.
        self.key_map = {
            "default": "name",
            "general": "name",
            "custom": "value",
            "ip": "address"
        }

    def get_hosts_list(self):
        """Retrieves hosts list from netbox API.

        Returns:
            A list of all hosts from netbox API.
        """

        if not self.api_url:
            print "Please check API URL in script configuration file."
            print "Current configuration file: %s" % (get_full_path(self.config_file))
            sys.exit(1)

        if self.host:
            data_source = "{}?name={}".format(self.api_url, self.host)
        else:
            data_source = self.api_url

        json_data = urllib.urlopen(data_source).read()
        hosts_list = json.loads(json_data)
        return hosts_list

    def add_host_to_inventory_groups(self, groups_categories, inventory_dict, host_data):
        """Add a host to its groups.

        It checks if host groups and adds it to these groups.
        The groups are defined in script config file.

        Args:
            groups_categories: A dict has a categories of groups that will be
                used as inventory groups.
            inventory_dict: A dict for inventory has groups and hosts.
            host_data: A dict has a host data which will be added to inventory.

        Returns:
            The same dict "inventory_dict" after update.
        """

        server_name = host_data.get("name")
        categories_source = {
            "default": host_data,
            "custom": host_data.get("custom_fields")
        }

        if groups_categories:
            for category in groups_categories:
                key_name = self.key_map[category]
                data_dict = categories_source[category]

                for group in groups_categories[category]:
                    group_name = get_value_by_path(data_dict, group + "." + key_name)

                if group_name:
                    if group_name not in inventory_dict:
                        inventory_dict.update({group_name: []})

                    if server_name not in inventory_dict[group_name]:
                        inventory_dict[group_name].append(server_name)
        else:
            if "no_group" not in inventory_dict:
                inventory_dict.setdefault("no_group", [server_name])
            else:
                inventory_dict["no_group"].append(server_name)
        return inventory_dict

    def get_host_vars(self, host_data, host_vars):
        """Find host vars.

        These vars will be used for host in the inventory.
        We can select whatever from netbox to be used as Ansible inventory vars.
        The vars are defined in script config file.

        Args:
            host_data: A dict has a host data which will be added to inventory.
            host_vars: A dict has selected fields to be used as host vars.

        Returns:
            A dict has all vars are associate with the host.
        """

        host_vars_dict = dict()
        if host_vars:
            categories_source = {
                "ip": host_data,
                "general": host_data,
                "custom": host_data.get("custom_fields")
            }

            for category in host_vars:
                key_name = self.key_map[category]
                data_dict = categories_source[category]

                for key, value in host_vars[category].iteritems():
                    var_name = key
                    var_value = get_value_by_path(data_dict, value + "." + key_name, ignore_key_error=True)
                    if var_value:
                        if host_vars.get("ip") and value in host_vars["ip"].values():
                            var_value = var_value.split("/")[0]
                        host_vars_dict.update({var_name: var_value})
        return host_vars_dict

    def update_host_meta_vars(self, inventory_dict, host_name, host_vars):
        """Update host meta vars.

        Add host and its vars to "_meta.hostvars" path in the inventory.

        Args:
            inventory_dict: A dict for inventory has groups and hosts.
            host_name: Name of the host that will have vars.
            host_vars: A dict has selected fields to be used as host vars.

        Returns:
            This function doesn't return, it updates the dict in place.
        """

        if host_vars and not self.host:
            inventory_dict['_meta']['hostvars'].update({host_name: host_vars})
        elif host_vars and self.host:
            inventory_dict.update({host_name: host_vars})

    def generate_inventory(self):
        """Generate Ansible dynamic inventory.

        Returns:
            A dict has inventory with hosts and their vars.
        """

        inventory_dict = dict()
        netbox_hosts_list = self.get_hosts_list()
        if netbox_hosts_list:
            inventory_dict.update({"_meta": {"hostvars": {}}})
            for current_host in netbox_hosts_list:
                server_name = current_host.get("name")
                self.add_host_to_inventory_groups(self.group_by, inventory_dict, current_host)
                host_vars = self.get_host_vars(current_host, self.hosts_vars)
                self.update_host_meta_vars(inventory_dict, server_name, host_vars)
        return inventory_dict

    def print_inventory_json(self, inventory_dict):
        """Print inventory.

        Args:
            inventory_dict: Inventory dict has groups and hosts.

        Returns:
            It prints the inventory in JSON format if condition is true.
        """

        if self.host:
            result = inventory_dict.setdefault(self.host, {})
        elif self.list:
            result = inventory_dict
        else:
            result = {}
        print json.dumps(result)

# Main.
if __name__ == "__main__":
    # Script vars.
    script = Script()
    args = script.cli_arguments()
    config_data = script.open_yaml_file(args.config_file)

    # Netbox vars.
    netbox = NetboxAsInventory(args, config_data)
    ansible_inventory = netbox.generate_inventory()
    netbox.print_inventory_json(ansible_inventory)
