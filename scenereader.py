# SCENEREADER.PY
# 1) Takes a picture with Rpi Camera, 2) Processes image for all contours,
# 3) Save these detected contours, 4) Associates contours with an audio file (create storything)
# all contours shoud in a CONTOUR_DIR. All audio should be in AUDIO_DIR. if an audiofile is in AUDIO_DIR, it should start with a unique number as an id

import os
import time
import RPIO
import cam
import cv2
from shapeDetection import ShapeDetector, IMAGE_DIR, CONTOUR_DIR
import storything
import re


GPIO_PLAY_PIN = 5
GPIO_CAPTURE_PIN = 17
#AUDIO_READY = False

detector = ShapeDetector()
parser = None
currentIdx = 0
prevIdx = 0
storythings = []

#TEST_FILE = test_file() #"./images/board6_combine-01.jpg"
testIdx = 0
def test_file():
    global testIdx
    files = []
    for file in os.listdir("./images/"):
        if file.endswith(".jpg"):
            files.append(file)

    testfile = files[testIdx]
    testIdx = testIdx + 1 if testIdx < len(files)-1 else 0
    print "Captured: ", testfile
    return "./images/"+testfile

#ON STARTUP
def setupEventCallbacks():
    RPIO.setmode(RPIO.BCM)
    RPIO.setup(5, RPIO.IN, pull_up_down=RPIO.PUD_UP)
    RPIO.setup(17, RPIO.IN, pull_up_down=RPIO.PUD_UP)

    RPIO.add_interrupt_callback(5, storyEventHandler, edge='falling', debounce_timeout_ms=50)
    RPIO.add_interrupt_callback(17, storyEventHandler, edge='falling', debounce_timeout_ms=50)


def createDetector():
    #Grab all saved contours from disk. Automatically populated to detector's list
    #detector = ShapeDetector()
    detector.loadSavedContours()

# MAIN PROCESS executed ON CAPTURE BUTTON PRESS
def resetScene():
    global currentIdx, storythings

    # on button press enter another loop of capture, associate, parse
    currentIdx, shapes_in_scene = captureScene()
    print "Captured up to {0} shapes. Shapes: {1}".format(currentIdx, shapes_in_scene)
    adjacencies = calculateShapeAdjacencies(shapes_in_scene)
    scenethings = setupAudioPlayback(shapes_in_scene, adjacencies)  # run audio set for new shapes[prevIdx:end]

    # --- add or update newthings in the ST list to keep track
    for st in scenethings:
        print st.adjacent

    for oldThing in storythings:
        for newThing in [newThing for newThing in scenethings if newThing.id == oldThing.id]:
            #print "found old thing {0}".format(oldThing.id)
            oldThing.update(newThing)
        #if oldThing.id in [newThing.id for newThing in scenethings]:
        #   print "foundOldThing ", oldThing.id
        #   oldThing.update(newThing)

    for thing in scenethings:
        oldId = [st.id for st in storythings]
        if thing.id not in oldId:
            storythings.append(thing)

    #storythings.extend(additions)

    # run parser only on shapes that are currently in scene.
    #inScene_shapes = [shape for shape in detector.detected_shapes if shape.id in shapes_in_scene]
    activeThings = [thing for thing in storythings if thing.id in shapes_in_scene]
    for thing in activeThings:
        print "{0} {1}".format(thing.id, thing.shape)

    # 6. initialize the rule parser to control playback
    parser = storything.StoryParser(activeThings)
    parser.runParser()


#Returns: index, list of the ID's of all shapes in scene
def captureScene():
    #1. Capture image
    #scene = cam.captureImage()
    testfile = test_file()
    scene = cv2.imread(testfile)

    #2. Find all contours in the image, save them to detectors internal list and to file
    cnts = detector.getContoursFromImage(scene)
    shapes_in_scene = []
    for c in cnts:
        id = detector.saveDetectedShape(shapeContour=c, image=scene)
        #print "Found or Created new {0}".format(id)
        shapes_in_scene.append(id)
    return detector.detection_index, shapes_in_scene

