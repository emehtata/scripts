# GPS tracker

## Files

    gps2mqtt.py - Read data from gpsd and send it to MQTT broker
    settings.py - Modify your MQTT broker settings and adjust THRESHOLD values

    requirements.txt - python modules required to run script

    create_tracker.sh - Helper script to create device_tracker in Home Assistant

## Requirements

`gpsd` must be installed and able to produce GPS data

Install required modules:

    pip install -r requirements.txt

