import Helper as h
from Helper import pprint as print, Fire
from pyapriltags import Detector
import os, numpy as np, yaml,cv2 

at_detector = Detector(searchpath=['apriltags'],families='tag36h11',nthreads=1, quad_decimate=1.0, quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25, debug=0)
cap = cv2.VideoCapture('/dev/video0')

def look_for_tag(dirpath:str, imgs:list)-> list:
    res=[]
    for i in (j for j in os.listdir(dirpath) if j in imgs):
        img = cv2.imread(dirpath+'/'+i, cv2.IMREAD_GRAYSCALE)
        cameraMatrix = np.array(h.parameters['Vision']['K']).reshape((3,3))
        camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )
        tags = at_detector.detect(img, True, camera_params, h.parameters['Vision']['tag_size'])
        res.append(tags)
    print(f"Found tags with IDs: {[i.tag_id for i in tags]}", "GREEN") if len(res) else print("No tags found", "RED")
    return res 
''' Start of OpenCV Code, leave this allone for now...
# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Parameters for ShiTomasi corner detection
feature_params = dict(maxCorners=100,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)

ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
''' #end of OpenCV Code, leave this allone for now..

def is_in_center(f:Fire)->bool: 
    variance = h.parameters['Vision']['centerborders']
    imgcenter = h.parameters['Vision'] ['center']
    return True if abs(imgcenter[0]-f.center[0])<variance[0]*1920 and abs(imgcenter[1]-f.center[1])<variance[1]*1080 else False

def setup():
    print("nothing to set up yet.")    

def main():
    print("I am your eyes.")


if __name__=="__main__": 
    #empty / debug main function. 
    try: 
        main()
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...")
        exit()
else: 
    try: 
        ##Module startup code here. 
        setup()  
    except KeyboardInterrupt: 
        print("goodbye, cleaning up before I leave...")
        exit()