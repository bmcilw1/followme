#!/usr/bin/env python
# Detects obstacles in path of robot
import Adafruit_BBIO.ADC as ADC
import math
ADC.setup()

from time import sleep
usonic="P9_40"
irL="P9_39"
irR="P"
irD="P"

while(1):
        '''
        usonicVal=ADC.read(usonic)
        usonicVolt=usonicVal*1.8 # Convert to voltage
        print "The ultrasonic voltage is: ", usonicVolt
        distanceInches = usonicVolt / 0.0075 # convert to inches via manual tuning
        print "There is an object ", distanceInches, "inches away."
        '''
        
        irLVal=ADC.read(irL)
        irLVolt=irLVal*1.8
        
        print "The left IR voltage is: ", irLVolt
        distanceInches = 1/irLVolt  # convert to inches via manual tuning
        print "There is an object ", distanceInches, "meters away."
        
        sleep(.5)