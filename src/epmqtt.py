"""
contains functionality for MQTT -- entry level for other stuff
"""
import os

import paho.mqtt.client as mqtt

import config
import endpoint
import subscribe
import dpublish

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
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect(srv_ip, srv_port, srv_keepalive)
    #vne::tbd:: failure handling or how to make it blocking with time limit
    print 'connection to broker successful'  
    
    #client.loop_forever()
    client.loop_start()
    dpublish.read_device_data('temperature', '1', client)
