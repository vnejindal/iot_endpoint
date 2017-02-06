import paho.mqtt.client as paho

def on_message(clnt, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = paho.Client()
mqttc.on_message = on_message
mqttc.tls_set("mosquitto.org.crt") # http://test.mosquitto.org/ssl/mosquitto.org.crt
mqttc.connect("test.mosquitto.org", 8883)
mqttc.subscribe("bbc/#")
mqttc.loop_forever()