
"""
This file contains the common global Variables and 
methods 
"""
import os
import socket
import json

import config
import templates
import device

#File path delimiters based on Windows or Linux
"""
node_id : the unique identifier of the node 
"""
global node_id
global platform_delim

global working_dir
global endpoint_config
### vne:: tbd
platform_config = '/'.join(['..', 'config', 'current', 'common', 'platform.json'])

### COMMON GLOBAL VARIABLES AND CONSTRUCTS ###
config_ext = '.json'

"""
Configuration directories 
"""
config_dir = 'config'
common_dir = 'common'
device_config_dir = None


"""
Configuration Files 
"""
platform_config_file = 'platform' + config_ext
endpoint_config_file = 'endpoint' + config_ext

"""
Node specific variables 
"""
node_type = 'endpoint'
device_type = 'temperature'
### COMMON METHODS ####


def get_node_id():
    global node_id
    return node_id

def get_platform_delim():
    global platform_delim 
    return platform_delim 

def get_device_config_dir():
    global device_config_dir
    return device_config_dir

def initialize():
    """
    This function should be called from main for initializing common modules
    """
    config.early_init()
    global platform_delim
    platform_delim = config.get_platorm_delim()
    print 'changing epplatform delimiter to ', platform_delim
    common_init()

    config.late_init()
    templates.initialize()
    device.initialize()
    
    
def common_init():
    global working_dir
    global endpoint_config
    global device_config_dir
    global platform_config 
    
    working_dir = platform_delim.join([config_dir, 'current'])
    endpoint_config = platform_delim.join([working_dir, node_type, endpoint_config_file])
    device_config_dir = platform_delim.join(['..',working_dir, node_type, 'device'])
    platform_config = platform_delim.join([working_dir, common_dir, platform_config_file])
    generate_node_identifier()
    

def generate_node_identifier():
    """
    generates node unique identifier
    It currently uses associated IPv4 address only 
    """
    ip_tuple = get_ip_address()
    global node_id 
    node_id = '_'.join([ip_tuple[0].replace('.','_'), str(ip_tuple[1])])
    print "Node Identifier", node_id
       
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()

def get_platfrom_configfile():
    return platform_config

def equal(a,b):
    try:
        return a.lower() == b.lower()
    except AttributeError:
        return a == b
                
def equals_ignore_case(a,b):
    return a.upper() == b.upper()


def create_json_file(json_data, file_name):
    """
    dumps json format data in file
    json_data: json data to be dumped into file_name
    file_name: name of file with its full path
    """
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False, separators=(',', ':'))

