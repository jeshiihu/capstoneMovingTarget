
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
import math
import serial

# CAMERA CONSTANTS
# Focal length of camera in um
cameraFocalLength = 3.29 * 1000
# Distance between cameras in um
cameraBaseLine = 214 * 1000
# Size of pixel on sensor in um
cameraPixelSize = 1.4 * 4
# Camera distortion factor (leaving as 0 for now)
cameraDistortion = 0

# Camera Settings
fps = 60
videoSize = (640, 480)
videoCenter = ((videoSize[0]/2), (videoSize[1]/2))

# Mask Settings
lowerHSVBound = np.array([160, 140, 90])
upperHSVBound = np.array([180, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'receive' : 3, 'analyze': 4, 'test': 5, 'topLeft' : 6, 'bottomRight' : 7, 'initY': 8}

HOST = '0.0.0.0'
PORT = 5005
BUFFER_SIZE = 128

curFrame = 0
framesGet = 10
throwAwayFrames1 = 0
throwAwayFrames2 = 0

topLeft = [[],[],[]]
bottomRight = [[],[],[]]
goalArea = {}
throw = []

scaleFactor = 1



def initSerial():
    ser = serial.Serial(
        port ='/dev/ttyUSB0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
)
    return ser

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
    
    
    if len(cnts) <= 0:
        return frame, -1, -1
    
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)

    if radius < 6:
        return frame, -1, -1
    
    
##    if checkProgram('track'):
    cv2.circle(frame, (int(x), int(y)), 1, displayColors['yellow'], 3)
    cv2.circle(frame, (int(x), int(y)), int(radius), displayColors['yellow'], 2)
##    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
##    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
##        cv2.imwrite("throw/frame.jpg", frame)
##        cv2.imwrite("throw/mask.jpg", mask)
                    

    return frame, int(x), int(y)

class LeftPiCameraAnalysis(PiRGBAnalysis):
    
    def __init__(self, camera):
        super(LeftPiCameraAnalysis, self).__init__(camera)
        self.camera = camera

    def analyze(self, frame):
        global trackedFrames, curFrame, topLeft, bottomRight
        
        if checkProgram('idle'):
            return
        
        if checkProgram('seek'):
            tracked, x, y = trackObject(frame)
            if x!= -1:
                setProgram('track')
                trackedFrames = {}
                curFrame = 0
                conn.sendall('track')
            return
            
        if checkProgram('track'):
            time = camera.frame.timestamp
##            if x == -1:
##                return
            
            if curFrame < throwAwayFrames1:
                curFrame += 1
                return
            
            if not trackedFrames.has_key("frame1Raw"):
                trackedFrames["frame1Raw"] = (frame, time)
                curFrame = 0
                return
            
            if curFrame < throwAwayFrames2:
                curFrame += 1
                return
                
            if not trackedFrames.has_key("frame2Raw"):
                trackedFrames["frame2Raw"] = (frame, time)
                return
            
            trackFrames()
            setProgram('receive')
##            setProgram('idle')
            return

        if checkProgram('topLeft'):
            if curFrame <= framesGet:
                (x, y, z) = getTopLeft(frame)
                topLeft[0].append(x)
                topLeft[1].append(y)
                topLeft[2].append(z)
                curFrame += 1
            else:
                getAverage('topLeft', topLeft)
                setProgram('idle')

        if checkProgram('bottomRight'):
            if curFrame < framesGet:
                (x, y, z) = getBottomRight(frame)
                bottomRight[0].append(x)
                bottomRight[1].append(y)
                bottomRight[2].append(z)
                curFrame += 1
            else:
                getAverage('bottomRight', bottomRight)
                print goalArea
                setProgram('idle')
                
        if checkProgram('initY'):
            yFactorAdjust(frame)
                
    
    
def startTCP(port):
    global conn
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.bind((HOST, port))
    tcpConnection.listen(1)
    conn, addr = tcpConnection.accept()
    data = conn.recv(BUFFER_SIZE)
    print "TCP init: ", data
    conn.sendall("Hello back from left Pi")
    
def startCamera():
    global camera, timeStart, conn
    conn.sendall("Picamera init")
    camera = PiCamera(resolution = videoSize, framerate = fps)
    time.sleep(2)
    
##    camera.shutter_speed = camera.exposure_speed
##    camera.exposure_mode = 'off'
##    g = camera.awb_gains
##    camera.awb_mode = 'off'
##    camera.awb_gains = g
##    camera.vflip = True
    camera.annotate_background = Color('black')
    
    conn.sendall("Start Preview")
    camera.start_preview(alpha=200)
    analyzer = LeftPiCameraAnalysis(camera)
    
    conn.sendall("Start Recording")
    camera.start_recording(analyzer, 'bgr')
    timeStart = datetime.datetime.now()
    
def stopCamera():
    camera.stop_recording()
    camera.stop_preview()
    
