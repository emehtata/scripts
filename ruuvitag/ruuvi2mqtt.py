#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import redis
import struct
import time
import paho.mqtt.client as mqtt
import json
import os
from ruuvitag_sensor.ruuvi import RuuviTagSensor

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')

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

r = redis.Redis(host='localhost', port=6379, db=0)

for tag in ruuvis:
  r.set(ruuvis[tag]+'.seen', time.time())

def set_redis_last(key, lastseen):
  try:
    r.set(key+'.seen', lastseen)
    logging.debug("key: "+key+", seen: "+str(lastseen))
  except:
    logging.error("Can not set redis value")

def get_redis_last(key):
  retval=float(r.get(key+'.seen'))
  logging.debug("%s %f" % (key, retval))
  if retval:
    return retval
  else:
    return time.time()

def handle_data(found_data):
  room=ruuvis[found_data[0]]
  topic="home/"+room
  logging.debug(room)
  jdata=found_data[1]
  jdata.update( { "room": room } )
  my_data=json.dumps(jdata).replace("'", '"')
  logging.debug(my_data)
  client.publish(topic, my_data)
  set_redis_last(room, time.time())
  for tag in ruuvis:
    lastseen = time.time()-get_redis_last(ruuvis[tag])
    if lastseen > 60:
      logging.warning("Not receiving data from %s" % tag)
      logging.error("Restarting")
      os.execv(sys.argv[0], sys.argv)
    else:
      logging.debug("%s last seen %f seconds ago" % ( tag, lastseen ) )

RuuviTagSensor.get_datas(handle_data)
