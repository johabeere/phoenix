import os, sys
import Camera as c, Vision as v, Helper as h
activator = './venv/bin/activate_this.py'  # Looted from virtualenv; should not require modification, since it's defined relatively

def main(): 
    h.pprint("Hello World!", "MAGENTA")
    c.start_camera()
    c.take_pictures(2)
    v.look_for_tag("./captures", ["capture0.jpg", "capture1.jpg"])
    clean_exit()


def in_venv():
    return sys.prefix != sys.base_prefix

def clean_exit(): 
    print("made it to EoP, shutting down gracefully..")
    c.camera_cleanup()
    exit()
if __name__ == "__main__":
    if not in_venv:
        #switch to venv
        with open(activator) as f:
            exec(f.read(), {'__file__': activator})
    #from hereon running in venv! #TODO: see how to resolve occuring import errors ...
    try: 
        main()
    except KeyboardInterrupt: 
        print("cleaning up and exiting....")
        c.camera_cleanup()
        exit()