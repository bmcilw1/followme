#!/usr/bin/env python
# Detects obstacles in path of robot
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.UART as UART
import serial
import time
import math
from time import sleep

ADC.setup()

# Sensor pins
U_SONIC="P9_40"
IR_L="P9_39"
IR_R="P9_38"
IR_D="P9_37"

# Sensor distance thresholds
CLIFF_DELTA = .5 # Minimum sensitivity to cliffs
COLLISION_THRESHOLD = .4 # in meters
TIME_PER_CYCLE = .0001 # in seconds
#TIME_PER_CYCLE = 1
TOP_SPEED = 500 # in micro-seconds (PWM signal to send to servos)

# IR sensor constants
IR_M = .4
IR_B = .79
IR_DELTA = 10**-6

# Motor controller UART
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

def readUS(pin):
    usonicVal=ADC.read(pin)
    usonicVolt=usonicVal*1.8 # Convert to voltage
    
    # Convert to meters via manual tuning
    # Mostly linear response
    distanceMetersUS = usonicVolt*6 # convert to meters via manual tuning
    return distanceMetersUS

def readIR(pin, usDist):
    irVal=ADC.read(pin)
    irVolt=irVal*1.8 # Convert to voltage
    
    # Convert to meters via manual tuning
    # Prevent divide by zero error add small delta
    # This equation only works for 1-5.5 meters distance
    distanceMetersIR = (1/(irVolt + IR_DELTA) - IR_B) / IR_M
    return distanceMetersIR
    
def avgArray(a):
    return reduce(lambda x, y: x + y, a) / float(len(a))
        
# Smooth readings by taking the average value of several readings
# Circular arrays to implement averaging
usDist = [0, 0, 0, 0]
irLDist = [0, 0, 0, 0]
irRDist = [0, 0, 0, 0]
irDDist = [0, 0, 0, 0]
startCtr = 0
i = 0

while(True):
    usDist[i] = readUS(U_SONIC)
    #print "There is an object ", usDist[i], "meters away US."
    
    # the avgDist to the nearest obstacle straight ahead
    avgDistUS = avgArray(usDist)
    #print "There is an object ", avgDist, "meters away."
    
    irLDist[i] = readIR(IR_L, avgDistUS)
    #print "There is an object ", irLDist[i], "meters away LIR."
    irRDist[i] = readIR(IR_R, avgDistUS)
    #print "There is an object ", irRDist[i], "meters away RIR."
    
    # Will generally be less than a meter
    irDDist[i] = readIR(IR_D, .05)
    #print "There is an object ", irDDist[i], "meters away DIR."
    
    # The avgDist for the old and new half of the down IR readings
    # If there is a sufficiently large gap assume cliff
    halfIrDDist = len(irDDist)/2
    avgDistDIROld = avgArray(irDDist[: halfIrDDist])
    avgDistDIRNew = avgArray(irDDist[halfIrDDist :])
    
    cliff = True if abs(avgDistDIRNew - avgDistDIROld) > CLIFF_DELTA else False
    
    if startCtr < len(usDist) - 1:
        # Wait until sufficent samples are taken
        DriveStraight(0)
    elif cliff:
        # Avoid cliff: back up and turn around
        # Check for this FIRST
        DriveStraight(-100)
        sleep(1)
        TurnInPlace(-180)
        startCtr = 0
    elif avgDistUS < COLLISION_THRESHOLD:
        # Avoid standing obstacle: choose the right
        TurnInPlace(45)
        startCtr = 0
    else:
        # We're free to go
        DriveStraight(TOP_SPEED)
    
    # Increment counters
    i = 0 if i == len(usDist) - 1 else i + 1
    startCtr = startCtr if startCtr == len(usDist) - 1 else startCtr + 1
    
    # Delay until next cycle
    # this should be FAST to react to cliffs
    sleep(TIME_PER_CYCLE)

# Stop
DriveStraight(0)
ser.close()
print "Commands send. Connection closed."
