import paho.mqtt.client as mqtt
from PIL import Image
import time

MQTT_BROKER = "mqtt-dashboard.com"
MQTT_ADA_BROKER = "io.adafruit.com"

TOPIC_PICO = 'TAFE/i-hess/button'
TOPIC_ADA_BUTTON = 'Izzy0234/feeds/button'


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to {MQTT_BROKER} with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("TAFE/i-hess/button")

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_PICO:
        print(msg.topic+": "+str(msg.payload))
        return

def on_connect_ada(client, userdata, flags, reason_code, properties):
    print(f"Connected to {MQTT_ADA_BROKER} with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC_ADA_BUTTON)

def on_message_ada(client, userdata, msg):
    if msg.topic == TOPIC_ADA_BUTTON:
        print(msg.topic+": "+str(msg.payload))
        return



mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(MQTT_BROKER)


mqttc_ada = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc_ada.on_connect = on_connect_ada
mqttc_ada.on_message = on_message_ada
mqttc_ada.connect(MQTT_BROKER)





mqttc.loop_start()
mqttc_ada.loop_start()

while True:
    time.sleep(1)  # Keep the main thread alive to allow MQTT loop to run
    mqttc_ada.publish("Izzy0234/groups/led-status", '{"feeds":{"led-status.led1":"ON","led-status.led2":"OFF"}}')  # Publish a message to the Adafruit button topic

mqttc.loop_stop()  # Stop the MQTT loop when done
mqttc_ada.loop_stop()  # Stop the MQTT loop when done


#get raw data from pico






# {
#     feeds:
#     {
#         led-status.led1: ON,
#         led-status.led2: OFF,
#     }
# }


# from PIL import Image, ImageDraw
# import base64
# from io import BytesIO

# # --- Create a blank image ---
# width, height = 400, 300
# img = Image.new("RGB", (width, height), color="white")

# # --- Draw a circle at a specific coordinate ---
# draw = ImageDraw.Draw(img)

# # Circle parameters
# x, y = 200, 150      # center coordinate
# radius = 50
# bbox = [(x - radius, y - radius), (x + radius, y + radius)]

# draw.ellipse(bbox, outline="red", width=4, fill="yellow")

# # --- Encode image to Base64 ---
# buffer = BytesIO()
# img.save(buffer, format="PNG")
# base64_bytes = base64.b64encode(buffer.getvalue())
# base64_string = base64_bytes.decode("utf-8")

# print(base64_string)