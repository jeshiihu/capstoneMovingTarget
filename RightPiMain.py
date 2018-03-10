
import cv2
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import time
import sys
import socket
import json

# Camera Settings
fps = 90
videoSize = (640, 480)

# Mask Settings
lowerHSVBound = np.array([60, 0, 100])
upperHSVBound = np.array([80, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'reset' : 3}

HOST = '0.0.0.0'
PORT = 5005
BUFFER_SIZE = 1024

class RightPiCameraAnalysis(PiRGBAnalysis):
    
    def analyze(self, frame):
        # Can be threaded to pipeline frames if needed
        processFrame(frame)


# Run program with "python main.py (left/right)"
def init():
    cv2.namedWindow("video")
    program = programStatus['idle']

    global tcpConnection
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.connect((HOST, PORT))
    tcpConnection.sendall("Hello from right Pi")
    date tcpConnection.recv(BUFFER_SIZE)
    print "TCP init: ", data

    camera = PiCamera(resolution = videoSize, framerate = fps)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.vflip = True
    analysis = RightPiCameraAnalysis(camera)
    camera.start_recording(analysis, format='bgr')
    time.sleep(2)

def processFrame(frame):
    global frame1, frame 2
    if program == programStatus['idle']:
        return

    elif program == programStatus['track']:
        if frame1 is None:
            (frame1, x1, y1, time1) = getTrackedFrame(frame)
            return
        if frame2 is None:
            (frame2, x2, y2, time2) = getTrackedFrame(frame)
            return
        
              
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

def main():
    init()

    while 1:
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            camera.close()
            break


main()
                 
            
