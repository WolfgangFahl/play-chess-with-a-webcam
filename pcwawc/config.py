"""
Created on 2019-12-31

@author: wf
"""

#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import os

import yaml


class Config:
    """configuration for Play Chess With a WebCam"""

    def __init__(self, configFile, config=None):
        self.configFile = configFile
        if config is not None:
            self.config = config
        else:
            if not os.path.isfile(configFile):
                print(
                    "%s is missing please create it if you'd like to e.g. use the lichess bot api"
                    % (configFile)
                )
                self.config = {}
            else:
                self.config = yaml.load(open(self.configFile), Loader=yaml.FullLoader)

    @staticmethod
    def default(configName="config", configPath=os.getenv("HOME") + "/.pcwawc/"):
        configFile = configPath + configName + ".yaml"
        return Config(configFile)
