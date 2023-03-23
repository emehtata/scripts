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

broker_address="192.168.7.8"
broker_port=11883

client=mqtt.Client("mrpi3-ruuviclient")

ruuvis = {
  "DD:17:F3:D7:86:CE": "pool",
  "EA:D5:76:69:70:99": "freezer",
  "EC:67:46:36:EA:60": "sauna",
  "FE:87:0F:93:69:AA": "biergarten",
  "E8:28:93:CE:5A:E8": "greenhouse",
  "D5:43:48:93:FE:F0": "fridge",
  "C5:7D:4C:65:9D:60": "car-interior",
  "E2:9D:53:95:0E:8B": "upstairs-small-bedroom",
  "D1:48:D2:7D:3D:02": "downstairs-bedroom"
  }

def send_single(jdata, keyname):
  topic=jdata['room']+f"/{keyname}"
  client.publish(topic, jdata[keyname])

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

def on_connect(client, userdata, flags, rc):
    if rc==0:
        logging.info(f"Connected OK Returned code {rc}")
    else:
        logging.error(f"Bad connection Returned code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.error("Unexpected MQTT disconnection. Will reconnect.")
        client.disconnect()
        time.sleep(10)
        client.connect(broker_address, port=broker_port)
        logging.info("Connected.")

if __name__ == '__main__':
  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  client.connect(broker_address, port=broker_port)
  try:
    RuuviTagSensor.get_data(handle_data)
  except Exception as e:
    logging.warning(f"get_data not working, trying get_datas: {e}")
    RuuviTagSensor.get_datas(handle_data)

