import Camera as c, Vision as v, Helper as h, Hardware as hw
from Helper import Fire, pprint as print
import os, sys

logcolor = "magenta"
activator = './venv/bin/activate_this.py'  # Looted from virtualenv; should not require modification, since it's defined relatively

def main(): 
    print("Hello World!", "MAGENTA")
    find_fire()
    clean_exit()

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

def clean_exit(): 
    print("made it to EoP, shutting down gracefully..")
    c.camera_cleanup()
    exit()

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt: 
        print("cleaning up and exiting....")
        c.camera_cleanup()
        exit()