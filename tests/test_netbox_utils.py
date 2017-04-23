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
         ["a_key", "b_key", "c_key"])
    ])
    def test_get_value_by_path_key_exists(self, source_dict, key_path):
        """
        """
        reduced_path = netbox.get_value_by_path(source_dict, key_path)
        assert reduced_path == "c_value"

    @pytest.mark.parametrize("source_dict, key_path", [
        ({"a_key": {"b_key": {"c_key": "c_value"}}},
         ["a_key", "b_key", "any"])
    ])
    def test_get_value_by_path_key_not_exists(self, source_dict, key_path):
        """
        """
        with pytest.raises(SystemExit) as key_not_exists:
            reduced_path = netbox.get_value_by_path(source_dict, key_path)
        assert key_not_exists

    @pytest.mark.parametrize("source_dict, key_path, ignore_key_error", [
        ({"a_key": {"b_key": {"c_key": "c_value"}}},
         ["a_key", "b_key", "any"],
         True)
    ])
    def test_get_value_by_path_key_not_exists_ignore_error(self, source_dict, key_path, ignore_key_error):
        """
        """
        reduced_path = netbox.get_value_by_path(source_dict, key_path, ignore_key_error)
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
