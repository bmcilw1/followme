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

def TestTurnInPlace():
    TurnInPlace(90)
    time.sleep(.1)
    TurnInPlace(-90)
    #TurnInPlace(45)

def Test360():
    TurnInPlace(-360)

def MiniTestDriveStraight():
    DriveStraight(40)
    time.sleep(4)
    DriveStraight(-40)
    time.sleep(4)
    DriveStraight(0)

def TestDriveStraight():
    DriveStraight(20)
    time.sleep(3)
    DriveStraight(500)
    time.sleep(1.25)
    DriveStraight(0)
    time.sleep(.2)
    DriveStraight(-20)
    time.sleep(3)
    DriveStraight(-500)
    time.sleep(1.25)
    DriveStraight(0)

def TestSquare():
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(90)
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(90)
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(90)
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(90)

def TestTriangle():
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(135)
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(135)
    DriveStraight(100)
    time.sleep(3)
    TurnInPlace(135)
    DriveStraight(0)
    
#TestTriangle()
#TestSquare()
#TestTurnInPlace()
TestDriveStraight()
#Test360()
#MiniTestDriveStraight()

# Stop
DriveStraight(0)
ser.close()
print "Commands send. Connection closed."