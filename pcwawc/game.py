#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.chessvision import IGame
from pcwawc.environment import Environment
from pcwawc.jsonablemixin import JsonAbleMixin
from time import strftime
from zope.interface import implementer

import chess
import os

@implementer(IGame) 
class Game(JsonAbleMixin):
    """ keeps track of a games state """
    
    def __init__(self, gameid):
        self.gameid = gameid
        self.fen = chess.STARTING_BOARD_FEN
        # http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm
        self.pgn = '[Date "%s"]' % (strftime('%Y.%m.%d'))
        self.locked = False
        self.moveIndex = 0 
        
    #def __getstate__(self):
    #    state={}
    #    state["gameid"]=self.gameid
    #    state["pgn"]=self.pgn
    #    state["locked"]=self.locked
    #    state["moveIndex"]=self.moveIndex
    #    return state
    
    #def __setstate__(self, state):
    #    self.gameid=state["gameid"]
    #   self.pgn=state["pgn"]   
    #    self.locked=state["locked"]
    #    self.moveIndex=state["moveIndex"]
        
    def showDebug(self):
        print ("fen: %s" % (self.fen))  
        print ("pgn: %s" % (self.pgn))
        print ("moveIndex: %d" % (self.moveIndex))     

    
class WebCamGame(JsonAbleMixin):
    """ keeps track of a webcam games state """
    
    def __init__(self, gameid):
        self.gameid = gameid
        self.game = Game(gameid)
        self.warp = None
        
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
           

