#!/usr/bin/python -tt

"""
#entry point file for this module 
"""
from time import sleep
import os

import common
import config 
import device
import epmqtt


def main():
    print "Starting read_n_dump..."
    common.initialize()
    
    device_id= str(10)
    device_type='temperature'
    epmqtt.device_client_start(device_type, device_id)
    sleep(10)  ##vne::tbd

    
def test_device_add(device_id, device_type):
    """ 
    Testing function for adding a device
    """
    device_data = {}
    device_data['id'] = device_id
    device_data['type'] = device_type
    device_data['dump_file'] = 'temp.log'
    device_data['sleep'] = 5
    device_data['status'] = 'registered'
    device_data['state'] = 'enabled'
    
    device.device_add(device_data)

if __name__ == '__main__':
    main()
