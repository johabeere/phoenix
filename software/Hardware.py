import os, time, Helper as h 
import RPi.GPIO as GPIO
from Helper import pprint as print



def main(): 
    print("Henlo", h.LogLevel.INFO, "CYAN")


def hw_init():
    print("Henlo",h.LogLevel.INFO,  "CYAN")

def wait_for_takeoff(d:h.Drone):
    print("Waiting for Takeoff...", h.LogLevel.INFO)
    oldacc = d.accelleration()
    while(True):
        acc = d.accelleration()        
        time.sleep(h.params['Hardware']['AccellWaitPolling'])
        oldacc = acc

def acquire_payload()-> None: 
    ##start pump for a predetermined amount of time. 
    print("...Starting payload aquisition..", h.LogLevel.INFO, "GREEN")
    time.sleep(h.parameters['Hardware']['pumpinterval'])
    print("..assuming payload aquisition finished...",h.LogLevel.INFO, "GREEN")
    ##end pump
    pass

def drop(d:h.Drone) -> None:
    if not d.active: 
        print("Can not drop payload, since a drop has already been deployed.", h.LogLevel.FAILURE, "RED")
        return
    #release servo pins
    return

def done()-> None:
    #set LED to symbol done.
    pass

def servo1():
    GPIO.setmode(GPIO.BCM)
    servo1PIN = 13
    GPIO.setup(servo1PIN, GPIO.OUT)
    p1 = GPIO.PWM(servo1PIN, 50)
    p1.start(7.5)
    p1.ChangeDutyCycle(7.5)
    time.sleep(1)
    p1.ChangeDutyCycle(12.5)
    time.sleep(1)
    p1.stop()
    GPIO.cleanup()

def servo2():
    GPIO.setmode(GPIO.BCM)
    servo2PIN = 12
    GPIO.setup(servo2PIN, GPIO.OUT)
    p2 = GPIO.PWM(servo2PIN, 50)
    p2.start(7.5)
    p2.ChangeDutyCycle(7.5)
    time.sleep(1)
    p2.ChangeDutyCycle(12.5)
    time.sleep(1)
    p2.stop()
    GPIO.cleanup()

def watersensor():
    waterpin = 19
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(waterpin, GPIO.IN)
    try:
        while True:
            sensor_value = GPIO.input(waterpin)
            if sensor_value == 1:
                print("Wasser erkannt!")
            else:
                print("Kein Wasser erkannt!")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

def get_angle():
    """
    Gets uptilt angle from Gyroscope. 


    
    """
    return None

if __name__ == "__main__": 
    hw_init()
    main() 
else: 
    hw_init()
    #module setup