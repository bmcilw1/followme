import Adafruit_BBIO.UART as UART
import serial
import time
import math

UART.setup("UART1") # P9_24

# Motor contoller constants
START_SIG = "\xAA"
CHAN0 = "\x00"
CHAN1 = "\x01"
NUM_OF_TARGETS = "\x02"
CENTER0 = CENTER1 = 1480

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
    target0 = CENTER0 + speed # 1485 micro seconds is median
    target0 = int(target0 * 4) # convert to quarter micro-seconds
    target0= ''.join([chr(target0 & 0x7F), chr((target0 >> 7) & 0x7F)])
    
    target1 = CENTER1 - speed # 1485 micro seconds is median
    target1 = int(target1 * 4) # convert to quarter micro-seconds
    target1= ''.join([chr(target1 & 0x7F), chr((target1 >> 7) & 0x7F)])
    
    SetMultiTarget(target0, target1)
    
def TurnInPlace(degree, speed=50):
    target0 = CENTER0 + speed if degree >= 0 else CENTER0 - speed # 1485 micro seconds is median
    target0 = int(target0 * 4) # convert to quarter micro-seconds
    target0= ''.join([chr(target0 & 0x7F), chr((target0 >> 7) & 0x7F)])
    
    target1 = CENTER1 + speed if degree >=0 else CENTER1 - speed # 1485 micro seconds is median
    target1 = int(target1 * 4) # convert to quarter micro-seconds
    target1= ''.join([chr(target1 & 0x7F), chr((target1 >> 7) & 0x7F)])
    
    SetMultiTarget(target0, target1)
    time.sleep(abs(degree)/90*3)
    DriveStraight(0)

def TestTurnInPlace():
    TurnInPlace(90)
    TurnInPlace(-90)
    TurnInPlace(45)
    TurnInPlace(-45)

def TestDriveStraight():
    DriveStraight(20)
    time.sleep(2)
    DriveStraight(500)
    time.sleep(.3)
    DriveStraight(0)
    time.sleep(.5)
    DriveStraight(-20)
    time.sleep(2)
    DriveStraight(-500)
    time.sleep(.3)
    DriveStraight(0)
    
TestTurnInPlace()
#TestDriveStraight()

ser.close()
print "Commands send. Connection closed."