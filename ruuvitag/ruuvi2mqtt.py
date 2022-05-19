#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import redis
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

r = redis.Redis(host='localhost', port=6379, db=0)

lastseen={}
last_in_redis={}

for tag in ruuvis:
  r.set(ruuvis[tag]+'.seen', time.time())
  lastseen[ruuvis[tag]]=time.time()
  last_in_redis[ruuvis[tag]]=0

logging.info(f"{lastseen}")

def set_redis_last(key, lastseen):
  try:
    r.set(key+'.seen', lastseen)
    logging.info("Writing key: "+key+", seen: "+str(lastseen))
  except:
    logging.error("Can not set redis value")

def get_redis_last(key):
  retval=float(r.get(key+'.seen'))
  logging.debug("%s %f" % (key, retval))
  if retval:
    return retval
  else:
    return time.time()

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
  logging.debug(my_data)
  client.publish(topic, my_data)
  lastseen[room]=time.time()
  if time.time()-last_in_redis[room] > MAX_IDLE/2:
    logging.info("="*40)
    last_in_redis[room]=time.time()
    set_redis_last(room, time.time())
    logging.info("="*40)
  for tag in ruuvis:
    if time.time()-lastseen[ruuvis[tag]] > MAX_IDLE:
        lastseen[tag] = get_redis_last(ruuvis[tag])

    if time.time()-lastseen[ruuvis[tag]] > MAX_IDLE:
      logging.error("No data received from %s for over %d seconds (%.02f)" % ( ruuvis[tag], MAX_IDLE, time.time()-lastseen[ruuvis[tag]] ))
      #os.execv(sys.argv[0], sys.argv)
      #os.kill(os.getpid(), 9)
    else:
      logging.info("%s - last seen %f seconds ago" % ( ruuvis[tag], time.time()-lastseen[ruuvis[tag]] ) )
  send_temperature(jdata)
  send_humidity(jdata)
  send_pressure(jdata)
  logging.info("-"*40)
RuuviTagSensor.get_datas(handle_data)
