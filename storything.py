# StoryThings: Take a shape, map it to an audio file, create some rules governing the playback
import pygame
import json
import os

AUDIO_DIR = "./audio/"

def getAllAvailableAudio():
    files = []
    for file in os.listdir(CONTOUR_DIR):
        if file.endswith(".wav"):
            files.append( file)

    return files



    class Recording(object):
    # give me a filename only. not a path
    def __init__(self, audioFile):
        self.clip = audioFile
        self.topics = []
        self.anti_topics = []

    def addAnti(self, topics):
        # extend the list, but get rid of duplicates
        self.anti_topics = list(set(self.anti_topics.extend(topics)))

    def addTopic(self, topics):
        self.topics = list(set(self.topics.extend(topics)))

    def play(self):
        print "playing"
        if not pygame.mixer:
            pygame.mixer.init()
        clip = pygame.mixer.Sound(AUDIO_DIR+ self.clip)
        clip.play()
        return clip.get_length()

    def stop(self):
        if pygame.mixer:
            pygame.mixer.fadeout(500)  # ms
            pygame.mixer.quit()


class StoryThing(object):
    def __init__(self, shape, audioFile, brec=None):
        self.default_rec = Recording(audioFile)
        self.b_rec = Recording(brec) if brec is not None else brec
        self.now_playing = None

        self.shape = shape
        self.adjacent = None
        # self.rules = [ PLAY, COMBINE] #these are rules that this chip observes. by default all chips PLAY and COMBINE
        # self.topics = ["keyword1", "keyword2",]
        # self.subjects = ["keyword", "keyword",]
        self.timelock = seconds
        self.topicLock = None

        self.LOCKED = False
        self.MORPHED = False

    def getTopics(self):
        if self.MORPHED:
            topics = self.brec.topics
            return topics
        else:
            return default_rec.topics

    def play(self):
        if now_playing is None:
            print "Nothing to play"
            return
        elif not self.LOCKED:
            now_playing.play()
        else:
            print "looks like {0} is locked".format(self)

    # for every storything, calc a L,R,A,B for each adjacent thing surrounding from the collection of storythings
    # the configuration is calculated dynamically for each thing because not all storythings are present in the scene
    # nor are they interacted with at all times. we can see
    def generateAdjacentThings(self, otherThings):
        adjacent["core"] = "me"
        adjacent["left"] = "shape_to_left"
        adjacent["right"] = "shape_to_right"
        adjacent["above"] = "shape_above"
        adjacent["below"] = "shape_below"
        self.adjacent = adjacent





class StoryParser(object):
    def __init__(self, storythings, ruleFile="./rules.json"):
        self.storythings = storythings  # order these things according to internal rule
        self.rules = self._ingestRules(ruleFile)
        self.configuration = []
        self.methods = self._createMethodDict()

    # expects a json or txt with json formating
    def _ingestRules(self, file):
        print os.path.join(file)
        with open("./rules.json") as saveFile:
            print saveFile
            return json.load(saveFile)

    def _createMethodDict(self):
        # later get this from a file too?
        methods = dict()
        methods["merge"] = self.action_combine
        methods["morph"] = self.action_morph
        methods["matchTopics"] = self.condition_matchTopics
        methods["test"] = self.condition_test
        return methods

    def _orderThings(self):
        pass

    def evaluateRule(self, context):
        condition_method = context["condition"]

        # evaluate the condition
        if condition_method is not None:
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
        pass

    # we already know when this is called that the configuration is adject because that's the rule type?
    def action_combine(thing1, context):
        print "Doing this action!", context["action"]

    # matches = matchTopics( thing1, thing2):


    def condition_test(self, context):
        print "A ({0}) matches B({1}) : {2}".format(context["thing"], context["configuration"],
                                                    context["thing"] == context["configuration"])
        return context["thing"] == context["configuration"]

    def action_silence(context):
        print "Doing this action!", context["action"]

    def action_morph(context):
        print "Doing this action!", context["action"]

    def action_block(context):
        print "Doing this action!", context["action"]

    def condition_matchTopics(self, thing, context):
        topicListA = thing.getTopics
        otherThingName = context["chips"]["alias"]
        topicListB = thing.adjacent[otherThingName].getTopics
        return matchTopics(topicListA, topicListA) is not None

    def matchTopics(topicListA, topicListB):
        matches = []

        # find the topics of shorter list in longer list
        list1 = topicListA if len(topicListB) < len(topicListA) else topicListB
        list2 = topicListB if list1 is topicListA else topicListA
        for topic in list1:
            if topic in list2:
                matches.append(topic)

        return matches if len(matches) > 0 else None


#### SAMPLE CODE
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

# for thing in parser.storythings:
#	config = parser.generateAdjacentThings(thing1)
#	for rule in parser.rules:
#		rule["configuration"] = "adjacent"

