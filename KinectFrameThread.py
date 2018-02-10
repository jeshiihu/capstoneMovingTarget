import numpy as np
import threading

class KinectFrameThread:

    def __init__(self):
        self.videoFrame = getVideoFrame()
        self.depthFrame = getDepthFrame()

    def start(self):
        Thread(target=self.update, args()).start()
        return self

    def update(self)
        while True:

            if self.stop:
                return

            self.videoFrame = getVideoFrame()
            self.depthFrame = getDepthFrame()

    def readVideoFrame(self):
        return self.videoFrame

    def readDepthFrame(self):
        return self.depthFrame

    def stopThread(self):
        self.stop = True

    def getVideoFrame():
        return freenect.sync_get_video()[0]

    def getDepthFrame():
        return freenect.sync_get_depth()[0]
