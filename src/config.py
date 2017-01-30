
"""
This file will read json config information 
"""
import os
import json

import common 


"""
Configuration Global Variables 
"""
global platform_config
global endpoint_config 


def validate_json_config(file_name):
    """
    The method will validate the json config file for conflicts 
    like: same id values, same log file names, invalid values etc.
    """
    print 'vne::tbd:: validate not defined yet...'
  
def log_json_config(json_data):
    """
    Prints Json data
    """
    print json_data['sensor']['files'][1]['data_file']

##### DEVICE CONFIGUURATION METHODS ############  

def log_endpoint_config():
    print read_endpoint_config()

def get_endpoint_comment():
    return endpoint_config['_comment']

def get_endpoint_broker_ip():
    return endpoint_config['broker_ip']

def get_endpoint_broker_port():
    return endpoint_config['broker_port']

def get_endpoint_broker_keepalive():
    return endpoint_config['broker_keepalive']

def read_endpoint_config():
    """
    reads endpoint config file
    """
    ep_config = open('..' + common.get_platform_delim() + common.endpoint_config).read()
    #tbd:: exception handling
    global endpoint_config
    endpoint_config = json.loads(ep_config)
    return endpoint_config

##### DEVICE CONFIGUURATION METHODS ############
    
def log_device_config():
    print read_device_config()
    
def read_device_config(type, id):
    """
    read device specific json config file 
    """
    #vne::tbd:: change to abs path
    #dfile = 'device_' + id + common.config_ext
    dfile = ''.join(['device_', id, common.config_ext])
    device_file = common.get_platform_delim().join(['..', common.device_dir, type, dfile])
 
    json_config = open(device_file).read()
    #tbd:: exception handling
    device_data = json.loads(json_config)
    return device_data
    
    
##### PLATFORM CONFIGUURATION METHODS ############
def log_platform_config():
    print read_platform_config()

def get_messaging_protocol():
    return platform_config['messaging']['protocol']

def get_subscribe_topic():
    return platform_config['messaging']['subtopic']

def read_platform_config():
    print 'reading epplatform configuration'
    plat_json = open(common.get_platfrom_configfile()).read()
    ##vne:: tbd:: error handling 
    global platform_config 
    platform_config = json.loads(plat_json)
    return platform_config

def get_platorm_delim():
    global platform_config 
    if common.equals_ignore_case(platform_config['os'], 'windows'):
        return '\\'
    else:
        return '/'

def early_init():
    read_platform_config()

def late_init():
    """
    This function will read and initialize configuration Variables
    """
    read_endpoint_config()
