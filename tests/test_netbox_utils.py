#!/usr/bin/env python
import netbox
import pytest


#
# Tests.
class TestNetboxUtils(object):

    @pytest.mark.parametrize("source_dict, key_path", [
        ({"a_key": {"b_key": {"c_key": "c_value"}}},
         ["a_key", "b_key", "c_key"])
    ])
    def test_reduce_path(self, source_dict, key_path):
        """
        """
        reduced_path = netbox.reduce_path(source_dict, key_path)
        assert reduced_path == "c_value"

    @pytest.mark.parametrize("source_dict, key_path", [
        ({"a_key": {"b_key": {"c_key": "c_value"}}},
         ["a_key", "b_key", "any"])
    ])
    def test_get_value_by_path(self, source_dict, key_path):
        """
        """
        reduced_path = netbox.get_value_by_path(source_dict, key_path, ignore_key_error=True)
        assert reduced_path is None

    @pytest.mark.parametrize("yaml_file", [
        "tests/files/test_netbox.yml"
    ])
    def test_open_yaml_file(self, yaml_file):
        """
        """
        config_output = netbox.open_yaml_file(yaml_file)
        assert config_output["netbox"]
        assert config_output["netbox"]["main"]["api_url"]
