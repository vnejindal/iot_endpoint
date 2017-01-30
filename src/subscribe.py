"""
functionality of subscribing to topics on MQTT broker 
"""

import common
import endpoint
import paho.mqtt.client as mqtt

def subscribe_control_topic(client):
    topic = '/'.join([common.get_node_id(), endpoint.get_subscribe_topic()])
    
    client.subscribe(topic)
    print 'Subscribed to topic: ', topic
    
    