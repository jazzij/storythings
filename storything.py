# StoryThings: Take a shape, map it to an audio file, create some rules governing the playback
import pygame
import json
import os

AUDIO_DIR = "./audio/"
AUDIO_READY = False
DIRECTIONS = ["left", "right", "above", "below"]

#returns relative paht ./audio/name.wav
def getAllAvailableAudio():
    files = []
    for file in os.listdir(AUDIO_DIR):
        if file.endswith(".wav") or file.endswith(".ogg"):
            files.append(AUDIO_DIR+file)

    return files

class Recording(object):
    # give me a filename only. not a path
    def __init__(self, audioFile):
        self.clip = audioFile
        self.topics = []
        self.anti_topics = []

    def __str__(self):
        return "Rec({0})".format(self.clip)

    #takes a lsit of topics
    def addAnti(self, topics):
        if topics is None:
            return "No topics given."
        # extend the list, but get rid of duplicates
        self.anti_topics.extend(topics)
        self.anti_topics = list(set(self.anti_topics))

    #takes a list of topics
    def addTopics(self, topics):
        if topics is None:
            return "No topics given."
        else:
            self.topics.extend(topics)
            self.topics = list(set(self.topics))

    def play(self):
        print "playing ", self.clip
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        s = pygame.mixer.Sound(self.clip)
        channel = s.play()
        while channel.get_busy():
            pygame.time.wait(500)
        #pygame.mixer.music.load(AUDIO_DIR + self.clip)
        #pygame.mixer.music.play()
        #return self.clip.get_length()

    def stop(self):
        print "mixer stop"
        #if pygame.mixer:
        #    pygame.mixer.fadeout(500)  # ms
        #    pygame.mixer.quit()


class StoryThing(object):
    def __init__(self, shape, audioFile, brec=None):
        self.default_rec = Recording(audioFile)
        self.b_rec = Recording(brec) if brec is not None else None
        self.now_playing = []

        self.shape = shape
        self.id = shape.id
        self.adjacent = dict()
        # self.rules = [ PLAY, COMBINE] #these are rules that this chip observes. by default all chips PLAY and COMBINE
        self.timelock = None #init in seconds, maybe this should be a function that calculates a time?
        self.topicKey = [] #a list of topics that will release the audio

        self.MORPHED = False
        self.TOPIC_LOCK = False

        self._setTopics(self.default_rec)
        if self.b_rec:
            self._setTopics(self.b_rec)
        print 'Created {0}: {1}'.format(self.id, self.default_rec.topics)

        self._setTopicLock()
        self.setDefaultNowPlay()


    def __str__(self):
        return "Thing{0} holding <{1}> and {2}".format(self.id, self.default_rec, self.shape)

    def _setTopics(self, recording):
        with open("./audio_metadata.json") as saveFile:
            metadata = json.load(saveFile)
        for m in metadata:
            #print "{0} =?= {1}".format(m["file"], recording.clip)

            if m["file"] == recording.clip:
                #print "Loading topics for {0}".format(recording.clip)
                topics = m["topics"]
                anti_topics = m["anti"]
                releaseKey = m["key"]

                if topics is not None:
                    recording.addTopics(topics)
                if anti_topics is not None:
                    recording.addAnti(anti_topics)
                if releaseKey is not None:
                    self.topicKey.extend(releaseKey)

    def _setTopicLock(self):
        if self.topicKey:
            self.TOPIC_LOCK = True

    #only the shape details can change (like orientation, center, etc) and the adjacencies.
    def update(self, newMe):
        self.shape = newMe.shape
        self.adjacent = newMe.adjacent

    def getTopics(self):
        if self.isLocked:
            return []
        elif self.MORPHED:
            topics = self.b_rec.topics
            return topics
        else:
            return self.default_rec.topics

    def play(self):
        if not self.now_playing:
            print "looks like {0} is locked".format(self)
            return
        else:
            for np in self.now_playing:
                np.play()


    #TIME LOCK is INTERNAL. TOPIC LOCK IS exTERNAL, based on configuration
    def isLocked(self):
        if self.timelock is None or self.timelock <= 0:
            return False
        elif self.timelock > 0:
            return True

    def tryAudioLink(self):
        if self.isLocked():
            return None
        elif self.TOPIC_LOCK == True:
            return None
        else:
            if len(self.now_playing) > 0:
                return self.now_playing[0]
            else:
                return None

    def combine(self, anotherRecording):
        if len(self.now_playing) == 0:
            self.addToNowPlay(self.default_rec)
        self.addToNowPlay( anotherRecording)

    def addToNowPlay(self, newClip):
        self.now_playing.append(newClip)

    def setDefaultNowPlay(self):
        print "DEFAULT ACTIVATION..."
        print self.now_playing
        if not self.now_playing:
            self.now_playing.append(self.default_rec)
        else:
            self.now_playing[0] = self.default_rec

    def brecNowPlay(self):
        if self.b_rec is not None:
            if not self.now_playing:
                self.now_playing.append(self.b_rec)
            else:
                self.now_playing[0] = self.b_rec

