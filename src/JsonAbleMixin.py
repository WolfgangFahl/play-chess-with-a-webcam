#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Json persistence
import jsonpickle
import os


class JsonAbleMixin(object):
    """ allow reading and writing derived objects from a json file"""
    debug = False

    # read me from a yaml file
    @staticmethod
    def readJson(name, postfix=".json"):
        jsonFileName = name + postfix
        # is there a jsonFile for the given name
        if os.path.isfile(jsonFileName):
            if JsonAbleMixin.debug:
                print("reading %s" % (jsonFileName))
            json = open(jsonFileName).read()
            result = jsonpickle.decode(json)
            if (JsonAbleMixin.debug):
                print (json)
                print (result)
            return result
        else:
            return None

    # write me to the json file with the given name (without postfix)
    def writeJson(self, name, postfix=".json"):
        jsonFileName = name + postfix
        json = jsonpickle.encode(self)
        if JsonAbleMixin.debug:
            print("writing %s" % (jsonFileName))
            print(json)
            print(self)
        jsonFile = open(jsonFileName, "w")
        jsonFile.write(json)
        jsonFile.close()
