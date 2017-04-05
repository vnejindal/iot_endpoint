"""
Functionality of templates reading and filling out data structures
"""
import os
import sys
import json

import common

templates_dir = ''

"""
Global json templates datastructures
"""
system_profile = None

template_temp = None  #temperature template
template_simtemp = None #temperature simulator template
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
    global template_simtemp
    template_simtemp = _read_sim_temperature_template()
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

def get_temperature_template(sim = False):
    if sim is True: 
        return template_simtemp
    else:
        return template_temp

### Internal Functions ###
def _read_endpoint_template():
    return _read_udo_templates('endpoint')

def _read_udo_templates(board_type):
    return _read_temperature_template(board_type, 'udo')

def print_temperature_template():
    print template_temp
    
def _read_temperature_template(board_type, board):
    """
    Reads temperature template json file as per board type
    """
    return _read_template(board_type, board, 'temperature')

def _read_sim_temperature_template():
    """
    Reads temperature simulation template json file 
    """
    return _read_template(None, None, 'temperature', True)

def _read_template(board_type, board, device_type, simulation = False):
    """
    reads temperature template config file
    board_type: endpoint, gateway, cloud
    board: udo, rasppi3
    device_type: temperature, lighting etc. 
     
    """
    global templates_dir
    fname = '.'.join([device_type, 'json'])
    
    fpath_vars = []
    if simulation is True:
        fpath_vars = [templates_dir, 'common', 'simulator', 'device', fname]
    else:
        fpath_vars = [templates_dir, board_type, board, 'device', device_type, fname]
    
    fpath = common.get_platform_delim().join(fpath_vars)
    print 'reading template file: ', fpath
    if not os.path.exists(fpath):
        print 'Config file does not exist: ', fpath
        sys.exit('Config file does not exist')
        
    json_config = open(fpath).read()
    #tbd:: exception handling
    device_data = json.loads(json_config)
    return device_data

def read_system_profile():
    """
    Reads the top level system template file 
    """
    fname = '.'.join(['system', 'json'])
    fpath = common.get_platform_delim().join(['..','config','templates', 'common', fname])
    print fpath
    
    if not os.path.exists(fpath):
        print 'Config file does not exist: ', fpath
        sys.exit('Config file does not exist')
    
    json_config = open(fpath).read()
    #tbd:: exception handling
    global system_profile
    system_profile = json.loads(json_config)