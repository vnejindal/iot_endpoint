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

def initialize():
    """
    Entry point function for device initialization 
    """
    devices_dict['temperature'] = {}
    

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
    
    publish_thread = Thread(target=device_publish_thread, args=(device_type, device_id,))
    publish_thread.start()
    devices_dict['temperature'][device_id] = device_template

def device_publish_thread(device_type, device_id):
    """
    this is the infinite publish thread for a device
    device_type: device type 
    device_id: device_id for the thread
    """
    print 'thread started ', device_type, device_id
    dpublish.read_device_data(device_type, device_id)
    
  
def process_device_msg(msg_topic, msg_payload):
    """
    processes control message recevied for device 
    msg_topic: topic  
    msg_payload: raw payload
    """
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
    if device_id in devices_dict[device_type]:
        print 'device ', device_id, 'exists'
        """
        Set/Get/Remove
        """
    else:
        print 'message to add new device id', device_id
        parsed_json['id'] = device_id
        parsed_json['type'] = device_type
        device_add(parsed_json)
        print 'new device id', device_id, 'added successfully'
        
    """
    Publish response
    """
    req_id = 'request_id'
    resp_topic = '/'.join([msg_topic, str(parsed_json[req_id])])
    resp_data = {}
    resp_data[req_id] = parsed_json[req_id]
    resp_data['status'] = 'ok'
    print 'publishing response: ', resp_topic, resp_data
    dpublish.publish_response(resp_topic, resp_data)
