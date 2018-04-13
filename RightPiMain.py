
import cv2
from picamera import Color
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import datetime
import time as t
import sys
import json
import socket
import numpy as np
# Camera Settings
fps = 60
videoSize = (640,480)
videoCenter = (videoSize[0]/2, videoSize[1]/2)

# Mask Settings
lowerHSVBound = np.array([160, 140, 90])
upperHSVBound = np.array([180, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

# programStatus = { 'idle' : 0 , 'track' : 1 , 'send' : 2, 'test' : 3}
programStatus = { 'idle' : 0 , 'track' : 1 , 'send' : 2, 'track1' : 3}

HOST = '169.254.48.206'
PORT = 5005
BUFFER_SIZE = 128

throwAwayFrames = 3
curFrame = 0

def getMicroseconds():
    time = datetime.datetime.now() - timeStart
    time = (time.seconds*1000000) + time.microseconds
    return time

def getMilliseconds():
    time = getMicroseconds()/1000
    return time

def trackObject(frame):
   
##    time = getMilliseconds()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerHSVBound, upperHSVBound)
    mask = cv2.erode(mask, None, iterations = 1)
    mask = cv2.dilate(mask, None, iterations = 1)
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
##    cv2.imshow("mask", mask)
    
    
    if len(cnts) <= 0:
        return frame, -1, -1
    
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)

    if radius < 6:
        return frame, -1, -1
    
##    if checkProgram('track'):
##        
    cv2.circle(frame, (int(x), int(y)), 1, displayColors['yellow'], 3)
    cv2.circle(frame, (int(x), int(y)), int(radius), displayColors['yellow'], 2)
##    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
##    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['yellow'], 2)
##    cv2.imwrite("throw/frame.jpg", frame)
##    cv2.imwrite("throw/mask.jpg", mask)

    return frame, int(x), int(y)

class RightPiCameraAnalysis(PiRGBAnalysis):
    
    def __init__(self, camera):
        super(RightPiCameraAnalysis, self).__init__(camera)
        self.camera = camera

    def analyze(self, frame):
        global trackedFrames, curFrame
        
        if checkProgram('idle'):
            return


        # if checkProgram('test'):
        # 	frame x, y, time = trackObject(frame)
        # 	trackedFrames = {}
        # 	if not trackedFrames.has_key("frame1R")
        # 		return
        # 	else
        # 		jsonFrames = json.dumps(trackedFrames)
       	# 		tcpConnection.sendall(jsonFrames)
       	# 		return


        if checkProgram('track'):
            time = camera.frame.timestamp/1000

            if not trackedFrames.has_key("frame1Raw"):
##                print "Frame1", camera.frame.index, time
##                cv2.imwrite("throw/frame1.jpg", tracked)
                trackedFrames["frame1Raw"] = (frame, time)
                curFrame = 0
                return
            
            if curFrame < throwAwayFrames:
                curFrame += 1
                return
            
            
            if not trackedFrames.has_key("frame2Raw"):
##                print "Frame2", camera.frame.index, camera.frame.timestamp/1000
##                cv2.imwrite("throw/frame2.jpg", tracked)
##                print(x, y, time)
                trackedFrames["frame2Raw"] = (frame, time)
                return
            
            trackFrames()
            setProgram('send')
            return
        
        if checkProgram('track1'):
            tracked, x, y = trackObject(frame)
            time = camera.frame.timestamp/1000
            
##            if x == -1:
##                return
            cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
            cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
            cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
            
            trackedFrames['frame1'] = (x, y, time)
            t.sleep(0.1)
            setProgram('send')
            return

def startTCP(port):
    global tcpConnection
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.connect((HOST, port))
    tcpConnection.sendall("Hello from right Pi")
    data = tcpConnection.recv(BUFFER_SIZE)
    print "TCP init: ", data


def startCamera():
    global camera, timeStart, tcpConnection
    tcpConnection.recv(BUFFER_SIZE)
    camera = PiCamera(resolution = videoSize, framerate = fps)
    t.sleep(2)
    
##    camera.shutter_speed = camera.exposure_speed
##    camera.exposure_mode = 'off'
##    g = camera.awb_gains
##    camera.awb_mode = 'off'
##    camera.awb_gains = g
##    camera.vflip = False
    camera.annotate_background = Color('black')
    tcpConnection.recv(BUFFER_SIZE)

    camera.start_preview(alpha=200)
    analyzer = RightPiCameraAnalysis(camera)
    tcpConnection.recv(BUFFER_SIZE)

    camera.start_recording(analyzer, 'bgr')
    timeStart = datetime.datetime.now()
    

def stopCamera():
    camera.stop_recording()
    camera.stop_preview()

def closeTCP():
    tcpConnection.shutdown(socket.SHUT_RDWR)
    tcpConnection.close()

def init(port):
    cv2.namedWindow("video")
    
    startTCP(port)
    startCamera()
    print('finished init')
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

def trackFrames():
    
    frame1 = trackedFrames.pop('frame1Raw')
    frame2 = trackedFrames.pop('frame2Raw')
    
##    print len(frame1[0][0])
    
    tracked1, x1, y1 = trackObject(frame1[0])
    tracked2, x2, y2 = trackObject(frame2[0])

##            if x == -1:
##                return
    cv2.putText(tracked1, 'X: ' + str(x1), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked1, 'Y: ' + str(y1), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked1, 'Time: ' + str(frame1[1]), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)

    cv2.putText(tracked2, 'X: ' + str(x2), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked2, 'Y: ' + str(y2), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked2, 'Time: ' + str(frame2[1]), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    
    cv2.imwrite('throw/frame1.jpeg', tracked1)
    cv2.imwrite('throw/frame2.jpeg', tracked2)
    
    trackedFrames['frame1R'] = (x1, y1, frame1[1])
    trackedFrames['frame2R'] = (x2, y2, frame2[1])

def listenForCommand():
    global trackedFrames
    if checkProgram('idle'):
        data = tcpConnection.recv(BUFFER_SIZE)
##        if data == 'track':
##            setProgram('track')
##            trackedFrames = {}
        trackedFrames = {}
        setProgram(data)
        # if data == 'test':
        	# setProgram('test')
        	# trackedFrames = {}
    # if checkProgram('test'):
    	# data = tcpConnection.recv(BUFFER_SIZE)
        # if data == 'endTest':
        	# setProgram('idle')
            

def main():
    init(int(sys.argv[1]))

    while True:

        listenForCommand()
        sendFrames()


        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break

    shutdown()



main()
                 
            
