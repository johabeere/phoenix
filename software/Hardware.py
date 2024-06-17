import os, time, sys, signal, Helper as h 
import RPi.GPIO as GPIO
import smbus
from Helper import pprint as print
from MPU6000 import MPU6000 as MPU
from typing import Literal

#loaded water value in ml. 
water:float=0.0
##MPU6000 object definiton. 
gyro:MPU = None
##PWM Objects
R = GPIO.PWM(h.pins['ledr'], 50)
G = GPIO.PWM(h.pins['ledg'], 50)
B = GPIO.PWM(h.pins['ledb'], 50)
S1 = GPIO.PWM(h.pins['Servo1'], 50)
S2 = GPIO.PWM(h.pins['Servo2'], 50)

def main(): 
    print("Henlo", h.LogLevel.INFO, "CYAN")

def hw_init():
    #define pinformat. 
    GPIO.setmode(GPIO.BCM)
    #define Inputs. 
    for i in (h.pins['Flow_rate_sensor'], h.pins['Pushbutton1'], h.pins['Pushbutton2']): 
        GPIO.setup(i, GPIO.IN)
    #define Outputs. 
    for o in (h.pins['Servo1'], h.pins['Servo2'], h.pins['LED_R'], h.pins['LED_G'], h.pins['LED_B']): 
        GPIO.setup(o, GPIO.OUT)
    GPIO.add_event_detect(h.pins['Pushbutton1'], GPIO.FALLING, callback=button_callback, bouncetime=300)
    #greet user. 
    print("Henlo",h.LogLevel.INFO,  "CYAN")
    #start PWM interfaces.    
    gyro = MPU()
    R.start(0) #argument is dutycycle in %
    G.start(0)
    B.start(0)
    S1.start(0)
    S2.start(0)

def hw_cleanup(): 
    #stop PWM interfaces. 
    R.stop()
    G.stop()
    B.stop()
    S1.stop()
    S2.stop()
    #cleanup pins. 
    GPIO.cleanup() 

def wait_for_takeoff():
    print("Waiting for Takeoff...", h.LogLevel.INFO)
    acc = gyro.read_accl()['z']
    while(acc<h.parameters['Hardware']['zaccell']):        
        acc = gyro.read_accl()['z']
        time.sleep(h.parameters['Hardware']['AccellWaitPolling'])
        print("Still waiting...", h.LogLevel.INFO)
    return

def acquire_payload()-> None: 
    ##start pump for a predetermined amount of time. 
    print("...Starting payload aquisition..", h.LogLevel.INFO, "GREEN")
    GPIO.output(h.pins['pump'], 1)
    time.sleep(h.parameters['Hardware']['pumpinterval'])
    GPIO.output(h.pins['pump'], 0)
    print("..assuming payload aquisition finished...",h.LogLevel.INFO, "GREEN")
    ##end pump
    pass

def drop(d:h.Drone) -> None:
    """
    Changes the servo position to drop the payload. 
    """
    if not d.active: 
        print("Can not drop payload, since a drop has already been deployed.", h.LogLevel.FAILURE, "RED")
        return
    #release servo pins
    d.active = False
    print("!!!!!Dropping payload!!!!!", h.LogLevel.INFO, "GREEN")
    set_servo_percent(h.parameters['Hardware']['drop_servo'], h.parameters['Hardware']['drop_position'])
    return

def done()-> None:
    """
    set LED to symbol done.
    """
    set_LED(0x00FF00)#Green. 
    pass

def set_servo_percent(servo:Literal[1, 2], dc:float)-> None:
    """
    Change dutycycle of one of the two servos. 
    """
    if not 0.0<dc<1.0: 
        print(f"Servo value needs to be between 0 and 1, not {dc}.", h.LogLevel.ERROR)
        return
    eval("Servo"+servo+".ChangeDutyCycle("+dc+")")
    return

def watersensor():
    """
    wait on mech team if is needed. 
    """
    return None

def get_buttons()-> list: 
    """
    returns a list of the two buttonstates. 
    """
    
    return [GPIO.input(h.pins['Pushbutton1']), GPIO.input(h.pins['Pushbutton2'])]

def set_LED(color:int):
    """
    Simple function to adress an RGB LED via PWM. accepts the classic hex color scheme: 0xRRGGBB. 
    
    """
    if color>0xFFFFFF: 
        print(f"Not a valid color: {hex(color)}", h.LogLevel.ERROR)
        return
    r, g, b = bytes(color)
    print(f"Color is: {list(r, g, b)}", h.LogLevel.INFO)
    R.ChangeDutyCycle(float((r/255)*100))
    G.ChangeDutyCycle(float((g/255)*100))
    B.ChangeDutyCycle(float((b/255)*100))
    return

def button_callback(channel):
    print("Button pressed! Restarting script...", h.LogLevel.FAILURE, "RED")
    set_LED(0xFF0000)#RED
    time.sleep(1)
    # Restart the script
    os.execv(sys.executable, ['python'] + sys.argv)


def get_angle()-> float:
    """
    Gets uptilt angle from Gyroscope. 


    
    """
    
    #TODO check which axis is front!!
    #TODO check return datatype!!
    return gyro.read_gyro()['x']

if __name__ == "__main__": 
    hw_init()
    main()
    hw_cleanup()
else: 
    hw_init()
    #module setup