# Constants
SPEED_THRESHOLD = 3 # km/h
DEGREE_THRESHOLD = 30  # Minimum bearing change (degrees)
TIME_THRESHOLD = 30  # Minimum time threshold (seconds)

# MQTT broker details
_brokers = [
    {'host': '192.168.7.8', 'port': 1883 },
    {'host': 'localhost', 'port': 1883 }
]
_mqtt_topic = 'gps_module/attributes'

