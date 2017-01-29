"""
Contains device specific functionality
"""

import common

def get_device_topic(type, id):
    return '/'.join([common.get_node_id(), 'device', type, id])

