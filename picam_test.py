import time
import picamera
import numpy

def getImage():
	with picamera.PiCamera() as camera:
		rawCap = PiRGBArray(camera)
		camera.resolution = (1024, 768)
		camera.capture(rawCap, format="bgr")
		image = rawCap.array
	
		return image

def getVideoSequence(int capTime):
	frame_res = (640, 480)
	with picamera.PiCamera() as camera:
		rawCap = PiRGBArray(camera, frame_res)
		camera.resolution = (1024, 768)
		camera.framerate = 32
		
		
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
			image = frame.array #numpy array 
			
			cv2.imshow("frame", image)
				
			#clear stream
			rawCap.truncate(0)



#image = getImage()
image = getImgSequence()


cv2.imshow("Image", image)
cv2.waitKey(0)

cv.destroyWindows()
print("bye")



