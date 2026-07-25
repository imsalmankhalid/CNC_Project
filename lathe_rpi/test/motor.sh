#!/bin/bash

STEP=17
DIR=27
ENABLE=22
CHIP="gpiochip0"

# Enable motor
gpioset --chip "$CHIP" $ENABLE=1 --daemonize

direction=1
gpioset --chip "$CHIP" $DIR=$direction --daemonize

echo "Motor moving... (changing direction every 5 seconds)"

DELAY=0.00005
last_switch=$(date +%s)

while true; do
    # Generate one step pulse
    gpioset --chip "$CHIP" $STEP=1
    sleep $DELAY
    gpioset --chip "$CHIP" $STEP=0
    sleep $DELAY

    # Check if 5 seconds have elapsed
    now=$(date +%s)
    if (( now - last_switch >= 5 )); then
        if (( direction == 1 )); then
            direction=0
        else
            direction=1
        fi

        gpioset --chip "$CHIP" $DIR=$direction --daemonize
        echo "Direction: $direction"

        last_switch=$now
    fi
done