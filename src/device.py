"""
Contains device specific functionality
"""

import common
import config
import templates

# List of connected devices
connected_devices = {}

def initialize():
    """
    Entry point function for device initialization 
    """
    connected_devices['temperature'] = {}
    

def get_device_topic(type, id):
    return '/'.join([common.get_node_id(), 'device', type, id])


def device_add(device_data):
    """
    adds a new device to this endpoint 
    device_data: dictionary of device parameters received 
    """
    device_template = {}
    """
    Read template json for that device 
    Add other current parameters 
    Dump json data into json file for that device
    Add device to existing list 
    """
    device_template = templates.get_temperature_template()
    device_template.update(device_data)
    
    device_id = device_data['id']
    fname = 'device_' + device_id + common.config_ext
     
    device_type = device_data['type']
    device_file = common.get_platform_delim().join([common.get_device_config_dir(), device_type, fname])
    common.create_json_file(device_template, device_file)
    
    ##vne::tbd check if id already exists
    connected_devices['temperature'][device_id] = device_template
   