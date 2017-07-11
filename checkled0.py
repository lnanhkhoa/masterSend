print ("Program Start")
import RPi.GPIO as GPIO
import time

channels = [36, 47]

print ("Turning off LED's")
GPIO.setmode(GPIO.BCM)
GPIO.setup(channels, GPIO.OUT)
GPIO.output(channels, GPIO.LOW)
time.sleep(5)

print ("Turning on LED's")
GPIO.output(channels, GPIO.HIGH)
time.sleep(5)

GPIO.cleanup()

print ("Program End")