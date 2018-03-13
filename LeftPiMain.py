
import cv2
from picamera import Color
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import datetime
import time
import sys
import socket
import numpy as np

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

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'recieve' : 3 'analyze': 4}

HOST = '0.0.0.0'
PORT = 5005
BUFFER_SIZE = 1024

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
        
##    cv2.circle(frame, (int(x), int(y)), 1, colors['yellow'], 3)
##    cv2.circle(frame, (int(x), int(y)), int(radius), colors['yellow'], 2)
##    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
##    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
##    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
##    cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)

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
                changeProgram('track')
                trackedFrames = {}
            print "Out of Frame" if x == -1 else (x, y, time)
            return
            
        if checkProgram('track'):
            frame, x, y, time = trackObject(frame)
            if x == -1:
                return
            
            if not trackedFrames.has_key("frame1L"):
                trackedFrames["frame1L"] = (x, y, time)
                return
                
            if not trackedFrames.has_key("frame2L"):
                trackedFrames["frame2L"] = (x, y, time)
                return
            
            changeProgram('recieve')
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
    
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    camera.vflip = True
    camera.annotate_background = Color('black')
    
    camera.start_preview(alpha=200)
    analyzer = LeftPiCameraAnalysis(camera)
    camera.start_recording(analyzer, 'bgr')
    timeStart = datetime.datetime.now()
    
def stopCamera():
    camera.stop_recording()
    camera.stop_preview()
    
def closeTCP():
    conn.close()
    
def init():
    cv2.namedWindow("video")
    
    startTCP()
    startCamera()
    changeProgram('idle')
    
def shutdown():
    stopCamera()
    closeTCP()
    
def changeProgram(status):
    global program
    program = programStatus[status]
    camera.annotate_text = status
    
def checkProgram(status):
    return program == programStatus[status]

def recieve():
    global trackedFrames
    if checkProgram('recieve'):
        tmp = conn.recv(BUFFER_SIZE)
        data = json.loads(tmp)
        trackedFrames["frame1R"] = data['frame1']
        trackedFrames["frame2R"] = data['frame2']
        print trackedFrames
        
def analyze():
    if checkProgram('analyze'):
        return
    
def main():
    init()
    while True:
        
        recieve()
        analyze()
        
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break
        elif key == ord('s'):
            changeProgram('seek')
        elif key == ord('i'):
            changeProgram('idle')
        
    shutdown()
    
main()

    

       
