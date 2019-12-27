'''
Created on 2019-12-16

@author: wf
'''
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import chess.engine
import shutil

class Engine:
    """ Chess Engines support e.g. Universal Chess Interface see https://chessprogramming.wikispaces.com/UCI """
    
    # shall we output debug information?
    debug=False
    
    # list of engines to search for
    engineConfigs=[
        {
            "name": "Crafty Computer Chess",
            "command":"crafty",
            "url": "http://www.craftychess.com/",
            "protocol": "?"
        },
        {
            "name": "GNU Chess",
            "command":"gnuchess",
            "url":"https://www.gnu.org/software/chess/",
            "protocol":"uci"
        },
        {
            "name": "Stockfish Chess",
            "command":"stockfish",
            "url":"https://stockfishchess.org/",
            "protocol":"uci"
        },
        {
            "name": "XBoard",
            "command":"xboard",
            "url":"https://www.gnu.org/software/xboard/manual/xboard.html",
            "protocol":"xboard"
        }  
        ]
    
    def __init__(self,engineConfig,timeout=5):
        self.engineCmd=engineConfig["command"]
        self.enginePath=engineConfig["path"]
        self.name=engineConfig["name"]
        self.url=engineConfig["url"]
        self.protocolName=engineConfig["protocol"]
        if self.protocolName=="uci":
            self.protocol=chess.engine.UciProtocol
        elif self.protocolName=="xboard":
            self.protocol=chess.engine.XBoardProtocol
        else:
            self.protocol=None
        self.timeout=timeout
        #asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())       
        # https://python-chess.readthedocs.io/en/latest/engine.html
        self.error=None
    
    def open(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engineCmd,timeout=self.timeout,debug=Engine.debug)
        except Exception as te:
            self.engine=None
            self.error=te
            pass
        return self.engine
        
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