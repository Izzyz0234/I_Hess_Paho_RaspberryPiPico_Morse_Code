import re
import time
import paho.mqtt.client as mqtt

ADAFRUIT_AIO_USERNAME = "Izzy0234"
ADAFRUIT_AIO_KEY = ""

MQTT_BROKER = "mqtt-dashboard.com"
MQTT_ADA_BROKER = "io.adafruit.com"

TOPIC_HIVEMQ = "TAFE/i-hess/morse-code"
TOPIC_PICO_RESP = "TAFE/i-hess/morse-code-respond"
TOPIC_ADA_BUTTON = "Izzy0234/feeds/morse-code.button"


def decode_morse(raw_message):
    value = str(raw_message)
    value = re.sub(r"b'|b\"|\[|\]|'|\"|,", "", value)
    value = value.replace(" ", "")

    if not value:
        return ""

    letters = value.split("=") if "=" in value else [value]
    decoder = {
        "._": "A", "_...": "B", "_._.": "C", "_..": "D", ".": "E", ".._.": "F",
        "__.": "G", "....": "H", "..": "I", ".___": "J", "_._": "K", "._..": "L",
        "__": "M", "_.": "N", "___": "O", ".__.": "P", "__._": "Q", "._.": "R",
        "...": "S", "_": "T", ".._": "U", "..._": "V", ".__": "W", "_.._": "X",
        "_.__": "Y", "__..": "Z", ".____": "1", "..___": "2", "...__": "3",
        "...._": "4", ".....": "5", "_....": "6", "__...": "7", "___..": "8",
        "____.": "9", "_____": "0"
    }

    text = ""
    for letter in letters:
        text += decoder.get(letter, "*")
    return text


def on_connect_hivemq(client, userdata, flags, reason_code, properties):
    print(f"Connected to {MQTT_BROKER} with result code {reason_code}")
    client.subscribe(TOPIC_HIVEMQ)


def on_message_hivemq(client, userdata, msg):
    if msg.topic != TOPIC_HIVEMQ:
        return

    decoded = decode_morse(msg.payload)
    print(f"HiveMQ {msg.topic}: {msg.payload} -> {decoded}")

    if "*" not in decoded and decoded.strip():
        mqttc.publish(TOPIC_PICO_RESP, "ledGreen2.on()")
        mqttc_ada.publish(TOPIC_ADA_BUTTON, "ON")
    else:
        mqttc.publish(TOPIC_PICO_RESP, "ledRed2.on()")
        mqttc_ada.publish(TOPIC_ADA_BUTTON, "OFF")


def on_connect_ada(client, userdata, flags, reason_code, properties):
    print(f"Connected to {MQTT_ADA_BROKER} with result code {reason_code}")
    client.subscribe(TOPIC_ADA_BUTTON)


def on_message_ada(client, userdata, msg):
    if msg.topic != TOPIC_ADA_BUTTON:
        return

    payload = str(msg.payload.decode("utf-8", "ignore")).strip().upper()
    print(f"Adafruit feed {msg.topic}: {payload}")

    if payload in ("ON", "1", "TRUE"):
        mqttc.publish(TOPIC_PICO_RESP, "ledGreen2.on()")
    elif payload in ("OFF", "0", "FALSE"):
        mqttc.publish(TOPIC_PICO_RESP, "ledGreen2.off()")
    else:
        mqttc.publish(TOPIC_PICO_RESP, "ledRed2.on()")



mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(MQTT_BROKER)


mqttc_ada = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc_ada.on_connect = on_connect_ada
mqttc_ada.username_pw_set(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)
mqttc_ada.on_message = on_message_ada
mqttc_ada.connect(MQTT_ADA_BROKER, 1883, 60)  # Connect to Adafruit IO broker
# mqttc_ada.publish(TOPIC_ADA_BUTTON, "ON")  # Publish a message to the Adafruit button topic



mqttc.loop_start()
mqttc_ada.loop_start()

while True:
    time.sleep(1)  # Keep the main thread alive to allow MQTT loop to run
    mqttc_ada.publish(TOPIC_ADA_BUTTON, "ON")  # Publish a message to the Adafruit button topic
    # mqttc_ada.publish("Izzy0234/groups/led-status", '{"feeds":{"led-status.led1":"ON","led-status.led2":"OFF"}}')  # Publish a message to the Adafruit button topic

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