
"""
This file will read json config information 
"""
import json

import common
import templates 
import epmqtt


"""
Configuration Global Variables 
"""
global system_config 
global platform_config

def get_system_config():
    return system_config

def get_system_device_actions():
    return system_config['device_actions']

def get_system_device_types():
    return system_config['sensor_types']

def get_system_device_status():
    return system_config['device_status']

def get_system_device_states():
    return system_config['device_states']

def get_system_resp_codes():
    return system_config['response_codes']

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

def get_mqtt_config():
    return platform_config['messaging']['mqtt']

def get_endpoint_broker_ip():
    return platform_config['messaging']['mqtt']['broker_ip']

def get_endpoint_broker_port():
    return platform_config['messaging']['mqtt']['broker_port']

def get_endpoint_broker_keepalive():
    return platform_config['messaging']['mqtt']['broker_keepalive']

##### DEVICE CONFIGURATION METHODS ############
    
def log_device_config():
    print read_device_config()
    
def read_device_config(type, id):
    """
    read device specific json config file 
    """
    #vne::tbd:: change to abs path
    #dfile = 'device_' + id + common.config_ext
    dfile = ''.join(['device_', id, common.config_ext])
    device_file = common.get_platform_delim().join([common.device_config_dir, type, dfile])
 
    json_config = open(device_file).read()
    #tbd:: exception handling
    device_data = json.loads(json_config)
    return device_data
    
    
##### PLATFORM CONFIGUURATION METHODS ############
def log_platform_config():
    print read_platform_config()

def get_platform_os():
    return platform_config['os']

def get_messaging_protocol():
    return platform_config['messaging']['protocol']

def get_subscribe_topic():
    return platform_config['messaging']['mqtt']['subtopic']['request']

def get_platform_role():
    return platform_config['role']

def get_platform_boardtype():
    return platform_config['board_type']

def get_platform_gw_id():
    return platform_config['gw_id']

def get_platform_node_id():
    return platform_config['node_id']

def validate_platform_config():
    #tbd::vne:: 
    pass 

def read_platform_config():
    print 'reading epplatform configuration'
    plat_json = open(common.get_platfrom_configfile()).read()
    ##vne:: tbd:: error handling 
    global platform_config 
    platform_config = json.loads(plat_json)
    validate_platform_config()
    return platform_config

def get_platorm_delim():
    global platform_config 
    if common.equals_ignore_case(platform_config['os'], 'windows'):
        return '\\'
    else:
        return '/'
def log_config_module_data():
    print 'Platform Config: '
    print platform_config 
    print 'System Config: '
    print system_config
    
def early_init():
    read_platform_config()

def late_init():
    """
    This function will read and initialize configuration Variables
    """
    global system_config
    system_config = templates.system_profile
    platform_config['gw_id'] = common.generate_gateway_identifier(get_endpoint_broker_ip())
    platform_config['node_id'] = common.get_node_id()
    log_config_module_data()
    #log_platform_config()
    epmqtt.initialize()
    pass
