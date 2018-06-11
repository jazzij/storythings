import os, math
import cv2
import imutils
from shapeDetection import Shape

#SETUP
CONTOUR_DIR = "./contours/"
IMAGE_DIR = "./images/"
RESIZE_WIDTH = 300
IMG_RATIO = 1
MIN_SIZE = 100

#take an image, and a background color (b or w), and returns an array of contours
def getContoursFromImage(image, background_color='w' ):
	binaryStyle = cv2.THRESH_BINARY if background_color == 'b' else cv2.THRESH_BINARY_INV

	resized = imutils.resize(image, width=RESIZE_WIDTH)
	ratio = image.shape[0] / float(resized.shape[0])
	IMG_RATIO = ratio
	
	gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(gray, (60 if binaryStyle==0 else 90), 255, binaryStyle)[1] #original thresh=60, inverted thresh = 90

	#	cv2.imwrite( "/home/pi/Documents/pyimagesearch/gray_"+args["image"], gray )
	#cv2.imwrite( CONTOUR_DIR+"/thresh.png", thresh )

	# find contours in the thresholded image
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = contours[0] if imutils.is_cv2() else contours[1]
			
	return cnts



def saveDetectedShape(shapeContour, image, id=None):
	
	s = Shape( id , shapeContour )
	s.getCenter(shapeContour, IMG_RATIO)
	
	#get relative size to discard noise
	shape_area = s.contour_size()
	if shape_area < MIN_SIZE: return
	
	#GET EXTREME POINTS OF THE CONTOUR
	c = shapeContour
	westx, westy = tuple(c[c[:, :, 0].argmin()][0])
	eastx, easty = tuple(c[c[:, :, 0].argmax()][0])
	northx, northy = tuple(c[c[:, :, 1].argmin()][0])
	southx, southy = tuple(c[c[:, :, 1].argmax()][0])
		
	s.rect_topLeft=(westx, northy)
	s.rect_bottomRight = ( eastx, southy)
		
	#save the contour to disk so it is remembered if program quits
	resizedImage = imutils.resize(image, width=RESIZE_WIDTH)
	s.saveContourToFile(resizedImage)


#get a image from directory
#DIRECTORY = os.getcwd() + "/"
testfile = IMAGE_DIR + "p4.jpg"

scene = cv2.imread(testfile)
#contours = getContoursFromImage(scene)
contours = getContoursFromImage(scene, background_color = 'b')

id=0
for c in contours:
	saveDetectedShape(shapeContour=c, image=scene, id=id)
	id = id + 1

	
print ("complete")




#change image to BW

#find countours