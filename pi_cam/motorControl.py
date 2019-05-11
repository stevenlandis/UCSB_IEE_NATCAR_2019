import serial
from time import sleep
import os
import sys

dirs = os.listdir('/dev')
port = None
if 'ttyACM0' in dirs:
    port = '/dev/ttyACM0'
elif 'ttyACM1' in dirs:
    port = '/dev/ttyACM1'
else:
    print("Error: Unable to connect to motor arduino")
    raise 1
    
ser = serial.Serial(port)

# int between 0 and 255
def speed(s):
    s = max(0,min(255,s))
    ser.write(bytearray([round(s)]))

