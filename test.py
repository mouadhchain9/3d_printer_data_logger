import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe("octoprint/#")

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.connect("localhost", 1883)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
