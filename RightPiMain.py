
import cv2
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import time
import sys
import socket
import json
import numpy as np
import datetime
# Camera Settings
fps = 90
videoSize = (640, 480)

# Mask Settings
lowerHSVBound = np.array([60, 0, 100])
upperHSVBound = np.array([80, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'track' : 1 , 'send' : 2}

HOST = '169.254.48.206'
PORT = 5005
BUFFER_SIZE = 1024

class RightPiCameraAnalysis(PiRGBAnalysis):
    
    def analyze(self, frame):
        global program

        if program == programStatus['idle']:
            cv2.imshow("video", frame)
            return

        if program == programStatus['track']:
            if not frame1Left:
                # Begin thread here
                getFirstFrame(frame)
                return
            
            if not frame2Left:
                # Begin thread here
                getSecondFrame(frame)
                return

            program = programStatus['send']
            return


# Run program with "python main.py (left/right)"
def init():
    global timeStart
    timeStart = datetime.datetime.now()
    cv2.namedWindow("video")
    
    global program
    program = programStatus['idle']

    global tcpConnection
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.connect((HOST, PORT))
    tcpConnection.sendall("Hello from right Pi")
    data = tcpConnection.recv(BUFFER_SIZE)
    print "TCP init: ", data

    global camera
    camera = PiCamera(resolution = videoSize, framerate = fps)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.vflip = True
    analysis = RightPiCameraAnalysis(camera)
    camera.start_recording(analysis, format='bgr')
    time.sleep(2)

   
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

def getMicroseconds():
    time = datetime.datetime.now() - timeStart
    return (time.seconds*1000000) + time.microseconds

def getMilliseconds():
    return getMilliseconds()/1000

def getFirstFrame(frame):
    tmp = trackObject(frame)
    if x != -1:
        global frame1, videoFrame1
        videoFrame1 = tmp[0]
        frame1Left = (tmp[1], tmp[2], tmp[3])

def getSecondFrame(frame):
    tmp = trackObject(frame)
    if x != -1:
        global frame2, videoFrame2
        videoFrame2 = tmp[0]
        frame2 = (tmp[1], tmp[2], tmp[3])

def sendCoorToLeftPi():
    msg = {"frame1" : frame1, "frame2": frame2}
    json = json.dumps(msg)
    tcpConnection.sendall(json)


def main():
    global program
    init()
    while 1:

        if program == programStatus['idle']:
            data = tcpConnection.recv(BUFFER_SIZE)
            if data == "track":
                program = programStatus['track']

        if program == programStatus['send']:
            sendCoorToLeftPi()
            program = programStatus['idle']

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            camera.close()
            break
        elif key == 32:
            program = programStatus['seek']

    tcpConnection.close()



main()
                 
            
