from colorama import Fore, Back, Style
from pyapriltags import Detector, Detection
import yaml, os, sys, inspect, time
import numpy as np
from enum import Enum, auto
import smbus, time, fnmatch

global pins
global debug 

seconds = time.time()
local_time = time.ctime(seconds)


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
    text = str(eval('Fore.'+ c) + f"{str(parent)}: \t" + eval('Fore.' + level.color)+ f"{level.name}\t"+ Style.RESET_ALL + eval('Fore.'+textcolor) + str(text) + Style.RESET_ALL)
    print(text, **kwargs)
    with open('./logs/' + local_time + '.log', 'a') as file:
        file.write(text + '\n', **kwargs)    
    return

def overwrite_yaml_attribute(linenumber:int, new_value:str):
    """
    Overwrites an existing attribute in a YAML file.

    :param attribute: The attribute to overwrite.
    :param new_value: The new value to set for the attribute.
    """
    try:
        # Read the existing YAML file
        with open("./config.yaml", 'r') as file: 
            lines = file.readlines()
        # Overwrite the attribute
        lines[linenumber] = new_value
        # Write the updated data back to the YAML file
        with open('./config.yaml', 'w') as file:
            file.writelines(lines)
        print(f"line '{linenumber}' updated successfully.")

    except Exception as e:
        print(f"Error updating line '{linenumber}': {e}")

def true_if_wait2s(oldtime): 
    return True if time.time()-oldtime>=2 else False


def shoelace_formula(vertices:list)->float:
    """
    area calculation used for height estimation in Vision.py. 
    """
    n = len(vertices)
    area:float = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    area = abs(area) / 2.0
    return area

def get_mm_per_px()-> float:
    #requires image crop of 0,0 to work properly.
    return (parameters['Camera']['physical'][1]/parameters['Camera']['resolution'][0]+parameters['Camera']['physical'][2]/parameters['Camera']['resolution'][1])/2

class Drone:
    """
    Storage and interface class for the physical drone. 
    
    """
    _angle:float
    _speed:float
    _height:float
    _active:bool
    buttons:list = [0, 0]
    def __init__(self, speed=0.0, angle=0.0, height=0.0):
        
        self._speed = speed
        self._height = height
        self._active = True
        self._angle = angle
    
    @property
    def speed(self)->float:
        return self._speed
    
    @speed.setter
    def speed(self, v:float)->None: 
        if not 0<v:#<10000: #Plausibility check. #TODO: get reasonable upper bound from testing. 
            raise ValueError(f"Drone speed can not be greater than 10000 or smaller than 0., Is {v}")    
        self._speed = v
    @property
    def angle(self)->float:
        return self._angle
    
    @angle.setter
    def angle(self, a:float)->None:
        self._angle = a
    @property 
    def active(self)-> bool:
        return self._active
    @active.setter
    def active(self, a:float)->None:
        self._active = a


    @property 
    def height(self)-> float:
        return self._height
    @height.setter
    def height(self, h:float): 
        if not 0<h<10000:
            raise ValueError("Height can not be outside 0 to 10 meters.")
        self._height=h
    

class Fire():
    """
    storage and interface class for a Fire.
    
    """
    
    center:list
    corners:list 
    active:bool
    height:float
    time_to_drop:float
    current_target:list

    def __init__(self, d:Detection):
        ##Transform to new coordinate system: Origin in middle of Frame. 
        self.center = [d.center[0]-(parameters['Camera']['resolution'][0]/2), d.center[1]-(parameters['Camera']['resolution'][1]/2), 0] 
        print(f"{self.center=}")
        self.corners = []#init empty
        for i in range(len(d.corners)): 
            self.corners.append([d.corners[i][0]-(parameters['Camera']['resolution'][0]/2), d.corners[i][1]-(parameters['Camera']['resolution'][1]/2), 0])
        self.current_target = [0, 0, 0]
        self.time_to_drop = 0
        self.active = True
    
    def __str__(self):
        return f"fire with image center at: {self.center}" 

    def arc_calc(self, vel:float, h:float) -> None: # setter method for the current_target.
        pprint(f"Got: {vel=}, {h=}", LogLevel.DEBUG)
        if h == 0: return# make sure height is set.
        g:float = 9810.0 #g in mm/s²
        self.current_target = [np.sqrt((2*h*vel*vel)/g), 0] #aim of drone if it was dropped now, in mm away from drone. 
        pprint(f"Current target would be: {self.current_target=}", LogLevel.DEBUG)
        drop_time= abs((self.center[0]*get_mm_per_px()-self.current_target[0])/vel) ##assuming linear drone motion, time to drop in x direction is t=s/v
        if not 0<drop_time<10 : 
            pprint("FAILED to calculate a realistic droptime. setting 3.5s and seeing what happens...", LogLevel.FAILURE, "RED")
            self.time_to_drop = 3.5
        else: 
            self.time_to_drop = drop_time
        pprint(f"finished arc, time to drop payload is {self.time_to_drop}.", LogLevel.INFO)
        return

if __name__ == "__main__": 
    print("henlo") ##never called.
else: 
    global parameters 
    parameters = get_params()
    pins = get_pins()
    get_debug()