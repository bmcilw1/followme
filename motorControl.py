import Adafruit_BBIO.UART as UART
import serial
 
UART.setup("UART1") # P9_24

ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600)
ser.close()
ser.open()

if ser.isOpen():
	print "Sending commands..."
	
#ser.write('AA0C0400701F'.decode('hex')) # Alternate method??
ser.write("\xAA") # Start Byte
ser.write("\x0C") # Device ID = 12
ser.write("\x04") # Command = Set Target
ser.write("\x00") # Channel = 0
ser.write("\x10") # Target position = 1000 us (typical minimum for servos)
ser.write("\x1F")

ser.close()
print "Commands send. Connection closed."