def closeTCP():
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    
def init(port):
    cv2.namedWindow("video")
    
    startTCP(port)
    startCamera()
    print "Done Init"
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

def receiveFrames():
    global trackedFrames
    if checkProgram('receive'):
        tmp = conn.recv(BUFFER_SIZE)
        data = json.loads(tmp)
        normalizeRightFrames(data['frame1R'], data['frame2R'])
##        trackedFrames["frame1R"] = data['frame1R']
##        trackedFrames["frame2R"] = data['frame2R']
        setProgram('analyze')

def normalizeRightFrames(frame1R, frame2R):
    global trackedFrames
    frame1L = trackedFrames["frame1L"]
    frame2L = trackedFrames["frame2L"]
    
    frame1RY = frame1R[1] + yAdjust
    frame2RY = frame2R[1] + yAdjust

    try:
        slope = (float(frame2RY)-float(frame1RY)) / (float(frame2R[0])-float(frame1R[0]))
    except ZeroDivisionError:
        print "stupid 0's"

    if (slope != 0):
        x1R = round(((frame1L[1]-frame1RY) / slope) + frame1R[0])
        x2R = round(((frame2L[1]-frame2RY) / slope) + frame2R[0])
    else:
        xSpeed = (frame2R[0] - frame1R[0]) / (frame2R[2]-frame1R[2])
        x1R = (xSpeed * (frame1R[2]-frame1L[2])) + frame1R[0]
        x2R = (xSpeed * (frame2R[2]-frame2L[2])) + frame2R[0]

    frame1RFixed = (x1R-10, frame1L[1], frame1L[2])
    frame2RFixed = (x2R-10, frame2L[1], frame2L[2])

    trackedFrames["frame1R"] = frame1RFixed
    trackedFrames["frame2R"] = frame2RFixed
    

def getTopLeft(frame):
    conn.sendall("track1")
    (tracked, x, y) = trackObject(frame)
    leftFrame = (x, y, time)
    tmp = conn.recv(BUFFER_SIZE)
    data = json.loads(tmp)
    rightFrame = data['frame1']
    (x, y, z) = getMMCoor(leftFrame, rightFrame)
    return x, y, z

def getBottomRight(frame):
    conn.sendall("track1")
    (tracked, x, y) = trackObject(frame)
    leftFrame = (x, y, time)
    tmp = conn.recv(BUFFER_SIZE)
    data = json.loads(tmp)
    rightFrame = data['frame1']
    (x, y, z) = getMMCoor(leftFrame, rightFrame)
    return x, y, z

def yFactorAdjust(frame):
    conn.sendall("track1")
    (tracked, x, y) = trackObject(frame)
    leftFrame = (x, y, time)
    tmp = conn.recv(BUFFER_SIZE)
    data = json.loads(tmp)
    rightFrame = data['frame1']
    global yAdjust
    yAdjust = leftFrame[1]-rightFrame[1]
    print "yADjedus: ", yAdjust
    setProgram('idle')
    
def getAverage(goalAreaLabel, xyzList):
    average = []
    for list in xyzList:
        if list:
            average.append(sum(list)/len(list))
        
    goalArea[goalAreaLabel] = average
    
