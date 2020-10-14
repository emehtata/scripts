#!/usr/bin/env python3
import logging
import signal
import sys
import logging
import paho.mqtt.client as mqtt
import json
from datetime import datetime

import RPi.GPIO as GPIO

BUTTON_GPIO = 11
MQTTHOST = "192.168.7.79"
topicContact="home/motion/rpi1/contact"
topicAvailability="home/motion/rpi1/availability"

logging.basicConfig(level=logging.DEBUG)

def on_publish(client,userdata,result):
    logging.info("%s - Publish data: %s" % result,userdata)
    pass

def signal_handler(sig, frame):
    topic="home/motion/rpi1/availability"
    client.publish(topic, "offline")
    GPIO.cleanup()
    sys.exit(0)

def motion_detected(channel):
    logging.info("[%s] Motion detected!" % datetime.now().time())
    ret,seq = client.publish(topicAvailability, "online")
    if( ret != 0 ):
        client.connect(MQTTHOST)
        ret,seq = client.publish(topicAvailability, "online")
        ret,seq = client.publish(topicContact, "ON")
    else:
        ret,seq = client.publish(topicContact, "ON")

if __name__ == '__main__':
    client=mqtt.Client("Motiondetect")
    client.on_publish = on_publish
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_GPIO, GPIO.IN)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING,
            callback=motion_detected)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
