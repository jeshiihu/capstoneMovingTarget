import freenect
import cv2
import numpy as np
import frame_convert2
import math

class kinect:

    def init():
        hoopArray = []
        for i in range(0,9):
            hoopArray.append(trackObject())

    def getVideoFrame():
        return freenect.sync_get_video()[0]

    def getDepthFrame():
        return freenect.sync_get_depth()[0]

    def getFrames():
        return (getVideoFrame(), getDepthFrame())

    def trackObject(video, depth):

        hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)
        
        lower = np.array([50, 100, 0])
        upper = np.array([100, 255, 255])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations = 2)
    ##    mask = cv2.dilate(mask, None, iterations = 2)
        
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
        x = 0
        y = 0
        if len(cnts) > 0:
            
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if radius > 6:
                return (int(x), int(y), depth[int(y)][int(x)])

        return -1

     def translationTo3D(xFrame, yFrame, depth):
        float horizDegPerPixel = 640 / 57
        float vertDegPerPixel = 480 / 43

        xzAngle = -(320-xFrame) * horizDegPerPixel
        yzAngle = (240-yFrame) * vertDegPerPixel

        xDist = depth * math.sin(math.radians(xzAngle))
        yzHyp = depth * math.cos(math.radians(xzAngle))

        yDist = yzHyp * math.sin(math.radians(yzAngle))
        zDist = yzHyp * math.cos(math.radians(yzAngle))

        return (xDist, yDist, zDist)

    def get3DCoordinates():
        (video, depth) = getFrames()
        (xFrame, yFrame, depth) = trackObject(video, depth)
        (x, y, z) = translationTo3D(xFrame, yFrame, depth)
        print((x, y, z))

while 1:
    get3DCoordinates()

    if (cv2.waitKey(5) & 0xFF) == 27:
            kinect.stopThread()
            fpsStop = True
            break
        
cv2.destroyAllWindows()


        