#! /usr/bin/python

import os
import re
import sys
import json
import yaml
import urllib
import argparse


class Script(object):
    '''
    All stuff related to script itself.
    '''

    def cliArguments(self):
        '''
        Script cli arguments.
        By default Ansible calls "--list" as argument.
        '''

        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-c","--config-file", default="netbox-inventory.yml", help="Path for configuration of the script.")
        parser.add_argument("-t", "--test-sample", default="api_sample.json", action="store_true",
                            help="Test sample of API output instead connect to the real API.")
        parser.add_argument("--list", "--ansible", help="Print output as Ansible dynamic inventory syntax.", action="store_true")
        cliArguments = parser.parse_args()
        return cliArguments

    def openYamlFile(self, yamlFile):
        '''
        Open Yaml file.

        Args:
            yamlFile: Relative or absolut path to yaml file.

        Returns:
            Content of yaml file.
        '''

        # Check if procs list file exists.
        try:
            os.path.isfile(yamlFile)
        except TypeError:
            print "Cannot open YAML file: %s." % (yamlFile)
            sys.exit(1)

        # Load content of Yaml file.
        with open(yamlFile, 'r') as procsYamlFile:
            try:
                yamlFileContent = yaml.load(procsYamlFile)
            except yaml.YAMLError as yamlError:
                print(yamlError)

        return yamlFileContent

#
class Utils(object):
    '''
    General utilities.
    '''

    def getValueByPath(self, sourceDict, keyPath, ignoreKeyError=False):
        '''
        Get key value from nested dict by path.

        Args:
            sourceDict: The dict that we look into.
            keyPath: The path of key in dot notion. e.g. "parentDict.childDict.keyName"
            ignoreKeyError: Ignore KeyError if the key not found in provided path.

        Returns:
            If key found in provided path, it will be returned.
            If not, None will be returned.
        '''

        try:
            keyOutput = reduce(lambda xdict, key: xdict[key], keyPath.split('.'), sourceDict)
        except KeyError, keyName:
            if ignoreKeyError:
                keyOutput = None
            else:
                print "The key %s is not found. Please remember, Python is case sensitive." % (keyName)
                sys.exit(1)
        except TypeError:
            keyOutput = None
        return keyOutput

#
class NetboxAsInventory(object):
    '''
    Netbox as a dynamic inventory for Ansible.

    Retrieves hosts list from netbox API and returens Ansible dynamic inventory (Json).

    Attributes:
        configData: Content of its config which comes from Yaml file.
    '''

    def __init__(self, configData):
        scriptConfig = configData.get("netboxInventory")
        self.api_url = scriptConfig["main"].get('api_url')
        self.groupBy = scriptConfig.setdefault("groupBy", {})
        self.hostsVars = scriptConfig.setdefault("hostsVars", {})
        self.utils = Utils()

    def getHostsList(self):
        '''
        Retrieves hosts list from netbox API.

        Returns:
            A list of all hosts from netbox API.
        '''
        if not self.api_url:
            print "Please check API URL in script configuration file."
            sys.exit(1)

        dataSource = self.api_url
        jsonData = urllib.urlopen(dataSource).read()
        allHostsList = json.loads(jsonData)
        return allHostsList

    def addHostToInvenoryGroups(self, groupsCategories, inventoryDict, hostData):
        '''
        Add a host to its groups.

        It checks if host groups and adds it to these groups.
        The groups are defined in script config file.

        Args:
            groupsCategories: A dict has a categories of groups that will be
                used as invntory groups.
            inventoryDict: A dict for inventory has groups and hosts.
            hostData: A dict has a host data which will be added to inventory.

        Returns:
            The same dict "inventoryDict" after update.
        '''
        serverName = hostData.get("name")
        serverCF = hostData.get("custom_fields")

        if groupsCategories:
            for category in groupsCategories:
                if category == 'default':
                    dataDict = hostData
                    keyName = "name"
                elif category == 'custom':
                    dataDict = serverCF
                    keyName = "value"

                for group in groupsCategories[category]:
                    groupValue = self.utils.getValueByPath(dataDict, group + "." + keyName)

                if groupValue:
                    if not inventoryDict.has_key(groupValue):
                        inventoryDict.update({groupValue: []})

                    if serverName not in inventoryDict[groupValue]:
                        inventoryDict[groupValue].append(serverName)
        else:
            inventoryDict["no_group"].append(serverName)
        return inventoryDict


    def getHostVars(self, hostData, hostVars):
        '''
        Find host vars.

        These vars will be used for host in the inventory.
        We can select whatever from netbox to be used as Ansible inventory vars.
        The vars are defined in script config file.

        Args:
            hostData: A dict has a host data which will be added to inventory.
            hostVars: A dict has selected fields to be used as host vars.

        Returns:
            A dict has all vars are associate with the host.
        '''

        hostVarsDict = dict()
        if hostVars:
            for category in hostVars:
                if category == 'ip':
                    dataDict = hostData
                    keyName = "address"
                elif category == 'general':
                    dataDict = hostData
                    keyName = "name"
                elif category == 'custom':
                    dataDict = hostData.get("custom_fields")
                    keyName = "value"

                for key, value in hostVars[category].iteritems():
                    varName = key
                    varValue = self.utils.getValueByPath(dataDict, value + "." + keyName, ignoreKeyError=True)
                    if varValue:
                        if hostVars.get("ip") and value in hostVars["ip"].values():
                            varValue = varValue.split("/")[0]
                        hostVarsDict.update({varName: varValue})
        return hostVarsDict

    def updateHostMetaVars(self, inventoryDict, hostName, hostVars):
        '''
        Update host meta vars.

        Add host and its vars to "_meta.hostvars" path in the inventory.

        Args:
            inventoryDict: A dict for inventory has groups and hosts.
            hostName: Name of the host that will have vars.
            hostVars: A dict has selected fields to be used as host vars.

        Returns:
            This function doesn't return, it updates the dict in place.
        ''' 

        if hostVars:
            inventoryDict['_meta']['hostvars'].update({hostName: hostVars})

    def generateInventory(self):
        '''
        Generate Ansible dynamic inventory.

        Returns:
            A dict has inventory with hosts and their vars.
        '''

        ansibleInvenory = {"no_group": [], "_meta": {"hostvars": {}}}
        netboxHostsList = self.getHostsList()

        for currentHost in netboxHostsList:
            serverName = currentHost.get("name")
            self.addHostToInvenoryGroups(self.groupBy, ansibleInvenory, currentHost)
            hostVars = self.getHostVars(currentHost, self.hostsVars)
            self.updateHostMetaVars(ansibleInvenory, serverName, hostVars)
        return ansibleInvenory

    def printInventoryJson(self, inventoryDict, printOutput):
        '''
        Print inventory.

        Args:
            inventoryDict: Inventory dict has groups and hosts.
            printOutput: A boolen, if true the inventory will be printed.

        Returns:
            It prints the inventory in Json format if condiction is true.
        '''
        if printOutput:
            print json.dumps(inventoryDict)

# Main.
if __name__ == "__main__":
    # Srcipt vars.
    script = Script()
    args = script.cliArguments()
    configData = script.openYamlFile(args.config_file)

    # Netbox vars.
    netbox = NetboxAsInventory(configData)
    ansibleInventory = netbox.generateInventory()
    netbox.printInventoryJson(ansibleInventory, args.list)
