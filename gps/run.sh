#!/bin/bash

ttydev=$($PWD/detect_tty.sh)

# bash $PWD/create_tracker.sh
python3 read_gps.py $ttydev
