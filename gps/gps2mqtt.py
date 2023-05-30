import json
import logging
import os
from time import sleep, time

import gpsd
import paho.mqtt.client as mqtt
from geopy.geocoders import Nominatim

from settings import DEGREE_THRESHOLD, TIME_THRESHOLD, brokers, mqtt_topic

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')
if 'DEBUG' in os.environ:
    logging.getLogger().setLevel(logging.DEBUG)

# Geocoding object
geolocator = Nominatim(user_agent='gps_reverse_geocoding')

# Variables to track previous data
previous_bearing = None
previous_time = None

clients=[]

# Connect to GPSD
gpsd.connect()

# Function to perform reverse geocoding
def perform_reverse_geocoding(latitude, longitude):
    location = geolocator.reverse((latitude, longitude))
    if location:
        address = location.raw.get('address', {})
        street = address.get('road', '')
        city = address.get('city', '')
        return street, city
    return '', ''

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
def main_loop():
    global previous_bearing, previous_time, clients

    i=0
    for broker in brokers:
        try:
            clients.append(mqtt.Client())
            clients[i].on_connect = on_connect
            clients[i].on_publish = on_publish

            clients[i].connect(broker['host'], port=broker['port'])

            clients[i].loop_start()
            i+=1
        except OSError:
            logging.error(f"Could not connect: {broker['host']}:{broker['port']}")

    if i == 0:
        logging.error(f"Could not connect any of the MQTT brokers: {brokers}")
        raise OSError

    street, city = '', ''
    while True:
        try:
            # Wait for new data to be received
            packet = gpsd.get_current()

            # Check if the data is valid
            if packet.mode >= 2:  # Valid data in 2D or 3D fix
                if hasattr(packet, 'lat') and hasattr(packet, 'lon') and hasattr(packet, 'speed') and hasattr(packet, 'track'):
                    # Get latitude, longitude, speed, and bearing
                    latitude = packet.lat
                    longitude = packet.lon
                    speed = packet.speed() * 3.6  # Convert speed from m/s to km/h
                    bearing = packet.track

                    if previous_bearing is None or abs(bearing - previous_bearing) >= DEGREE_THRESHOLD or \
                            (previous_time is not None and time() - previous_time >= TIME_THRESHOLD):
                        street, city = perform_reverse_geocoding(latitude, longitude)

                    # Create a JSON object
                    data = {
                        'latitude': latitude,
                        'longitude': longitude,
                        'speed': speed,
                        'bearing': bearing,
                        'street': street,
                        'city': city,
                        'room': 'car'
                    }
                    logging.debug(f"{data}")
                    # Convert the JSON object to a string
                    json_data = json.dumps(data)

                    previous_bearing = bearing
                    previous_time = time()
                    # Publish the JSON data to each MQTT broker
                    for client in clients:
                        client.publish("gps_module/attributes", json_data)


            sleep(1)
        except KeyboardInterrupt:
            # Exit the loop if Ctrl+C is pressed
            break
        except Exception as e:
            logging.error(f"Unhandled exception {e}")

if __name__ == '__main__':
    main_loop()