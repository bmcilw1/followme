#!/bin/bash

# Configure appropiate port types
if [ -f /var/lib/cloud9/followme/configPins.sh ]; then
    source /var/lib/cloud9/followme/configPins.sh
fi

# Run specified script
if [ -f /var/lib/cloud9/followme/motorControl.py ]; then
    sudo python /var/lib/cloud9/followme/obstacleAvoidance.py
fi
