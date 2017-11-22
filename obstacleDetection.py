#!/usr/bin/env python
# Detects obstacles in path of robot
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.UART as UART
import serial
import time
import math
from time import sleep

ADC.setup()

usonic="P9_40"
irL="P9_39"
irR="P9_38"
irD="P9_37"

# Smooth readings by taking the average value of several readings
usDist = [0, 0, 0, 0, 0]
irLDist = [0, 0, 0, 0, 0]
irRDist = [0, 0, 0, 0, 0]
irDDist = [0, 0, 0, 0, 0]
i = 0;

def readUS(pin):
        usonicVal=ADC.read(usonic)
        usonicVolt=usonicVal*1.8 # Convert to voltage
        #print "The ultrasonic voltage is: ", usonicVolt
        # linear response
        distanceMetersUS = usonicVolt*8 # convert to meters via manual tuning
        return distanceMetersUS

def readIR(pin, usDist):
        irVal=ADC.read(pin)
        irVolt=irVal*1.8
        
        # Convert to meters via manual tuning
        # Prevent divide by zero error add small delta 
        distanceMetersIR = 1/(irVolt + .0000001)
        return distanceMetersIR

while(True):
        usDist[i] = readUS(usonic)
        print "There is an object ", usDist[i], "meters away US."
        
        # the avgDist to the nearest obstacle straight ahead
        avgDistUS = reduce(lambda x, y: x + y, usDist) / float(len(usDist))
        #print "There is an object ", avgDist, "meters away."
        
        irLDist[i] = readIR(irL, avgDistUS)
        print "There is an object ", irLDist[i], "meters away LIR."
        
        irRDist[i] = readIR(irR, avgDistUS)
        print "There is an object ", irRDist[i], "meters away RIR."
        
        # Will always be less than a meter
        irDDist[i] = readIR(irD, .05)
        print "There is an object ", irDDist[i], "meters away DIR."
        
        '''
        if avgDist < .1:
            print "turn"
        else:
            print "straight"
        '''
        
        i = 0 if len(usDist) else i + 1
        sleep(1)