import Helper as h, Camera as c
from Helper import pprint as print, Fire
from pyapriltags import Detector
import os, numpy as np, yaml,cv2, time

at_detector = Detector(searchpath=['apriltags'],families='tag36h11',nthreads=1, quad_decimate=1.0, quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25, debug=0)

def look_for_tag(dirpath:str, imgs:list)-> list:
    res=[]
    for i in (j for j in os.listdir(dirpath) if j in imgs):
        img = cv2.imread(dirpath+'/'+i, cv2.IMREAD_GRAYSCALE)
        cameraMatrix = np.array(h.parameters['Vision']['K']).reshape((3,3))
        camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )
        tags = at_detector.detect(img, True, camera_params, h.parameters['Vision']['tag_size'])
        res.append(tags)
    print(f"Found tags with IDs: {[i.tag_id for i in tags]}", h.LogLevel.INFO, "GREEN") if len(res) else print("No tags found",h.LogLevel.ERROR, "RED")
    return res 

#* Start of OpenCV Code, leave this allone for now...
# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for ShiTomasi corner detection
feature_params = dict(maxCorners=100,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)

#ret, old_frame = cap.read()
#old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
#p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)



def get_SOMETHING():
    # Take the first frame and find corners in it
    ret, old_frame = c.picam2.capture_array()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    # Known parameters
    focal_length_pixels =1000  # Example value, adjust based on your camera calibration
    ground_speed = 10  # Ground speed of the drone in meters per second (known or estimated)
    frame_rate = 30  # Frame rate of the video in frames per second

def get_speed(n:int=1) -> float:
    """Get speed from Camera.
    
    Returns speed as gathered from OpenCV image pixel shift.
    
    Args:
        :param n :Number of times to iterate, returns average speed 
    
    Returns: 
        float: The speed in pixels/s
    """
    frame_rate = 30
    res:list=[]
    old_frame = c.picam2.capture_array()
    cv2.imwrite("CV2.jpg", old_frame) 
    if old_frame is None:
        print("Didn't get image.", h.LogLevel.ERROR, "RED")

    old_gray = old_frame
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    i=0
    while i<n: 
        p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
        frame = c.picam2.capture_array()
   
        if frame is None:
            return None
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if h.debug: 
            for name, img in {"old_gray": old_gray, "old_frame": old_frame, "frame": frame, "frame_gray": frame_gray}.items():
                cv2.imwrite(f"./captures/Vision_{str(name)}_{time.time()}.jpg", img) 
        # Calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        # Select good points
        good_new = p1[st == 1]
        good_old = p0[st == 1]

        # Calculate the displacement (distances) between new and old points
        displacement = np.sqrt((good_new[:, 0] - good_old[:, 0]) ** 2 + (good_new[:, 1] - good_old[:, 1]) ** 2)

        # Estimate the average motion (displacement) per frame
        average_displacement = np.mean(displacement)

        # Assuming frame rate is known (e.g., 30 FPS), calculate speed (pixels per second)
        speed = average_displacement * frame_rate
        res.append(speed)
        print(f"Pass {n}", h.LogLevel.DEBUG)
        print("Estimated speed: {:.2f} pixels/second".format(speed), h.LogLevel.DEBUG) 
        print("teststring")
        print("Teststring", h.LogLevel.ERROR)
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)
        i+=1
    ## got all values, now returning average...
    print(f"Got speeds: {res}",h.LogLevel.INFO,"YELLOW")
    return sum(i for i in res)/n


#* end of OpenCV Code, leave this allone for now..

def is_in_center(f:Fire)->bool: 
    variance = h.parameters['Vision']['centerborders']
    imgcenter = h.parameters['Vision'] ['center']
    return True if abs(imgcenter[0]-f.center[0])<variance[0]*1920 and abs(imgcenter[1]-f.center[1])<variance[1]*1080 else False

def setup():
    print("nothing to set up yet.", h.LogLevel.DEBUG)    

def main():
    print("I am your eyes.", h.LogLevel.DEBUG)


if __name__=="__main__": 
    #empty / debug main function. 
    try: 
        main()
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...", h.LogLevel.INFO)
        exit()
else: 
    try: 
        ##Module startup code here. 
        setup()  
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...")
        exit()