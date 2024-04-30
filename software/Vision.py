from pyapriltags import Detector
import os, numpy, yaml,cv2, Helper as h

at_detector = Detector(searchpath=['apriltags'],families='tag36h11',nthreads=1, quad_decimate=1.0, quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25, debug=0)

global paramters

def get_params():
    with open( './config.yaml', 'r') as stream:
        p= yaml.safe_load(stream)
    return p 

def look_for_tag(dirpath:str, imgs:list):
    for i in (j for j in os.listdir(dirpath) if j in imgs):
        img = cv2.imread(dirpath+'/'+i, cv2.IMREAD_GRAYSCALE)
        cameraMatrix = numpy.array(parameters['Vision']['K']).reshape((3,3))
        camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )
        tags = at_detector.detect(img, True, camera_params, parameters['Vision']['tag_size'])
        print("Found tags ", end='')
        h.pprint(tags)
        

def setup():
    global parameters
    parameters = get_params()

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