def trackFrames():
    
    frame1 = trackedFrames['frame1Raw']
    frame2 = trackedFrames['frame2Raw']

                
    tracked1, x1, y1 = trackObject(frame1[0])
    tracked2, x2, y2 = trackObject(frame2[0])
    
    cv2.putText(tracked1, 'X: ' + str(x1), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked1, 'Y: ' + str(y1), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked1, 'Time: ' + str(frame1[1]), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)

    cv2.putText(tracked2, 'X: ' + str(x2), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked2, 'Y: ' + str(y2), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(tracked2, 'Time: ' + str(frame2[1]), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    
    cv2.imwrite("throw/frame1.jpeg", tracked1)
    cv2.imwrite("throw/frame2.jpeg", tracked2)
    
    trackedFrames['frame1L'] = (x1, y1, frame1[1])
    trackedFrames['frame2L'] = (x2, y2, frame2[1])
                

def getMMCoor(leftFrame, rightFrame):
    (x, y, z) = getCoordinates(leftFrame[0], leftFrame[1], rightFrame[0], rightFrame[1])
    return x, y, z

def analyzeFrames():
    if checkProgram('analyze'):
        pos1 = getMMCoor(trackedFrames["frame1L"], trackedFrames["frame1R"])
        pos2 = getMMCoor(trackedFrames["frame2L"], trackedFrames["frame2R"])

        (x,y,z) = getPrediction(pos1, pos2, trackedFrames["frame1L"][2], trackedFrames["frame2L"][2])
    
        setProgram('idle')
        
def sumOfSquares(a, b, c):
    return math.sqrt((a**2)+(b**2)+(c**2))

def getCoordinates(leftI, leftJ, rightI, rightJ):
    (leftX, leftY) = fromCenter(leftI, leftJ)
    (rightX, rightY) = fromCenter(rightI, rightJ)


##    z = ((cameraBaseLine * cameraFocalLength) / ((leftX - rightX) * cameraPixelSize)) * scaleFactor
    z = 3800000
    x = (leftX * cameraPixelSize) * (z / cameraFocalLength) 
    y = (leftY * cameraPixelSize) * (z / cameraFocalLength)
    
    return x, y, z

def mmToIn(x, y, z):
    return x/25.4, y/25.4, z/25.4

def getPrediction(pos1, pos2, time1, time2):
    topLeft = goalArea['topLeft']
    bottomRight = goalArea['bottomRight']
    
    xGoal = (topLeft[0] + bottomRight[0]) / 2
    
    (x1, y1, z1) = (pos1[0], pos1[1], pos1[2])
    (x2, y2, z2) = (pos2[0], pos2[1], pos2[2])
    
    xDiff = x2-x1
    yDiff = y2-y1
    zDiff = z2-z1
    timeDiff = time2-time1
    

    
    xVelocity = xDiff/timeDiff
    yVelocity = yDiff/timeDiff
    zVelocity = zDiff/timeDiff
    
    timeHit = abs((xGoal- x1)/1000000) / abs(xVelocity)
    
    yHit = ((yVelocity * timeHit) - (0.5*9.81*(timeHit**2)))*1000000 + y1
    zHit = (zVelocity * timeHit)*1000000 + z1
    
    print yHit
    
    xPoss, yPoss = getMotorPossibilities(topLeft[0], topLeft[1], bottomRight[0], bottomRight[1])
    nearestX, nearestY = getClosestMotorPoint(xGoal, yHit, xPoss, yPoss)
    nearestX, nearestY = changeToMotorDivisions(nearestX, nearestY)
    print (0, nearestY)
    sendToFPGA(0,nearestY)
    
    return xGoal, yHit, zHit
    
    

def getMotorPossibilities(x1, z1, x2, z2):
    xPossibilities = np.linspace(x1, x2, 33)
    zPossibilities = np.linspace(z1, z2, 33)
    return xPossibilities, zPossibilities

def findNearestPosition(array, value):
    idx = (np.abs(array-value)).argmin()
    return idx

def getClosestMotorPoint(xEnd, zEnd, xPossibilities, zPossibilities):
    nearestX = findNearestPosition(xPossibilities, xEnd)
    nearestZ = findNearestPosition(zPossibilities, zEnd)
    return nearestX, nearestZ

def changeToMotorDivisions(nearestX, nearestZ):
    return nearestX-16, 16-nearestZ    

def sendToFPGA(nearestX, nearestZ):
    global ser
    if ser.isOpen():
        input = str(nearestX) + ',' + str(nearestZ)
##        input = str(-4) + ',' + str(5)
        ser.write(input + '\n')
        out = ''
        time.sleep(0.5)
    
def fromCenter(i,j):
    return (i - videoCenter[0]), (videoCenter[1] - j)

##def reverseDistortion(i, j):
##    
##    (iCenter, jCenter) = fromCenter(i,j)
##    
##    
##    xDistorted = (iCenter) * cameraPixelSize
##    yDistorted = (jCenter) * cameraPixelSize
####    xDistorted = (i) * cameraPixelSize
####    yDistorted = ((abs(j - 480)) * cameraPixelSize)
##    rDSquared = (xDistorted * xDistorted) + (yDistorted * yDistorted)
##    x = xDistorted * (1 + (cameraDistortion * rDSquared))
##    y = yDistorted * (1 + (cameraDistortion * rDSquared))
##    return x, y

def velocity(pos1, pos2, timedelta):
    return ((pos2-pos1)/float(timedelta))

def getVelocities(pos1, pos2, time1, time2):
    timedelta = time2-time1
    xVel = velocity(pos1[0], pos2[0], timedelta)
    yVel = velocity(pos1[1], pos2[1], timedelta)
    zVel = velocity(pos1[2], pos2[2], timedelta)
    return xVel, yVel, zVel
    


##def test():
##    if checkProgram('test'):
##        conn.sendall('test')
##        while True:
##            
##            key = cv2.waitKey(5) & 0xFF
##            if key == ord('e'):
##                conn.sendall('idle')


    
def main():
    init(int(sys.argv[1]))
    global curFrame, topLeft, bottomRight, ser
    ser = initSerial()
    while True:
        
        receiveFrames()
        analyzeFrames()
##        test()
        
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break
        elif key == ord('s'):
            setProgram('seek')
        elif key == ord('i'):
            setProgram('idle')
        elif key == ord('t'):
            curFrame = 0
            topLeft = [[],[],[]]
            setProgram('topLeft')
        elif key == ord('b'):
            bottomRight = [[],[],[]]
            curFrame = 0
            setProgram('bottomRight')
##        elif key == ord('t'):
##            setProgram('test')
        elif key == ord('y'):
            setProgram('initY')
        
    shutdown()
    
main()

    

       
