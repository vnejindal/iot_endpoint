
"""
## this file contains functionality of publishing device updates to MQTT broker
"""
import os
import time
import json 
import sys 
#import sys
#sys.path.append('../pylib/paho.mqtt.python/src/paho/mqtt')

import paho.mqtt.client as mqtt
import config
import common 
import device
import epmqtt
from imageop import scale
#from paho.mqtt import client


def get_endpoint_config():
    return config.read_endpoint_config()

def publish_temperature_data(dtype, did, client, device_config = None):
    """
    Reads the device type temperature
    """
    if device_config is None: 
        device_config = device.get_device_profile(dtype, did)

    fs_path = device_config['sensor']['fs_path'] + '/'
    file1 = fs_path + device_config['sensor']['files'][0]['data_file'] 
    file2 = fs_path + device_config['sensor']['files'][1]['data_file']
    
    sleep_time = 1
    while True:
        #vne::tbd:: if device.is_device_delete(dtype, did):
        #    return 
        if device.is_device_enabled(dtype, did):
            sleep_time = device_config['frequency'] 
            
            if not os.path.exists(file1) or not os.path.exists(file2):
                print 'Device unavailable: ', dtype, did
                device.device_disable({'type': dtype, 'id':did })
                continue
              
            infile1 = open(file1, "r")
            infile2 = open(file2, "r")
            tscale = infile1.read()
            traw = infile2.read()
            infile1.close()
            infile2.close()
    
            unit = device_config['unit']
            def_unit = device_config['default_unit']
            
            if unit == def_unit: 
                in_temp = float(tscale) * float(traw)
            else:
                """convert it to fahernite and report """
                in_temp = 9.0/5.0 * float(tscale)*float(traw) + 32
                
            temp_data = {}
            #temp_data['timestamp'] = time.asctime(time.localtime(time.time()))
            temp_data['timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(time.time()))
            temp_data['temperature'] = str(in_temp)
            temp_data['unit'] = unit
            print 'publishing data: ', temp_data
            """
            temp_data['in_temp_scale'] = tscale.strip()
            temp_data['in_temp_raw'] = traw.strip()
            """
            data_string = json.dumps(temp_data)
            #print 'data_string : ', data_string 
        
            topic = device.get_device_topic(dtype, did)
            print 'publish topic:', topic
            #publish the data
            infot = client.publish(topic, data_string, qos=0)
        time.sleep(sleep_time)
        #print 'sleeping...', sleep_time

    
def read_device_data(dtype, did, client = None):
    """Reads and publishes data 
    """
    device_config = config.read_device_config(dtype, did)
    print 'reading device: ', device_config['sensor']['type'], device_config['id']
    if not common.equals_ignore_case(device_config['sensor']['type'], dtype) :
        print 'Device type mismatch', device_config['sensor']['type'], dtype
        return
    if client is None: 
        client = epmqtt.get_mqtt_client()
        
    if common.equals_ignore_case(device_config['sensor']['type'], 'temperature') :
        publish_temperature_data(dtype, did, client)
        #publish_temperature_data(type, id, client, device_config)

def publish_response(topic, payload, client = None):
    """
    publishes payload on the topic to connected client 
    """
    if client is None:
        client = epmqtt.get_mqtt_client()
    
    data_string = json.dumps(payload)
    infot = client.publish(topic, data_string, qos=0)
    
    
