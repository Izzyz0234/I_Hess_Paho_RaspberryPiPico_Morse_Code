from picozero import LED, Button, pico_led
from machine import ADC, Pin
from time import sleep
from umqtt.simple import MQTTClient
import utime, time, network, dht, ujson
# import paho.mqtt.client as mqtt

# SETUP
# WEBSITE: https://www.hivemq.com/demos/websocket-client/
# PORT: 8884
# CLIENTID: clientId-EoD7b24R9r
# CLIENTID: clientId-482sO0L372
# HOST: mqtt-dashboard.com
# TOPIC: TAFE//i-hess/morse-code
# TOPIC2: TAFE//i-hess/morse-code-respond

# Convert morse code in paho/python/subscriber-side code when displaying the message

def mqtt_on_message(topic, msg):
    # There is only 1 callback, but you can filter based on what the topic was.
    # You will need to add more client.subscribe calls after connecting to subscribe to additional topics.
    print(topic, msg)
    

MQTT_CLIENT_ID = "clientId-EoD7b24R9r"
MQTT_BROKER    = "mqtt-dashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPICS     = [b"TAFE/i-hess/morse-code", b"TAFE/i-hess/morse-code-respond"]
MQTT_TOPIC_TARGET1    = "TAFE/i-hess/morse-code"
MQTT_TOPIC_TARGET2    = "TAFE/i-hess/morse-code-respond"

BUTTON_PIN = 16 
LED_PIN = 15

press_time = None
not_press_time = None
print_space = False
print_long_space = False
stop_message = False

button_pressed_times = 0

morse_code_list = []

ledRed = LED(10)
ledYellow = LED(11)
ledGreen = LED(12)
ledRed2 = LED(13)
ledGreen2 = LED(8)

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

client = None

<!-- # wifi_ssid = "TelstraEC9E55"
# wifi_password = "pjvgqwjrgvn6"

wifi_ssid = "Skynet"
wifi_password = "comewithmeifyouwanttolive"

-->

wifi_ssid = ""
wifi_password = ""


# Connect to wifi
print("\nConnecting to WiFi...", end="")
pico_led.on() # use pico_led to know when it's running
ledRed.pulse()
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(wifi_ssid, wifi_password)

while not wifi.isconnected():
  print(".", end="")
  ledYellow.off()
  utime.sleep(0.1)
  
print("Connected!")
print(f"Wi-Fi: {wifi.ifconfig()}")

def message_callback(topic, msg):
    if topic in MQTT_TOPICS:
        print("Received message on topic:", topic.decode())
        print("Message content:", msg.decode())

def on_message(topic, msg):
    print("Topic:", topic)
    if topic == b'TAFE/i-hess/morse-code-respond':
        print(f"[TARGET] Received from {topic.decode()}: {msg.decode()}")
        
        if msg.decode() == "ledGreen2.off()":
            ledGreen2.off()
        if msg.decode() == "ledGreen2.on()":
            ledGreen2.blink(.4)
            
        if msg.decode() == "ledRed2.off()":
            ledRed2.off()
        if msg.decode() == "ledRed2.on()":
            ledRed2.blink(.4)
        
        utime.sleep(3)
        ledRed2.off()
        ledGreen2.off()
    else:
        print(f"[IGNORED] Received from {topic.decode()}")
        
def connect_and_subscribe(client):
    client.connect()
    for t in MQTT_TOPICS:
        client.subscribe(t)
        print(f"Subscribed: {t.decode()}")
        
def process_queue():
    while message_queue:
        try:
            topic, msg, ts = message_queue.pop(0)
            # Example processing logic
            print(f"[{ts}] Processing message from {topic.decode()}: {msg.decode()}")
        except Exception as e:
            print(f"Error processing message: {e}")

