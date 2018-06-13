#ARUCO DETECT
import numpy as np
import cv2
import cv2.aruco as aruco

IMAGE_DIR = "./arcimg/"

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