class StoryParser(object):
    def __init__(self, storythings, ruleFile="./rules.json"):
        self.storythings = storythings
        self.rules = self._ingestRules(ruleFile)
        self.isReady = False
        self.methods = self._createMethodDict()

        #first order the things from L-R
        self._orderThings()

    # expects a json or txt with json formatting. returns a list of rule dicts ordered by priority
    def _ingestRules(self, file):
        with open("./rules.json") as saveFile:
            rules = json.load(saveFile)
        ordered = sorted(rules, key=lambda k: k["priority"], reverse=True)
        return ordered

    def _createMethodDict(self):
        # later get this from a file too?
        methods = dict()
        #CONDITIONS
        methods["matchTopic"] = self.condition_matchTopics
        methods["checkLock"] = self.condition_checkLock
        methods["test"] = self.condition_test
        methods["noBRec"] = self.condition_noBRec

        #ACTIONS
        methods["merge"] = self.action_mergeAudio
        methods["morph"] = self.action_morph
        methods["blockAudio"] = self.action_block
        methods["lockUp"] = self.action_lockUp
        methods["play"] = self.action_simplePlay
        methods["releaseLock"] = self.action_unlock_by_topic

        return methods

    #enable execution of rules from L to R
    def _orderThings(self):
        #v1 Sort from left to right (dominant), top to bottom when L-R is the same
        self.storythings = sorted(self.storythings, key=lambda thing:(thing.shape.center[0], -(thing.shape.center[1])))
        #v2 Sort from top to bottom (dominant), left to right when TB is the same. standard row-columm traversal
        #l2 = sorted(coords, key=lambda k:(-k[1], k[0]))
        print "Parser status: "
        for thing in self.storythings:
            print thing

    #given a keyword and an adjacency dic, evaluate whether the keyword conditions are fulfilled
    def _evalConfiguration(self, configuration, adjacencies):
        directions = ["right", "left", "above", "below"]
        if configuration == "adjacent_any": # any direction, but at least one, must be present
            for d in directions:
                if adjacencies[d] is not None:
                    return True
            return False
        if configuration == "adjacent_all": #all directions must be present
            for d in directions:
                if adjacencies[d] is None:
                    return False
            return True
        if configuration == "around": #this one means all objects in the scene get evaluated
            pass
        if configuration == "single": #single means only core matters
            return True

        if configuration in directions: #check this direction to see if it exists
            if adjacencies[configuration] is not None:
                return True
            else:
                return False

        #any other term is an unrecognized config
        print "Unrecognized config {0}".format(configuration)
        return False


    def evaluateRule(self, context):
        #verify the configuration as a precondition
        neededConfig = context["configuration"]
        coreThing = context["thing"]
        configCheck = self._evalConfiguration(neededConfig, coreThing.adjacent)
        if not configCheck:
            print "{0} failed config check for for {1}".format(context["thing"], context["configuration"])
            return False

        # evaluate the condition
        condition_method = context["condition"]
        if condition_method is not None and condition_method != "None":
            result = self.methods[condition_method](context)
            return result

        # if the rule has no conditions, then its always true
        return True

    def executeRule(self, context):
        action_method = context["action"]
        # execute the action associated with rule
        if action_method is not None:
            self.methods[action_method](context)

    # in this function, all rules are evaluated on each thing
    def runParser(self):
        #evaluate each rule on each thing from L-R
        for rule in [rule for rule in self.rules]:
            print "Eval Rule {0}".format(rule["name"])
            if rule["name"] in ["simplePlay", "combine", "morph"]:
                for thing in self.storythings:
                    context = rule["context"]
                    context["thing"] = thing

                    result = self.evaluateRule(context)
                    #print "{0} for rule {1}".format(result, rule["name"])
                    if result:
                        self.executeRule(context)
                    else:
                        print "Rule failed"

        global AUDIO_READY
        AUDIO_READY = True
        #self.playReadySound()

        for thing in self.storythings:
            print "{0} now playing {1}".format(thing.id, thing.now_playing)

    def playReadySound(self):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        clipname = AUDIO_DIR + "9_audience_applause.wav"
        print "Readysound: ", clipname
        pygame.mixer.music.load(clipname)
        pygame.mixer.music.play()

    # REQUIRES config="right"
    def action_mergeAudio(self, context):
        print "Doing this action!", context["action"]
        core = context["thing"]
        right = core.adjacent[context["configuration"]]
        if right is None:
            print "MERGE: augh failure :((("
            return

        right_audio = right.tryAudioLink() #returns []
        if right_audio is not None and right_audio is not []:
            core.combine(right_audio)
        else:
            print "hm, combine for {0} is acting on None".format(core)



    def action_silence(self, context):
        print "Doing this action!", context["action"]

    def action_morph(self, context):
        print "Doing this action!", context["action"]

    def action_block(self, context):
        print "Doing this action!", context["action"]

    def action_lockUp(self, context):
        print "Doing this action!", context["action"]

    def action_unlock_by_topic(self, context):
        print "Doing this action!", context["action"]
        #get all storythings in the scene
        allTopics = self.getAllTopics()
        #get key
        keyTopics = context["thing"].topicKey
        for key in keyTopics:
            if key in allTopics:
                context["thing"].TOPIC_LOCK = False

    # Simple Play, if no other rules are True, than simply play the default clip
    def action_simplePlay(self, context):
        print "Doing this action, simplePlay"
        core = context["thing"]
        #print core.now_playing
        #print "Locked" if core.isLocked() else "Unlocked"
        if not core.isLocked() and len(core.now_playing) == 0:
            core.setDefaultNowPlay()

    def condition_test(self, context):
        print "A ({0}) matches B({1}), so execute C{2} ".format(context["thing"], context["configuration"],
                                                    context["action"])
        return True

    def condition_noBRec(self, context):
        print "Condition _ NoBRec"
        thing = context["thing"]
        return thing.b_rec is None

    def condition_matchTopics(self, context):
        whichThing = context["configuration"]
        core = context["thing"]
        topicListA = core.getTopics()
        directions = ["left", "right", "above", "below"]
        print "Matching topics {0} and {1}".format(topicListA, whichThing)

        if whichThing == "adjacent_all":
            common = []
            numThings = 0
            # get matches for all 4 adjacents. if matches do not equal number of surronding things, then this rul is false
            for thing in core.adjacent:
                topicListB = thing.getTopics()
                matches =self.matchTopics(topicListA, topicListB)
                common.extend(matches)
                numThings += 1
            counted = []
            for topic in common:
                if common.count(topic) >= numThings:
                    counted.append(topic)
            return counted

        elif whichThing in directions:
            topicListB = core.adjacent[whichThing].getTopics()
            matches = self.matchTopics(topicListA, topicListB)
            return matches #<-- there is a match

        elif whichThing == "adjacent_any":
            matches =[]
            for d in directions:
                testThing = core.adjacent[d]
                if testThing is not None:
                    topicListB = testThing.getTopics()
                    matches.extend( self.matchTopics(topicListA, topicListB))
            return matches
        else:
            print "Condition for {0}: No matches found".format(core)
            return []

    def matchTopics(self, topicListA, topicListB):
        matches = []

        # find the topics of shorter list in longer list
        list1 = topicListA if len(topicListB) < len(topicListA) else topicListB
        list2 = topicListB if list1 is topicListA else topicListA
        for topic in list1:
            if topic in list2:
                matches.append(topic)

        return matches

    def getAllTopics(self):
        topics = []
        for st in self.storythings:
            st.extend(st.getTopics())

    #TRUE IF LOCKED, FALSE IF UNLOCKED
    def condition_checkLock(self, context):
        #check both locks
        print "checking the locks"

        #evaluate internal lock first. if internal lock is not true, then eval external lock (a second if, not an else if)
        if context["configuration"] == "single":
            if thing.isLocked():
                return True

        # eval external lock
        if context["configuration"] == "adjacent":
            #evalTopicLock for all adjacent
            if thing.topicLock is None:
                return False

            commonTopics = list( self.condition_matchTopics(context))
            for c in commonTopics:
                    if c in thing.topicLock:
                        return False
            return True #lock exists, and holds because no common topics to unlock it
        else:
            print "Error! This condition should never be reached!"
            return False




#### SAMPLE CODE

#audioFiles = getAllAvailableAudio()
#numShapes = len(audioFiles)
#ids = list(range(0, numShapes))
#for i, a in enumerate(audioFiles):
#    t = StoryThing((i, "triangle"), a)
    #print "{0} {1}".format(t.id, t.default_rec.topics)

#parser = StoryParser(things)




#files = getAllAvailableAudio()
#for file in files:
#    print file
#parser = StoryParser(["thing1", "thing2"])
#parser.playReadySound()


# get list of "live" objects to be worked on
#storythings = ["right", "left", "adjacent"]

# generate configuration of these objects
# for thing in storythings:
# thing.generateAdjacentThings(storythings)
# print thing.adjacent

# init the parser with configured things, and rules for the configuration
#parser = StoryParser(storythings, "rules.json")

# evaluate each rule on each thing from L-R
#for rule in [rule for rule in parser.rules if (rule["name"] == "test")]:
#    print rule
#    for thing in storythings:
#        context = rule["context"]
#        context["thing"] = thing
#        result = parser.evaluateRule(context)
#        if result:
#            parser.executeRule(context)



