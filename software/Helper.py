from colorama import Fore, Back, Style
from pyapriltags import Detector
import yaml, os, sys, inspect
import numpy as np
from enum import Enum, auto

global pins
global debug 



class LogLevel(Enum): 
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FAILURE = 4
    def __init__(self, _): 
        color_mapping = {
            'DEBUG': 'WHITE', 
            'INFO': 'WHITE', 
            'WARNING': "YELLOW", 
            'ERROR': "RED", 
            'FAILURE': "RED"
        }
        self.color = color_mapping[self.name]
    def __int__(self): 
        return self.value
    def __str__(self): 
        return self.name
    
def get_params():
    with open( './config.yaml', 'r') as stream:
        p= yaml.safe_load(stream)
    return p 

def get_pins():
    with open( './pins.yaml', 'r') as stream:
        p= yaml.safe_load(stream)
    return p

def get_debug(): 
    global debug
    debug = parameters['User']['debug']


def pprint(text:str, level:LogLevel=LogLevel.INFO, textcolor:str="WHITE",  **kwargs):
        
    frm = inspect.stack()[1]
    parent = inspect.getmodule(frm[0]).__name__
    try: 
        #Try to get color from parent script 
        c = str(parameters[f'{parent}']['logcolor'])
    except Exception as e:
        #Log color not found, throwing exception.
        print("COLOR EXCEPTION: invalid log color string." + str(e))
        c = "WHITE"
    if(int(level) < parameters['User']['log_level']):
        ##not printed since prority too low. 
        return
    #print(textcolor)
    #print(eval('Fore.'+str(textcolor)))
    print(eval('Fore.'+ c) + f"{str(parent)}: \t" + eval('Fore.' + level.color)+ f"{level.name}\t"+ Style.RESET_ALL + eval('Fore.'+textcolor) + str(text) + Style.RESET_ALL, **kwargs)
    return

def patch():
    return parameters['Camera']['libcameraloglevel']

class Drone:

    tilt:float
    speed:float
    height:float
    active:bool
    
    def __init__(self, i1:str, i2:str):
        self.tilt = self.get_angle(i1)
        self.speed = self.get_speed(i1, i2)
        self.height = self.get_height()
        self.active = True
    def get_speed(self, i1, i2):
        # TODO: write method
        return 0.0

    def get_angle(self, i1)->float:
        # TODO: write method
        #return parameters['Helper']
        return 0.0

    def get_height(self)-> float:
        #Todo: add openCV height detection.
        return 0.0

class Fire:
    center:list
    corners:list 
    active:bool
    height:float
    time_to_drop:float
    current_target:list

    def __init__(self, d:Detector):
        self.center = d.center
        self.corners = d.corners
        self.current_target = [0, 0]
        active = True
    
    def __str__(self):
        return f"fire with image center at: {self.center}" 
 
    def arc_calc(self, vel:float, h:float) -> None: # setter method for the current_target.
        if h == 0: return# make sure height is set.
        g:float = 9.81
        self.current_target = [np.sqrt(2*h*vel^2/g), 0]
        self.time_to_drop = 0
        return 

if __name__ == "__main__": 
    print("henlo") ##never called.
else: 
    global parameters 
    parameters = get_params()
    pins = get_pins()
    get_debug()