import cv2
from picamera import Color
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
from Tkinter import *
import io
import time
import threading
import picamera

fps = 60
videoSize = (640, 480)

lowerHSVBound = np.array([0, 0, 0])
upperHSVBound = np.array([255, 255, 255])

class Sliders(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        
    def callback(self):
        self.root.quit()
        
    def run(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        global hL, hU, sL, sU, vL, vU
        hL = Scale(self.root, from_=0, to=180, label='hueLower', length=600, tickinterval=10, orient=HORIZONTAL)
        hL.pack()
        hU = Scale(self.root, from_=0, to=180, label='hueUpper', length=600, tickinterval=10, orient=HORIZONTAL)
        hU.pack()
        sL = Scale(self.root, from_=0, to=255, label='satLower', length=600, tickinterval=10, orient=HORIZONTAL)
        sL.pack()
        sU = Scale(self.root, from_=0, to=255, label='satUpper', length=600, tickinterval=10, orient=HORIZONTAL)
        sU.pack()
        vL = Scale(self.root, from_=0, to=255, label='valLower', length=600, tickinterval=10, orient=HORIZONTAL)
        vL.pack()
        vU = Scale(self.root, from_=0, to=255, label='valUpper', length=600, tickinterval=10, orient=HORIZONTAL)
        vU.pack()
        self.root.mainloop()



def testHue(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerHSVBound, upperHSVBound)
    mask = cv2.erode(mask, None, iterations = 1)
    mask = cv2.dilate(mask, None, iterations = 1)
    cv2.imshow("Mask", mask)

def main():
    camera = PiCamera(resolution = videoSize, framerate = fps)
    rawCapture = PiRGBArray(camera)
    time.sleep(2)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        hLower = hL.get()
        hUpper = hU.get()
        sLower = sL.get()
        sUpper = sU.get()
        vLower = vL.get()
        vUpper = vU.get()

        if hLower > hUpper:
            hL.set(hUpper)
            hLower = hUpper

        if sLower > sUpper:
            sL.set(sUpper)
            sLower = sUpper

        if vLower > vUpper:
            vL.set(vUpper)
            vLower = vUpper

        global lowerHSVBound, upperHSVBound
        lowerHSVBound = np.array([hLower, sLower, vLower])
        upperHSVBound = np.array([hUpper, sUpper, vUpper])

        testHue(frame.array)

	rawCapture.truncate(0)

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break
    
sliders = Sliders()
main()
