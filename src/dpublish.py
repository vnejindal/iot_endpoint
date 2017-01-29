
"""
## this file contains functionality of publishing device updates to MQTT broker
"""
import os
import time
#import sys
#sys.path.append('../pylib/paho.mqtt.python/src/paho/mqtt')

import paho.mqtt.client as mqtt
import config
import common 
import device
#from paho.mqtt import client

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
#vne::tbd    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("vne:: "+msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
    pass


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
        fline = ','.join([time.asctime(time.localtime(time.time())), line1.strip(),line2.strip()])
        print 'vne', fline
       
        topic = device.get_device_topic(type, id)
        #publish the data
        infot = client.publish(topic ,fline, qos=0)
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

def device_client_start(type, id):
    
    ep_config = get_endpoint_config()
    srv_ip = ep_config["broker_ip"]
    srv_port = ep_config["broker_port"]
    srv_keepalive = ep_config["broker_keepalive"]
    
    print 'connecting to broker:', srv_ip,':', srv_port, ' ', srv_keepalive
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect(srv_ip, srv_port, srv_keepalive)
    #vne::tbd:: failure handling or how to make it blocking with time limit
    print 'connection to broker successful'  
    
    read_device_data(type, id, client)
    
#    print("tuple")
#    infot = client.publish("/ep/1/thermometer" ,"{\"scale\": 0.0625, \"value\":303}", qos=0)
#    print(rc, mid)
#    infot = client.publish("class", "bar", qos=2)
#    infot.wait_for_publish()
    client.loop_forever()
