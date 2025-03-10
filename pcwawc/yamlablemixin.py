#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

import io
import os

# Yaml persistence
import yaml


class YamlAbleMixin(object):
    """allow reading and writing derived objects from a yaml file"""

    debug = False

    # read me from a yaml file
    @staticmethod
    def readYaml(name):
        yamlFile = name
        if not yamlFile.endswith(".yaml"):
            yamlFile = yamlFile + ".yaml"
        # is there a yamlFile for the given name
        if os.path.isfile(yamlFile):
            with io.open(yamlFile, "r") as stream:
                if YamlAbleMixin.debug:
                    print("reading %s" % (yamlFile))
                result = yaml.load(stream, Loader=yaml.Loader)
                if YamlAbleMixin.debug:
                    print(result)
                return result
        else:
            return None

    # write me to my yaml file
    def writeYaml(self, name):
        yamlFile = name
        if not yamlFile.endswith(".yaml"):
            yamlFile = yamlFile + ".yaml"
        with io.open(yamlFile, "w", encoding="utf-8") as stream:
            yaml.dump(self, stream)
            if YamlAbleMixin.debug:
                print(yaml.dump(self))
