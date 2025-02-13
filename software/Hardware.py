import os, time, sys, signal, Helper as h 
import RPi.GPIO as GPIO
import smbus
from Helper import pprint as print
from MPU6000 import MPU6000 as MPU
from typing import Literal

#loaded water value in ml. 
water:float=0.0

def main(): 
    print("Henlo", h.LogLevel.INFO, "CYAN")
    while True: 
        S1.ChangeDutyCycle(5)
        S2.ChangeDutyCycle(5)
        time.sleep(1)
        S1.ChangeDutyCycle(7.5)
        S2.ChangeDutyCycle(7.5)
        time.sleep(1)
        S1.ChangeDutyCycle(10)
        S2.ChangeDutyCycle(10)
        time.sleep(1)
        print("looping")

def set_killswitch(restart_callback)-> None: 
    GPIO.add_event_detect(h.pins['Pushbutton1'], GPIO.FALLING, callback=restart_callback, bouncetime=300)
    return

def hw_init()-> None:
    #define pinformat. 
    GPIO.setmode(GPIO.BCM)
    #define Inputs. 
    for i in (h.pins['Flow_rate_sensor'], h.pins['Pushbutton1'], h.pins['Pushbutton2']): 
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Pullup = 22, Pulldown = 21, off = 20
    #define Outputs. 
    for o in (h.pins['Servo1'], h.pins['Servo2'], h.pins['LED_R'], h.pins['LED_G'], h.pins['LED_B'], h.pins['pump']): 
        GPIO.setup(o, GPIO.OUT)
    global R, G, B, S1, S2
    global gyro
    #initialize Gyro. 
    gyro = MPU()
    #PWM population. 
    R = GPIO.PWM(h.pins['LED_R'], 50)
    G = GPIO.PWM(h.pins['LED_G'], 50)
    B = GPIO.PWM(h.pins['LED_B'], 50)
    S1 = GPIO.PWM(h.pins['Servo1'], 50)
    S2 = GPIO.PWM(h.pins['Servo2'], 50)
    
    #greet user. 
    print("Henlo",h.LogLevel.INFO,  "CYAN")
    #start PWM interfaces.    
    R.start(0) #argument is dutycycle in %
    G.start(0)
    B.start(0)
    S1.start(0)
    S2.start(0)
    set_camera_angle(h.parameters['Hardware']['camera_downtilt'])

def hw_cleanup():  
    #stop PWM interfaces. 
    # see https://github.com/waveform80/rpi-lgpio/issues/15
    global R, G, B, S1, S2
    R.stop()
    G.stop()
    B.stop()
    S1.stop()
    S2.stop()
    time.sleep(1)
    del R, G, B, S1, S2
    #cleanup pins. 
    time.sleep(1)
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
    set_servo_percent(1, 4.0)# move servo closed here.
    set_LED(0x98F5FF)#light blue
    ##start pump for a predetermined amount of time. 
    print("...Starting payload aquisition..", h.LogLevel.INFO, "GREEN")
    GPIO.output(h.pins['pump'], 1)
    time.sleep(h.parameters['Hardware']['pumpinterval'])
    GPIO.output(h.pins['pump'], 0)
    print("..assuming payload aquisition finished...",h.LogLevel.INFO, "GREEN")
    set_LED(0xFFFFFF)#back to white.
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

def set_mounting() -> None: 
    set_servo_percent(h.parameters['Hardware']['drop_servo'], h.parameters['Hardware']['mounting_position'])
    return

def done()-> None:
    """
    set LED to symbol done.
    """
    set_LED(0x00FF00)#Green. 
    return

def set_servo_percent(servo:Literal[1, 2], dc:float)-> None:
    """
    Change dutycycle of one of the two servos. 
    """
    if not 0<dc<100: 
        print(f"Servo value needs to be between 0% and 100%, not {dc}.", h.LogLevel.ERROR)
        return
    eval("S"+str(servo)+".ChangeDutyCycle(" + str(dc) +")")
    return

def watersensor():
    """
    wait on mech team if is needed. 
    """
    return None

def set_camera_angle(angle:float) -> None:
    if not 0<angle<90: 
        print(f"Systen does not support an angle outside of 0 to 90°, was given: {angle=}", h.LogLevel.INFO)
        return
    set_servo_percent(h.parameters['Hardware']['cam_servo'], h.parameters['Hardware']['camservo_angles'][0]+((h.parameters['Hardware']['camservo_angles'][0]-h.parameters['Hardware']['camservo_angles'][1])/90)*angle)


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
    r = ((color>>16) & 0xFF)^0xFF
    g = ((color>>8) & 0xFF)^0xFF
    b = (color & 0xFF)^0xFF
    print(f"Color is: {list([r, g, b])}", h.LogLevel.DEBUG)
    R.ChangeDutyCycle(float((r/255)*100))
    G.ChangeDutyCycle(float((g/255)*100))
    B.ChangeDutyCycle(float((b/255)*100))
    return

def get_angle()-> float:
    """
    Gets downtilt angle from Gyroscope. 
    """
    
    #TODO check which axis is front!!
    #TODO check return datatype!!
    return gyro.read_gyro().get('x')

if __name__ == "__main__": 
    hw_init()
    main()
    hw_cleanup()
else: 
    hw_init()
    #module setup