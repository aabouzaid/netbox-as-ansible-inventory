#!/usr/bin/env python
import netbox
import responses
import json

# Paths.
test_cfg = {
    "netbox_config": "tests/files/test_netbox.yml",
    "api_sample": "tests/files/test_api_output.json"
}

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

# Get Netbox config and API output.
config = netbox.open_yaml_file(test_cfg["netbox_config"])
with open(test_cfg["api_sample"]) as data_file:
    netbox_api_output = data_file.read()


# Fake API response.
def fake_json_response(url, json_payload, status):
    responses.add(responses.GET, url,
                  body=json_payload, status=status,
                  content_type='application/json')
