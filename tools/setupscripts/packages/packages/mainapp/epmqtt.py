"""
contains functionality for MQTT -- entry level for other stuff
"""
import os
import json
import sys

import paho.mqtt.client as mqtt

import config
import endpoint
import subscribe
import dpublish
import device 
import common

mqtt_rc_codes = {
                    0: 'Connection successful',
                    1: 'Connection refused - incorrect protocol version',
                    2: 'Connection refused - invalid client identifier',
                    3: 'Connection refused - server unavailable',
                    4: 'Connection refused - bad username or password',
                    5: 'Connection refused - not authorised'
                }

mqtt_profile = {}

def get_mqtt_client():
    return mqtt_profile['client']

def log_mqtt_profile():
    print 'MQTT profile: '
    print mqtt_profile
    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    
    if rc == 0:
        print 'Client connected successfully'
        subscribe.subscribe_mqtt_topics(client)
    else:
        print 'Client connection failed: ', str(rc), mqtt_rc_codes[rc]
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #vne::tbd::later    client.subscribe("$SYS/#")

def on_disconnect(client, userdata, rc):
    if rc == 0:
        print 'Client disconnected successfully'
    else:
        print 'Client disconnection issue: ', str(rc)

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
    """
    vne::tbd
    ep_config = endpoint.get_broker_details()
    srv_ip = ep_config[0]
    srv_port = ep_config[1]
    srv_keepalive = ep_config[2]
    """
    
    global mqtt_profile
    mqtt_profile.update(config.get_mqtt_config())
    
    srv_ip = mqtt_profile['broker_ip']
    srv_port = mqtt_profile['broker_port']
    srv_keepalive = mqtt_profile['broker_keepalive']
    
    print 'connecting to broker:', srv_ip,':', srv_port, ' ', srv_keepalive
    
    mqtt_client = mqtt.Client(config.get_platform_node_id(), 
                              mqtt_profile['clean_session'],
                              mqtt_profile['userdata'])
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.on_disconnect = on_disconnect
    
    if mqtt_profile['username'] == 'default':
        print 'Please profile non-default client id to connect to'
        return False
    
    if mqtt_profile['transport'] == 'tls':
        server_cert = common.get_platform_delim().join(['..', 
                                                         common.get_device_working_dir(),
                                                         mqtt_profile['cert_directory'], 
                                                         mqtt_profile['ca_cert']])
        client_cert = common.get_platform_delim().join(['..',
                                                         common.get_device_working_dir(),
                                                         mqtt_profile['cert_directory'],
                                                         mqtt_profile['client_cert']])
        client_key = common.get_platform_delim().join(['..',
                                                       common.get_device_working_dir(),
                                                       mqtt_profile['cert_directory'],
                                                       mqtt_profile['client_key']])
        mqtt_client.tls_set(server_cert, client_cert, client_key) 

    mqtt_client.username_pw_set(mqtt_profile['username'], mqtt_profile['password'])
    mqtt_client.connect(srv_ip, srv_port, srv_keepalive)

    mqtt_profile['client'] = mqtt_client
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
    
def initialize():
    """
    intializes mqtt subscribe Module
    """
    role = config.get_platform_role()
    global mqtt_profile
    mqtt_profile['pub'] = {}
    mqtt_profile['sub'] = {}
    
    print 'vne:: role is ', role
    if common.equals_ignore_case(role, 'endpoint'):
        print 'setting up endpint topics '
        mqtt_profile['pub']['gw_topic'] = '/'.join([config.get_platform_gw_id(), 
                                           config.get_platform_node_id()])
        mqtt_profile['sub']['endpoint_topic'] = '/'.join([config.get_platform_gw_id(), 
                                                 config.get_platform_node_id(), 
                                                 endpoint.get_subscribe_topic(), '#'])
    
    log_mqtt_profile()
    