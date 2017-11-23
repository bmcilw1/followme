#!/usr/bin/env python
# Detects obstacles in path of robot
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.UART as UART
import serial
import time
import math
from time import sleep

ADC.setup()

U_SONIC="P9_40"
IR_L="P9_39"
IR_R="P9_38"
IR_D="P9_37"
CLIFF_DELTA = .1
COLLISION_THRESHOLD = .1

# IR constants
IR_M = .4
IR_B = .79
IR_DELTA = 10**-6

# US constants
US_M = .142
US_B = -5.67*10**-3

# Smooth readings by taking the average value of several readings
usDist = [0, 0, 0, 0, 0, 0, 0, 0]
irLDist = [0, 0, 0, 0, 0, 0, 0, 0]
irRDist = [0, 0, 0, 0, 0, 0, 0, 0]
irDDist = [0, 0, 0, 0, 0, 0, 0, 0]
startCtr = 0
i = 0

def readUS(pin):
    usonicVal=ADC.read(pin)
    usonicVolt=usonicVal*1.8 # Convert to voltage
    # linear response
    distanceMetersUS = (usonicVolt - US_B) / US_M # convert to meters via manual tuning
    return distanceMetersUS

def readIR(pin):
    irVal=ADC.read(pin)
    irVolt=irVal*1.8 # Convert to voltage
        
    # Convert to meters via manual tuning
    # Prevent divide by zero error add small delta
    # This equation only works for 1-5.5 meters distance
    distanceMetersIR = (1/(irVolt + IR_DELTA) - IR_B) / IR_M
    return distanceMetersIR
    
def avgArray(a):
    return reduce(lambda x, y: x + y, a) / float(len(a))

while(True):
    usDist[i] = readUS(U_SONIC)
    #print "There is an object ", usDist[i], "meters away US."
    
    # the avgDist to the nearest obstacle straight ahead
    avgDistUS = reduce(lambda x, y: x + y, usDist) / float(len(usDist))
    
    irLDist[i] = readIR(IR_L)

    irRDist[i] = readIR(IR_R)
    
    irDDist[i] = readIR(IR_D)
    
    # The avgDist for the old and new half of the down IR readings
    # If there is a sufficiently large gap assume cliff
    halfIrDDist = len(irDDist)/2
    avgDistDIROld = avgArray(irDDist[: halfIrDDist])
    avgDistDIRNew = avgArray(irDDist[halfIrDDist :])
    
    #print "avgDistDIROld ", avgDistDIROld
    #print "avgDistDIRNew ", avgDistDIRNew
    cliff = True if abs(avgDistDIRNew - avgDistDIROld) > CLIFF_DELTA else False
    
    print "There is an object ", avgArray(irLDist) , "meters away LIR."
    print "There is an object ", avgArray(usDist) , "meters away US."
    
    if startCtr < len(usDist) - 1:
        print "startup"
    elif avgDistUS < COLLISION_THRESHOLD:
        print "stop"
    elif cliff:
        print "cliff"
        startCtr = 0
    else:
        print "go"
        
    i = 0 if i == len(usDist) - 1 else i + 1
    startCtr = startCtr if startCtr == len(usDist) - 1 else startCtr + 1
    sleep(.1)
