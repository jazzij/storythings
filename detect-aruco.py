"""
THIS CODE DEVELOPED USING ARUCO OPENCV LIB = https://docs.opencv.org/3.4/d5/dae/tutorial_aruco_detection.html
AND WITH HELP FROM PYTHON TUTORIAL PROVIDED BY : http://www.philipzucker.com/aruco-in-opencv/
"""
#ARUCO DETECT
import numpy as np
import cv2
import cv2.aruco as aruco

IMAGE_DIR = "./arcimg/"
SMALL_DICT = cv.aruco.DICT_4X4_50

'''
GENERATE DEFINE DICTIONARY
THIS IS RUN ONCE during system initiation
'''
def printMarkers():


'''
CAPTURE AN IMAGE 
'''
def captureScene():
    #1. Capture image
    #scene = cam.captureImage()
	testfile = IMAGE_DIR + "p5.jpg"

	scene = cv2.imread(testfile)
	resized = imutils.resize(scene, width=RESIZE_WIDTH)
	gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

	#generate a dictionary of markers (should be same as printed)
	aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
	parameters = aruco.DetectorParameters_create()
	
	'''
	DETECT MARKER IN IMAGE
	'''
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
	
	#test
	gray = aruco.drawDetectedMarkers(gray, corners)
	cv2.imshow('frame', gray)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
		
captureScene()

cv2.destroyAllWindows()
print ("complete")


