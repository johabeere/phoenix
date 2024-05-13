from colorama import Fore, Back, Style
from pyapriltags import Detector
import yaml, os, sys, inspect
import numpy as np
global paramters

def get_params():
    with open( './config.yaml', 'r') as stream:
        p= yaml.safe_load(stream)
    return p 

def pprint(text:str, Color:str = "WHITE", **kwargs):
    frm = inspect.stack()[1]
    parent = inspect.getmodule(frm[0]).__name__
    try: 
        #Try to get color from parent script 
        c = str(parameters[f'{parent}']['logcolor'])
    except Exception as e:
        print("COLOR EXCEPTION: invalid log color string." + str(e))
        c = "WHITE"
    print(eval('Fore.'+ c) + f"{str(parent)}:" + eval('Fore.'+Color) + str(text) + Style.RESET_ALL, **kwargs)

def patch():
    return parameters['Camera']['libcameraloglevel']

class Drone

    tilt:float
    speed:float

    def __init__(self, i1, i2):
        self.tilt = get_angle(i1)
        self.speed = get_speed(i1, i2)

    def get_speed(i1, i2):
        # TODO: write method
        pass

    def get_angle(i1):
        # TODO: write method
        pass


class Fire:
    
    active:bool
    height:float
    time_to_drop:float
    current_target:list

    def __init__(self, d:Detector):
        self.center = d.center
        self.corners = d.corners
        active = True
    
    def __str__(self):
        return f"fire with image center at: {self.center}" 

    def get_height(): 
        #* get height estimate from camera area
        return 0     


def arc_calc(f:Fire):
    if f.height == 0: f.get_height()    # make sure height is set.
    a:float
    g:float = 9.81
    v:float = 0
    f.current_target = [np.sqrt(2*f.height*v^2/g), 0]
    f.time_to_drop = 0
    return f 

if __name__ == "__main__": 
    print("henlo") ##never called.
else: 
    global parameters 
    parameters = get_params()