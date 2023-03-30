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
from settings import brokers
from settings import ruuvis

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

clients = {}

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

