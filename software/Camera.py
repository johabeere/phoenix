import Helper as h
from Helper import pprint as print
from picamera2 import Picamera2
from libcamera import controls #rpi-libcamera package
import os, fnmatch, time

picam2 = Picamera2()
frame_rate = h.parameters['Camera']['frame_rate']
##set camera res mode
mode = picam2.sensor_modes[h.parameters['Camera']['sensor_mode']]
config = picam2.create_video_configuration(main = {'size': tuple(h.parameters['Camera']['resolution'])}, sensor = {'output_size': mode['size'], 'bit_depth': mode['bit_depth']}, controls = {'FrameRate': frame_rate, "AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})

picam2.configure(config)

burst_delay = 0.1



def main():
    make_img_dir()
    start_camera()
    print(f"Running as debug script now, initialized successfully.")
    #TODO add debug info here. ??Needed? 


# function for starting camera capture. 
def start_camera(): 
    os.environ["LIBCAMERA_LOG_LEVELS"] = "3"# h.parameters['Camera']['libcameraloglevel']
    picam2.start(show_preview=False)
    picam2.set_controls({})  #* This could be moved into the video config. Works either way and i want to go to sleep
    picam2.set_logging(Picamera2.ERROR)

def take_pictures(num_pictures:int): 
    for i in range(num_pictures): 
        picam2.capture_file(f"{h.parameters['Camera']['imagepath']}/capture{i}.jpg")
        time.sleep(burst_delay)

def make_img_dir(): 
    if not os.path.isdir(h.parameters['Camera']['imagepath']): 
        os.makedirs(h.parameters['Camera']['imagepath'])
    
def camera_cleanup():
    for i in os.listdir(h.parameters['Camera']['imagepath']):
        if fnmatch.fnmatch(i, "capture*"): 
            print(f"i={i}, removing {h.parameters['Camera']['imagepath']+'/'+i}")
            os.remove(f"{h.parameters['Camera']['imagepath']+'/'+i}")

def get_mm_per_px()-> float: 
    return (h.parameters['Camera']['physical'][1]/h.parameters['Camera']['physical'][3]+h.parameters['Camera']['physical'][2]/h.parameters['Camera']['physical'][4])/2

if __name__=="__main__": 
    #empty / debug main function. 
    try: 
        start_camera()
        main()
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...", h.LogLevel.INFO)
        exit()
else: 
    try: 
        ##Module startup code here. 
        make_img_dir()
        start_camera()
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...", h.LogLevel.INFO)
        camera_cleanup() 
        exit()