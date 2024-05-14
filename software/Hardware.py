import os, time, Helper as h 
from Helper import pprint as print



def main(): 
    print("Henlo", "CYAN")


def hw_init():
    print("Henlo", "CYAN")

def wait_for_takeoff(d:h.Drone):
    print("Waiting for Takeoff...")
    oldacc = d.accelleration()
    while(True):
        acc = d.accelleration()        
        time.sleep(h.params['Hardware']['AccellWaitPolling'])
        oldacc = acc

def acquire_payload()-> None: 
    ##start pump for a predetermined amount of time. 
    print("...Starting payload aquisition..", "GREEN")
    time.sleep(h.parameters['Hardware']['pumpinterval'])
    print("..assuming payload aquisition finished...", "GREEN")
    ##end pump
    pass

def drop(d:h.Drone) -> None:
    if not d.active: 
        print("Can not drop payload, since a drop has already been deployed.", "RED")
        return
    #release servo pins
    return

def done()-> None:
    #set LED to symbol done.
    pass


if __name__ == "__main__": 
    hw_init()
    main() 
else: 
    hw_init()
    #module setup