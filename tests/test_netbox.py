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


# Fake args.
class Args(object):
    config_file = test_cfg["netbox_config"]
    host = None
    list = True

# Init Netbox class.
netbox = netbox.NetboxAsInventory(Args, config)


# Fake Netbox API response.
def nebox_json_response():
    commons.fake_json_response(netbox.api_url, netbox_api_output, 200)

# Fake single host.
fake_host = json.loads('''
  {
    "id": 1,
    "name": "fake_host",
    "display_name": "Fake Host",
    "device_type": {
      "id": 1,
      "manufacturer": {
        "id": 8,
        "name": "Fake Manufacturer",
        "slug": "fake_manufacturer"
      },
      "model": "all",
      "slug": "all"
    },
    "device_role": {
      "id": 8,
      "name": "Fake Server",
      "slug": "fake_server"
    },
    "tenant": null,
    "platform": null,
    "serial": "",
    "asset_tag": "fake_tag",
    "rack": {
      "id": 1,
      "name": "fake_rack01",
      "facility_id": null,
      "display_name": "Fake Rack01"
    },
    "position": null,
    "face": null,
    "parent_device": null,
    "status": true,
    "primary_ip": {
      "id": 1,
      "family": 4,
      "address": "192.168.0.2/32"
    },
    "primary_ip4": {
      "id": 1,
      "family": 4,
      "address": "192.168.0.2/32"
    },
    "primary_ip6": null,
    "comments": "",
    "custom_fields": {
      "label": "Web",
      "env": {
        "id": 1,
        "value": "Prod"
      }
    }
  }
''')


#
# Tests.
class TestNetboxAsInventory(object):

    @responses.activate
    def test_get_hosts_list(self):
        """
        Test get hosts list from API and make sure it returns a list.
        """
        nebox_json_response()
        hosts_list = netbox.get_hosts_list(netbox.api_url)
        assert isinstance(hosts_list, list)

    @pytest.mark.parametrize("server_name, group_value, inventory_dict", [
        ("fake_server", "fake_group", {})
    ])
    def test_add_host_to_group(self, server_name, group_value, inventory_dict):
        """
        Test add host to its group inside inventory dict.
        """
        netbox.add_host_to_group(server_name, group_value, inventory_dict)
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
        netbox.add_host_to_inventory(groups_categories, inventory_dict, host_data)
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
            netbox.add_host_to_inventory(groups_categories, inventory_dict, host_data)
        assert wrong_category_error

    @pytest.mark.parametrize("groups_categories, inventory_dict, host_data", [
        ({},
         {"_meta": {"hostvars": {}}},
         fake_host),
    ])
    def test_add_host_to_inventory_with_empty_group(self, groups_categories, inventory_dict, host_data):
        """
        """
        netbox.add_host_to_inventory(groups_categories, inventory_dict, host_data)
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
            netbox.add_host_to_inventory(groups_categories, inventory_dict, host_data)
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
        host_vars = netbox.get_host_vars(host_data, host_vars)
        assert host_vars["ansible_ssh_host"] == "192.168.0.2"
        assert host_vars["rack_name"] == "fake_rack01"

    @pytest.mark.parametrize("inventory_dict, host_name, host_vars", [
        (
            {"_meta": {"hostvars": {}}},
            "fake_host",
            {"rack_name": "fake_rack01"}
        )
    ])
    def test_update_host_meta_vars(self, inventory_dict, host_name, host_vars):
        """
        Test update host vars in inventory dict.
        """
        netbox.update_host_meta_vars(inventory_dict, host_name, host_vars)
        assert inventory_dict["_meta"]["hostvars"]["fake_host"]["rack_name"] == "fake_rack01"

    @responses.activate
    def test_generate_inventory(self):
        """
        Test generateing final Ansible inventory before convert it to JSON.
        """
        nebox_json_response()
        ansible_inventory = netbox.generate_inventory()
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
                },
            },
        }
    ])
    def test_print_inventory_json(self, capsys, inventory_dict):
        """
        Test printing final Ansible inventory in JSON format.
        """
        netbox.print_inventory_json(inventory_dict)
        function_stdout, function_stderr = capsys.readouterr()
        assert not function_stderr
        assert json.loads(function_stdout) == inventory_dict
