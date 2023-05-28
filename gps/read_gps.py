import serial
import json
import paho.mqtt.client as mqtt
from datetime import datetime

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

def parse_nmea_data(line):
    data = line.split(',')

    if data[0] == '$GPRMC':
        parsed_data = {
            'time': convert_timestamp(data[1]),
            'latitude': convert_latitude(data[3], data[4]),
            'longitude': convert_longitude(data[5], data[6]),
            'speed': float(data[7]),  # Speed in knots
        }
        return parsed_data

    if data[0] == '$GPGGA':
        parsed_data = {
            'time': float(data[1]),
            'time_string': convert_timestamp(data[1]),
            'fix_quality': data[6],
            'latitude': convert_latitude(data[2], data[3]),
            'longitude': convert_longitude(data[4], data[5]),
            'satellites': data[7],
            'gps': [
                 convert_latitude(data[2], data[3]),
                 convert_longitude(data[4], data[5])
            ],
            'gps_accuracy': float(data[8]),
            'horizontal_dilution': data[8],
            'altitude': float(data[9]),
            'altitude_units': data[10],
            'geoidal_separation': float(data[11]),
            'geoidal_separation_units': data[12],
            'age_of_differential_data': data[13],
            'differential_reference_station_id': data[14].split('*')[0]
        }
        return parsed_data
    else:
        return None

def read_nmea_data(port, baud_rate, broker_address):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(broker_address)
    client.loop_start()

    while True:
        with serial.Serial(port, baud_rate, timeout=1) as gps_serial:
            try:
                line = gps_serial.readline().decode('utf-8').strip()
                parsed_data = parse_nmea_data(line)
                if parsed_data:
                    json_data = json.dumps(parsed_data, indent=4)
                    print(json_data)
                    client.publish("gps_module/attributes", json_data)
            except Exception as e:
                print(f"{e} trying again")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
    else:
        print("Failed to connect, return code: ", rc)

def on_publish(client, userdata, mid):
    print("Message published")

# Replace '/dev/ttyUSB0' with the appropriate port for your GPS module
port = '/dev/ttyUSB3'

# Set the baud rate based on the specifications of your GPS module
baud_rate = 9600

# Replace "192.168.7.8" with the IP address of your MQTT broker
broker_address = "192.168.7.8"

read_nmea_data(port, baud_rate, broker_address)

