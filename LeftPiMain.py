
import cv2
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from picamera.streams import PiCameraCircularIO
import time
import sys
import socket
import numpy as np
import datetime

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

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'analyze': 3}

HOST = '0.0.0.0'
PORT = 5005
BUFFER_SIZE = 1024

delayFrames = 5


videoFrame1 = None
videoFrame2 = None
frame1Left = None
frame2Left = None
frame1Right = None
frame2Right = None


class LeftPiCameraAnalysis(PiRGBAnalysis):

    def analyze(self, frame):
        global program

        if program == programStatus['idle']:
            cv2.imshow("video",frame)
            return
        
        if program == programStatus['seek']:
            print ballInFrame(frame)
##            if ballInFrame(frame):
##                program = programStatus['track']
##                global frame1Left, frame2Left
##                frame1Left = None
##                frame2Left = None
##                delayCounter = 0
            return

        if program == programStatus['track']:
            print "track"
            if delayCounter < delayFrames:
                delayCounter += 1
                return

            if delayCounter == delayFrames:
                delayCounter +=1
                conn.sendall("track")


            if not frame1Left:
                # Begin thread here
                getFirstFrame(frame)
                return
            
            if not frame2Left:
                # Begin thread here
                getSecondFrame(frame)
                return

            program = programStatus['analyze']
            return



# Run program with "python main.py (left/right)"
def init():
    global timeStart
    timeStart = datetime.datetime.now()
    
    cv2.namedWindow("video")
    global program
    program = programStatus['idle']

    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.bind((HOST, PORT))
    tcpConnection.listen(1)

    global conn
    conn, addr = tcpConnection.accept()
    data = conn.recv(BUFFER_SIZE)
    print "TCP init: ", data
    conn.sendall("Hello back from left Pi")

    global camera
    camera = PiCamera(resolution = videoSize, framerate = fps)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.vflip = True
    analysis = LeftPiCameraAnalysis(camera)
    camera.start_recording(analysis, format='bgr')
    time.sleep(2)
    
def getMicroseconds():
    time = datetime.datetime.now() - timeStart
    return (time.seconds*1000000) + time.microseconds

def getMilliseconds():
    return getMilliseconds()/1000

def getFirstFrame(frame):
    tmp = trackObject(frame)
    if x != -1:
        global frame1Left, videoFrame1
        videoFrame1 = tmp[0]
        frame1Left = (tmp[1], tmp[2], tmp[3])

def getSecondFrame(frame):
    tmp = trackObject(frame)
    if x != -1:
        global frame2Left, videoFrame2
        videoFrame2 = tmp[0]
        frame2Left = (tmp[1], tmp[2], tmp[3])

def ballInFrame(frame):
    tracked, x, y, time = trackObject(frame)
    if x != -1:
        return True
    return False

def getCoorFromRightPi():
    tmp = conn.recv(BUFFER_SIZE)
    data = json.loads(tmp)
    global frame1Right, frame2Right
    frame1Right = data['frame1']
    frame2Right = data['frame2']
   
def trackObject(frame):

    time = getMilliseconds()
    
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
    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)

    return frame, int(x), int(y), time

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
    global program
    init()
    while 1:

        if program == programStatus['analyze']:
            print "analyze"
            getCoorFromRightPi()
            print "Frame 1 Left: ", frame1Left
            print "Frame 1 Right: ", frame1Right
            print "Frame 2 Left: ", frame2Left
            print "Frame 2 Right: ", frame2Right
            program = programStatus['idle']

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            conn.close()
##            camera.close()
            break
        elif key == 32:
            program = programStatus['seek']

    conn.close()


main()
                 
            
