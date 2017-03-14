"""
functionality related to endpoint  
"""

import config

def get_messaging_protocol():
    return config.get_messaging_protocol()

def get_subscribe_topic():
    return config.get_subscribe_topic()

def get_broker_details():
    return [config.get_endpoint_broker_ip(), config.get_endpoint_broker_port(), config.get_endpoint_broker_keepalive()]