
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
# Camera Settings
fps = 20
videoSize = (800, 800)

# Mask Settings
lowerHSVBound = np.array([60, 0, 100])
upperHSVBound = np.array([80, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'track' : 1 , 'send' : 2}

HOST = '169.254.48.206'
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
        
##    cv2.circle(frame, (int(x), int(y)), 1, colors['yellow'], 3)
##    cv2.circle(frame, (int(x), int(y)), int(radius), colors['yellow'], 2)
##    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
##    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
##    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
##    cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)

    return frame, int(x), int(y), time

class RightPiCameraAnalysis(PiRGBAnalysis):
    
    def __init__(self, camera):
        super(RightPiCameraAnalysis, self).__init__(camera)

    def analyze(self, frame):
        global trackedFrames

        if checkProgram('idle'):
            return

        if checkProgram('track'):
            frame, x, y, time = trackObject(frame)
##            if x == -1:
##                return
            
            if not trackedFrames.has_key("frame1R"):
                print(x, y, time)
                trackedFrames["frame1R"] = (x, y, time)
                return
                
            if not trackedFrames.has_key("frame2R"):
                print(x, y, time)
                trackedFrames["frame2R"] = (x, y, time)
                return
            
            setProgram('send')
            return

def startTCP():
    global tcpConnection
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.connect((HOST, PORT))
    tcpConnection.sendall("Hello from right Pi")
    data = tcpConnection.recv(BUFFER_SIZE)
    print "TCP init: ", data

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
    analyzer = RightPiCameraAnalysis(camera)
    camera.start_recording(analyzer, 'bgr')
    timeStart = datetime.datetime.now()

def stopCamera():
    camera.stop_recording()
    camera.stop_preview()

def closeTCP():
    tcpConnection.close()

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

def sendFrames():
    if checkProgram('send'):
        jsonFrames = json.dumps(trackedFrames)
        tcpConnection.sendall(jsonFrames)
        setProgram('idle')


def listenForCommand():
    global trackedFrames
    if checkProgram('idle'):
        data = tcpConnection.recv(BUFFER_SIZE)
        if data == 'track':
            setProgram('track')
            trackedFrames = {}
            

def main():
    init()
    while True:

        listenForCommand()
        sendFrames()


        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break

    shutdown()



main()
                 
            
