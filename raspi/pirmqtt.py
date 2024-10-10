#!/usr/bin/env python3
# Import required libraries
import logging  # For logging messages to console
import signal   # For handling signals like Ctrl+C
import sys      # For system-related functions
import paho.mqtt.client as mqtt  # MQTT client library
import json     # For handling JSON data
from datetime import datetime  # For timestamping events

import RPi.GPIO as GPIO  # Raspberry Pi GPIO library for input/output

# Define GPIO pin number for the motion sensor button
BUTTON_GPIO = 11

# MQTT broker host address and topics
MQTTHOST = "192.168.7.8"
topicContact = "home/motion/rpi1/contact"  # Topic to publish motion detection events
topicAvailability = "home/motion/rpi1/availability"  # Topic for device availability status

# Set up logging for debugging and info messages
logging.basicConfig(level=logging.DEBUG)

# Callback function when MQTT connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected OK, Returned code=%d" % rc)
    else:
        logging.warning("Bad connection, Returned code=%d" % rc)

# Callback function when a message is published to an MQTT topic
def on_publish(client, userdata, mid):
    logging.info("%s - Publish data: %s" % (mid, userdata))

# Function to handle cleanup and exit when Ctrl+C is pressed
def signal_handler(sig, frame):
    # Publish 'offline' status before disconnecting
    client.publish(topicAvailability, "offline")
    client.disconnect()  # Disconnect MQTT client
    GPIO.cleanup()  # Clean up GPIO settings
    sys.exit(0)  # Exit the program

# Callback function triggered when motion is detected
def motion_detected(channel):
    logging.info("[%s] Motion detected!" % datetime.now().time())  # Log motion event with timestamp
    ret, seq = client.publish(topicAvailability, "online")  # Publish 'online' status

    if ret != 0:  # If publish fails, try reconnecting
        client.connect(MQTTHOST, keepalive=1800)
        ret, seq = client.publish(topicAvailability, "online")  # Retry publishing 'online' status
        ret, seq = client.publish(topicContact, "ON")  # Publish 'ON' to indicate motion
    else:
        ret, seq = client.publish(topicContact, "ON")  # Publish 'ON' to indicate motion

# Main program starts here
if __name__ == '__main__':
    # Initialize MQTT client with 'Motiondetect' as client ID
    client = mqtt.Client("Motiondetect")

    # Set MQTT callbacks for publishing and connecting
    client.on_publish = on_publish
    client.on_connect = on_connect

    # Connect to the MQTT broker
    client.connect(MQTTHOST, keepalive=1800)

    # Set up GPIO pin mode and define button pin as input
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_GPIO, GPIO.IN)

    # Attach event detection to the button GPIO for rising edge (motion detected)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, callback=motion_detected)

    # Set up signal handler for cleanup on exit (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Pause the program, waiting for events
    signal.pause()

