#!/bin/env python3

import logging
import os
import subprocess

from flask import Flask, render_template

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')
if 'DEBUG' in os.environ:
    logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():
    supervisor_status = check_supervisor_status()
    return render_template('index.html', supervisor_status=supervisor_status)

@app.route('/start_supervisor')
def start_supervisor():
    subprocess.run(['sudo', 'service', 'supervisor', 'start'])
    return "Supervisor started!"

@app.route('/stop_supervisor')
def stop_supervisor():
    subprocess.run(['sudo', 'service', 'supervisor', 'stop'])
    return "Supervisor stopped!"

@app.route('/restart_supervisor')
def restart_supervisor():
    subprocess.run(['sudo', 'service', 'supervisor', 'restart'])
    return "Supervisor restarted!"

def check_supervisor_status():
    result = subprocess.run(['sudo', 'service', 'supervisor', 'status'], capture_output=True, text=True)
    output = result.stdout.lower()
    print(output)
    if 'running' in output:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(host="0.0.0.0")