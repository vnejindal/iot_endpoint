"""
Functionality of templates reading and filling out data structures
"""
import os
import json

import common

templates_dir = ''

"""
Global json templates datastructures
"""
system_profile = None

template_temp = None  #temerature template

"""
template_board_fn = {
                        'read_udo_template': _read_endpoint_template 
                    }
"""

def initialize():
    """
    Entry point function - must be called first 
    """
    read_system_profile()
    
    global templates_dir
    templates_dir = common.get_platform_delim().join(['..', 'config', 'templates'])
    global template_temp
    template_temp = _read_endpoint_template()
    
    """
    if board is 'udo'
        read_temperature_template
        read_lighting_template 
        read_hvac_template
    if board is 'raspberrypi'
        read_temperature_template
        read_lighting_template
    
    """

def get_temperature_template():
    return template_temp

### Internal Functions ###
def _read_endpoint_template():
    return _read_udo_templates('endpoint')

def _read_udo_templates(board_type):
    return _read_temperature_template(board_type, 'udo')

def print_temperature_template():
    print template_temp
    
def _read_temperature_template(board_type, board):
    return read_template(board_type, board, 'temperature')

def read_template(board_type, board, device_type):
    """
    reads temperature template config file
    board_type: endpoint, gateway, cloud
    board: udo, rasppi3
    device_type: temperature, lighting etc. 
     
    """
    global templates_dir
    fname = '.'.join([device_type, 'json'])
    fpath = common.get_platform_delim().join([templates_dir, board_type, board, 'device', device_type, fname])
    print fpath
    
    json_config = open(fpath).read()
    #tbd:: exception handling
    device_data = json.loads(json_config)
    return device_data

def read_system_profile():
    """
    Reads the top level system template file 
    """
    fname = '.'.join(['system', 'json'])
    fpath = '\\'.join(['..','config','templates', 'common', fname])
    print fpath
    
    json_config = open(fpath).read()
    #tbd:: exception handling
    global system_profile
    system_profile = json.loads(json_config)
    


    
