#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.Environment import Environment
from pcwawc.JsonAbleMixin import JsonAbleMixin
from pcwawc.YamlAbleMixin import YamlAbleMixin
from time import strftime
import numpy as  np
import chess
import os

class Game(JsonAbleMixin):
    """ keeps track of a games state in a JavaScript compatible way to exchange game State information
    across platforms e.g. between Python backend and JavaScript frontend"""
    
    def __init__(self, gameid):
        self.gameid = gameid
        self.fen = chess.STARTING_BOARD_FEN
        # http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm
        self.pgn = '[Date "%s"]' % (strftime('%Y.%m.%d'))
        self.locked = False
        self.moveIndex = 0 
        
    def showDebug(self):
        print ("fen: %s" % (self.fen))  
        print ("pgn: %s" % (self.pgn))
        print ("moveIndex: %d" % (self.moveIndex))     

    
class WebCamGame(JsonAbleMixin):
    """ keeps track of a webcam games state in a JavaScript compatible way to exchange game and webcam/board State information
    across platforms e.g. between Python backend and JavaScript frontend"""
    
    def __init__(self, gameid):
        self.gameid = gameid
        self.game = Game(gameid)
        self.warp = Warp()
        
    def checkEnvironment(self, env):
        Environment.checkDir(env.games)    
        
    def save(self, path="games"):
        env = Environment()
        savepath = str(env.projectPath) + "/" + path
        Environment.checkDir(savepath)
        savedir = savepath + "/" + self.gameid
        Environment.checkDir(savedir)
        jsonFile = savedir + "/" + self.gameid + "-webcamgame"
        self.writeJson(jsonFile)
        gameJsonFile = savedir + "/" + self.gameid
        self.game.writeJson(gameJsonFile)
        
        if self.game.locked is not None and not self.game.locked:
            if self.game.fen is not None:
                fenFile = savedir + "/" + self.gameid + ".fen"
                print (self.game.fen, file=open(fenFile, 'w'))
            if self.game.pgn is not None:
                pgnFile = savedir + "/" + self.gameid + ".pgn"
                # see https://python-chess.readthedocs.io/en/latest/pgn.html
                print (self.game.pgn, file=open(pgnFile, 'w'), end="\n\n")
        return savedir    
            
    @staticmethod       
    def getWebCamGames(path):
        webCamGames = {}
        for file  in os.listdir(path):
            if file.endswith(".json"):
                filePath = os.path.join(path, file)
                webCamGame = WebCamGame.readJson(filePath, '')
                if isinstance(webCamGame,WebCamGame):
                    webCamGames[webCamGame.gameid] = webCamGame
                else:
                    raise Exception("invalid json file %s" % filePath)    
        return webCamGames               
        
           
class Warp(YamlAbleMixin, JsonAbleMixin):
    """ holds the trapezoid points to be use for warping an image take from a peculiar angle """

    # construct me from the given setting
    def __init__(self, pointList=[], rotation=0, bgrColor=(0, 255, 0)):
        self.rotation = rotation
        self.bgrColor = bgrColor
        self.pointList = pointList
        self.updatePoints()

    def rotate(self, angle):
        """ rotate me by the given angle"""
        self.rotation = self.rotation + angle
        if self.rotation >= 360:
            self.rotation = self.rotation % 360

    def updatePoints(self):
        """ update my points"""
        pointLen = len(self.pointList)
        if pointLen == 0:
            self.points = None
        else:
            self.points = np.array(self.pointList)
        self.warping = pointLen == 4

    def addPoint(self, px, py):
        """ add a point with the given px,py coordinate
        to the warp points make sure we have a maximum of 4 warpPoints if warppoints are complete when adding reset them
        this allows to support click UIs that need an unwarped image before setting new warp points.
        px,py is irrelevant for reset """
        if len(self.pointList) >= 4:
            self.pointList = []
        else:
            self.pointList.append([px, py])
        self.updatePoints()
