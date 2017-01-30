#!/usr/bin/python -tt

"""
#entry point file for this module 
"""
from time import sleep


import os

import common
import config 
import epmqtt


def main():
    print "Starting read_n_dump..."
    common.initialize()
    
    device_id= str(1)
    device_type='temperature'
    epmqtt.device_client_start(device_type, device_id)
    sleep(10)  ##vne::tbd

if __name__ == '__main__':
    main()
