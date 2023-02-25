#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import struct
import time
import paho.mqtt.client as mqtt
import json
import sys
import os
from ruuvitag_sensor.ruuvi import RuuviTagSensor

MAX_IDLE=300

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.ERROR,
    datefmt='%Y-%m-%d %H:%M:%S')

client=mqtt.Client("Ruuvireader")
client.connect("localhost")

ruuvis = {
  "DD:17:F3:D7:86:CE": "pool",
  "EA:D5:76:69:70:99": "freezer",
  "EC:67:46:36:EA:60": "sauna",
  "FE:87:0F:93:69:AA": "biergarten",
  "E8:28:93:CE:5A:E8": "greenhouse",
  "D5:43:48:93:FE:F0": "fridge"
  }

def send_single(jdata, keyname):
  topic=jdata['room']+f"/{keyname}"
  client.publish(topic, jdata[keyname])

def send_temperature(jdata):
  topic=jdata["room"]+"/temperature"
  client.publish(topic, jdata["temperature"])

def send_humidity(jdata):
  topic=jdata["room"]+"/humidity"
  client.publish(topic, jdata["humidity"])

def send_pressure(jdata):
  topic=jdata["room"]+"/pressure"
  client.publish(topic, jdata["pressure"])

def handle_data(found_data):
  room=ruuvis[found_data[0]]
  topic="home/"+room
  logging.debug(room)
  jdata=found_data[1]
  jdata.update( { "room": room } )
  my_data=json.dumps(jdata).replace("'", '"')
  logging.info(my_data)
  client.publish(topic, my_data)
  for j in jdata:
    send_single(jdata, j)
  logging.info("-"*40)

if __name__ == '__main__':
  RuuviTagSensor.get_datas(handle_data)
