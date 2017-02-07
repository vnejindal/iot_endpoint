"""
Control Client for Application
"""
import os
import json
from time import sleep

import paho.mqtt.client as mqtt

scenario = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    process_actions()

def on_message(client, userdata, msg):
    print("vne:: "+msg.topic+" "+str(msg.payload))
    
    #if msg.payload is 'ok'
    print 'processing next action '
    process_actions()
    
        
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
    pass

def create_mqtt_client(srv_ip, srv_port, srv_keepalive = 60):
    """
    Connects with MQTT broker
    """
    print 'connecting to broker:', srv_ip,':', srv_port, ' ', srv_keepalive
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(srv_ip, srv_port, srv_keepalive)
    print 'connection to broker successful'  
    global scenario 
    scenario['client'] = mqtt_client
    mqtt_client.loop_forever()
    
    #client.loop_start()
    #dpublish.read_device_data('temperature', '1', client)


def read_scenario_file(file_name):
    json_config = open(file_name).read()
    scenario = json.loads(json_config)
    
    #print scenario
    return scenario

def generate_node_id(node_id):
    return '_'.join([node_id.replace('.','_')])

def start_scenario(file_name):
    
    global scenario 
    scenario = read_scenario_file(file_name)
    create_mqtt_client(scenario['broker_ip'], scenario['broker_port'])
    
    request_common = {}

def publish_data(data_string):
    print 'publishing data: ', scenario['topic'], data_string
    
    pub_data = json.dumps(data_string)
    (rc, mid) = scenario['client'].publish(scenario['topic'], pub_data, qos=2)
    print 'published: ', rc, mid
    
def subscribe_topic(topic):
    scenario['client'].subscribe(topic)
    
def process_actions():
    
    global scenario

    for action in scenario['actions']:
        print 'sleeping for seconds: ', action['wait']
        sleep(action['wait'])
        action['request_id'] = scenario['request_id_start']
        process_next_action(action)
        print 'action executed: ', action 
        
        scenario['actions'].remove(action)
        scenario['request_id_start'] += 1
        break
        
def process_next_action(action):
    
    print 'processing action: ', action
    
    global scenario 
    
    request_common = {}
    
    if scenario['gateway_id'] != 'none':
        scenario['topic'] = '/'.join([scenario['gateway_id'], 
                                           scenario['endpoint_id'], 
                                           'device', 
                                           scenario['device_type'],
                                           str(scenario['device_id'])]
                                           )
    
    request_common['topic'] = scenario['topic']
    
    request = {}
    request.update(request_common)
    request.update(action)
    request.pop('_comment', None)
    request.pop('wait', None)
    
    publish_data(request)
    scenario['response'] = {}
    scenario['response']['topic'] = '/'.join(['response', request['topic']])
    scenario['response']['wait'] = 1
    subscribe_topic(scenario['response']['topic'])
        
start_scenario('scenario.json')