import Helper as h
from Helper import pprint as print
from pyapriltags import Detector
import os, numpy, yaml,cv2 

at_detector = Detector(searchpath=['apriltags'],families='tag36h11',nthreads=1, quad_decimate=1.0, quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25, debug=0)

def look_for_tag(dirpath:str, imgs:list):
    res=[]
    for i in (j for j in os.listdir(dirpath) if j in imgs):
        img = cv2.imread(dirpath+'/'+i, cv2.IMREAD_GRAYSCALE)
        cameraMatrix = numpy.array(h.parameters['Vision']['K']).reshape((3,3))
        camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )
        tags = at_detector.detect(img, True, camera_params, h.parameters['Vision']['tag_size'])
        res.append(tags)
    print(f"Found tags with IDs: {[i.tag_id for i in tags]}", "GREEN") if len(res) else print("No tags found", "RED")
    return res 

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