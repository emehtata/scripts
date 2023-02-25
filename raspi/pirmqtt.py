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
MQTTHOST = "192.168.7.8"
topicContact="home/motion/rpi1/contact"
topicAvailability="home/motion/rpi1/availability"

logging.basicConfig(level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        logging.info("connected OK Returned code=%d" % rc)
    else:
        logging.warning("Bad connection Returned code=%d" % rc)

def on_publish(client,userdata,mid):
    logging.info("%s - Publish data: %s" % (mid,userdata))

def signal_handler(sig, frame):
    topic="home/motion/rpi1/availability"
    client.publish(topic, "offline")
    client.disconnect()
    GPIO.cleanup()
    sys.exit(0)

def motion_detected(channel):
    logging.info("[%s] Motion detected!" % datetime.now().time())
    ret,seq = client.publish(topicAvailability, "online")
    if( ret != 0 ):
        client.connect(MQTTHOST, keepalive=1800)
        ret,seq = client.publish(topicAvailability, "online")
        ret,seq = client.publish(topicContact, "ON")
    else:
        ret,seq = client.publish(topicContact, "ON")

if __name__ == '__main__':
    client=mqtt.Client("Motiondetect")
    client.on_publish = on_publish
    client.on_connect = on_connect
    client.connect(MQTTHOST, keepalive=1800)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_GPIO, GPIO.IN)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING,
            callback=motion_detected)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
