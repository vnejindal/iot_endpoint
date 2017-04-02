"""
This file will read from a mqtt topic and dump into a file. 
Config File: subscribe_config.json 

"""
import os
import json
from time import sleep

import paho.mqtt.client as mqtt

###############################################################################

file_json = {}

def open_out_file(file_name):
    out_file = open(file_name, 'a')
    return out_file

def read_json_file(file_name):
    json_config = open(file_name).read()
    file_json = json.loads(json_config)
    #print file_json
    return file_json

def decode_mqtt_payload(msg_payload):
    """
    returns the json payload format of raw data 
    """
    json_data = msg_payload.decode('utf-8')
    return json.loads(json_data)


def create_mqtt_client(srv_ip, srv_port, srv_keepalive = 60):
    """
    Connects with MQTT broker
    """
    print 'connecting to broker:', srv_ip,':', srv_port, ' ', srv_keepalive
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(srv_ip, srv_port, srv_keepalive)
    print 'connection to broker successful'  
    global file_json 
    file_json['client'] = mqtt_client
    mqtt_client.loop_forever()
    
def subscribe_topic(topic):
    print 'subscribing to: ', topic
    file_json['client'].subscribe(topic)
    
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
    pass

def on_message(client, userdata, msg):
    print("vne:: "+msg.topic+" "+str(msg.payload))
    payload_json = decode_mqtt_payload(msg.payload)
    
    dump_str = ','.join([payload_json['timestamp'], payload_json['temperature'], payload_json['unit']])    
    file_json['ofile_fd'].write( dump_str + "\n")
    file_json['ofile_fd'].flush()
    
      
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    subscribe_topic(file_json['subsribe_topic'])
    
def start_app(file_name):
    global file_json
    file_json = read_json_file(file_name)
    ofile_fd = open_out_file(file_json['output_file'])
    file_json['ofile_fd'] = ofile_fd
    
    create_mqtt_client(file_json['broker_ip'], file_json['broker_port'])

    
start_app('subscribe_config.json')