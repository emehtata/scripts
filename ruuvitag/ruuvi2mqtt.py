#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import struct
import time
import paho.mqtt.client as mqtt
import json
import sys
import os
import platform
from ruuvitag_sensor.ruuvi import RuuviTagSensor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

clients = {}

brokers = {
    "192.168.7.8":  { "port": 11883 }
}

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

def send_single(jdata, keyname, client):
  topic=jdata['room']+f"/{keyname}"
  logging.debug(f"{topic}: {jdata[keyname]}")
  client.publish(topic, jdata[keyname])

def handle_data(found_data):
  logging.info(found_data)
  room=ruuvis[found_data[0]]
  topic="home/"+room
  logging.debug(room)
  jdata=found_data[1]
  jdata.update( { "room": room } )
  jdata.update( { "client": myhostname } )
  my_data=json.dumps(jdata).replace("'", '"')
  logging.info(my_data)
  for b in brokers:
    clients[b].publish(topic, my_data)
    for j in jdata:
      send_single(jdata, j, clients[b])
  logging.info("-"*40)

def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected, returned code {rc}")
    if rc==0:
        logging.info(f"Connected OK Returned code {rc}")
    else:
        logging.error(f"Bad connection Returned code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.error("Unexpected MQTT disconnection. Will reconnect all clients.")
        for b in brokers:
            clients[b].disconnect()
            time.sleep(10)
        for b in brokers:
            clients[b].connect(b, port=brokers[b]['port'])

if __name__ == '__main__':
  myhostname=platform.node()
  for b in brokers:
    logging.info(f"Connecting Broker: {b} {brokers[b]}")
    clients[b]=mqtt.Client(f"{myhostname}-ruuviclient")
    clients[b].on_connect = on_connect
    clients[b].on_disconnect = on_disconnect
    clients[b].connect(b, port=brokers[b]['port'])
    logging.info(f"Connection OK {clients[b]}  {brokers[b]}")
  try:
    RuuviTagSensor.get_data(handle_data)
  except Exception as e:
    logging.warning(f"get_data not working, trying get_datas: {e}")
    RuuviTagSensor.get_datas(handle_data)

