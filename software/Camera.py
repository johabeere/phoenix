import Helper as h
from Helper import pprint as print
from picamera2 import Picamera2
from libcamera import controls #rpi-libcamera package
import os, fnmatch, time

picam2 = Picamera2()
imagepath = "./captures"
burst_delay = 0.1



def main():
    make_img_dir()
    start_camera()
    print(f"Running as debug script now, initialized successfully.")
    #TODO add debug info here.


# function for starting camera capture. 
def start_camera(): 
    os.environ["LIBCAMERA_LOG_LEVELS"] = "3"# h.parameters['Camera']['libcameraloglevel']
    picam2.start(show_preview=False)
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
    picam2.set_logging(Picamera2.ERROR)

def take_pictures(num_pictures:int): 
    for i in range(num_pictures): 
        picam2.capture_file(f"{imagepath}/capture{i}.jpg")
        time.sleep(burst_delay)

def make_img_dir(): 
    if not os.path.isdir(imagepath): 
        os.makedirs(imagepath)
    
def camera_cleanup():
    for i in os.listdir(imagepath):
        if fnmatch.fnmatch(i, "capture*"): 
            print(f"i={i}, removing {imagepath+'/'+i}")
            os.remove(f"{imagepath+'/'+i}")

if __name__=="__main__": 
    #empty / debug main function. 
    try: 
        start_camera()
        main()
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...")
        exit()
else: 
    try: 
        ##Module startup code here. 
        make_img_dir()
        start_camera()
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...")
        camera_cleanup() 
        exit()