try:
    print("Connecting to MQTT server... ", end="")
    ledRed.pulse()
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.set_callback(on_message)
    print("Connected!")
    
    connect_and_subscribe(client)
    
    ledRed.off()
    ledYellow.pulse()
    print("Syncing to Rasberry Pi Pico... ", end="")
    print_short_space = False
    print_long_space = False
    
    # Sleep to let have the board sync properly
    utime.sleep(3)
    ledYellow.off()
    ledGreen.pulse()
    print("Synced!")


        
    utime.sleep(2)
    button_pressed_times = 0
    ledGreen.brightness = .1
    ledYellow.brightness = .1
    ledRed.brightness = .1
    
    def get_button():
        # Checks if button was pressed
        return not button.value()
    
    def button_press_function():
        global press_time
        global not_press_time
        # Starts timers for printing . _
        if press_time is None:  # Only record the first press
            press_time = int(current_ms_1)
            not_press_time = int(current_ms_2)
            ledGreen2.off()
            ledGreen.brightness = .2
            ledYellow.brightness = .2
            ledRed.brightness = .2
            
        # If you can enter _ brighten the lights more
        duration = current_ms_1 - press_time
        if duration >= 1000:
            ledGreen.brightness = .5
            ledYellow.brightness = .5
            ledRed.brightness = .5
            
    def button_released_function():
        global press_time
        global not_press_time
        if press_time is not None:
            duration = current_ms_1 - press_time
            
            # If button was pressed quickly print .
            if duration >= 0 and duration < 1000:
                morse_code_list.append(".")
                print(*morse_code_list[1:])
                ledGreen2.off()
                ledGreen.off()
                ledYellow.on()
                ledRed.off()

            # If button was pressed longer print _
            if duration >= 1000:
                morse_code_list.append("_")
                print(*morse_code_list[1:])
                ledGreen2.off()
                ledGreen.on()
                ledYellow.on()
                ledRed.on()
                
            press_time = None                    

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe("TAFE//i-hess/morse-code-respond")
        
    while True:
        try:
            client.check_msg()
            process_queue()
        except OSError:
            # Handle broker disconnection
            print("Broker disconnected, attempting to reconnect...")
            connect_and_subscribe(client)
        get_button()
        button_pressed_times = 0
        current_ms_1 = int(time.time() * 1000)
        current_ms_2 = int(time.time() * 1000)
        
        if get_button() == True:
            button_pressed_times += 1
            print_short_space = True
            print_long_space = True
            stop_message = True
            button_press_function()

        if get_button() == False:
            button_released_function()
            
            if not_press_time is None:
                not_press_time = int(current_ms_2)
            if not_press_time is not None:
                duration = current_ms_2 - not_press_time
                
                # Add space for letters
                if duration > 1000 and print_short_space == True:
                    morse_code_list.append(" ")
                    print(*morse_code_list[1:])
                    not_press_time = int(current_ms_2)
                    ledGreen.off()
                    ledRed.off()
                    ledYellow.off()
                    ledGreen2.brightness = .2
                    print_short_space = False
                
                # Add space for word
                if duration > 2000 and print_long_space == True:
                    morse_code_list.append("  ")
                    print(*morse_code_list[1:])
                    not_press_time = int(current_ms_2)
                    ledGreen2.brightness = 1
                    print_long_space = False
                
                # Publishing message to mqtt-dashboard.com
                if duration > 3000 and stop_message == True:
                    ledGreen2.off()
                    ledYellow.pulse()
                    get_button()
                    if get_button == True:
                        button_press_function()
                    if get_button == False:
                        button_released_function()
                    
                    print(f"Publishing message to {MQTT_TOPIC_TARGET1}... ", end="")
                    utime.sleep(3)
                    ledYellow.off()
                    ledGreen.on()
                    message = ujson.dumps(morse_code_list)
                    client.publish(MQTT_TOPIC_TARGET1, message)
                    client.check_msg()
                    print("Published!")
                    utime.sleep(1)
                    

                    
                    # mqttc.on_connect = on_connect
                    # mqttc.on_message = on_message
                    # Reseting lights and values
                    ledGreen2.off()
                    ledGreen.brightness = .1
                    ledYellow.brightness = .1
                    ledRed.brightness = .1
                    morse_code_list = []
                    button_pressed_times = 0
                    stop_message = False
    
finally:
    pico_led.off()
    ledRed.off()
    ledYellow.off()
    ledGreen.off()
    ledGreen2.off()
    ledRed2.off()
