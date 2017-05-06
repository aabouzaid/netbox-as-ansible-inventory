#!/usr/bin/env python
import netbox
from . import commons
import pytest
import responses
import json

#
# Init.

# Common vars.
test_cfg = commons.test_cfg
config = commons.config
netbox_api_output = commons.netbox_api_output
fake_host = commons.fake_host
fake_host_json = json.dumps(commons.fake_host)


# Fake args.
class Args(object):
    config_file = test_cfg["netbox_config"]
    host = None
    list = True

# Init Netbox class.
netbox_inventory = netbox.NetboxAsInventory(Args, config)
Args.host = "fake_host"
netbox_inventory_single = netbox.NetboxAsInventory(Args, config)


# Fake Netbox API response.
def netbox_json_response(single_host=False):
    if single_host:
        json_payload = fake_host_json
    else:
        json_payload = netbox_api_output
    commons.fake_json_response(netbox_inventory.api_url, json_payload, 200)


#
# Tests.
class TestNetboxAsInventory(object):

    @pytest.mark.parametrize("args, config", [
        (Args, {})
    ])
    def test_empty_config_dict(self, args, config):
        """
        """
        with pytest.raises(SystemExit) as empty_config_error:
            netbox.NetboxAsInventory(args, config)
        assert empty_config_error

    @responses.activate
    @pytest.mark.parametrize("api_url", [
        netbox_inventory.api_url
    ])
    def test_get_hosts_list(self, api_url):
        """
        Test get hosts list from API and make sure it returns a list.
        """
        netbox_json_response()
        hosts_list = netbox_inventory.get_hosts_list(api_url)
        assert isinstance(hosts_list, list)

    @responses.activate
    @pytest.mark.parametrize("api_url", [
        None
    ])
    def test_get_hosts_list_none_url_value(self, api_url):
        """
        """
        netbox_json_response()
        with pytest.raises(SystemExit) as none_url_error:
            netbox_inventory.get_hosts_list(api_url)
        assert none_url_error

    @responses.activate
    @pytest.mark.parametrize("api_url, host_name", [
        (netbox_inventory_single.api_url, netbox_inventory_single.host)
    ])
    def test_get_hosts_list_single_host(self, api_url, host_name):
        """
        """
        netbox_json_response(single_host=True)
        host_data = netbox_inventory_single.get_hosts_list(
            api_url,
            specific_host=host_name)
        assert host_data["name"] == "fake_host"

    @pytest.mark.parametrize("server_name, group_value, inventory_dict", [
        ("fake_server", "fake_group", {})
    ])
    def test_add_host_to_group(self, server_name, group_value, inventory_dict):
        """
        Test add host to its group inside inventory dict.
        """
        netbox_inventory.add_host_to_group(server_name, group_value, inventory_dict)
        assert server_name in inventory_dict[group_value]

    @pytest.mark.parametrize("groups_categories, inventory_dict, host_data", [
        ({"default": ["device_role", "rack", "platform"]},
         {"_meta": {"hostvars": {}}},
         fake_host)
    ])
    def test_add_host_to_inventory(self, groups_categories, inventory_dict, host_data):
        """
        Test add host to its group in inventory dict (grouping).
        """
        netbox_inventory.add_host_to_inventory(groups_categories, inventory_dict, host_data)
        assert "hostvars" in inventory_dict["_meta"]
        assert "fake_rack01" in inventory_dict
        assert "fake_host" in inventory_dict["fake_rack01"]

    @pytest.mark.parametrize("groups_categories, inventory_dict, host_data", [
        ({"arbitrary_category_name": []},
         {"_meta": {"hostvars": {}}},
         fake_host),
    ])
    def test_add_host_to_inventory_with_wrong_category(self, groups_categories, inventory_dict, host_data):
        """
        """
        with pytest.raises(KeyError) as wrong_category_error:
            netbox_inventory.add_host_to_inventory(groups_categories, inventory_dict, host_data)
        assert wrong_category_error

    @pytest.mark.parametrize("groups_categories, inventory_dict, host_data", [
        ({},
         {"_meta": {"hostvars": {}}},
         fake_host),
        ({},
         {"no_group": [], "_meta": {"hostvars": {}}},
         fake_host)
    ])
    def test_add_host_to_inventory_with_no_group(self, groups_categories, inventory_dict, host_data):
        """
        """
        netbox_inventory.add_host_to_inventory(groups_categories, inventory_dict, host_data)
        assert "fake_host" in inventory_dict["no_group"]

    @pytest.mark.parametrize("groups_categories, inventory_dict, host_data", [
        ({"default": ["arbitrary_group_name"]},
         {"_meta": {"hostvars": {}}},
         fake_host),
    ])
    def test_add_host_to_inventory_with_wrong_group(self, groups_categories, inventory_dict, host_data):
        """
        """
        with pytest.raises(SystemExit) as no_group_error:
            netbox_inventory.add_host_to_inventory(groups_categories, inventory_dict, host_data)
        assert no_group_error

    @pytest.mark.parametrize("host_data, host_vars", [
        (fake_host,
         {"ip": {"ansible_ssh_host": "primary_ip"}, "general": {"rack_name": "rack"}})
    ])
    def test_get_host_vars(self, host_data, host_vars):
        """
        Test get host vars based on specific tags
        (which come from inventory script config file).
        """
        host_vars = netbox_inventory.get_host_vars(host_data, host_vars)
        assert host_vars["ansible_ssh_host"] == "192.168.0.2"
        assert host_vars["rack_name"] == "fake_rack01"

    @pytest.mark.parametrize("inventory_dict, host_name, host_vars", [
        ({"_meta": {"hostvars": {}}},
         "fake_host",
         {"rack_name": "fake_rack01"})
    ])
    def test_update_host_meta_vars(self, inventory_dict, host_name, host_vars):
        """
        Test update host vars in inventory dict.
        """
        netbox_inventory.update_host_meta_vars(inventory_dict, host_name, host_vars)
        assert inventory_dict["_meta"]["hostvars"]["fake_host"]["rack_name"] == "fake_rack01"

    @responses.activate
    def test_generate_inventory(self):
        """
        Test generateing final Ansible inventory before convert it to JSON.
        """
        netbox_json_response()
        ansible_inventory = netbox_inventory.generate_inventory()
        assert "fake_host01" in ansible_inventory["_meta"]["hostvars"]
        assert isinstance(ansible_inventory["_meta"]["hostvars"]["fake_host02"], dict)

    @pytest.mark.parametrize("inventory_dict", [
        {
            "fake_rack01": ["fake_host01", "fake_host02"],
            "Fake Server": ["fake_host01"],
            "Server": ["fake_host02"],
            "_meta": {
                "hostvars": {
                    "fake_host02": {"rack_name": "fake_rack01"},
                    "fake_host01": {"ansible_ssh_host": "192.168.0.2", "rack_name": "fake_rack01"}
                }
            }
        }
    ])
    def test_print_inventory_json(self, capsys, inventory_dict):
        """
        Test printing final Ansible inventory in JSON format.
        """
        netbox_inventory.print_inventory_json(inventory_dict)
        function_stdout, function_stderr = capsys.readouterr()
        assert not function_stderr
        assert json.loads(function_stdout) == inventory_dict
