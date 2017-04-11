"""
functionality of subscribing to topics on MQTT broker 
"""

import config
import epmqtt
import paho.mqtt.client as mqtt


def subscribe_mqtt_topics(client):
    t_list = config.get_control_topics()
    for topic in t_list: 
        print 'subscribing to ', topic
        client.subscribe(topic)
    """
    vne::tbd
    sub_topics = epmqtt.mqtt_profile['sub']
    
    for key in sub_topics.keys():
        print 'subscribing to ', key, ":", sub_topics[key]
        client.subscribe(sub_topics[key])    
    """

    