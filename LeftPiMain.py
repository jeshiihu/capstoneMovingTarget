
import cv2
from picamera import Color
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import datetime
import time
import sys
import json
import socket
import numpy as np

# CAMERA CONSTANTS
# Focal length of camera in mm
cameraFocalLength = 3.29
# Distance between cameras in mm
cameraBaseLine = 130.5
# Size of pixel on sensor in mm
cameraPixelSize = (1.4 / 1000) * 4
# Camera distortion factor (leaving as 0 for now)
cameraDistortion = 0

# Camera Settings
fps = 60
videoSize = (640, 480)
videoCenter = (videoSize[0]/2, videoSize[1]/2)

# Mask Settings
lowerHSVBound = np.array([50, 100, 50])
upperHSVBound = np.array([75, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'recieve' : 3, 'analyze': 4, 'test': 5}

HOST = '0.0.0.0'
PORT = 5005
BUFFER_SIZE = 128

def getMicroseconds():
    time = datetime.datetime.now() - timeStart
    time = (time.seconds*1000000) + time.microseconds
    return time

def getMilliseconds():
    time = getMicroseconds()/1000
    return time

def trackObject(frame):
    
    time = getMilliseconds()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerHSVBound, upperHSVBound)
    mask = cv2.erode(mask, None, iterations = 1)
    mask = cv2.dilate(mask, None, iterations = 1)
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    
    if len(cnts) <= 0:
        return frame, -1, -1, time
    
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)

    if radius < 6:
        return frame, -1, -1, time
    
    
    if checkProgram('track'):
        cv2.circle(frame, (int(x), int(y)), 1, displayColors['yellow'], 3)
        cv2.circle(frame, (int(x), int(y)), int(radius), displayColors['yellow'], 2)
        cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
        cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
        cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
        cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
        cv2.imwrite("throw/frame.jpg", frame)
        cv2.imwrite("throw/mask.jpg", mask)
                    

    return frame, int(x), int(y), time

class LeftPiCameraAnalysis(PiRGBAnalysis):
    
    def __init__(self, camera):
        super(LeftPiCameraAnalysis, self).__init__(camera)

    def analyze(self, frame):
        global trackedFrames
        
        if checkProgram('idle'):
            return
        
        if checkProgram('seek'):
            frame, x, y, time = trackObject(frame)
            if x!= -1:
                setProgram('track')
                trackedFrames = {}
                conn.sendall('track')
##            print "Out of Frame" if x == -1 else (x, y, time)
            return
            
        if checkProgram('track'):
            frame, x, y, time = trackObject(frame)
##            if x == -1:
##                return
            
            if not trackedFrames.has_key("frame1L"):
                trackedFrames["frame1L"] = (x, y, time)
                return
                
            if not trackedFrames.has_key("frame2L"):
                trackedFrames["frame2L"] = (x, y, time)
                return
            
            setProgram('recieve')
##            setProgram('idle')
            return
    
    
def startTCP():
    global conn
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.bind((HOST, PORT))
    tcpConnection.listen(1)
    conn, addr = tcpConnection.accept()
    data = conn.recv(BUFFER_SIZE)
    print "TCP init: ", data
    conn.sendall("Hello back from left Pi")
    
def startCamera():
    global camera, timeStart
    camera = PiCamera(resolution = videoSize, framerate = fps)
    time.sleep(2)
    
##    camera.shutter_speed = camera.exposure_speed
##    camera.exposure_mode = 'off'
##    g = camera.awb_gains
##    camera.awb_mode = 'off'
##    camera.awb_gains = g
##    camera.vflip = True
    camera.annotate_background = Color('black')
    
    camera.start_preview(alpha=200)
    analyzer = LeftPiCameraAnalysis(camera)
    camera.start_recording(analyzer, 'bgr')
    timeStart = datetime.datetime.now()
    
def stopCamera():
    camera.stop_recording()
    camera.stop_preview()
    
def closeTCP():
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    
def init():
    cv2.namedWindow("video")
    
    startTCP()
    startCamera()
    setProgram('idle')
    
def shutdown():
    stopCamera()
    closeTCP()
    
def setProgram(status):
    global program
    program = programStatus[status]
    camera.annotate_text = status
    
def checkProgram(status):
    return program == programStatus[status]

def recieveFrames():
    global trackedFrames
    if checkProgram('recieve'):
        tmp = conn.recv(BUFFER_SIZE)
        data = json.loads(tmp)
        trackedFrames["frame1R"] = data['frame1R']
        trackedFrames["frame2R"] = data['frame2R']
        setProgram('analyze')
        
def analyzeFrames():
    if checkProgram('analyze'):
        leftFrame = trackedFrames["frame1L"]
        rightFrame = trackedFrames["frame1R"]
        (xMM, yMM, zMM) = getCoordinates(leftFrame[0], leftFrame[1], rightFrame[0], rightFrame[1])
        (x, y, z) = mmToIn(xMM, yMM, zMM)
        print leftFrame, rightFrame
        print x, y, z
        print ""
        setProgram('idle')

def getCoordinates(leftI, leftJ, rightI, rightJ):
    (leftX, leftY) = reverseDistortion(leftI, leftJ)
    (rightX, rightY) = reverseDistortion(rightI, rightJ)

    z = ((cameraBaseLine * cameraFocalLength) / (leftX - rightX))
    x = leftX * (z / cameraFocalLength) 
    y = leftY * (z / cameraFocalLength)
    
    return x, y, z

def mmToIn(x, y, z):
    return x/25.4, y/25.4, z/25.4

def reverseDistortion(i, j):
    xDistorted = (i - videoCenter[0]) * cameraPixelSize
    yDistorted = (j - videoCenter[1]) * cameraPixelSize
    rDSquared = (xDistorted * xDistorted) + (yDistorted * yDistorted)
    x = xDistorted * (1 + (cameraDistortion * rDSquared))
    y = yDistorted * (1 + (cameraDistortion * rDSquared))
    return x, y


##def test():
##    if checkProgram('test'):
##        conn.sendall('test')
##        while True:
##            
##            key = cv2.waitKey(5) & 0xFF
##            if key == ord('e'):
##                conn.sendall('idle')


    
def main():
    init()
    while True:
        
        recieveFrames()
        analyzeFrames()
##        test()
        
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break
        elif key == ord('s'):
            setProgram('seek')
        elif key == ord('i'):
            setProgram('idle')
##        elif key == ord('t'):
##            setProgram('test')
        
    shutdown()
    
main()

    

       
