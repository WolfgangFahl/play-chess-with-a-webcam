#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from Game import WebCamGame
from pathlib import Path
import os
# get image with the given number

class TheTestEnv:
    """ Test Environment - with prefix The to not be collected by pytest"""
    def __init__(self):
        """ get the directory in which the testMedia resides """
        self.scriptPath = Path(__file__).parent
        self.projectPath=self.scriptPath.parent
        self.testMediaPath=Path(self.projectPath,'testMedia')
        self.testMedia=str(self.testMediaPath.absolute())+"/"
        

    def getWebCamGames(self):
        webCamGames={}
        for file  in os.listdir(self.testMediaPath):
            if file.endswith(".json"):
                filePath=os.path.join(self.testMediaPath,file)
                webCamGame=WebCamGame.readJson(filePath, '')
                webCamGames[webCamGame.name]=webCamGame
        return webCamGames        
                
    
    def getImage(self,num):
        video=Video()
        filename=self.testMedia+"chessBoard%03d.jpg" % (num)
        image=video.readImage(filename)
        height, width = image.shape[:2]
        print ("read image %s: %dx%d" % (filename,width,height))
        return image
