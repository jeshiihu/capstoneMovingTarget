
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
fps = 90
videoSize = (640, 480)
videoCenter = (videoSize[0]/2, videoSize[1]/2)

# Mask Settings
lowerHSVBound = np.array([160, 175, 120])
upperHSVBound = np.array([180, 255, 255])
displayColors = {'yellow':(0, 255, 255), 'black':(0,0,0)}

# programStatus = { 'idle' : 0 , 'track' : 1 , 'send' : 2, 'test' : 3}
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
                time = getMilliseconds()
                try:
                    self.stream.seek(0)
                    self.analyze(bytes_to_rgb(self.stream, owner.camera.resolution), time)
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

    def analyze(self, frame, time):
        global trackedFrames
        
        if checkProgram('idle'):
            return

        if checkProgram('track'):
            tracked, xTopLeft, yTopLeft, time = trackObject(frame)
            x = videoCenter[0] - xTopLeft
            y = videoCenter[1] - yTopLeft
            cv2.putText(frame, 'X: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['yellow'], 2)
            cv2.putText(frame, 'Y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['yellow'], 2)
            cv2.putText(frame, 'Time: ' + str(time), (20,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, displayColors['yellow'], 2)
            
            if not trackedFrames.has_key("frame1R"):
                cv2.imwrite("throw/frame1.jpg", tracked)
##                print(x, y, time)
                trackedFrames["frame1R"] = (x, y, time)
                return
                
            if not trackedFrames.has_key("frame2R"):
                cv2.imwrite("throw/frame2.jpg", tracked)
##                print(x, y, time)
                trackedFrames["frame2R"] = (x, y, time)
                return
            
            setProgram('send')
            return

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
    global tcpConnection
    tcpConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpConnection.connect((HOST, PORT))
    tcpConnection.sendall("Hello from right Pi")
    data = tcpConnection.recv(BUFFER_SIZE)
    print "TCP init: ", data


def startCamera():
    global camera, timeStart
    camera = PiCamera(resolution = videoSize, framerate = fps)
    t.sleep(2)
    timeStart = datetime.datetime.now()
    
##    camera.shutter_speed = camera.exposure_speed
##    camera.exposure_mode = 'off'
##    g = camera.awb_gains
##    camera.awb_mode = 'off'
##    camera.awb_gains = g
##    camera.vflip = False
    camera.annotate_background = Color('black')
    
    camera.start_preview(alpha=200)
    output = ProcessOutput(camera)
    camera.start_recording(output, 'bgr')


def stopCamera():
    camera.stop_recording()
    camera.stop_preview()

def closeTCP():
    tcpConnection.shutdown(socket.SHUT_RDWR)
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
    init()
    while True:

        listenForCommand()
        sendFrames()


        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break

    shutdown()



main()
                 
            
