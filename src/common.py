
"""
This file contains the common global Variables and 
methods 
"""
import os
import socket

import config

#File path delimiters based on Windows or Linux
"""
node_id : the unique identifier of the node 
"""
global node_id
global platform_delim

global working_dir
global endpoint_config
global device_dir
### vne:: tbd
platform_config = '\\'.join(['..', 'config', 'current', 'common', 'platform.json'])

### COMMON GLOBAL VARIABLES AND CONSTRUCTS ###
config_ext = '.json'

"""
Configuration directories 
"""
config_dir = 'config'
common_dir = 'common'

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


def initialize():
    """
    This function should be called from main for initializing common modules
    """
    config.initialize()
    global platform_delim
    platform_delim = config.get_platorm_delim()
    print 'changing platform delimiter to ', platform_delim
    common_init()

def common_init():
    global working_dir
    global endpoint_config
    global device_dir
    global platform_config 
    
    working_dir = platform_delim.join([config_dir, 'current'])
    endpoint_config = platform_delim.join([working_dir, node_type, endpoint_config_file])
    device_dir = working_dir + \
                platform_delim + \
                node_type + \
                '/device'
    platform_config = platform_delim.join([working_dir, common_dir, platform_config_file])
    
    generate_node_identifier()
    
    

def get_node_id():
    global node_id
    return node_id
  
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