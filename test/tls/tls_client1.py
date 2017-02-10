import paho.mqtt.client as paho

mqtt_rc_codes = {
                    0: 'Connection successful',
                    1: 'Connection refused - incorrect protocol version',
                    2: 'Connection refused - invalid client identifier',
                    3: 'Connection refused - server unavailable',
                    4: 'Connection refused - bad username or password',
                    5: 'Connection refused - not authorised'
                }

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        print 'Client connected successfully'
        client.publish('topic/test', 'abcd')
    else:
        print 'Client connection failed: ', str(rc), mqtt_rc_codes[rc]

def on_message(clnt, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = paho.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect 
#mqttc.tls_set("keys/ca.crt") 
mqttc.tls_set("keys/ca.crt", "keys/client.crt", "keys/client.key") 
print 'connecting to broker...'
mqttc.connect("192.168.88.100", 8883)
mqttc.loop_forever()