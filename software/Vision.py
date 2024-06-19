import Helper as h, Camera as c
from Helper import pprint as print, Fire, parameters
from pyapriltags import Detector
import os, numpy as np, yaml,cv2, time, glob, itertools
from scipy.spatial.transform import Rotation as R


at_detector = Detector(searchpath=['apriltags'],families='tag36h11',nthreads=1, quad_decimate=1.0, quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25, debug=0)

def look_for_tag(dirpath:str, imgs:list)-> list:
    res=[]
    for i in (j for j in os.listdir(dirpath) if j in imgs):
        img = cv2.imread(dirpath+'/'+i, cv2.IMREAD_GRAYSCALE)
        cameraMatrix = np.array(parameters['Vision']['K']).reshape((3,3))
        camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )
        tags = at_detector.detect(img, True, camera_params, parameters['Vision']['tag_size'])
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

def get_speed(n:int=1) -> float:
    """
    Get speed from Camera.
    
    Returns speed as gathered from OpenCV image pixel shift.
    
    Args:
        :param n: Number of times to iterate, returns average speed. defaults to 1. 
        :type n: int or convertible. 
    Returns: 
        :return: The speed in pixels/s
        :rtype: float
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
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)
        i+=1
    ## got all values, now returning average...
    print(f"Got speeds: {res}",h.LogLevel.DEBUG,"YELLOW")
    ##perform nan checks here already:
    clean_res = list((i for i in res if str(i)!='nan'))
    print(f"{c.get_mm_per_px()}")
    res_mm = list((i*c.get_mm_per_px() for i in clean_res)) 
    print(f"converted speeds in mm/s: {res_mm=}", h.LogLevel.INFO, "CYAN")
    return sum(res_mm)/n #changed to accout for nan values.

def calibrate():
    """
    Calibrates the attached Camera using the OpenCV2 Camera calibration. 
    
    Args: 
        None.
    Returns: 
        :returns: None. 
    
    """
    if not os.path.isfile(f"{parameters['Camera']['imagepath']}/calibration0.jpg"): 
        #Take Calibration Images: 
        for i in range(9): 
            oldtime = time.time()
            while input(f"Press any key to take calibration picture No. {i+1}:.... [will automatically take picture in 2 seconds...]")==None and not h.true_if_wait2s(oldtime):
                pass 
            print("click", h.LogLevel.DEBUG)
            c.picam2.capture_file(f"{str(parameters['Camera']['imagepath'])}/calibration{i}.jpg")

    # Defining the dimensions of checkerboard
    CHECKERBOARD = (6, 9)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 

    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    images = glob.glob(f"{parameters['Camera']['imagepath']}/calibration*.jpg")
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE +cv2.CALIB_USE_INTRINSIC_GUESS)
     
        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display 
        them on the images of checker board
        """
        if ret == True:
            print("Found Checkerboard Corners and appending to img.")
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
         
            imgpoints.append(corners2)
 
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
     
        #cv2.imwrite(f"{parameters['Camera']['imagepath']}/SHOW_{fname}",gray)
        cv2.imwrite(f"./captures/SHOW_{time.time()}.jpg", gray)
        cv2.waitKey(0)
 
    #cv2.destroyAllWindows() #TODO check if this is necessary for non-display use.
 
    h2,w = img.shape[:2]
 
    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
 
    print("Camera matrix : \n")
    print(mtx)
    print("dist : \n")
    print(dist)
    print("rvecs : \n")
    print(rvecs)
    print("tvecs : \n")
    print(tvecs)
    print("writing to yaml now....", h.LogLevel.INFO, "MAGENTA")
    #TODO: try and activate.
    K:list = list(itertools.chain.from_iterable(mtx))#convert 3x3 matrix to list. 
    print(f"flattened list: {K}")
    h.overwrite_yaml_attribute(3, f"\tK: {K} #This needs to be in line 4, too lazy to dynamically check where attribute is stored.\n")

def get_height(f:h.Fire, angle:float)-> float: 
    """
    get height via computervision and trigonometry.
    Arguments: 
        :parameter: f is the Fire which we want to estimate the height from. 
        :parameter: angle is the angle obove the horizon which the camera currently faces. (gyro-angle-uptilt).
    Returns: 
        :returns: float height above ground in m. 
    """
    #skipping this check for first testflight. #! TODO add Back. 
    #if not -45<angle<45: 
    #    print(f"Angle for height calculation is out of bounds, please check input: {angle=}", h.LogLevel.ERROR)
    #    return 2000.0
    ###Idea: get apriltag size. relate image size to physical april tag size. by that, we can estimate 
    c = np.array(f.corners)    
    #Transform coordinates to be orthagonal to camera viewcone: 
    r = R.from_euler('y', angle, degrees=True)
    c_transformed = np.dot(c, r) # Transform into new CS
    ##calculate tag area by using shoelace formula in transformed coordinates: 
    A = h.shoelace_formula(f.corners)
    #height = (tag_size_mm*focal_length_mm)/(no_distortion_side_lengths_px * pixel_width)
    height_in_mm = (h.parameters['Vision']['tag_size']*h.parameters['Camera']['physical'][0])/(np.sqrt(A)*c.get_mm_per_px())
    #TODO: calculate height by physical to pixel area relation. 
    print(f"Height would be\t{height_in_mm=}, or in m:\t{height_in_mm/1000}, returning 2000.0")
    return 2000.0 #! TODO replace with below
    #return height_in_mm

#* end of OpenCV Code, leave this allone for now..

def is_in_center(f:Fire)->bool: 
    print(f"trying to find center...{f.center=}")
    variance = h.parameters['Vision']['centerborders']
    imgcenter = h.parameters['Vision'] ['center']
    return True if abs(imgcenter[0]-f.center[0])<variance[0]*640 and abs(imgcenter[1]-f.center[1])<variance[1]*480 else False

def setup():
    if h.parameters['Camera']['calibrated']:
        print("Starting Camera Calibration...", h.LogLevel.INFO)
        c.calibrate()
    else: 
        print("nothing to set up.", h.LogLevel.DEBUG)


def main():
    print("I am your eyes.", h.LogLevel.DEBUG)
    calibrate() #test calibration function.

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