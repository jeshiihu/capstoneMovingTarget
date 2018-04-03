
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
fps = 90
videoSize = (640, 480)
videoCenter = (videoSize[0]/2, videoSize[1]/2)

# Mask Settings
lowerHSVBound = np.array([160, 175, 120])
upperHSVBound = np.array([180, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

programStatus = { 'idle' : 0 , 'seek' : 1 , 'track' : 2 , 'receive' : 3, 'analyze': 4, 'test': 5, 'topLeft' : 6, 'bottomRight' : 7}

HOST = '0.0.0.0'
PORT = 5005
BUFFER_SIZE = 128

goalArea = {}

def getMicroseconds():
    time = datetime.datetime.now() - timeStart
    time = (time.seconds*1000000) + time.microseconds
    return time

def getMilliseconds():
    time = getMicroseconds()/1000
    return time

def trackObject(frame, time):
    
##    time = getMilliseconds()
    
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
    
    
##    if checkProgram('track'):
    cv2.circle(frame, (int(x), int(y)), 1, displayColors['yellow'], 3)
    cv2.circle(frame, (int(x), int(y)), int(radius), displayColors['yellow'], 2)
##    cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
##    cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(frame, 'Radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
    cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['black'], 2)
##        cv2.imwrite("throw/frame.jpg", frame)
##        cv2.imwrite("throw/mask.jpg", mask)
                    

    return frame, int(x), int(y), time

class ImageProcessor(threading.Thread):
    def __init__(self, owner):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.owner = owner
        self.start()

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    self.analyze(bytes_to_rgb(self.stream, owner.camera.resolution))
                    self.owner.done = True
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #self.owner.done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the available pool
                    with self.owner.lock:
                        self.owner.pool.append(self)

    def analyze(self, frame):
        global trackedFrames
        time = getMilliseconds()
        
        if checkProgram('idle'):
            return
        
        if checkProgram('seek'):
            tracked, x, y, time = trackObject(frame, time)
            if x!= -1:
                setProgram('track')
                trackedFrames = {}
                conn.sendall('track')
##            print "Out of Frame" if x == -1 else (x, y, time)
            return
            
        if checkProgram('track'):
            tracked, xTopLeft, yTopLeft, time = trackObject(frame, time)
            x = videoCenter[0] - xTopLeft
            y = videoCenter[1] - yTopLeft
            
            cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['yellow'], 2)
            cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['yellow'], 2)
            
##            if x == -1:
##                return
            
            if not trackedFrames.has_key("frame1L"):
                cv2.imwrite("throw/frame1.jpeg", tracked)
                trackedFrames["frame1L"] = (x, y, time)
                return
                
            if not trackedFrames.has_key("frame2L"):
                cv2.imwrite("throw/frame2.jpeg", tracked)
                trackedFrames["frame2L"] = (x, y, time)
                return
            
            setProgram('receive')
##            setProgram('idle')
            return

        if checkProgram('topLeft'):
            getTopLeft(frame)

        if checkProgram('bottomRight'):
            getBottomRight(frame)

class ProcessOutput(object):
    def __init__(self, camera):
        self.camera = camera
        self.done = False
        # Construct a pool of 4 image processors along with a lock
        # to control access between threads
        self.lock = threading.Lock()
        self.pool = [ImageProcessor(self) for i in range(4)]
        self.processor = None

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame; set the current processor going and grab
            # a spare one
            if self.processor:
                self.processor.event.set()
            with self.lock:
                if self.pool:
                    self.processor = self.pool.pop()
                else:
                    # No processor's available, we'll have to skip
                    # this frame; you may want to print a warning
                    # here to see whether you hit this case
                    self.processor = None
        if self.processor:
            self.processor.stream.write(buf)

    def flush(self):
        # When told to flush (this indicates end of recording), shut
        # down in an orderly fashion. First, add the current processor
        # back to the pool
        if self.processor:
            with self.lock:
                self.pool.append(self.processor)
                self.processor = None
        # Now, empty the pool, joining each thread as we go
        while True:
            with self.lock:
                try:
                    proc = self.pool.pop()
                except IndexError:
                    pass # pool is empty
            proc.terminated = True
            proc.join()    
    
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
    output = ProcessOutput(camera)
    camera.start_recording(output, 'bgr')
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