# Associate all detected shapes with an audio file
# The ID's ROI_ID -> shape_ID -> ID_audioname are the KEY to matching
# maybe put this in a different function... shapes_in_scene are the only ones given to the parser
# SHAPES_IN_SCENE IS A LIST OF ID'S not a list of shapes
def setupAudioPlayback(shapes_in_scene, adjacencies):
    #4. Create storythings with ID's that match savedshapes ID with audio ID
    audioList = storything.getAllAvailableAudio()
    alist = [(int(re.search(r'\d+', audio).group()), audio) for audio in audioList] #create tuple (id, audio) to match with shape id
    shapeList = list(set([shape for shape in detector.detected_shapes if shape.id in shapes_in_scene]))

    for shape in shapeList:
        candidates = [a for a in alist if a[0] == shape.id] #match audID with shapeID
        #myAdjacent = [adj[1] for adj in adjacencies if shape.id == adj[0]].pop()
        #print "Adjacents for ID:{0} are {1}".format(shape.id, myAdjacent)
        if candidates:
            id, audioName = candidates[0]
            thing = storything.StoryThing( shape, audioName) #there should be only one. duplicate id's ignored
            #thing.adjacent.addAdjacent(myAdjacent)
            storythings.append(thing)

    #get objects for all adjacencies
    directions = storything.DIRECTIONS
    for adj in adjacencies:
        for d in directions:
            if adj[1][d] is not None:
                adj[1][d] = getThingForShape(adj[1][d])
        print adj
            #myAdjacent = [adj[1] for adj in adjacencies if thing.id == adj[0]].pop()

    for scenething in [scenething for scenething in storythings if scenething.id in [shapes_in_scene]]:
         pass

    for adj in adjacencies:
        for st in storythings:
            if st.id == adj[0]:
                st.adjacent = adj[1]

    return storythings

#Returns a list ( of dictionaries where the keys are (id, adjancency_dict)
def calculateShapeAdjacencies(shapes_in_scene):
    shapeList = [shape for shape in detector.detected_shapes if shape.id in shapes_in_scene]
    adjacencies = []
    #5. Calculate the configuration of all shapes in the scene
    for core in shapeList:
        adjacency = detector.calculateAdjacent(core, shapeList)
        adjacencies.append( (core.id, adjacency) )

    return adjacencies

def getThingForShape(shape):
    for thing in storythings:
        if thing.id == shape.id:
            return thing

def activeShapes():
    return [shape.id for shape in detector.detected_shapes if shape.center is not None]




#play everything on the board
def playSceneAudio():
    #print "PlayScene Audio: {0} {1}".format(parser, parser.isReady)

    if storything.AUDIO_READY:
        for thing in storythings:
            thing.play()



def storyEventHandler(GPIO_id, value):

    if GPIO_id is GPIO_CAPTURE_PIN:
        storything.AUDIO_READY = False
        resetScene()


    elif GPIO_id is GPIO_PLAY_PIN:
        print "Playtime!"
        playSceneAudio()


######## TEST SCRIPT ####################################################################
#main, the script should always start here when it start

try:
    createDetector()
    #resetScene()
    #playSceneAudio()
    setupEventCallbacks()
    RPIO.wait_for_interrupts()

except KeyboardInterrupt:
    print "bye bye"
finally:
    RPIO.cleanup()



#on button press enter another loop of capture, associate, parse
#currentIdx, shapes_in_scene = captureScene()
#print "Captured up to {0} shapes. Shapes: {1}".format(currentIdx, shapes_in_scene)
#scenethings = setupAudioPlayback(shapes_in_scene) #run audio set for new shapes[prevIdx:end]

#--- add or update newthings in the ST list to keep track
#oldthings = []
#for thing in scenethings:
#     oldId =  [st.id for st in storythings]
#     if thing.id not in oldId:
#        storythings.append(thing)
#     else:
#        for story in [story for story in storythings if story.id is thing.id]:
#            story.update(thing)
#            print "Updated: {0}".format( story   )

#run parser only on shapes that are currently in scene.
#inScene_shapes = [shape for shape in detector.detected_shapes if shape.id in shapes_in_scene]
#activeThings = [thing for thing in storythings if thing.id in shapes_in_scene]
#for thing in activeThings:
#        print "{0} {1}".format(thing.id, thing.shape)

#print "Simulating loop, running capture scene again..."
#captureScene()
#parser = setupRuleParser(activeThings)
#parser.runParser()



# for filename in os.listdir(AUDIO_DIR):
    #    rec = Recording( filename)
    #    print filename
    #    length = rec.play()
    #    time.sleep( length)
    #    print "Recording finished..."