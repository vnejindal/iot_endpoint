"""
contains functionality for MQTT -- entry level for other stuff
"""
import os
import json

import paho.mqtt.client as mqtt

import config
import endpoint
import subscribe
import dpublish
import device 

mqtt_client = None

def get_mqtt_client():
    return mqtt_client
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #vne::tbd::later    client.subscribe("$SYS/#")
    subscribe.subscribe_control_topic(client)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("vne:: "+msg.topic+" "+str(msg.payload))
    process_message(client, userdata, msg)
        
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
    pass

def device_client_start(type, id):
    """
    Connects with MQTT broker
    """
    ep_config = endpoint.get_broker_details()
    srv_ip = ep_config[0]
    srv_port = ep_config[1]
    srv_keepalive = ep_config[2]
    
    print 'connecting to broker:', srv_ip,':', srv_port, ' ', srv_keepalive
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(srv_ip, srv_port, srv_keepalive)
    #vne::tbd:: failure handling or how to make it blocking with time limit
    print 'connection to broker successful'  
    
    mqtt_client.loop_forever()
    #client.loop_start()
    #dpublish.read_device_data('temperature', '1', client)

def process_message(client, userdata, msg):
    """
    Processes message received from broker 
    """
    print("vne:: "+msg.topic+" "+str(msg.payload))
    device.process_device_msg(msg.topic, msg.payload)
    