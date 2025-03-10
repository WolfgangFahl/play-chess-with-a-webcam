#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

import os

# Json persistence
import jsonpickle


class JsonAbleMixin(object):
    """allow reading and writing derived objects from a json file"""

    debug = False

    # read me from a yaml file
    @staticmethod
    def readJson(name, postfix=".json"):
        jsonFileName = name
        if not name.endswith(postfix):
            jsonFileName = name + postfix
        # is there a jsonFile for the given name
        if os.path.isfile(jsonFileName):
            if JsonAbleMixin.debug:
                print("reading %s" % (jsonFileName))
            json = open(jsonFileName).read()
            result = jsonpickle.decode(json)
            if JsonAbleMixin.debug:
                print(json)
                print(result)
            return result
        else:
            return None

    def asJson(self):
        json = jsonpickle.encode(self)
        return json

    # write me to the json file with the given name (without postfix)
    def writeJson(self, name, postfix=".json"):
        jsonFileName = name + postfix
        json = self.asJson()
        if JsonAbleMixin.debug:
            print("writing %s" % (jsonFileName))
            print(json)
            print(self)
        jsonFile = open(jsonFileName, "w")
        jsonFile.write(json)
        jsonFile.close()
