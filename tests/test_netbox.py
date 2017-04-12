#!/usr/bin/env python
import netbox
import pytest
import responses
import json

#
# Init.

# Paths.
test_cfg = {
    "netbox_config": netbox.get_full_path("tests/files/test_netbox.yml"),
    "api_sample": netbox.get_full_path("tests/files/test_api_output.json")
}

# Get Netbox config and API output.
config = netbox.open_yaml_file(test_cfg["netbox_config"])
with open(test_cfg["api_sample"]) as data_file:    
    netbox_api_output = data_file.read()


# Fake args.
class Args(object):
    config_file = test_cfg["netbox_config"]
    host = None
    list = True

# Init Netbox class.
netbox = netbox.NetboxAsInventory(Args, config)

# Fake API response.
responses.add(responses.GET, netbox.api_url,
              body=netbox_api_output, status=200,
              content_type='application/json')

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
      "display_name": "Fack Rack01"
    },
    "position": null,
    "face": null,
    "parent_device": null,
    "status": true,
    "primary_ip": null,
    "primary_ip4": null,
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
        hosts_list = netbox.get_hosts_list(netbox.api_url)
        assert isinstance(hosts_list, list)


    @pytest.mark.parametrize("server_name, group_value, inventory_dict", [
        ("fake_server", "fake_group", {}),
    ])
    def test_add_host_to_group(self, server_name, group_value, inventory_dict):
        """
        Test add host to its group inside inventory dict.
        """

        netbox.add_host_to_group(server_name, group_value, inventory_dict)
        assert server_name in inventory_dict[group_value]


    @pytest.mark.parametrize("groups_categories, inventory_dict, host_data", [
        (
            {"default": ["device_role", "rack", "platform"]},
            {"_meta": {"hostvars": {}}},
            fake_host
        )
    ])
    def test_add_host_to_group(self, groups_categories, inventory_dict, host_data):
        """
        Test add host to its group in inventory dict (grouping).
        """

        netbox.add_host_to_inventory(groups_categories, inventory_dict, host_data)
        assert "hostvars" in inventory_dict["_meta"]
        assert "fake_rack01" in inventory_dict
        assert "fake_host" in inventory_dict["fake_rack01"]
