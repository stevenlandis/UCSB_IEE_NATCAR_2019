import RPi.GPIO as GPIO
from time import sleep
import math

minR = 70.25/2
carL = 10.25
maxA = math.atan2(carL, minR)
loPWM = 9.4
hiPWM = 15.0
# mid = 12.3
halfPWM = (hiPWM-loPWM)/2
midPWM = (loPWM+hiPWM)/2
pwm = None

def init():
    global pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    pwm = GPIO.PWM(18, 100)
    pwm.start(5)

# amount in [-1, 1]
def turn(amount):
    x = midPWM + halfPWM*amount
    # print(x)
    pwm.ChangeDutyCycle(x)

def getTurn(c):
    ang = math.atan(carL/c)
    return ang/maxA

# init()
# pwm.ChangeDutyCycle(hiPWM)
# while True: sleep(1)
# pwm.ChangeDutyCycle(loPWM)
# sleep(1)
# pwm.ChangeDutyCycle(hiPWM)
# sleep(1)
# pwm.ChangeDutyCycle(loPWM)
# sleep(1)
# pwm.ChangeDutyCycle(hiPWM)
# sleep(1)

# sleep(5);
