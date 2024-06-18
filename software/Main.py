import Camera as c, Vision as v, Helper as h, Hardware as hw
from Helper import Fire, Drone, pprint as print
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
    #set the killswitch. 
    hw.set_killswitch(restart_exit)
    #Object initialization
    f:Fire = None
    d:Drone = Drone()
    #greet user. 
    hw.set_LED(0xFFFFFF)
    time.sleep(1)
    hw.set_LED(0xE2FF00)
    if h.parameters['Main']['coolmode']:
        print(greetstring, h.LogLevel.INFO, "RED")
    else: 
        print("Hello World", h.LogLevel.INFO, "MAGENTA")
    
    polling(d, f) # function that calls itself repeatedly until stopped.  
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
    polling(d,f)#make sure we have the most recent polling data.
    extinguish(d, f)
    hw.done()
    time.sleep(h.parameters['Main']['afterrun_time'])
    clean_exit()

def polling(d:Drone, f:Fire)-> None: 
    d.speed = v.get_speed(3) ##set Drone speed. 
    d.angle = hw.get_angle() ##set Drone angle. 
    d.buttons = hw.get_buttons()
    
    print(f"\n{20*'-'}\nAverage speed\t{d.speed}\nAngle is:\t{d.angle}\nbuttonstates:\t{d.buttons}\n{20*'-'}", h.LogLevel.INFO, "CYAN")
    
    if f is not None:
        ## Fire found.  
        f = find_fire() ##update Apriltag position, regenerate fire object.  
        d.height = v.get_height()##set Drone height. (requires visible Apriltag.) 
    
    threading.Timer(h.parameters['Main']['polling_timer'], polling(d, f)).start()



def find_fire()-> Fire:
    """
    Tries to find a corresponding apriltag in the image and produce a Fire Object. 
    If unsuccessfull, returns None, else a populated Fire Object. 
    """
    
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
    max_cycles = 100 #prevents endless loop
    while max_cycles>0: 
        max_cycles-=1
        print(f"{max_cycles=}")
        f.arc_calc(d.speed, d.height)
        if(abs(f.current_target[0]- f.center[0])<h.parameters['Vision']['target_threshold']*1920):
            time.sleep(f.time_to_drop)
            hw.drop()
            break
        else: 
            continue

def restart_exit(channel): 
    print("restart exit call...", h.LogLevel.FAILURE)
    c.camera_cleanup()
    hw.hw_cleanup()
    exit(3)

def clean_exit(): 
    print("made it to EoP, shutting down gracefully..", h.LogLevel.INFO)
    c.camera_cleanup()
    hw.hw_cleanup()
    exit()

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt: 
        print("cleaning up and exiting....", h.LogLevel.INFO)
        c.camera_cleanup()
        hw.hw_cleanup()
        exit()  