#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from pathlib import Path


class Environment:
    """ Test and Runtime Environment """

    def __init__(self):
        """ get the directory in which the testMedia resides """
        self.scriptPath = Path(__file__).parent
        self.projectPath = self.scriptPath.parent
        self.testMediaPath = Path(self.projectPath, 'testMedia')
        self.testMedia = str(self.testMediaPath.absolute()) + "/"
    
    # get image with the given number
    def getImage(self, num):
        video = Video()
        filename = self.testMedia + "chessBoard%03d.jpg" % (num)
        image = video.readImage(filename)
        height, width = image.shape[:2]
        print ("read image %s: %dx%d" % (filename, width, height))
        return image
