# Motion Detection with Raspberry Pi and MQTT

This project uses a Raspberry Pi connected to a motion sensor and integrates with an MQTT broker to send motion detection events. When motion is detected, the Raspberry Pi publishes the event to the MQTT topics for further processing (e.g., home automation systems).

## Features

- Detects motion using a GPIO-connected sensor on a Raspberry Pi.
- Publishes motion events and availability status to an MQTT broker.
- Handles clean shutdown and GPIO cleanup when interrupted (Ctrl+C).

## Prerequisites

Before you start, ensure you have the following:

- A Raspberry Pi (any model with GPIO support).
- A motion sensor connected to GPIO pin 11 (modifiable in the code).
- An MQTT broker running on your local network (or externally).
- Python 3 installed on your Raspberry Pi.

### Required Python Libraries

- `paho-mqtt` for MQTT client operations.
- `RPi.GPIO` for GPIO control on the Raspberry Pi.
- `logging` for logging messages.

You can install the necessary Python libraries by running:

    pip3 install paho-mqtt RPi.GPIO

## Setup

1. Clone this repository or copy the script to your Raspberry Pi.
1. Update the MQTT host IP in the script (MQTTHOST) to match your broker's IP.
1. Connect your motion sensor to GPIO pin 11, or change the pin number in the script if needed.
1. Run the script using:

    python3 pirmqtt.py

The script will start monitoring the motion sensor and will publish events to the configured MQTT topics.
MQTT Topics

- home/motion/rpi1/contact: Publishes ON when motion is detected.
- home/motion/rpi1/availability: Publishes online or offline depending on the device status.

## Handling Interruptions

The script gracefully handles shutdowns using a signal handler. Pressing Ctrl+C will:

1. Publish an offline message to the availability topic.
1. Disconnect the MQTT client.
1. Clean up the GPIO settings.

## License

This project is open-source and licensed under the MIT License.
