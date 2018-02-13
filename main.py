import freenect
import cv2
import numpy as np
import frame_convert2
import math
from decimal import *
import datetime


def init():
    hoopArray = []
    for i in range(0,9):
        hoopArray.append(trackObject())

def getVideoFrame():
    return freenect.sync_get_video()[0]

def getDepthFrame():
    return freenect.sync_get_depth(0, freenect.DEPTH_MM)[0]

def getFrames():
    time = datetime.datetime.now()
    return (getVideoFrame(), getDepthFrame(), time.microsecond)

def trackObject(video, depth):

    hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)
    
    lower = np.array([50, 100, 0])
    upper = np.array([100, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations = 4)
    mask = cv2.dilate(mask, None, iterations = 2)
    
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
    x = 0
    y = 0
    if len(cnts) > 0:
        
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if radius > 6:
            cv2.circle(video, (int(x), int(y)), int(radius), (0,255,255), 2)
            return (int(x), int(y), depth[int(y)][int(x)])

    return -1

def translationTo3D(xFrame, yFrame, depth):
    horizDegPerPixel = Decimal(57) / Decimal(640)
    vertDegPerPixel = Decimal(43) / Decimal(480)

    xzAngle = (Decimal(-(320.0000-xFrame)) * horizDegPerPixel)
    yzAngle = (Decimal(240.0000-yFrame) * vertDegPerPixel)
    
    xDist = depth * math.sin(math.radians(xzAngle))
    yzHyp = depth * math.cos(math.radians(xzAngle))

    yDist = yzHyp * math.sin(math.radians(yzAngle))
    zDist = yzHyp * math.cos(math.radians(yzAngle))

    return (xDist, yDist, zDist)

def calculateXVelocity(x1, x2, timedelta):
    return ((x2-x1)/timedelta) * 1000

def calculateYVelocity(y1, y2, timedelta):
    return ((y2-y1)/timedelta) * 1000

def calculateZVelocity(z1, z2, timedelta):
    return ((z2-z1)/timedelta) * 1000


def test3DCoordinates():
    frames = getFrames()
    cv2.imshow("Video", frames[0])
    object = trackObject(frames[0], frames[1])
##    print(object[0], object[1], object[2])
    if (object == -1):
        return
    coordinates = translationTo3D(object[0], object[1], object[2])
    print(coordinates[0], coordinates[1], coordinates[2])
    
def testVelocity():
    while 1:
        if (cv2.waitKey(5) & 0xFF) == 27:
            return
        firstFrames = getFrames()
        cv2.imshow("Video", firstFrames[0])
        object = trackObject(firstFrames[0], firstFrames[1])
        if (object != -1):
            firstCoordinates = translationTo3D(object[0], object[1], object[2])
            break
    while 1:
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            return       
        frames = getFrames()
        cv2.imshow("Video", frames[0])
        object = trackObject(frames[0], frames[1])
        if (object != -1):
            coordinates = translationTo3D(object[0], object[1], object[2])
            xV = calculateXVelocity(firstCoordinates[0], coordinates[0], frames[2]-firstFrames[2])
            yV = calculateYVelocity(firstCoordinates[1], coordinates[1], frames[2]-firstFrames[2])
            zV = calculateZVelocity(firstCoordinates[2], coordinates[2], frames[2]-firstFrames[2])
            firstFrames = frames
            firstCoordinates = coordinates
            print(yV)
            
def saveFrames():
    print("saveFrames")
    while 1:
        if (cv2.waitKey(5) & 0xFF) == 27:
            return
        firstFrames = getFrames()
        cv2.imshow("Video", firstFrames[0])
        object = trackObject(firstFrames[0], firstFrames[1])
        if (object != -1):
            firstCoordinates = translationTo3D(object[0], object[1], object[2])
            break
    for i in range(0, 60):
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            return       
        frames = getFrames()
        cv2.imshow("Video", frames[0])
        object = trackObject(frames[0], frames[1])
        if (object != -1):
            coordinates = translationTo3D(object[0], object[1], object[2])
            xV = calculateXVelocity(firstCoordinates[0], coordinates[0], frames[2]-firstFrames[2])
            yV = calculateYVelocity(firstCoordinates[1], coordinates[1], frames[2]-firstFrames[2])
            zV = calculateZVelocity(firstCoordinates[2], coordinates[2], frames[2]-firstFrames[2])
            colors = {'yellow':(0, 0, 0)}
            cv2.putText(frames[0], 'y1: ' + str(firstCoordinates[1]), (500,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['yellow'], 2)
            cv2.putText(frames[0], 'y2: ' + str(coordinates[1]), (500,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['yellow'], 2)
            cv2.putText(frames[0], 't1: ' + str(firstFrames[2]), (500,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['yellow'], 2)
            cv2.putText(frames[0], 't2: ' + str(frames[2]), (500,140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['yellow'], 2)
            cv2.putText(frames[0], 'yV: ' + str(yV), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'], 2)
            cv2.imwrite("throw/throw" + str(i) + ".jpg", frames[0])
            firstFrames = frames
            firstCoordinates = coordinates


if __name__ == "__main__":
    while 1:
        test3DCoordinates()
        key = cv2.waitKey(100) & 0xFF
        if key == 27:
            break
        elif key == 32:
            saveFrames()
    cv2.destroyAllWindows()


        