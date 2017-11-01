DOCUMENTING STORYTHINGS Demo v1
Last update 7/3/2017, by Jasmine Jones

Demo 1 - OpenCV, on Raspberry PI 3, Python 2.7, 
Foundations: 
Python Virtual Environments - Python 2.7
OpenCV Python wrapper cv2
PyGame (pygame library for audio output)
GPIO (RPIO, os libraries)
PiCamera (python cam library)

Uses Python Virtual Environment for OpenCV/Python install b/c I wanted to use Python 2, but Pi 3 has python 3

NOTABLE FILES
1)
# SCENEREADER.PY
# 1) Takes a picture with Rpi Camera, 2) Processes image for all contours,
# 3) Save these detected contours, 4) Associates contours with an audio file (create storything)
# all contours shoud in a CONTOUR_DIR. All audio should be in AUDIO_DIR. if an audiofile is in AUDIO_DIR, it should start with a unique number as an id

2) (Main) 
# StoryThings: Take a shape, map it to an audio file, create some rules governing the playback

3) 
#Rules.json
Format:
[ {
	"name":"test",
	"context":{
		"configuration": "right",
		"condition": "test",
		"action": "merge"
	},
	"priority":1
},
]


STORYTHINGS API

Recordings:
	- initialize with audio file, topic keywords, and anti-topics (negative keywords)
	- Add topics (list of topics)
	- Add Anti (list of antitopics)
	- Play
	- Stop

StoryThing
	- initialize with shape, audio file, alternate audio file (brec)
	- update (change the associated shape. Does not change the audio recording)
	- getTopics
	- play
	- isLocked (cannot play)
	- tryAudioLink ??
	- play order for multiple clips
		tryAudioLink
		AddToNowPlay
		setDefaultNowPlay 
		brecNowPlay
	Rule Responses
	- combine (what to do when COMBINE RULE is detected)
	- ...

APP
StoryParser (DRIVER)
	 - initialize with a list of storythings and a rule file
	 - evaluateRule
	 - executeRule
	 - runParser (will evaluate all rules on each object, ordered spatially from L-R)
	 - action_*, and condition_* are implementing rules features that the parser responds to
	 - matchTopics is utility funciton to check if any topics co-occur across ListA and ListB. returns a list of all matches
	 
	 
SCENEREADER API
(handles input and output from buttons, camera, etc)
- setup RPIO event callbacks for buttons
- storyEventHandler as callback function
- createDetector for detecting new shapes and loading images of any previously detected shapes for recognition
- resetScene whenever something new is added or the configuration is changed. Activated manually by user. Takes captured images,
	and calculates where they are in the scene, associates shapes with audio, and runs the rule parser to figure out ohow audio should be accessed
- captureScene take image and extract all detectable shapes from the image
- setupAudioPlayback takes shapes and calculated positions and associates each shape with an audiorecording and neighbors
- calculate adjancencies - openCV math to figure out which shapes are next to each other
- play Scene Audio
- helper: getThingForShape (given a shape, retrieved an already creating association object), activeShapes (only ones currently in the scene)
- play scene audio - activate playback. should be ordered 
