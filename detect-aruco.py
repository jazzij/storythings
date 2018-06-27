"""
THIS CODE DEVELOPED USING ARUCO OPENCV LIB = https://docs.opencv.org/3.4/d5/dae/tutorial_aruco_detection.html
AND WITH HELP FROM PYTHON TUTORIAL PROVIDED BY : http://www.philipzucker.com/aruco-in-opencv/
"""
#ARUCO DETECT
import numpy as np
import cv2
import cv2.aruco as aruco

IMAGE_DIR = "./arcimg/"
DICT_MAX = 50  #: cv.aruco.DICT_4X4_50

'''
GENERATE DEFINE DICTIONARY
THIS IS RUN ONCE during system initiation
4x4 marker size = 16pix + border size = 1 (default) ==> 25 pix minimum ?
'''
def printMarkers():
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
	for i in range(0, DICT_MAX):
		img = aruco.drawMarker(aruco_dict, i, 200)
		filename = "marker_small-"+str(i)+".jpg"
		cv2.imwrite(filename, img)
		

'''
CAPTURE AN IMAGE 
'''
def captureScene():
	#1. Capture image
	#scene = cam.captureImage()
	testfile = "arucotest.jpg"

	scene = cv2.imread(testfile)
	#resized = imutils.resize(scene, width=RESIZE_WIDTH)
	gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
	
	'''
	DETECT MARKER IN IMAGE
	'''
	aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
	parameters = aruco.DetectorParameters_create()
	
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
	print(corners)
	
	#test
	gray = aruco.drawDetectedMarkers(gray, corners)
	
	cv2.imwrite("arc_detect_result.jpg", gray)
		
##########

captureScene()

cv2.destroyAllWindows()
print ("complete")


