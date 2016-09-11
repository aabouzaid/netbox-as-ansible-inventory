#! /usr/bin/python

import os
import re
import json
import yaml
import urllib
import argparse


# Open Yaml file.
def openYamlFile(yamlFile):
    # Check if procs list file exists.
    try:
        os.path.isfile(yamlFile)
    except TypeError:
        print "Cannot open YAML file: %s." % (yamlFile)
        sys.exit(1)
    
    # Load content of Yaml file.
    with open(yamlFile, 'r') as yamlFileData:
        try:
            yamlFileContent = yaml.load(yamlFileData)
        except yaml.YAMLError as yamlError:
            print(yamlError)
  
    return yamlFileContent

#
def getFromDict(dataDict, mapList):
    try:
        keyOutput = reduce(lambda xdict, key: xdict[key], mapList, dataDict)
        ipPattern = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}")
        if ipPattern.match(keyOutput):
            keyOutput = keyOutput.split("/")[0]
    except TypeError:
        keyOutput = None

    return keyOutput

#
def initInventory():
    mainDict = {}
    mainDict.update({"_meta": {"hostvars": {}}})

    return mainDict

#
def addToInventory(inventoryDict, groupList, jsonData):
    for host in jsonData:
        serverName = getFromDict(host,['name'])
        serverIP = getFromDict(host, ['primary_ip','address'])

        #
        for group in groupList:
            if isinstance(host.get(group), dict) and host.has_key(group):
                groupName = host[group].get('name')
            elif isinstance(host.get(group), str) and host.has_key(group):
                groupName = host.get(group)

            #
            if not inventoryDict.has_key(groupName):
                inventoryDict.update({groupName: []})
            if serverName not in inventoryDict[groupName]:
                inventoryDict[groupName].append(serverName)

        # 
        if serverIP:
            inventoryDict['_meta']['hostvars'].update({serverName: {"ansible_ssh_host": serverIP}})

    return inventoryDict

#
def getApiJson(source, configFile):
    defaults = configFile['defaults']

    if source == 'file':
        dataSource = defaults.get('sample')
        with open(dataSource, 'r') as jsonOutput:
            jsonData = jsonOutput.read()
    elif source == 'url':
        dataSource = defaults.get('api_url')
        jsonOutput = urllib.urlopen(dataSource)
        jsonData = jsonOutput.read()

    apiJsonOutput = json.loads(jsonData)

    return apiJsonOutput

#
if __name__ == "__main__":

    # Script options.
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c","--config-file", default="netbox-inventory.yml", help="Path for configuration of the script.")
    parser.add_argument("--list", "--ansible", help="Print output as Ansible dynamic inventory syntax.", action="store_true")
    parser.add_argument("-t", "--test-sample", help="Test sample of API output instead connect to the real API.", action="store_true")
    args = parser.parse_args()

    #
    configFile = openYamlFile(args.config_file)

    #
    if args.test_sample:
        dataSource = 'file'
    else:
        dataSource = 'url'
    apiJsonOutput = getApiJson(dataSource, configFile)

    #
    groupList = configFile['groupBy']

    #
    ansibleInventory = initInventory()

    #
    if args.list:
        print addToInventory(ansibleInventory, groupList, apiJsonOutput)
