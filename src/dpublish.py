
"""
This file contains functionality of publishing device updates to MQTT broker
"""
import os
import time
import json 
import sys
import urllib2
 
#sys.path.append('../pylib/paho.mqtt.python/src/paho/mqtt')

import paho.mqtt.client as mqtt
import config
import common 
import device
import epmqtt
import dtemperature


def get_endpoint_config():
    return config.read_endpoint_config()

def publish_temperature_data(dtype, did, client, device_config = None):
    """
    Reads the device type temperature
    """
    if device_config is None: 
        device_config = device.get_device_profile(dtype, did)

    sleep_time = 1
    while True:
        #vne::tbd
        #if device.is_device_delete(dtype, did):
        #    return 
        if device.is_device_enabled(dtype, did):
            sleep_time = device_config['frequency'] 
            
            
            """
            unit = device_config['unit']
            def_unit = device_config['default_unit']
            
            if unit == def_unit: 
                in_temp = float(tscale) * float(traw)
            else:
                in_temp = 9.0/5.0 * float(tscale)*float(traw) + 32
            """
            (temp_reading, user_data) = _get_temperature_reading(device_config)
            
            temp_data = {}
            temp_data['id'] = device_config['gid']
            #temp_data['timestamp'] = time.asctime(time.localtime(time.time()))
            temp_data['timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(time.time()))
            temp_data['temperature'] = str(temp_reading)
            temp_data['unit'] = device_config['unit']
            temp_data.update(user_data)
            print 'publishing data: ', temp_data
            """
            temp_data['in_temp_scale'] = tscale.strip()
            temp_data['in_temp_raw'] = traw.strip()
            """
            data_string = json.dumps(temp_data)
            topic = device_config['data_topic']
            print 'publish topic:', topic
            client.publish(topic, data_string, qos=0)
        time.sleep(sleep_time)
        #print 'sleeping...', sleep_time

def _get_temperature_reading(device_config):
    """
    Top level abstraction for reading temperature data. It takes care of conversion as well.
    
    """
    #vne::tbd:: get mode value from a common place to adapt to future changes
    if device_config['sim_mode'] is True:
        (temp_reading, user_data) = _get_sim_temperature(device_config)
    else:
        (temp_reading, user_data) = _get_udo_temperature_sensor(device_config)

    #Temperature Unit conversion         
    final_reading = dtemperature.convert_unit(temp_reading, device_config['default_unit'], device_config['unit'])
    
    return (final_reading, user_data)
    
def _get_udo_temperature_sensor(device_config):
    """
    Gets temperature sensor reading from UDOO Neo board sensor 
    tbd::vne:: introduce generality here.
    
    returns a tuple: temperature and user_data dict
    """
    dtype = device_config['type']
    did = device_config['id']
    fs_path = device_config['sensor']['fs_path'] + '/'
    file1 = fs_path + device_config['sensor']['files'][0]['data_file'] 
    file2 = fs_path + device_config['sensor']['files'][1]['data_file']
    
    ##vne::tbd:: how to handle a failure like this here
    if not os.path.exists(file1) or not os.path.exists(file2):
        print 'Device unavailable: ', dtype, did
        device.device_disable({'type': dtype, 'id':did })
        return 0
              
    infile1 = open(file1, "r")
    infile2 = open(file2, "r")
    tscale = infile1.read()
    traw = infile2.read()
    infile1.close()
    infile2.close()
    
    user_data = {}
    
    return (float(tscale) * float(traw), user_data) 
    
def _get_sim_temperature(device_config):
    """
    Reads temperature reading from web
    returns a tuple: temperature and user_data dict
    """
    web_config = device_config['sensor']['web']
    url = web_config['url'] + \
                      '?zip=' + \
                      web_config['location_zip'] + \
                      ',' + \
                      web_config['country_code'] + \
                      '&appid=' + \
                      web_config['apikey'] \
                      
    url_data = urllib2.urlopen(url)
    json_string = url_data.read()
    parsed_json = json.loads(json_string)
    url_data.close()
    
    user_data = {}
    user_data['zip'] = web_config['location_zip']
    user_data['country_code'] = web_config['country_code']
    user_data['time'] = parsed_json['dt']

    return (parsed_json['main']['temp'], user_data)
    
  
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
    client.publish(topic, data_string, qos=0)