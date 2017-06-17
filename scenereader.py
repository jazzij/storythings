# SCENEREADER.PY
# 1) Takes a picture with Rpi Camera, 2) Processes image for all contours,
# 3) Save these detected contours, 4) Associates contours with an audio file (create storything)
# all contours shoud in a CONTOUR_DIR. All audio should be in AUDIO_DIR. if an audiofile is in AUDIO_DIR, it should start with a unique number as an id

from shapeDetection import ShapeDetector, IMAGE_DIR, CONTOUR_DIR
from storything import AUDIO_DIR
from cam import captureImage
from storything import StoryThing, StoryParser
import storything
import os, time
import re
import argparse
import cv2

detector = ShapeDetector()

def initDetector():
    #Grab all saved contours from disk. Automatically populated to detector's list
    detector.loadSavedContours()

def captureScene():
    #1. Capture image
    scene = captureImage()

    #2. Find all contours in the image, save them to detectors internal list and to file
    detector = ShapeDetector()
    cnts = detector.getContoursFromImage(scene)

    for c in cnts:
        detector.saveDetectedShape(shapeContour=c, image=scene)


def setupAudioPlayback():
    storythings = []
    #4. Create storythings with ID's that match shapes with audio
    shapes_in_scene = [shape for shape in detector.detected_shapes if shape.center is not None]
    audioList = storything.getAllAvailableAudio()
    alist = [( int(audio[:1]), audio) for audio in audioList] #create tuple (id, audio) to match with shape id
    for shape in shapes_in_scene:

        candidates = [a for a in alist if shape.id == a[0]]

        thing = StoryThing( shape, candidates[0])
        storythings.append(thing)

    #5. Calculate the configuration of all shapes in the scene
    for thing in storythings:
        adjacency = detector.calculateAdjacent(thing.shape, shapes_in_scene)
        thing.adjacent = adjacency

    # 6. initialize the rule parser to control playback
    parser = StoryParser(storythings)


def setupEventCallbacks():
    # button press for play
    # button press for stop
    # button press for capture scene
    pass









    # for filename in os.listdir(AUDIO_DIR):
    #    rec = Recording( filename)
    #    print filename
    #    length = rec.play()
    #    time.sleep( length)
    #    print "Recording finished..."