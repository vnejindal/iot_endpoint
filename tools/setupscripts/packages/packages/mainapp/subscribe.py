"""
functionality of subscribing to topics on MQTT broker 
"""

import common
import epmqtt
import paho.mqtt.client as mqtt


def subscribe_mqtt_topics(client):
    sub_topics = epmqtt.mqtt_profile['sub']
    
    for key in sub_topics.keys():
        print 'subscribing to ', key, ":", sub_topics[key]
        client.subscribe(sub_topics[key])    


    