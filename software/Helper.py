from colorama import Fore, Back, Style
from pyapriltags import Detector
import yaml, os, sys, inspect, time
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

def overwrite_yaml_attribute(attribute, new_value):
    """
    Overwrites an existing attribute in a YAML file.

    :param attribute: The attribute to overwrite.
    :param new_value: The new value to set for the attribute.
    """
    try:
        # Read the existing YAML file
        with open('./config.yaml', 'r') as file:
            data = yaml.safe_load(file)

        # Split the attribute to handle nested attributes
        keys = attribute.split('.')
        d = data
        for key in keys[:-1]:
            d = d[key]

        # Overwrite the attribute
        d[keys[-1]] = new_value

        # Write the updated data back to the YAML file
        with open('./config.yaml', 'w') as file:
            yaml.safe_dump(data, file)

        print(f"Attribute '{attribute}' updated successfully.")

    except Exception as e:
        print(f"Error updating attribute '{attribute}': {e}")

def true_if_wait2s(oldtime): 
    return True if time.time()-oldtime>=2 else False


def shoelace_formula(vertices:list)->float:
    n = len(vertices)
    area:float = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    area = abs(area) / 2.0
    return area



class Drone:

    _angle:float
    _speed:float
    _height:float
    _active:bool
    
    def __init__(self, speed=0.0, angle=0.0, height=0.0):
        
        self._speed = speed
        self._height = height
        self._active = True
        self._angle = angle
    
    @property
    def speed(self)->float:
        return self.speed
    
    @speed.setter
    def speed(self, v:float)->None: 
        if not 0<v<100: #Plausibility check.
            raise ValueError("Drone speed can not be greater than 100 or smaller than 0.")    
        self._speed = v
    @property
    def angle(self)->float:
        return self._angle
    
    @angle.setter
    def angle(self, a:float)->None:
        self._angle = a
    
    @property 
    def height(self)-> float:
        return self._height
    @height.setter
    def height(self, h:float): 
        if not 0<h<10:
            raise ValueError("Height can not be outside 0 to 10 meters.")
        self._height=height
    

class Fire:
    center:list
    corners:list 
    active:bool
    height:float
    time_to_drop:float
    current_target:list

    def __init__(self, d:Detector):
        ##Transform to new coordinate system: Origin in middle of Frame. 
        self.center = [d.center[0]-960, d.center[1]-540, 0] 
        for i in enumerate(d.corners): 
            self.corners[i]=[d.corners[i][0]-960, d.corners[i][1]-540, 0]
        self.current_target = [0, 0, 0]
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
    overwrite_yaml_attribute('Helper.Test', "Boo")
else: 
    global parameters 
    parameters = get_params()
    pins = get_pins()
    get_debug()