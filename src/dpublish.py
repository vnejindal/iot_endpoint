
"""
## this file contains functionality of publishing device updates to MQTT broker
"""
import os
import time
import json 
#import sys
#sys.path.append('../pylib/paho.mqtt.python/src/paho/mqtt')

import paho.mqtt.client as mqtt
import config
import common 
import device
#from paho.mqtt import client


def get_endpoint_config():
    return config.read_endpoint_config()

def publish_temperature_data(type, id, client, device_config):
    """
    Reads the device type temperature
    """
    fs_path = device_config['sensor']['fs_path'] + '/'
    file1 = fs_path + device_config['sensor']['files'][0]['data_file'] 
    file2 = fs_path + device_config['sensor']['files'][1]['data_file']
    sleep_time = device_config['sensor']['sleep'] 

    while True:
        infile1 = open(file1, "r")
        infile2 = open(file2, "r")
        line1 = infile1.read()
        line2 = infile2.read()
        infile1.close()
        infile2.close()
    
        temp_data = {}
        temp_data['timestamp'] = time.asctime(time.localtime(time.time()))
        temp_data['in_temp_scale'] = line1.strip()
        temp_data['in_temp_raw'] = line2.strip()
        data_string = json.dumps(temp_data)
        #print 'data_string : ', data_string 
        
        topic = device.get_device_topic(type, id)
        #publish the data
        infot = client.publish(topic, data_string, qos=0)
        time.sleep(sleep_time)

    
def read_device_data(type, id, client):
    """Reads and publishes data 
    """
    device_config = config.read_device_config(type, id)
    print 'reading device: ', device_config['sensor']['type'], device_config['sensor']['id']
    if not common.equals_ignore_case(device_config['sensor']['type'], type) :
        print 'Device type mismatch', device_config['sensor']['type'], type
        return
    
    if common.equals_ignore_case(device_config['sensor']['type'], 'temperature') :
        publish_temperature_data(type, id, client, device_config)


