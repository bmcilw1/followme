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

UART.setup("UART1") # P9_24

# Motor contoller constants
START_SIG = "\xAA"
CHAN0 = "\x00"
CHAN1 = "\x01"
NUM_OF_TARGETS = "\x02"

# Account for slight differences of motor center points
CENTER0 = 1479.25
CENTER_DIFF = 2
CENTER1 = CENTER0-CENTER_DIFF

ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600)
ser.close()
ser.open()

if ser.isOpen():
	print "Sending commands..."

def SetTarget(channel, target, device_id="\x0C", cmd = "\x04"):
    # Protocol setup
    ser.write(START_SIG)
    ser.write(device_id)
    ser.write(cmd)
    ser.write(channel)
    ser.write(target)

def SetMultiTarget(target0, target1, device_id="\x0C", cmd = "\x1F"):
    # Protocol setup
    ser.write(START_SIG)
    ser.write(device_id)
    ser.write(cmd)
    ser.write(NUM_OF_TARGETS)
    ser.write(CHAN0)
    ser.write(target0)
    ser.write(target1)


def DriveStraight(speed):
    # Use different center points for driving straight
    # Due to physical differences in motors - center points are not exactly
    # the same.
    target0 = CENTER0 + speed
    target0 = int(target0 * 4) # convert to quarter micro-seconds
    target0= ''.join([chr(target0 & 0x7F), chr((target0 >> 7) & 0x7F)])
    
    target1 = CENTER1 - speed
    target1 = int(target1 * 4) # convert to quarter micro-seconds
    target1= ''.join([chr(target1 & 0x7F), chr((target1 >> 7) & 0x7F)])
    
    SetMultiTarget(target0, target1)
    
def TurnInPlace(degree, speed=50, sec_for_90_degree=2.9):
    # speed=100, sec_for_90_degree=1.4
    # Use the same center point for turning in place
    target0 = CENTER0 + speed if degree >= 0 else CENTER0 - speed
    target0 = int(target0 * 4) # convert to quarter micro-seconds
    target0= ''.join([chr(target0 & 0x7F), chr((target0 >> 7) & 0x7F)])
    
    target1 = CENTER0 + speed if degree >=0 else CENTER1 - speed
    target1 = int(target1 * 4) # convert to quarter micro-seconds
    target1= ''.join([chr(target1 & 0x7F), chr((target1 >> 7) & 0x7F)])
    
    SetMultiTarget(target0, target1)
    time.sleep(abs(degree)/90.0*sec_for_90_degree)
    DriveStraight(0)

# Smooth readings by taking the average value of several readings
usDist = [0, 0, 0, 0, 0]
irLDist = [0, 0, 0, 0, 0]
i = 0;

while(True):
        usonicVal=ADC.read(usonic)
        usonicVolt=usonicVal*1.8 # Convert to voltage
        #print "The ultrasonic voltage is: ", usonicVolt
        #distanceInches = usonicVolt / 0.0075 # convert to inches via manual tuning
        # linear response
        distanceMetersUS = usonicVolt*8 # convert to meters via manual tuning
        usDist[i] = distanceMetersUS
        #print "There is an object ", distanceMetersUS, "meters away US."
        
        irLVal=ADC.read(irL)
        irLVolt=irLVal*1.8
        
        #print "The left IR voltage is: ", irLVolt
        # TODO: find formula for non-linear response
        distanceMetersIRL = 1/irLVolt # convert to meters via manual tuning
        irLDist[i] = distanceMetersIRL
        #print "There is an object ", distanceMetersIRL, "meters away LIR."
        
        # the avgDist to the nearest obstacle straight ahead
        avgDist = reduce(lambda x, y: x + y, usDist) / float(len(usDist))
        #print "There is an object ", avgDist, "meters away."
        
        if avgDist < .1:
            TurnInPlace(45);
        else:
            DriveStraight(500);
        
        i = 0 if len(usDist) else i + 1
        sleep(.001)

# Stop
DriveStraight(0)
ser.close()
print "Commands send. Connection closed."
