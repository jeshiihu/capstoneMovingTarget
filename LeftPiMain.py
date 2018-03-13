
import cv2
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
from picamera.streams import PiCameraCircularIO
import time
import sys
import socket
import numpy as np


# Camera Settings
fps = 30
videoSize = (300, 300)

# Mask Settings
lowerHSVBound = np.array([60, 0, 100])
upperHSVBound = np.array([80, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

class LeftPiCameraAnalysis(PiRGBAnalysis):
    
    def __init__(self, camera):
        super(LeftPiCameraAnalysis, self).__init__(camera)

    def analyze(self, frame):
        cv2.imshow("frame", frame)

def getMicroseconds():
    time = datetime.datetime.now() - timeStart
    return (time.seconds*1000000) + time.microseconds

def getMilliseconds():
    return getMilliseconds()/1000

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
        
    cv2.circle(frame, (int(x), int(y)), 1, colors['yellow'], 3)
    cv2.circle(frame, (int(x), int(y)), int(radius), colors['yellow'], 2)
    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
    cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)

    return frame, int(x), int(y), time
        
with PiCamera(resolution = videoSize, framerate = fps) as camera:
    camera.awb_mode = 'off'
    camera.awb_gains = (1.4, 1.5)
    camera.vflip = True
    
##    camera.start_preview(alpha=128)
##    camera.stop_preview()
    
    with LeftPiCameraAnalysis(camera) as analyzer:
        camera.start_recording(analyzer, 'bgr')
        timeStart = datetime.datetime.now()

        while True:
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
            
        camera.stop_recording()
       
