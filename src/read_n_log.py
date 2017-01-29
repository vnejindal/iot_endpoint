#!/usr/bin/python -tt

import os 
import json
import time

def validate_json_config(file_name):
  """
   The method will validate the json config file for conflicts 
   like: same id values, same log file names, invalid values etc.
  """
  print 'vne::tbd:: validate not defined yet...'


def read_json_config(file_name):
  """
  vne::tbd::
  """
  print 'config file: ', file_name
  json_config=open(file_name).read()
  #tbd:: exception handling
  data=json.loads(json_config)
  log_json_config(data)

  #vne::tbd:: logic to be replace by a iteration to read all values  
  read_sensor(data['sensor'][0])


def log_json_config(json_data):
  """
  Prints Json data
  """
  print json_data['sensor'][0]['files'][1]['data_file']
  #print data['sensor'][0]['type']
  #print data['sensor'][1]['type']

def read_sensor(sensor_data):
  """ 
  It will read the sensor data json object and dump it in the specified file"
  """
  print 'reading sensor:', sensor_data['type'],'/',sensor_data['id']
  fs_path = sensor_data['fs_path'] + '/'
  file1 = fs_path + sensor_data['files'][0]['data_file'] 
  file2 = fs_path + sensor_data['files'][1]['data_file']
  dump_file = 'output/' + sensor_data['dump_file']
  sleep_time = sensor_data['sleep']

  print file1, file2, dump_file
  outfile = open(dump_file, "a")
  #vne::tbd:: exceptional handling
  while True:
    infile1 = open(file1, "r")
    infile2 = open(file2, "r")
    line1 = infile1.read()
    line2 = infile2.read()
    infile1.close()
    infile2.close()
    fline = time.asctime(time.localtime(time.time())) + ',' + line1.strip() + ',' + line2.strip() + '\n'
    outfile.write(fline)
    outfile.flush()
    print 'written: ', fline, 'now sleeping...'
    time.sleep(sleep_time)
  
  close(outfile)


def main():
  print "Starting read_n_dump..." 
  f_json='config/sensor.json'
  read_json_config(f_json) 

if __name__ == '__main__':
  main()
