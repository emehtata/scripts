#!/bin/env python3

import json
import logging
import os
from time import sleep, time

import gpsd as _gpsd
import paho.mqtt.client as mqtt
from geopy.geocoders import Nominatim

from settings import DEGREE_THRESHOLD, SPEED_THRESHOLD, TIME_THRESHOLD, _brokers, _mqtt_topic

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')
if 'DEBUG' in os.environ:
    logging.getLogger().setLevel(logging.DEBUG)

class Status:
    def __init__(self):
        self._bearing_time = None
        self._previous_bearing = None
        self._previous_time = None
        self._clients = []
        self._geolocator = Nominatim(user_agent='ha_address_finder')

        # Connect to gpsd
        self.gpsd.connect()

        # settings
        self._brokers = _brokers
        self._mqtt_topic = _mqtt_topic

    # Setter and getter for 'bearing_time' variable
    @property
    def bearing_time(self):
        return self._bearing_time

    @bearing_time.setter
    def bearing_time(self, value):
        self._bearing_time = value

    # Setter and getter for 'previous_bearing' variable
    @property
    def previous_bearing(self):
        return self._previous_bearing

    @previous_bearing.setter
    def previous_bearing(self, value):
        self._previous_bearing = value

    # Setter and getter for 'previous_time' variable
    @property
    def previous_time(self):
        return self._previous_time

    @previous_time.setter
    def previous_time(self, value):
        self._previous_time = value

    # Setter and getter for 'clients' variable
    @property
    def clients(self):
        return self._clients

    @clients.setter
    def clients(self, value):
        self._clients = value

    # Getter for 'gpsd' object
    @property
    def gpsd(self):
        return _gpsd

    # Getter for 'geolocator' object
    @property
    def geolocator(self):
        return self._geolocator

    @property
    def brokers(self):
        return self._brokers

    @property
    def mqtt_topic(self):
        return self._mqtt_topic
# Function to perform reverse geocoding


def perform_reverse_geocoding(status, latitude, longitude):
    location = status.geolocator.reverse((latitude, longitude))
    if location:
        address = location.raw.get('address', {})
        return address
    return None


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker")
    else:
        logging.error("Failed to connect, return code: ", rc)


def on_publish(client, userdata, mid):
    logging.debug(f"Message published {mid}")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.error("Unexpected MQTT disconnection.")

# Main loop to continuously read GPS data

def connect_brokers(status):
    i = 0
    for broker in status.brokers:
        try:
            status.clients.append(mqtt.Client())
            status.clients[i].on_connect = on_connect
            status.clients[i].on_publish = on_publish
            status.clients[i].connect(broker['host'], port=broker['port'])
            status.clients[i].loop_start()
            i += 1
        except OSError:
            logging.error(
                f"Could not connect: {broker['host']}:{broker['port']}")

    if i == 0:
        logging.error(f"Could not connect any of the MQTT brokers: {brokers}")
        raise OSError

    return status

def main_loop(status):
    status = connect_brokers(status)

    street = city = country = postcode = ''
    while True:
        try:
            # Wait for new data to be received
            packet = status.gpsd.get_current()
            # Check if the data is valid
            if packet.mode >= 2:  # Valid data in 2D or 3D fix
                if hasattr(packet, 'lat') and hasattr(packet, 'lon'):
                    # Get latitude, longitude, speed, and bearing
                    latitude = packet.lat
                    longitude = packet.lon
                    speed = packet.hspeed * 3.6
                    if speed < SPEED_THRESHOLD:
                        speed = 0
                    bearing = packet.track
                    gps_time = packet.time

                    if (status.previous_bearing is None or
                        (speed > 0 and abs(bearing - status.previous_bearing) >= DEGREE_THRESHOLD) or
                            (speed > 0 and status.previous_time is not None and time() - status.previous_time >= TIME_THRESHOLD)):
                        address = perform_reverse_geocoding(
                            status, latitude, longitude)
                        if address:
                            street = address.get('road', '')
                            city = address.get('city', '')
                            postcode = address.get('postcode', '')
                            country = address.get('country_code', '')
                        status.previous_bearing = bearing
                        bearing_time = time()

                    if hasattr(packet, 'alt') and hasattr(packet, 'climb'):
                        altitude = packet.alt
                        climb = packet.climb
                    else:
                        altitude = climb = 0

                    # Create a JSON object
                    data = {
                        'latitude': latitude,
                        'longitude': longitude,
                        'altitude': altitude,
                        'climb': climb,
                        'speed': round(speed,1),
                        'bearing': bearing,
                        'gps_accuracy': packet.position_precision()[0],
                        'street': street,
                        'postcode': postcode,
                        'city': city,
                        'country': country,
                        'time': gps_time,
                        'satellites': packet.sats,
                        'room': 'car',
                    }
                    logging.debug(f"{data}")
                    # Convert the JSON object to a string
                    json_data = json.dumps(data)
                    if bearing_time is None or time() - bearing_time > 5:
                        logging.debug(f"Storing previous bearing.")
                        status.previous_bearing = bearing
                        bearing_time = time()
                    status.previous_time = time()
                    # Publish the JSON data to each MQTT broker
                    for client in status.clients:
                        client.publish(status.mqtt_topic, json_data)
            else:
                logging.info(f"Waiting for valid data. ({packet.mode} < 2)")
            sleep(1)
        except KeyboardInterrupt:
            # Exit the loop if Ctrl+C is pressed
            break
        except Exception as e:
            logging.error(f"Unhandled exception {e}")


if __name__ == '__main__':
    status = Status()
    main_loop(status)
