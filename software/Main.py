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

stop_flag = threading.Event()
exit_flag = threading.Event()

def main(): 
    #set the killswitch. 
    hw.set_killswitch(restart_exit)
    #Object initialization
    f:Fire = None
    d:Drone = Drone()
    #greet user. 
    hw.set_LED(0xFFFFFF)#SET WHITE
    if h.parameters['Main']['coolmode']:
        print(greetstring, h.LogLevel.INFO, "RED")
    else: 
        print("Hello World", h.LogLevel.INFO, "MAGENTA")
    polling_thread = start_polling(d, f) # function that calls itself repeatedly until stopped.  
    ##Load water
    hw.acquire_payload()
    ##in-air loop: 
    while not exit_flag.is_set():# This is a while True loop adjusted to allow restart functionality. It exits either because the restart button is pressed or if a fire was found to be extinguished.  
        f = find_fire()
        if f!=None and v.is_in_center(f): 
            hw.set_LED(0xD02090)#magenta
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
    print("made it to EoP, shutting down gracefully..", h.LogLevel.INFO)
    return

def polling(d:Drone, f:Fire)-> None: 
    while not stop_flag.is_set():
        d.speed = v.get_speed(3) ##set Drone speed. 
        d.angle = hw.get_angle() ##set Drone angle. 
        d.buttons = hw.get_buttons()
    
        print(f"\n{20*'-'}\nAverage speed\t{d.speed}\nAngle is:\t{d.angle}\nbuttonstates:\t{d.buttons}\n{20*'-'}", h.LogLevel.INFO, "CYAN")
    
        if f is not None:
            ## Fire found.  
            f = find_fire() ##update Apriltag position, regenerate fire object.  
            d.height = v.get_height(f, d.angle)##set Drone height. (requires visible Apriltag.) 
        time.sleep(h.parameters['Main']['polling_timer'])
        #threading.Timer(h.parameters['Main']['polling_timer'], polling(d, f)).start()
    return

def stop_polling(): 
    stop_flag.set()

def start_polling(d: Drone, f:Fire): 
    polling_thread = threading.Thread(target=polling, args=(d, f))
    polling_thread.daemon = True  # Ensure the thread exits when the main program exits
    polling_thread.start()
    return polling_thread

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
    d.height = v.get_height(f, d.angle)#make sure height is as acurate as possible, manual polling.
    hw.set_LED(0x0000FF)#Blue
    max_cycles = 100 #prevents endless loop
    while max_cycles>0: 
        max_cycles-=1
        print(f"{max_cycles=}", h.LogLevel.DEBUG)
        f.arc_calc(d.speed, d.height)
        dtc = abs(f.current_target[0]- f.center[0])
        print(f"Distance to center: {dtc=}")
        if(dtc<h.parameters['Vision']['target_threshold']*h.parameters['Camera']['resolution'][0]):
            time.sleep(f.time_to_drop)
            break
        else: 
            time.sleep(2.5/100)
            continue
    c.final_image()
    hw.drop(d)
    hw.set_LED(0xFFFFFF)#WHITE
    return

def restart_exit(channel): 
    """
    Called by the GPIO event of the reset button. sets the flags to stop polling (subthread) and main (main thread). 
    """
    print("restart exit call...", h.LogLevel.FAILURE)
    hw.set_LED(0xFF0000)
    exit_flag.set()
    stop_flag.set()

def cleanup(): 
    """
    Cleanup function that calls all cleanups of submodules and stops the polling thread. time.sleep is needed to stop errors in GPIO Cleanup. 
    """
    stop_polling()
    time.sleep(1)
    c.camera_cleanup()
    hw.hw_cleanup()


if __name__ == "__main__":
    """
    Program entry and exit point. 
    try except catches Keyboard interrupts, main function monitors exit_flag to enable restart functionality.
    exits based on program state to either restart (3) or shut down (0). 
    """
    try: 
        while not exit_flag.is_set():
            main()
    except KeyboardInterrupt as e: 
        print("cleaning up and exiting....", h.LogLevel.INFO)
    finally:    
        cleanup()
        exit_code = 3 if exit_flag.is_set() else 0
        exit(exit_code)
