"""
Contains device specific functionality
"""
from threading import Thread

import common
import config
import templates
import dpublish


# List of connected devices
devices_dict = {}
device_action_sm = {}
device_fn_sm = {}
device_actions = []
device_status = None
device_states = None
resp_codes = None

def generate_device_sm():
    """
    generates device state machines 
    """
    global device_actions
    device_actions = config.get_system_device_actions()
    global device_status
    device_status = config.get_system_device_status()
    global device_states
    device_states = config.get_system_device_states()
    global resp_codes
    resp_codes = config.get_system_resp_codes()
    """
    SM States: 
    none:  device being added for first time 
    registered: device has been added
    unregistered: device has been deleted 
    """
    global device_action_sm
    device_action_sm[device_status[0]] = device_actions[0] 
    device_action_sm[device_status[1]] = device_actions[1:]
    device_action_sm[device_status[2]] = device_actions[0]

    global device_fn_sm
    for action in device_actions:
        fn_name = 'device_' + action
        device_fn_sm[action] = eval(fn_name)
        
def log_device_module():
    
    print 'Device Dictionary: ', devices_dict
    print 'Device Actions State Machine: ', device_action_sm
    print 'Device Function State Machine:  ', device_fn_sm
    print 'Device Actions: ', device_actions
    print 'Device Status: ', device_status
    print 'Device States: ', device_states
            
def initialize():
    """
    Entry point function for device initialization 
    """
    generate_device_sm()
    log_device_module()
    global devices_dict
    devices_dict['temperature'] = {}
    

def get_device_topic(type, id):
    return '/'.join(['publish', devices_dict[type][id]['topic']])
    #return '/'.join([common.get_node_id(), 'device', type, id])


def device_add(device_data):
    """
    adds a new device to this endpoint 
    device_data: dictionary of device parameters received 

    Read template json for that device 
    Add other current parameters 
    Dump json data into json file for that device
    Add device to existing list 
    """
    retval = 0
    device_template = {}
    device_template = templates.get_temperature_template()
    device_template.update(device_data)
    
    device_id = device_data['id']
    fname = 'device_' + device_id + common.config_ext
     
    device_type = device_data['type']
    
    #device_type['status'] = 'registered'

    global devices_dict
    devices_dict[device_type][device_id] = device_template
    set_device_status(device_type, device_id, device_status[1])
    
    device_file = common.get_platform_delim().join([common.get_device_config_dir(), device_type, fname])
    device_template['device_file'] = device_file
    common.create_json_file(device_template, device_file)
           
    publish_thread = Thread(target=device_publish_thread, args=(device_type, device_id,))
    publish_thread.start()
    print 'device added successfully', device_type, device_id
    return retval
    

def device_delete(device_data):
    """
    deletes a device to this endpoint 
    device_data: dictionary of device parameters received 
    """
    retval = 0
    global devices_dict
    devices_dict[device_data['type']].pop(device_data['id'], None)
    print 'device removed successfully', device_data['type'], device_data['id']
    """
    vne::tbd:: remove the json file as well
    """
    return retval


def device_get(device_data):
    """
    adds a new device to this endpoint 
    device_data: dictionary of device parameters received 
    """
    retval = 0
    pass #vne:: tbd
    return retval


def device_set(device_data):
    """
    adds a new device to this endpoint 
    device_data: dictionary of device parameters received 
    """
    retval = 0
    global devices_dict
    devices_dict[device_data['type']][device_data['id']].update(device_data)
    common.create_json_file(devices_dict[device_data['type']][device_data['id']], 
                            devices_dict[device_data['type']][device_data['id']]['device_file'])
    return retval
    


def device_enable(device_data):
    """
    Enables this device 
    device_data: dictionary of device parameters received 
    """
    retval = 0
    set_device_state(device_data['type'], device_data['id'], device_states[0])
    print 'device enabled', device_data['type'], device_data['id']
    common.create_json_file(devices_dict[device_data['type']][device_data['id']], 
                            devices_dict[device_data['type']][device_data['id']]['device_file'])

    #vne::gbd:: dump this into config file as well
    return retval
    
def device_disable(device_data):
    """
    disables this endpoint 
    device_data: dictionary of device parameters received 
    """
    retval = 0
    set_device_state(device_data['type'], device_data['id'], device_states[1])
    #devices_dict[device_data['id']]['state'] = device_states[1]
    common.create_json_file(devices_dict[device_data['type']][device_data['id']], 
                            devices_dict[device_data['type']][device_data['id']]['device_file'])

    print 'device disabled', device_data['type'], device_data['id']
    #vne::gbd:: dump this into config file as well
    return retval 


def device_publish_thread(device_type, device_id):
    """
    this is the infinite publish thread for a device
    device_type: device type 
    device_id: device_id for the thread
    """
    print 'thread started ', device_type, device_id
    dpublish.read_device_data(device_type, device_id)

    
def get_device_status(type, id):
    global devices_dict
    return devices_dict[type][id]['status']

def set_device_status(type, id, status):
    """
    Sets device status 
    """
    global devices_dict
    devices_dict[type][id]['status'] = status 

def get_device_state(type, id):
    global devices_dict
    return devices_dict[type][id]['state']

def set_device_state(type, id, state):
    """
    Sets device state 
    """
    global devices_dict
    devices_dict[type][id]['state'] = state

def is_device_enabled(type, id):
    return get_device_state(type, id) == 'enabled'

def get_device_profile(type, id):
    return devices_dict[type][id]
     
def process_device_msg(msg_topic, msg_payload):
    """
    processes control message recevied for device 
    msg_topic: topic  
    msg_payload: raw payload
    """
    retval = 0
    resp_status = resp_codes[0]
    msgtopic = msg_topic.split("/")
    device_type, device_id = msgtopic[-2:]
    #print("Message received: "+ msg_payload)
    parsed_json = common.decode_mqtt_payload(msg_payload)
    #print 'vne:: ', parsed_json
    """
    check if this device exists or not
    decode the json payload to get action 
    perform the action 
    """
    action = parsed_json['action']
    if device_id in devices_dict[device_type]:
        allowed_actions = device_action_sm[get_device_status(device_type, device_id)]
    else:
        allowed_actions = device_action_sm[device_status[0]]
    if action.lower() in allowed_actions:
        parsed_json['id'] = device_id
        parsed_json['type'] = device_type
        print 'calling action: ', action, ': ', type(parsed_json)
        #retval = device_add(parsed_json)
        retval = device_fn_sm[action](parsed_json)
    else:
        print 'Action not allowed in state', action
        resp_status = resp_codes[1]
    
    if retval != 0:
        resp_status = resp_codes[1]
    """
    Publish response
    """
    req_id = 'request_id'
    resp_topic = '/'.join(['response', msg_topic, str(parsed_json[req_id])])
    resp_data = {}
    resp_data[req_id] = parsed_json[req_id]
    resp_data['status'] = resp_status
    print 'publishing response: ', resp_topic, resp_data
    dpublish.publish_response(resp_topic, resp_data)
