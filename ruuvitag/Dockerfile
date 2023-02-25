FROM python:buster

WORKDIR /usr/src/app

COPY . .

# RUN apt update && apt upgrade -y

RUN pip3 install paho-mqtt
RUN pip3 install ruuvitag-sensor

ENTRYPOINT [ "python3", "ruuvi2mqtt.py" ]
