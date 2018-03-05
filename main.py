
import cv2
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from picamera.streams import PiCameraCircularIO
import time
import sys

# CAMERA CONSTANTS
# Focal length of camera in mm
cameraFocalLength = 3.29
# Distance between cameras in mm
cameraBaseLine = 200
# Size of pixel on sensor in mm
cameraPixelSize = 1.4 / 1000

# Camera Settings
fps = 90
videoSize = (640, 480)

# Mask Settings
lowerHSVBound = np.array([60, 0, 100])
upperHSVBound = np.array([80, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'reset' : 3}
piSide = {'left': 0, 'right': 1}



class FrameAnalysis(PiRGBAnalysis):

    def analyze(self, frame):
        # Can be threaded to pipeline frames if needed
        processFrame(frame)


def init():
    global thisPi
    
    if (len(sys.argv) != 2):
        raise ArgumentError('Invalid arguments, run again with: python main.py (left/right)')
    
    if str(sys.argv[1]) == 'left':
        thisPi = piSide['left']
    elif str(sys.argv[1]) == 'right':
        thisPi = piSide['right']
    else:
        raise ArgumentError('Invalid arguments, run again with: python main.py (left/right)')
    
    cv2.namedWindow("video")
    
    program = programStatus['idle']
    
    camera = PiCamera(resolution = videoSize, framerate = fps)
    analysis = FrameAnalysis(camera)
    
    camera.exposure_mode = 'off'
    self.awb_mode = 'off'
    self.vflip = True
    
    camera.start_recording(analysis, format='bgr')
    time.sleep(2)

def processFrame(frame):
    global frame1, frame 2
    if program == programStatus['idle']:
        (tracked, _, _, _) = getTrackedFrame(frame)
        cv2.imshow('video', tracked)
    
    elif program == programStatus['seek']:
        (tracked, x, y, _) = getTrackedFrame(frame)
        if x != -1:
            program = programStatus['track']
            frameCount = 0
            frame1 = None
            frame2 = None

    elif program == programStatus['track']:
        if frame1 is None:
            (frame1, x1, y1, time1) = getTrackedFrame(frame)
            return
        if frame2 is None:
            (frame2, x2, y2, time2) = getTrackedFrame(frame)
            return

        if thisPi == piSide['left']:
            (xRight1, yRight1, timeRight1) = getRightPiCoor(1)
            (xRight2, yRight2, timeRight2) = getRightPiCoor(2)

            (xCart1, yCart1, zCart1) = getCartesianCoordinates(x1, y1, xRight1, yRight1)
            (xCart2, yCart2, zCart2) = getCartesianCoordinates(x2, y2, xRight2, yRight2)

            yGoal = projectileMotion(xCart1, xCart2, yCart1, yCart2, time2-time1, 100)

            print(yGoal)
        elif thisPi == piSide['right']:
            giveLeftPiCoor()
                
        program = programStatus['reset']
        

    elif program == programStatus['reset']:
        programStatus['idle']
   
def trackObject(frame):
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(hsv, lowerHSVBound, upperHSVBound)
    mask = cv2.erode(mask, None, iterations = 1)
    mask = cv2.dilate(mask, None, iterations = 1)
    
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    if len(cnts) <= 0:
        return frame, -1, -1

    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)

    if radius < 6:
        return frame, -1, -1
        
    cv2.circle(frame, (int(x), int(y)), 1, colors['yellow'], 3)
    cv2.circle(frame, (int(x), int(y)), int(radius), colors['yellow'], 2)
    cv2.putText(frame, 'x: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)

    return frame, int(x), int(y)

def getTrackedFrame(frame):
    (tracked, x, y) = trackObject(frame)
    if x != -1:
        return True, tracked, x, y, time
    return False

def cameraOriginToCenterX(x):
    return 320-x

def cameraOriginToCenterY(y):
    return 240-y

def getXCoor(xLeftPixel, Z):
    return (xLeftPixel * cameraPixelSize) * (Z / cameraFocalLength)

def getYCoor(yLeftPixel, Z):
    return (yLeftPixel * cameraPixelSize) * (Z / cameraFocalLength)

def getZCoor(xLeftPixel, xRightPixel):
    return (cameraFocalLength * cameraBaseLine) / ((xLeftPixel - xRightPixel) * cameraPixelSize)

# Only to be done on one of the Pi's, probably the left one
# Coordinates system origin at left camera sensor
def getCartesianCoordinates(xLeft, yLeft, xRight, yRight):
    Z = getZCoor(cameraOriginToCenterX(xLeft), cameraOriginToCenterX(xRight))
    X = getXCoor(cameraOriginToCenterX(xLeft), Z)
    Y = getYCoor(cameraOriginToCenterY(yLeft), Z)
    return (X, Y, Z)

def getRightPiCoor():
    # Server side get coordinates from Right Pi

def giveRightPiCoor():
    # Client side give coordinates to Left Pi


def xVelocity(x1, x2, timedelta):
    return ((x2-x1)/float(timedelta))

def yVelocity(y1, y2, timedelta):
    return ((y2-y1)/float(timedelta))

def zVelocity(z1, z2, timedelta):
    return ((z2-z1)/float(timedelta))

def projectileMotion(x1, x2, y1, y2, timedelta, xGoal):
    vX = xVelocity(x1, x2, timedelta)
    vY = yVelocity(y1, y2, timedelta)
    timeGoal = (xGoal-x1) / vX
    yGoal = (vY * timeGoal) - (0.5 * 9.81 * (timeGoal ** 2)) + y1
    return yGoal

def main():
    init()

    while 1:
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            camera.close()
            break


main()
                 
            
