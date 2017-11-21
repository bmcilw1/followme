#!/bin/bash

# Get pyserial plugin
sudo apt-get install python-serial

# Set up service script to begin on restart
sudo systemctl enable senior_design.service
sudo systemctl start senior_design.service
