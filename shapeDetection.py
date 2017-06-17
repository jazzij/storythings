#from pyimagesearch tutorial #2
#detect a shape using countour approximation (split and merge
import os
import math, random
import imutils, json
import cv2
import atexit

CONTOUR_DIR = "./contours/"
IMAGE_DIR = "./images/"
RESIZE_WIDTH = 300

class Shape(object):
	def __init__(self, id, contour):
		self.id = id
		self.contour = contour
		self.center = (0,0)
		self.rect_topLeft = (0,0)
		self.rect_bottomRight = (1,1)
	
	def __str__(self):
		return "Shape<{0}>: {1}".format(self.id, self.center)

	def getCenter(self, contour, ratio=1):
		# compute the center of the contour
		M = cv2.moments(contour);
		if int(M["m00"]) != 0:
			cX = int((M["m10"] / M["m00"]) * ratio)
			cY = int((M["m01"] / M["m00"]) * ratio)
		else:
			cX = 0
			cY = 0

		self.center = (cX, cY)

	#to save a contour, you have to create an image out of it, then save to file. Image should be WIDTH= 300	
	def saveContourToFile(self, image):
		c = self.contour
		
		#get bounding rect from the edge points of the contour
		# bound the rectangle: cv2.rectangle( dest_image, (extLeft[0]-10, extTop[1]-10), (extRight[0]+10, extBottom[1]+10), (0, 255, 100), thickness=2)
		# cv2.rectangle( resizedImage, (westx-10, northy-10), (eastx+10, southy+10), (0, 255, 100), thickness=2)				

		width, height = image.shape[:2]
		alpha = 10
		y1 = (self.rect_topLeft[1] - alpha) if (self.rect_topLeft[1] -alpha > 0) else 0
		y2 = (self.rect_bottomRight[1] + alpha) if (self.rect_bottomRight[1] + alpha < height) else self.rect_bottomRight[1]
		x1 = (self.rect_topLeft[0] -alpha) if (self.rect_topLeft[0]-alpha > 0) else 0
		x2 = (self.rect_bottomRight[0] +alpha) if (self.rect_bottomRight[0] + alpha < width) else self.rect_bottomRight[0]
		
		roi = image[y1:y2, x1:x2]
		filename  = "{0}roi{1}.jpg".format(CONTOUR_DIR, self.id)
		cv2.imwrite(filename, roi)

	#returns a float euclidean distance between this shape and another
	def euclidean_distance(self, otherShape):
		x1 = self.center[0]
		x2 = otherShape.center[0]
		y1 = self.center[1]
		y2 = otherShape.center[1]
		phrase = (x1 - x2) ** 2 + (y1 - y2) ** 2
		return (math.sqrt(abs(phrase)) if phrase > 0 else 0)


	#returns a float. Negative numbers mean the otherShape is to the Cartesian left
	def x_distanceBetween(self, otherShape):
		x1 = self.center[0]
		x2 = otherShape.center[0]
		return x1 - x2


	#returns a float. Negative numbers mean the otherShape is below in Cartesian space (negative y)
	def y_distanceBetween(self, otherShape):
		y1 = self.center[1]
		y2 = otherShape.center[1]
		return y1-y2

