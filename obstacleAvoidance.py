#!/usr/bin/env python
# An implementation of obstacle avoidance
# This system uses the following sensors
# Forward facing:
#   - Left IR (IR_L)
#   - Right IR (IR_R)
#   - Center Ultrasonic (U_SONIC)
# Downward facing, suspended ahead of robot
#   - Down IR (IR_D)
#
# Senior design LSU EE/ECE Fall 2017
# Author: Brian McIlwain, brianwmcilwain@gmail.com
# Group Members: Alex Watson, Andre Nguyen, Raymond Hinchee, Brian McIlwain

import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.UART as UART
import serial
import time
import math
from time import sleep
from collections import deque

################################################################################
# Tunable parametes

# Sensor distance thresholds
COLLISION_THRESHOLD = .8 # smaller: .5 # in meters
TIME_PER_CYCLE = 10**-3 # debugging: .5 # in seconds
TOP_SPEED = 500 # in micro-seconds (PWM signal to send to servos)
CLIFF_DELTA = .5 # Minimum sensitivity to declare a cliff
DEGREES_TURN_COLLISION_AVOIDANCE = 22.5 # Degrees to turn on obstacle < threshold

# IR sensor constants
IR_M = .4
IR_B = .79
IR_DELTA = 10**-6

# Minimum number of cycles to keep turning the same direction if not yet free
MIN_TURN_CYCLES = 16

# US sensor constants
US_M = .142
US_B = -5.67*10**-3

# Number of past samples to average per cycle
CIRCULAR_ARRAY_LENGTH = 6

# Account for slight differences of motor center points
CENTER0 = 1479.5
CENTER_DIFF = 2
CENTER1 = CENTER0-CENTER_DIFF
DEFAULT_TURN_SPEED = 100 # slower: 50
DEFAULT_SEC_FOR_90_DEGREE_TURN = 1.4 # slower: 2.9

# END Section tunable parameters
################################################################################

# Setup sensor pins
ADC.setup()
U_SONIC = "P9_40"
IR_L = "P9_39"
IR_R = "P9_38"
IR_D = "P9_37"

# Motor controller UART
UART.setup("UART1") # P9_24

# Motor contoller constants
START_SIG = "\xAA"
CHAN0 = "\x00"
CHAN1 = "\x01"
NUM_OF_TARGETS = "\x02"

ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600)
ser.close()
ser.open()

if ser.isOpen():
	print "Sending commands..."

def SetMultiTarget(target0, target1, device_id="\x0C", cmd = "\x1F"):
    # Motor UART Protocol setup dual target
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
    
def TurnInPlace(degree, speed=DEFAULT_TURN_SPEED, 
                sec_for_90_degree=DEFAULT_SEC_FOR_90_DEGREE_TURN):
    # Use the same center point for turning in place
    target0 = CENTER0 + speed if degree >= 0 else CENTER0 - speed
    target0 = int(target0 * 4) # convert to quarter micro-seconds
    target0= ''.join([chr(target0 & 0x7F), chr((target0 >> 7) & 0x7F)])
    
    target1 = CENTER0 + speed if degree >=0 else CENTER1 - speed
    target1 = int(target1 * 4) # convert to quarter micro-seconds
    target1= ''.join([chr(target1 & 0x7F), chr((target1 >> 7) & 0x7F)])
    
    SetMultiTarget(target0, target1)
    time.sleep(abs(degree)/90.0*sec_for_90_degree)

def readUS(pin):
    usonicVal=ADC.read(pin)
    usonicVolt=usonicVal*1.8 # Convert to voltage
    
    # Convert to meters via manual tuning
    # This equation works for .3 - 7.5 meters
    distanceMetersUS = (usonicVolt - US_B) / US_M
    return distanceMetersUS

def readIR(pin):
    irVal=ADC.read(pin)
    irVolt=irVal*1.8 # Convert to voltage
    
    # Prevent divide by zero error add small delta
    # This equation only works for 1-5.5 meters distance
    distanceMetersIR = (1/(irVolt + IR_DELTA) - IR_B) / IR_M
    return distanceMetersIR
    
def avgArray(a):
    return reduce(lambda x, y: x + y, a) / float(len(a))
        
# Smooth readings by taking the average value of several readings
# Circular arrays of length CIRCULAR_ARRAY_LENGTH to implement averaging
usDist = deque([0] * CIRCULAR_ARRAY_LENGTH)
irLDist = deque([0] * CIRCULAR_ARRAY_LENGTH)
irRDist = deque([0] * CIRCULAR_ARRAY_LENGTH)
irDDist = deque([0] * CIRCULAR_ARRAY_LENGTH)
startCtr = 0
i = 0
lastTurnDirection = 1
lastTurnCtr = 0

# Main loop of execution
while(True):
    # Remove oldest element from right
    usDist.pop()
    irLDist.pop()
    irRDist.pop()
    irDDist.pop()
    
    # Add new readings on left
    usDist.appendleft(readUS(U_SONIC))
    irLDist.appendleft(readIR(IR_L))
    irRDist.appendleft(readIR(IR_R))
    irDDist.appendleft(readIR(IR_D))
    
    # The avgDist for the old and new half of the down IR readings
    halfIrDDist = len(irDDist)/2
    avgDistDIROld = avgArray(list(irDDist)[: halfIrDDist])
    avgDistDIRNew = avgArray(list(irDDist)[halfIrDDist :])
    
    # If there is a sufficiently large gap assume cliff
    cliff = True if abs(avgDistDIRNew - avgDistDIROld) > CLIFF_DELTA else False
    
    # Use simple average to filter outliers
    avgUS = avgArray(usDist)
    avgirL = avgArray(irLDist)
    avgirR = avgArray(irRDist)
    nearestObject = min(avgUS, avgirL, avgirR)
    #print "object ", nearestObject, " meters away"
    
    if startCtr < len(usDist) - 1:
        # Don't go until we know the way is clear
        DriveStraight(0)
    
    elif cliff:
        # Avoid cliff: back up and turn around
        # Check for this FIRST
        DriveStraight(-100)
        sleep(1)
        TurnInPlace(-180, 100, 1.4) # Fast turn
        startCtr = 0
    
    elif nearestObject < COLLISION_THRESHOLD:
        # Avoid standing obstacle
        # If we've just turned choose the same direction
        if (lastTurnCtr > MIN_TURN_CYCLES):
            if (avgirL < avgirR):
                lastTurnDirection = 1
            else:
                lastTurnDirection = -1
            
        # Right is positive, left negative
        TurnInPlace(DEGREES_TURN_COLLISION_AVOIDANCE * lastTurnDirection)
        
        # Reset counters
        lastTurnCtr = 0
        startCtr = 0
    
    else:
        # We're free to go
        DriveStraight(TOP_SPEED)
    
    # Increment counters
    i = 0 if i == len(usDist) - 1 else i + 1
    startCtr = startCtr if startCtr == len(usDist) - 1 else startCtr + 1
    lastTurnCtr += 1
    
    # Delay until next cycle
    # this should be FAST to react to cliffs
    sleep(TIME_PER_CYCLE)