import Camera as c, Vision as v, Helper as h, Hardware as hw
from Helper import Fire, Drone, pprint as print
from MPU6000 import MPU6000 as MPU
import os, sys, time, threading

greetstring = "\n\
                     ++++++=-------                     \n\
                *##+++++++++----------..                \n\
               ####++++++++++=---------....             \n\
           -   *####+++++++++++----------.....          \n\
           -    #####+++++++++++++---------:....        \n\
           --+    ####*++++++++++++++---------....      \n\
     **    -=--     #####+++++               ---...     \n\
    **#     =====      *######++          -    ---..    \n\
   *####     =======       #######            -----..   \n\
  #######      =========-     ###   *       =--------.  \n\
   ########      +==========   *#   ##     ++++-------. \n\
    #########*          ======      *#*    ++++++------ \n\
#    *###########*            =-     **#    +++++++-----\n\
##      ###################*    =     =##*   +++++++----\n\
####       ####################       +=###   #++++++---\n\
######          **####*        #       ==##    ##+++++--\n\
  ########                             ===##    ##+++++-\n\
    ###########*#    #*#####           ===#*    ###++++=\n\
      ###################             ====#     ####+++ \n\
            *######*                 =+++#      *###+++ \n\
                                    ++++#    *  *###*+  \n\
                                 *+++++    *#   *###*   \n\
               ###########**********      *#    ####    \n\
             ##############***         *###     ###     \n\
           *##                      #####      ##       \n\
                       ###       ######       ##        \n\
                  #####       #######        #          \n\
                ######      #######                     \n\
                ####       ######                       \n\
                          ######                        \n\
"

def main(): 
    f:Fire
    d:Drone = Drone()
    if h.parameters['Main']['coolmode']:
        print(greetstring, h.LogLevel.INFO, "RED")
    else: 
        print("Hello World", h.LogLevel.INFO, "MAGENTA")
    polling() # function that calls itself repeatedly until stopped.  
    print(f"Average speed is: {v.get_speed(2)}")
    hw.servo1()
    ##Load water
    hw.acquire_payload()
    ##in-air loop: 
    while True: 
        f = find_fire()
        if f!=None and v.is_in_center(f): 
            print("Fire was found and centered.", h.LogLevel.INFO, "MAGENTA")
            print(f"center at {f.center}", h.LogLevel.INFO)
            break
            
            ##Found Fire, proceeding 
            ##check if extinguishable
        else: 
            time.sleep(h.parameters['Main']['fire_polling'])
            continue
            ##no fire found    
    #extinguish: 
    extinguish(d, f)
    hw.done()
    time.sleep(h.parameters['Main']['afterrun_time'])
    clean_exit()

def polling(d:Drone, f:Fire)-> None: 
    d.speed = v.get_speed(3) ##set Drone speed. 
    d.angle = hw.get_angle() ##set Drone angle. 

    if f is not None:
        ## Fire found.  
        f = find_fire() ##update Apriltag position, regenerate fire object.  
        d.height = v.get_height()##set Drone height. (requires visible Apriltag.) 
    
    threading.Timer(h.parameters['Main']['polling_timer'], polling()).start()



def find_fire()-> Fire:
    arraypos=[-1, -1]
    c.take_pictures(2)
    read_Tags= v.look_for_tag("./captures", ["capture0.jpg", "capture1.jpg", "test_img.jpg"])
    for i in range(len(read_Tags)): 
        for j in range(len(read_Tags[i])):
            if(read_Tags[i][j].tag_id==h.parameters['Vision']['tag_to_search_for']):
                #print(f"Found a fire with tag ID: {read_Tags[i][j].tag_id} with coordinates: ({read_Tags[i][j].center[0]},{read_Tags[i][j].center[1]})", "GREEN") 
                arraypos = [i,j]
                return Fire(read_Tags[arraypos[0]][arraypos[1]])
    return None

def extinguish(d:Drone, f:Fire) -> None:
    ##start rapidly polling for drop time detection. 
    ##we can already assume that a fire is present and in a theoretically droppable path. 
    while True: 
        f.arc_calc(d.get_speed('not implemented', 'yet'), d.get_height())
        if(abs(f.current_target[0]- f.center[0])<h.parameters['Vision']['target_threshold']*1920):
            hw.drop()
            break
        else: 
            continue


def clean_exit(): 
    print("made it to EoP, shutting down gracefully..", h.LogLevel.INFO)
    c.camera_cleanup()
    exit()

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt: 
        print("cleaning up and exiting....", h.LogLevel.INFO)
        c.camera_cleanup()
        exit()