def receiveFrames():
    global trackedFrames
    if checkProgram('receive'):
        tmp = conn.recv(BUFFER_SIZE)
        data = json.loads(tmp)
        normalizeRightFrames(data['frame1R'], data['frame2R'])
        setProgram('analyze')

def normalizeRightFrames(frame1R, frame2R):
    global trackedFrames
    frame1L = trackedFrames["frame1L"]
    frame2L = trackedFrames["frame2L"]

    print('original right frame1: x: ', frame1R[0], 'y: ', frame1R[1], 'time: ', frame1R[2])
    print('original right frame2: x: ', frame2R[0], 'y: ', frame2R[1], 'time: ', frame2R[2])
    
    print('left frame1: x: ', frame1L[0], 'y: ', frame1L[1], 'time: ', frame1L[2])
    print('left frame2: x: ', frame2L[0], 'y: ', frame2L[1], 'time: ', frame2L[2])
    
    slope = (float(frame2R[1])-float(frame1R[1])) / (float(frame2R[0])-float(frame1R[0]))
    print('slope: ', slope)

    if (slope != 0):
        x1R = round(((frame1L[1]-frame1R[1]) / slope) + frame1R[0])
        x2R = round(((frame2L[1]-frame2R[1]) / slope) + frame2R[0])
    else:
        xSpeed = (frame2R[0] - frame1R[0]) / (frame2R[2]-frame1R[2])
        x1R = (xSpeed * (frame1R[2]-frame1L[2])) + frame1R[0]
        x2R = (xSpeed * (frame2R[2]-frame2L[2])) + frame2R[0]

    frame1RFixed = (x1R, frame1L[1], frame1L[2])
    frame2RFixed = (x2R, frame2L[1], frame2L[2])

    print('fixed right frame1: x: ', frame1RFixed[0], 'y: ', frame1RFixed[1], 'time: ', frame1RFixed[2])
    print('fixed right frame2: x: ', frame2RFixed[0], 'y: ', frame2RFixed[1], 'time: ', frame2RFixed[2])
   
    trackedFrames["frame1R"] = frame1RFixed
    trackedFrames["frame2R"] = frame2RFixed

def getTopLeft(frame):
    conn.sendall("topLeft")
    (_, x, y, time) = trackObject(frame)
    leftFrame = (x, y, time)
    tmp = conn.recv()
    data = json.loads(tmp)
    rightFrame = data['rightFrame']
    (x, y, z) = getMMCoor(leftFrame, rightFrame)
    goalArea['topLeft'] = (x, y, z)

def getBottomRight(frame):
    conn.sendall("bottomRight")
    (_, x, y, time) = trackObject(frame)
    leftFrame = (x, y, time)
    tmp = conn.recv()
    data = json.loads(tmp)
    rightFrame = data['rightFrame']
    (x, y, z) = getMMCoor(leftFrame, rightFrame)
    goalArea['bottomRight'] = (x, y, z)
    print goalArea

def getMMCoor(leftFrame, rightFrame):
    (x, y, z) = getCoordinates(leftFrame[0], leftFrame[1], rightFrame[0], rightFrame[1])
    return x, y, z

def analyzeFrames():
    if checkProgram('analyze'):
        pos1 = getMMCoor(trackedFrames["frame1L"], trackedFrames["frame1R"])
        pos2 = getMMCoor(trackedFrames["frame2L"], trackedFrames["frame2R"])
        velocities = getVelocities(pos1, pos2, trackedFrames["frame1L"][2], trackedFrames["frame2L"][2])
        print('Position 1: ', pos1, 'Position 2: ', pos2, 'Frame 1 time: ', trackedFrames["frame1L"][2], 'Frame 2 time: ', trackedFrames["frame2L"][2])
        print ('Total velocity in m/s: ', sumOfSquares(velocities[0], velocities[1], velocities[2]))
        print ('xVel: ', velocities[0], 'yVel: ', velocities[1], 'zVel: ', velocities[2])
        setProgram('idle')
        
def sumOfSquares(a, b, c):
    return math.sqrt((a**2)+(b**2)+(c**2))

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
    init()
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
            setProgram('topLeft')
        elif key == ord('b'):
            setProgram('bottomRight')
##        elif key == ord('t'):
##            setProgram('test')
        
    shutdown()
    
main()

    

       
