from colorama import Fore, Back, Style
from pyapriltags import Detector
import yaml, os, sys, inspect
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

class Fire:
    
    active:bool
    
    def __init__(self, d:Detector):
        self.center = d.center
        self.corners = d.corners
        active = True
    
    def __str__(self):
        return f"fire with image center at: {self.center}" 

if __name__ == "__main__": 
    print("henlo") ##never called.
else: 
    global parameters 
    parameters = get_params()