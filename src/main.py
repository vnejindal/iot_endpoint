#!/usr/bin/python -tt

"""
#entry point file for this module 
"""
from time import sleep

"""
-- read configuration 
-- 
"""

import os

import common
import config 
import dpublish

def main():
    print "Starting read_n_dump..."
    common.initialize()
    
    device_id= str(1)
    device_type='temperature'
    dpublish.device_client_start(device_type, device_id)
    sleep(10)

if __name__ == '__main__':
    main()
