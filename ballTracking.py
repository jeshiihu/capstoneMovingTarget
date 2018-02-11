#import the necessary modules
import freenect
import cv2
import numpy as np
import threading
import os.path
import csv
import frame_convert2
import KinectFrameThread
from datetime import datetime
 

frames = 0
prevFrames = 0
fps = 0
fpsStop = False

kinect = KinectFrameThread.KinectFrameThread()


##cv2.namedWindow('Depth')
##cv2.namedWindow('Video')

# https://naman5.wordpress.com/2014/06/24/experimenting-with-kinect-using-opencv-python-and-open-kinect-libfreenect/
#function to get RGB image from kinect
# https://pastebin.com/WVhfmphS
def getVideoFrame():
    return freenect.sync_get_video()[0]
##    return frame_convert2.video_cv(freenect.sync_get_video()[0])

def getDepthVideoFrame():
    return frame_convert2.pretty_depth_cv(freenect.sync_get_depth(0, freenect.DEPTH_11BIT)[0])
 
#function to get depth image from kinect
def getDepthFrame():
    return freenect.sync_get_depth()[0]

fieldnames = ['frame', 'x', 'y', 'predicted']

# MIGHT NEED TO CONVERT TO RAD
def GetMaxX(initVel, tmax, angle):
    return initVal*tmx*np.cos(angle)

def CalculatePredicted(x1, x2, y1, y2, t):
    (physX1, physY1) = Pixel2Physical(x1, y1)
    (physX2, physY2) = Pixel2Physical(x2, y2)

    velocityX = (physX2-physX1)/t
    velocityY = (physY2-physY1)/t

    angle = np.arctan((physY2-physY1)/(physX2-physX1))
    velocity = np.sqrt(np.square(velocityX)+np.square(velocityY))

    xMax = GetMaxX(velocity, tmax, angle)
    time = SEC_PER_FRAME


def CalculateVelocity(frmCount, x, y):
    with open('trajectory.csv', "a+") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # pred = CalculatePredicted();
        writer.writerow({'frame': frmCount,'x': x, 'y': y, 'predicted': 0})

def DetectHSV():
    #get a frame from RGB camera
    frame = get_video()
##  frame = get_depth()
    global frames
    frames = frames + 1

    #get a frame from depth sensor
    # depth = get_depth()
    #display RGB image

    # define the lower and upper boundaries of the colors in the HSV color space
    lower = {'red':(166, 84, 141), 'green':(66, 122, 129), 'blue':(97, 100, 117), 'yellow':(23, 59, 119), 'orange':(0, 50, 80)} #assign new item lower['blue'] = (93, 10, 0)
    upper = {'red':(186,255,255), 'green':(86,255,255), 'blue':(117,255,255), 'yellow':(54,255,255), 'orange':(20,255,255)}
     
    # define standard colors for circle around the object
    colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0), 'yellow':(0, 255, 217), 'orange':(0,140,255)}

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    #for each color in dictionary check object in frame
    # for key, value in upper.items():
    # construct a mask for the color from dictionary`1, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    kernel = np.ones((9,9),np.uint8)
    mask = cv2.inRange(hsv, lower['yellow'], upper['yellow'])
    mask = cv2.morphologyEx(
mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
           
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
   
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
   
        # only proceed if the radius meets a minimum size. Correct this value for your obect's size
        if radius > 0.3:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), colors['yellow'], 2)
            cv2.putText(frame,'yellow' + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'],2)
        
        cv2.putText(frame, 'x: ' + str(x) + ", y: " + str(y), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'],2)
        CalculateVelocity(frames,x, y)
 
    # show the frame to our screen
    # cv2.imshow("Depth", depth)
    height, width = frame.shape[:2]
    cv2.putText(frame, 'height: ' + str(height) + ", width: " + str(width), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['yellow'],2)
    cv2.imshow("Frame", frame)
    
def trackObject():
##    print("In Track Object")
    global frames
    frames = frames + 1
##    print("Upped Framecount")
    start = datetime.now()
    frame = getVideoFrame()
    depth = getDepthFrame()
    framesGot = datetime.now()
##    print("Got Frame")
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
##    print("Got HSV")
    
    lower = np.array([50, 100, 0])
    upper = np.array([100, 255, 255])
##    
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations = 2)
##    mask = cv2.dilate(mask, None, iterations = 2)
##    print("Got Mask")
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    x = 0
    y = 0
    if len(cnts) > 0:
        
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
##        M = cv2.moments(c)
##        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        print(radius)
        if radius > 6:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
    
##    res = cv2.bitwise_and(frame, frame, mask= mask)
    
    colors = {'yellow':(0, 255, 217)}
    
    
    cv2.putText(frame, 'fps: ' + str(fps), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'], 2)
##    cv2.putText(frame, 'Depth: ' + str(depth[int(y)][int(x)]), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'], 2)
    cv2.imshow("Video", frame)
    end = datetime.now()
    print("total: " + str((end.microsecond-start.microsecond)))
    print("frame: " + str((framesGot.microsecond-start.microsecond)))
    print("proccessing: " + str((end.microsecond-framesGot.microsecond)))
    print()
    
##    cv2.imwrite("ballimage.jpg", res)
##    print("Print Frame")
    
        
def getDepthVideo():
    frame = get_depth_video()
    global frames
    frames = frames + 1
    cv2.imshow("Depth", frame)
    
def getVideo():
##    frame = kinect.readVideoFrame()
    start = datetime.now()
    frame = getVideoFrame()
    end = datetime.now()
    print((end.microsecond-start.microsecond)/1000)
    global frames
    frames = frames + 1
    cv2.imshow("Video", frame)

def printit():
    if fpsStop:
        return
    threading.Timer(1.0, printit).start()
    global fps, prevFrames
    fps = frames - prevFrames
    prevFrames = frames
    
def displayFrameThread():
    while 1:
    # frame = get_video()
    # cv2.imshow("Frame", frame)

##        DetectHSV()
##        getVideo()
##        showDepthVideo()
    
        trackObject()
    
    
    # quit program when 'esc' key is pressed
        if (cv2.waitKey(5) & 0xFF) == 27:
            kinect.stopThread()
            fpsStop = True
            break
        
    cv2.destroyAllWindows()

if __name__ == "__main__":
    printit()
##    if not os.path.isfile('./trajectory.csv'):
##        with open('trajectory.csv', "w+") as csvfile:
##            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
##            writer.writeheader()
            
##    trackObject()
##    kinect.start()    

    threading.Thread(target=displayFrameThread, args=()).start()

