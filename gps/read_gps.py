import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
import serial
import json
import paho.mqtt.client as mqtt
import sys
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim

from time import time
from datetime import datetime

delay_addr_fetch = 30
prev_addr_fetch = time()-delay_addr_fetch
address = "Finding address"
old_coords = [91, 0]
last_time = 0

def convert_latitude(latitude, direction):
    degrees = int(latitude[:2])
    minutes = float(latitude[2:])
    decimal_degrees = degrees + minutes / 60.0
    if direction == 'S':
        decimal_degrees *= -1
    return round(decimal_degrees, 6)

def convert_longitude(longitude, direction):
    degrees = int(longitude[:3])
    minutes = float(longitude[3:])
    decimal_degrees = degrees + minutes / 60.0
    if direction == 'W':
        decimal_degrees *= -1
    return round(decimal_degrees, 6)

def convert_timestamp(timestamp):
    time = datetime.strptime(timestamp, '%H%M%S.%f')
    return time.strftime('%H:%M:%S.%f')[:-3] + 'Z'

def nmea_to_unix(nmea_timestamp):
    # Parse NMEA timestamp string
    utc_date = datetime.utcnow().strftime("%Y%m%d")
    nmea_format = "%Y%m%d%H%M%S.%f"
    nmea_timestamp = f"{utc_date}{nmea_timestamp}"
    nmea_datetime = datetime.strptime(nmea_timestamp, nmea_format)

    # Convert to Unix timestamp
    unix_timestamp = float(nmea_datetime.timestamp())

    return unix_timestamp

def get_address(latitude, longitude, curr_time):
    global prev_addr_fetch
    global address

    if curr_time - prev_addr_fetch > delay_addr_fetch:
        geolocator = Nominatim(user_agent='home_assistant_geolocator')  # Specify a user agent string
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
    else:
       return address.get('road', ''), address.get('city', '')

    if location:
        address = location.raw['address']
        street = address.get('road', '')
        print(street)
        city = address.get('city', '')
        return street, city
    else:
        return "Unknown", "Unknown"

def calculate_speed(old_co, new_co, time_difference):
    if old_co[0] > 90:
       return 0
    # Convert latitude and longitude to radians
    lat1 = radians(old_co[0])
    lon1 = radians(old_co[1])
    lat2 = radians(new_co[0])
    lon2 = radians(new_co[1])

    # Radius of the Earth in meters
    radius = 6371000.0

    # Calculate the change in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    # Calculate the distance in meters
    distance = radius * c

    # Calculate the speed in kilometers per hour
    speed = distance / time_difference * 3.6

    return speed

def parse_nmea_data(line):
    global old_coords
    global last_time
    data = line.split(',')
    logging.debug(line)
    if data[0] == '$GPGGA':
        lat_dec = convert_latitude(data[2], data[3])
        long_dec = convert_longitude(data[4], data[5])
        timestamp = nmea_to_unix(data[1])
        new_coords = [ lat_dec, long_dec ]
        speed = calculate_speed( old_coords, new_coords, timestamp-last_time)

        if lat_dec == 0 and long_dec == 0:
            return None
        curr_time = time()
        street, city = get_address(lat_dec, long_dec, curr_time)
        parsed_data = {
            'time': timestamp,
            'time_string': convert_timestamp(data[1]),
            'fix_quality': int(data[6]),
            'latitude': lat_dec,
            'longitude': long_dec,
            'satellites': int(data[7]),
            'gps': new_coords,
            'gps_accuracy': float(data[8]),
            'horizontal_dilution': float(data[8]),
            'altitude': float(data[9]),
            'altitude_units': data[10],
            'geoidal_separation': float(data[11]),
            'geoidal_separation_units': data[12],
            'age_of_differential_data': data[13],
            'differential_reference_station_id': data[14].split('*')[0],
            'speed': round(speed, 1),
            'street': street,
            'city': city,
            'room': 'car'
        }
        old_coords = [ lat_dec, long_dec ]
        last_time = timestamp
        return parsed_data
    else:
        return None

def read_nmea_data(port, baud_rate, brokers):
    clients={}
    for broker_address in brokers:
       clients[broker_address] = mqtt.Client()
       clients[broker_address].on_connect = on_connect
       clients[broker_address].on_publish = on_publish

       clients[broker_address].connect(broker_address, port=brokers[broker_address]['port'])

       clients[broker_address].loop_start()

    while True:
        with serial.Serial(port, baud_rate, timeout=1) as gps_serial:
            try:
                line = gps_serial.readline().decode('utf-8').strip()
                parsed_data = parse_nmea_data(line)
                if parsed_data:
                    json_data = json.dumps(parsed_data, indent=4)
                    logging.info(json_data)
                    for broker_address in brokers:
                        clients[broker_address].publish("gps_module/attributes", json_data)
            except serial.serialutil.SerialException as e:
                logging.info(f"{e} trying again")
            except Exception as e:
                logging.warning(f"Unhandled exception {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker")
    else:
        logging.error("Failed to connect, return code: ", rc)

def on_publish(client, userdata, mid):
    logging.info("Message published")

# Replace '/dev/ttyUSB0' with the appropriate port for your GPS module

port = '/dev/ttyUSB0'
if len(sys.argv) > 1:
    port = sys.argv[1]

# Set the baud rate based on the specifications of your GPS module
baud_rate = 9600

# Replace "192.168.7.8" with the IP address of your MQTT broker
# broker_address = "localhost"

brokers = {
  "192.168.7.8": { "port": 1883 },
  "localhost": { "port": 1883 }
}

read_nmea_data(port, baud_rate, brokers)

