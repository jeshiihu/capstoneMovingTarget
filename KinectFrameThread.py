import numpy as np
import threading
import freenect

class KinectFrameThread:

    def __init__(self):
        self.videoFrame = freenect.sync_get_video()[0]
        self.depthFrame = freenect.sync_get_depth()[0]
        self.stop = False

    def start(self):
        print "thread start"
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            print "update start"

            if self.stop:
                return

            self.videoFrame = freenect.sync_get_video()[0]
            self.depthFrame = freenect.sync_get_depth()[0]

    def readVideoFrame(self):
        return self.videoFrame

    def readDepthFrame(self):
        return self.depthFrame

    def stopThread(self):
        freenect.sync_stop()
        self.stop = True

