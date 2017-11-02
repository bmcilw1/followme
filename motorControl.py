import Adafruit_BBIO.UART as UART
import serial
import time

UART.setup("UART1") # P9_24

# Motor contoller constants
START_SIG = "\xAA"
CHAN0 = "\x00"
CHAN1 = "\x01"

ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600)
ser.close()
ser.open()

if ser.isOpen():
	print "Sending commands..."

def SetTarget(channel, target, device_id="\x0C", cmd_set_target = "\x04"):
    # Protocol setup
    ser.write(START_SIG)
    ser.write(device_id)
    ser.write(cmd_set_target)
    ser.write(channel)
    ser.write(target)

def DriveStraight(speed):
    target0 = 1485 + speed # 1485 micro seconds is median
    target0 = int(target0 * 4) # convert to quarter micro-seconds
    target0= ''.join([chr(target0 & 0x7F), chr((target0 >> 7) & 0x7F)])
    SetTarget(CHAN0, target0)
    
    target1 = 1485 - speed # 1485 micro seconds is median
    target1 = int(target1 * 4) # convert to quarter micro-seconds
    target1= ''.join([chr(target1 & 0x7F), chr((target1 >> 7) & 0x7F)])
    SetTarget(CHAN1, target1)
    

DriveStraight(20)
time.sleep(2)
DriveStraight(500)
time.sleep(.3)
DriveStraight(-500)
time.sleep(.3)
DriveStraight(-20)
time.sleep(2)
DriveStraight(0)

ser.close()
print "Commands send. Connection closed."