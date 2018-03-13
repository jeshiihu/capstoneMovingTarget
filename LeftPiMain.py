
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
        
with PiCamera(resolution = videoSize, framerate = fps) as camera:
    camera.awb_mode = 'off'
    camera.awb_gains = (1.4, 1.5)
    camera.vflip = True
    
##    camera.start_preview(alpha=128)
##    camera.stop_preview()
    
    with LeftPiCameraAnalysis(camera) as analyzer:
        camera.start_recording(analyzer, 'bgr')

        while True:
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
            
        camera.stop_recording()
       