class ShapeDetector(object):
	
	def __init__(self):
		self.detected_shapes = [] #empty list
		self.ratio = 1
		self.detection_index = 0
		
		#atexit.register(self.saveToFile)
	
					
		
	def getContoursFromImage(self, image, background_color='w' ):
		binaryStyle = cv2.THRESH_BINARY if background_color == 'b' else cv2.THRESH_BINARY_INV

		resized = imutils.resize(image, width=RESIZE_WIDTH)
		self.ratio = image.shape[0] / float(resized.shape[0])

		gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
		thresh = cv2.threshold(gray, (60 if binaryStyle==0 else 90), 255, binaryStyle)[1] #original thresh=60, inverted thresh = 90

		#	cv2.imwrite( "/home/pi/Documents/pyimagesearch/gray_"+args["image"], gray )
		#	cv2.imwrite( "/home/pi/Documents/pyimagesearch/thresh_"+args["image"], thresh )

		# find contours in the thresholded image
		contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = contours[0] if imutils.is_cv2() else contours[1]
		
		#save this contour
		for c in cnts:
			#initialit shape name & approximate contour: a_compute perimeter, b_feed into algorithm. 
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.04 * peri, True) #common values between .01-.05		
			#print("detected %s vertices", len(approx))
			
		#save cnts
		return cnts
		
	def loadSavedContours(self, directory=CONTOUR_DIR):
		for file in os.listdir(CONTOUR_DIR):
			if "roi" in file:
				img = cv2.imread(CONTOUR_DIR + file)
				# should only be one shape in the contour file, if there are multiple, choose the largest one, which is the main one
				if img is not None:
					file_id = int(re.search(r'\d+', file).group())  # recycle id,*/roiID.jpg
					cts = self.getContoursFromImage(img)
					c = max(cts, key=cv2.contourArea)  # get largest
					self.loadOldShape(c, img, file_id)

	def detectandname(self, c):
		#initialit shape name & approximate contour: a_compute perimeter, b_feed into algorithm. 
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True) #common values between .01-.05
		print("detected %s vertices", len(approx))
		#shape detection rules. approx will be list of vertices detected
		if len(approx) == 3:
			shape = "triangle"
			
		# if the shape has 4 vertices, it is either a square or
		# a rectangle
		elif len(approx) == 4:
			# compute the bounding box of the contour and use the
			# bounding box to compute the aspect ratio
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)
 
			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
 
		# if the shape is a pentagon, it will have 5 vertices
		elif len(approx) == 5:
			shape = "pentagon"
 
		# otherwise, we assume the shape is a circle
		else:
			shape = "circle"
 
		# return the name of the shape
		return shape

	def saveDetectedShape(self, shapeContour, image, id=None):
		previous = self.findThisShape(shapeContour)
		if previous >= 0:
			print "found shape in ROI", previous
			return previous

		#create shape object to store contour and metadata
		if id is None:
			id = self.detection_index 
		s = Shape( id , shapeContour )
		s.getCenter(shapeContour, self.ratio)

		#GET EXTREME POINTS OF THE CONTOUR
		c = shapeContour
		westx, westy = tuple(c[c[:, :, 0].argmin()][0])
		eastx, easty = tuple(c[c[:, :, 0].argmax()][0])
		northx, northy = tuple(c[c[:, :, 1].argmin()][0])
		southx, southy = tuple(c[c[:, :, 1].argmax()][0])
		
		s.rect_topLeft=(westx, northy)
		s.rect_bottomRight = ( eastx, southy)

		#save the shape to a list for easy finding, and update auto-id
		self.detected_shapes.append(s)
		self.detection_index = self.detection_index+1 
		
		#save the contour to disk so it is remembered if program quits
		resizedImage = imutils.resize(image, width=RESIZE_WIDTH)
		s.saveContourToFile(resizedImage)

		return s.id
		

		
	#old shapes are there for recognition purposes only, but they cannot be used in configurations. So no center
	def loadOldShape (self, shapeContour, image, id=0):
		resizedImage = imutils.resize(image, width=RESIZE_WIDTH)

		width, height = image.shape[:2]
		s = Shape( id , shapeContour )
		s.center = None #self.getCenter(shapeContour)
		s.rect_topLeft = (0,0)
		s.rect_bottomRight = (width, height)
		#shape should be a vector of points (ie countour)		
		self.detected_shapes.append(s)
		self.detection_index = self.detection_index+1
		
		
	def findThisShape(self, shapeContour):
		print "Comparing against ", len(self.detected_shapes), " saved shapes."
		#search for this shape by name
		for savedShape in self.detected_shapes:
			ret = cv2.matchShapes(shapeContour, savedShape.contour, 1, 0.0)
			print "Match score: ", ret
			if ret < .01 :
				return savedShape.id
						
		return -1	

	def drawThisShape(self, contour, dest_image, img_name="default.jpg", extLeft=None, extRight=None, extTop=None, extBottom=None):
	 	# multiply the contour (x, y)-coordinates by the resize ratio,
		# then draw the contours and the name of the shape on the image
		c = contour.astype("float")
		c *= self.ratio
		c = c.astype("int")
		# draw the contour and center of the shape on the image
		#cv2.drawContours(dest_image, [c], -1, (100, 255, 0), 2)
		#cv2.drawContours(dest_image, [c], -1, (100, 100, 0), 2, thickness=cv2.cv.CV_FILLED) #use this line to draw the contour on a blank sheet
	
		#if extLeft is not None:
		#	cv2.circle( dest_image, extLeft, 8, (255, 0, 0), -1)
		#if extRight is not None:
		#	cv2.circle( dest_image, extRight, 8, (0, 255, 0), -1)	 
		#if extTop is not None:
		#	cv2.circle( dest_image, extTop, 8, (255, 255, 0), -1)
		#if extBottom is not None:
		#	cv2.circle( dest_image, extBottom, 8, (0, 255, 255), -1)
		
		#cv2.rectangle( dest_image, (extLeft[0]-10, extTop[1]-10), (extRight[0]+10, extBottom[1]+10), (0, 100, 100))
		cv2.rectangle( dest_image, (extLeft[0]-10, extTop[1]-10), (extRight[0]+10, extBottom[1]+10), (0, 255, 100), thickness=2)

						
		cv2.imwrite( img_name, dest_image )
		#print "Wrote "  + img_name
		print "Draw rectangle: {0}, {1}".format( (extLeft[0], extTop[1]), (extRight[0], extBottom[1]))

	#I only need to save the contours so I can maintain the identification pool
	# and I need to save the associations (
	def saveToFile(self):
		for shape in self.detected_shapes:
			shape.saveContourToFile()
		#with open('detected_shapes.txt', 'w') as saveFile:
		#	for shape in self.detected_shapes:
		#		json.dump( shape.__dict__, saveFile, ensure_ascii=False )				
				#json.dump( self.detected_shapes, saveFile, ensure_ascii=False)

	def loadFromFile(self):
		with open('detected_shapes.txt') as saveFile:
			detected_shapes = json.load(saveFile)
	

 
	def calculateAdjacent(self, selectedShape, comparisonShapes = None, maxDistance=-1):
		center = selectedShape
		otherShapes = comparisonShapes if comparisonShapes is not None else self.detected_shapes
		# List: { "x":xdist, "y":ydist, "e":edist, "shape":shape
		sortedShapes = []

		#1 get euclidean distance for overall closest to farthest
		for shape in otherShapes:
			e = center.euclidean_distance (shape)
			h = center.x_distanceBetween(shape)
			v = center.y_distanceBetween(shape)
			distances = dict()
			distances["x"] = h
			distances["y"] = v
			distances["e"] = e
			distances["shape"] = shape
 			sortedShapes.append( distances )

		#2 get only shapes perpendicular to shape. ie RIGHT: ydist==0, xdist > 0. "right" should be whatever of these has smallest e
		right =  [s for s in sortedShapes if s["y"] == 0 and s["x"] < 0]
		left = [s for s in sortedShapes if s["y"] == 0 and s["x"] > 0]
		above = [s for s in sortedShapes if s["x"] == 0 and s["y"] < 0]
		below = [s for s in sortedShapes if s["x"] == 0 and s["y"]  > 0]

		right.sort(key = lambda x: abs( x["e"] ) )
		left.sort(key = lambda x: abs( x["e"] ) )
		below.sort(key = lambda x: abs( x["e"] ) )
		below.sort(key = lambda x: abs( x["e"] ) )

		#3 get closest shape( first element in list) for the adjacency
		adjacent = dict()
		adjacent["right"] = right[0]["shape"] if len(right) > 0 else None
		adjacent["left"] = left[0]["shape"] if len(left) > 0 else None
		adjacent["above"] = above[0]["shape"] if len(above) > 0 else None
		adjacent["below"] = below[0]["shape"] if len(below) > 0 else None

		return adjacent



##	TEST SCRIPT
#sampleShapes = []
#detector = ShapeDetector()
#for i in range(0,10):
#		sampleShapes.append( Shape(i, "blah"))
#		sampleShapes[i].center = ( random.randint(-10,10), random.randint(-10,10))
#		print sampleShapes[i]

#for shape in sampleShapes:
#	adjacent = detector.calculateAdjacent(shape, sampleShapes)
#	print "Center shape: {0}".format(shape)
#	print "Adjacent: {0},  {1},  {2},  {3}".format( adjacent["left"], adjacent["right"] ,adjacent["above"], adjacent["below"])



	
	
		