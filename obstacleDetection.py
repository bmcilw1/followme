#!/usr/bin/env python
# Detects obstacles in path of robot
import Adafruit_BBIO.ADC as ADC
ADC.setup()

from time import sleep
usonic="P9_40"

while(1):
        usonicVal=ADC.read(usonic)
        usonicVolt=usonicVal*1.8 # Convert to voltage
        print "The ultrasonic voltage is: ", usonicVolt
        distanceInches = usonicVolt / 0.0075 # convert to inches via manual tuning
        print "There is an object ", distanceInches, "inches away."
        sleep(.5)