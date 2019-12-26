'''
Created on 2019-12-16

@author: wf
'''
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import chess.engine
import asyncio
import shutil

class Engine:
    """ Chess Engines support e.g. Universal Chess Interface see https://chessprogramming.wikispaces.com/UCI """
    
    # shall we output debug information?
    debug=False
    
    # list of engines to search for
    engineConfigs=[
        {
            "name": "GNU Chess",
            "command":"gnuchess",
            "url":"https://www.gnu.org/software/chess/"
        },
        {
            "name": "Crafty Computer Chess",
            "command":"crafty",
            "url": "http://www.craftychess.com/"
        },
        {
            "name:": "Stockfish Chess",
            "command":"stockfish",
            "url":"https://stockfishchess.org/"
        }]
    
    def __init__(self,engineConfig):
        self.engineCmd=engineConfig["command"]
        self.enginePath=engineConfig["path"]
        self.name=engineConfig["name"]
        self.url=engineConfig["url"]
        
    def start(self):
        # https://python-chess.readthedocs.io/en/latest/engine.html
        pass    
        
    def __str__(self):
        text="chess engine %s called via %s at %s" % (self.name,self.engineCmd,self.enginePath)
        return text    
    
    @staticmethod
    def findEngines():
        engineDict={}
        for engineConfig in Engine.engineConfigs:
            engineCmd=engineConfig["command"]
            enginePath=shutil.which(engineCmd)
            if enginePath is not None:
                if Engine.debug:
                    print ("found %s engine at %s" % (engineCmd,enginePath))
                engineConfig["path"]=enginePath    
                engineDict[engineCmd]=engineConfig
        return engineDict            