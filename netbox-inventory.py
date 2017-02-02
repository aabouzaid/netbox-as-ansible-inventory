#! /usr/bin/python

import os
import sys
import json
import yaml
import urllib
import argparse


class Script(object):
    def __init__(self):
        # General utils.
        self.utils = Utils()

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
        parser.add_argument("--list", help="Print all hosts with vars as Ansible dynamic inventory syntax.", action="store_true")
        parser.add_argument("--host", help="Print specific host vars as Ansible dynamic inventory syntax.", action="store")
        cliArguments = parser.parse_args()
        return cliArguments

    def openYamlFile(self, yamlFile):
        '''
        Open Yaml file.

        Args:
            yamlFile: Relative or absolute path to yaml file.

        Returns:
            Content of yaml file.
        '''

        # Check if Yaml file exists.
        if not os.path.isfile(yamlFile):
            print "Cannot open YAML file: %s" % (self.utils.getFullPath(yamlFile))
            sys.exit(1)

        # Load content of Yaml file.
        with open(yamlFile, 'r') as configYamlFile:
            try:
                yamlFileContent = yaml.load(configYamlFile)
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

    def getFullPath(self, fileName):
        fullPath = os.path.dirname(os.path.realpath(__file__)) + "/" + fileName
        return fullPath

#
class NetboxAsInventory(object):
    '''
    Netbox as a dynamic inventory for Ansible.

    Retrieves hosts list from netbox API and returns Ansible dynamic inventory (Json).

    Attributes:
        configData: Content of its config which comes from Yaml file.
    '''

    def __init__(self, scriptArgs, configData):
        # General utils.
        self.utils = Utils()

        # Script arguments.
        self.config_file = scriptArgs.config_file
        self.list = scriptArgs.list
        self.host = scriptArgs.host

        # Script configuration.
        scriptConfig = configData.get("netboxInventory")
        self.api_url = scriptConfig["main"].get('api_url')
        self.groupBy = scriptConfig.setdefault("groupBy", {})
        self.hostsVars = scriptConfig.setdefault("hostsVars", {})

        # Get value based on key.
        self.keyMap = {
            "default": "name",
            "general": "name",
            "custom": "value",
            "ip": "address"
        }

    def getHostsList(self):
        '''
        Retrieves hosts list from netbox API.

        Returns:
            A list of all hosts from netbox API.
        '''

        if not self.api_url:
            print "Please check API URL in script configuration file."
            print "Current configuration file: %s" % (self.utils.getFullPath(self.config_file))
            sys.exit(1)

        if self.host:
            dataSource = "{}?name={}".format(self.api_url, self.host)
        else:
            dataSource = self.api_url

        jsonData = urllib.urlopen(dataSource).read()
        hostsList = json.loads(jsonData)
        return hostsList

    def addHostToInvenoryGroups(self, groupsCategories, inventoryDict, hostData):
        '''
        Add a host to its groups.

        It checks if host groups and adds it to these groups.
        The groups are defined in script config file.

        Args:
            groupsCategories: A dict has a categories of groups that will be
                used as inventory groups.
            inventoryDict: A dict for inventory has groups and hosts.
            hostData: A dict has a host data which will be added to inventory.

        Returns:
            The same dict "inventoryDict" after update.
        '''

        serverName = hostData.get("name")
        categoriesSource = {
            "default": hostData,
            "custom": hostData.get("custom_fields")
        }

        if groupsCategories:
            for category in groupsCategories:
                keyName = self.keyMap[category]
                dataDict = categoriesSource[category]

                for group in groupsCategories[category]:
                    groupValue = self.utils.getValueByPath(dataDict, group + "." + keyName)

                if groupValue:
                    if not inventoryDict.has_key(groupValue):
                        inventoryDict.update({groupValue: []})

                    if serverName not in inventoryDict[groupValue]:
                        inventoryDict[groupValue].append(serverName)
        else:
            if not inventoryDict.has_key("no_group"):
                inventoryDict.setdefault("no_group", [serverName])
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

        if hostVars:
            hostVarsDict = dict()
            categoriesSource = {
                "ip": hostData,
                "general": hostData,
                "custom": hostData.get("custom_fields")
            }

            for category in hostVars:
                keyName = self.keyMap[category]
                dataDict = categoriesSource[category]

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

        if hostVars and not self.host:
            inventoryDict['_meta']['hostvars'].update({hostName: hostVars})
        elif hostVars and self.host:
            inventoryDict.update({hostName: hostVars})

    def generateInventory(self):
        '''
        Generate Ansible dynamic inventory.

        Returns:
            A dict has inventory with hosts and their vars.
        '''

        netboxHostsList = self.getHostsList()
        if netboxHostsList:
            ansibleInvenory = {"_meta": {"hostvars": {}}}
            for currentHost in netboxHostsList:
                serverName = currentHost.get("name")
                self.addHostToInvenoryGroups(self.groupBy, ansibleInvenory, currentHost)
                hostVars = self.getHostVars(currentHost, self.hostsVars)
                self.updateHostMetaVars(ansibleInvenory, serverName, hostVars)
        else:
            ansibleInvenory = dict()
        return ansibleInvenory

    def printInventoryJson(self, inventoryDict):
        '''
        Print inventory.

        Args:
            inventoryDict: Inventory dict has groups and hosts.
            printOutput: A boolean, if true the inventory will be printed.

        Returns:
            It prints the inventory in Json format if condition is true.
        '''

        if self.host:
            result = inventoryDict.setdefault(self.host, {})
        elif self.list:
            result = inventoryDict
        else:
            result = {}

        print json.dumps(result)

# Main.
if __name__ == "__main__":
    # Srcipt vars.
    script = Script()
    args = script.cliArguments()
    configData = script.openYamlFile(args.config_file)

    # Netbox vars.
    netbox = NetboxAsInventory(args, configData)
    ansibleInventory = netbox.generateInventory()
    netbox.printInventoryJson(ansibleInventory)
