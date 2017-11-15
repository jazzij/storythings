#!/home/pi/.virtualenv/mtkcv/bin/python
#Adapted from pyimagesearch tutorial
#Enables a R-Pi camera module to capture images in numpy array format necessary for opencv use

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import datetime
import cv2

def captureImage():
    #initiatilize camera (sleep is time to let camera warm up, not needed if you put this in initial setup)
    camera = PiCamera()
    camera.resolution = (320, 240)	
    camera.zoom = (0.0, 0.1, 1.0, 0.8)	
    rawCapture = PiRGBArray(camera)
    time.sleep(0.1)

    #get image
    camera.capture( rawCapture, format="bgr")
    image = rawCapture.array

    #save image to file
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    filename = "./images/stcapture_{0}.jpg".format(timestamp)
    cv2.imwrite(filename, image)

    camera.close()
    return image

print('hello')
