#!/bin/bash

# Update packages
sudo apt-get update

# Get pyserial plugin
sudo apt-get install python-serial

# Set up service script to begin on restart
if [ ! -f /etc/systemd/senior_design.service ]; then
	ln /var/lib/cloud9/followme/senior_design.service /etc/systemd/senior_design.service
fi

sudo systemctl enable senior_design.service
sudo systemctl start senior_design.service
