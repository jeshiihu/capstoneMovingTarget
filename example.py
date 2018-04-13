#import the necessary modules
import freenect
import cv2
import numpy as np
import threading
 
prev = 0;
framecount = 0;

# https://naman5.wordpress.com/2014/06/24/experimenting-with-kinect-using-opencv-python-and-open-kinect-libfreenect/
#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array
 
#function to get depth image from kinect
def get_depth():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array


def DetectHSV():

    #get a frame from RGB camera
        frame = get_video()
        global framecount
        framecount = framecount + 1;


        #get a frame from depth sensor
        depth = get_depth()
        #display RGB image
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # cv2.imshow("HSV", hsv)

        # define the lower and upper boundaries of the colors in the HSV color space
        lower = {'red':(166, 84, 141), 'green':(66, 122, 129), 'blue':(97, 100, 117), 'yellow':(23, 59, 119)} #assign new item lower['blue'] = (93, 10, 0)
        upper = {'red':(186,255,255), 'green':(86,255,255), 'blue':(117,255,255), 'yellow':(54,255,255)}
         
        # define standard colors for circle around the object
        colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0), 'yellow':(0, 255, 217)}

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
        #for each color in dictionary check object in frame
        for key, value in upper.items():
            # construct a mask for the color from dictionary`1, then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            kernel = np.ones((9,9),np.uint8)
            mask = cv2.inRange(hsv, lower['yellow'], upper['yellow'])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                   
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
           
            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
           
                # only proceed if the radius meets a minimum size. Correct this value for your obect's size
                if radius > 0.5:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius), colors['yellow'], 2)
                    cv2.putText(frame,'yellow' + " ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'],2)
                
                cv2.putText(frame, 'x: ' + str(x) + ", y: " + str(y), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'],2)
                
         
            # show the frame to our screen
            cv2.imshow("Frame", frame)
            cv2.imshow("Depth", depth)
            height, width = frame.shape[:2]
            cv2.putText(frame, 'height: ' + str(height) + ", width: " + str(width), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['yellow'],2)


def printit():
    threading.Timer(1.0, printit).start()
    print str(framecount - prev) + " frames/sec"
    global prev
    prev = framecount

if __name__ == "__main__":
    #printit()
    while 1:
        # frame = get_video()
        # cv2.imshow("Frame", frame)

        DetectHSV()
        
        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()