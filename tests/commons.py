#!/usr/bin/env python
import netbox
import responses

# Paths.
test_cfg = {
    "netbox_config": "tests/files/test_netbox.yml",
    "api_sample": "tests/files/test_api_output.json"
}

# Get Netbox config and API output.
config = netbox.open_yaml_file(test_cfg["netbox_config"])
with open(test_cfg["api_sample"]) as data_file:
    netbox_api_output = data_file.read()


# Fake API response.
def fake_json_response(url, json_payload, status):
    responses.add(responses.GET, url,
                  body=json_payload, status=status,
                  content_type='application/json')
