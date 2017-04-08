#!/usr/bin/env python
import netbox
import responses

#
# Init.

# Pathes.
test_cfg = {
  "netbox_config": netbox.get_full_path("tests/files/test_netbox.yml"),
  "api_sample": netbox.get_full_path("tests/files/test_api_output.json")
}

# Get Netbox config and API output.
config = netbox.open_yaml_file(test_cfg["netbox_config"])
with open(test_cfg["api_sample"]) as data_file:    
    netbox_api_output = data_file.read()

# Fake args.
class args(object):
    config_file=test_cfg["netbox_config"]
    host=None
    list=True

# Init Netbox class.
netbox = netbox.NetboxAsInventory(args, config)

# Fake API response.
responses.add(responses.GET, netbox.api_url,
    body=netbox_api_output, status=200,
    content_type='application/json')


#
# Tests.
class TestNetboxAsInventory(object):

    @responses.activate
    def test_get_hosts_list(self):
        hosts_list = netbox.get_hosts_list(netbox.api_url)
        assert isinstance(hosts_list, list)