import cv2
from picamera import Color
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
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

def initSliders():
    master = Tk()
    scale = Scale(master, from_=0, to=180, label='hueLower', length=600, tickinterval=10, variable=hL)
    scale.pack()
    scale = Scale(master, from_=0, to=180, label='hueUpper', length=600, tickinterval=10, variable=hU)
    scale.pack()
    scale = Scale(master, from_=0, to=255, label='satLower', length=600, tickinterval=10, variable=sL)
    scale.pack()
    scale = Scale(master, from_=0, to=255, label='satUpper', length=600, tickinterval=10, variable=sU)
    scale.pack()
    scale = Scale(master, from_=0, to=255, label='valLower', length=600, tickinterval=10, variable=vL)
    scale.pack()
    scale = Scale(master, from_=0, to=255, label='valUpper', length=600, tickinterval=10, variable=vU)
    scale.pack()


def testHue(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerHSVBound, upperHSVBound)
    mask = cv2.erode(mask, None, iterations = 1)
    mask = cv2.dilate(mask, None, iterations = 1)
    cv2.imshow("Mask", mask)

def main():
    initSliders()
    camera = PiCamera(resolution = videoSize, framerate = fps)
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

main()