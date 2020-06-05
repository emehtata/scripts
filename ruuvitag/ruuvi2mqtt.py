#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import paho.mqtt.client as mqtt
import json
from ruuvitag_sensor.ruuvi import RuuviTagSensor

logging.basicConfig(level=logging.DEBUG)

client=mqtt.Client("Ruuvireader")
client.connect("localhost")

ruuvis = {
  "DD:17:F3:D7:86:CE": "fridge",
  "EA:D5:76:69:70:99": "freezer",
  "EC:67:46:36:EA:60": "sauna",
  "D5:43:48:93:FE:F0": "cage",
  "E8:28:93:CE:5A:E8": "greenhouse",
  "FE:87:0F:93:69:AA": "biergarten"
  }

def handle_data(found_data):
  room=ruuvis[found_data[0]]
  topic="home/"+room
  print(room)
  jdata=found_data[1]
  jdata.update( { "room": room } )
  my_data=json.dumps(jdata).replace("'", '"')
  print(my_data)
  client.publish(topic, my_data)

RuuviTagSensor.get_datas(handle_data)

