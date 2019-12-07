#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pathlib import Path
import os

class Environment:
    """ Runtime Environment """
    debugImagePath="/tmp/pcwawc/"

    def __init__(self):
        """ get the directory in which the testMedia resides """
        self.scriptPath = Path(__file__).parent
        self.projectPath = self.scriptPath.parent
        self.testMediaPath = Path(self.projectPath, 'testMedia')
        self.testMedia = str(self.testMediaPath.absolute()) + "/"
        self.games = str(self.projectPath) + "/games"
        
    @staticmethod    
    def checkDir(path):    
        #print (path)
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except OSError:
                print ("Creation of the directory %s failed" % path)
            else:
                print ("Successfully created the directory %s " % path)    
