"""
Test file for reading templates 
"""
import os
import json
import device


def read_template(board_type, board, device_type):
    """
    reads temperature template config file 
    """
    fname = '.'.join([device_type, 'json'])
    fpath = '\\'.join(['..','config','templates', board_type, board, 'device', device_type, fname])
    print fpath
    
    json_config = open(fpath).read()
    #tbd:: exception handling
    device_data = json.loads(json_config)
    print device_data
    create_json_file(device_data)
    
def read_system_template():
    """
    reads system template config file 
    """
    fname = '.'.join(['system', 'json'])
    fpath = '\\'.join(['..','config','templates', 'common', fname])
    print fpath
    
    json_config = open(fpath).read()
    #tbd:: exception handling
    device_data = json.loads(json_config)
    #print device_data
    #create_json_file(device_data)
    print device_data['board_types']['udo']
    
    
def create_json_file(json_data):
    """
    dumps json format data in file
    """
    #add a mew parameter in json data and then dump 
    json_data['new_data'] = 'new_data1234'
    json_data['id'] = 1
    
    with open('data.txt', 'w') as outfile:
        json.dump(json_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False, separators=(',', ':'))
    
#read_template('endpoint', 'udo', 'temperature')
read_system_template()