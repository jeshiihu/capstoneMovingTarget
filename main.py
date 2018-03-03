
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from picamera.streams import PiCameraCircularIO
import time


fps = 90
videoSize = (640, 480)
rotation = 180

def init():
    cv2.namedWindow("video")
    global camera, rawCapture
    camera = PiCamera(resolution = videoSize, framerate = fps)
    rawCapture = PiRGBArray(camera, size = videoSize)
    camera.rotation = rotation
    time.sleep(2)
    
def getFrame():
    rawCapture.truncate(0)
    image = camera.capture(rawCapture, format='bgr', use_video_port=True)
    return image.array





    key = cv2.waitKey(5) & 0xFF
    if key == 27:
        camera.close()
        break
                 
            