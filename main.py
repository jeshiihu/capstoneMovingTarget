
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from picamera.streams import PiCameraCircularIO
import time


fps = 90
videoSize = (640, 480)
rotation = 180

class FrameAnalysis(PiRGBAnalysis):
    def analyze(frame):
        (tracked, x, y) = trackObject(frame)
        cv2.imshow('video', tracked)

    def trackObject(video):
        
        hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations = 1)
        mask = cv2.dilate(mask, None, iterations = 1)
        
        # TEST
        cv2.imshow("Masked", mask)
        
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        if len(cnts) <= 0:
            return video, -1, -1

        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if radius < 6:
            return video, -1, -1
            
        cv2.circle(video, (int(x), int(y)), 1, colors['yellow'], 3)
        cv2.circle(video, (int(x), int(y)), int(radius), colors['yellow'], 2)
        cv2.putText(video, 'x: ' + str(x), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
        cv2.putText(video, 'y: ' + str(y), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)
        cv2.putText(video, 'radius: ' + str(radius), (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['black'], 2)

        return video, int(x), int(y)



def init():
    cv2.namedWindow("video")
    global camera, rawCapture
    camera = PiCamera(resolution = videoSize, framerate = fps)
    analysis = FrameAnalysis(camera)
##    rawCapture = PiRGBArray(camera, size = videoSize)
    camera.rotation = rotation
    camera.start_recording(analysis, format='bgr')
    time.sleep(2)
    
def getFrame():
    rawCapture.truncate(0)
    image = camera.capture(rawCapture, format='bgr', use_video_port=True)
    return image.array



def main():
    init()
    while 1:

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            camera.close()
            break

main()
                 
            
