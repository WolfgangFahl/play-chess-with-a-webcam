#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import os
from time import strftime

import chess
import chess.pgn
from zope.interface import implementer

from pcwawc.chessvision import IGame
from pcwawc.environment import Environment
from pcwawc.jsonablemixin import JsonAbleMixin


@implementer(IGame)
class Game(JsonAbleMixin):
    """keeps track of a games state"""

    def __init__(self, gameid):
        self.gameid = gameid
        self.fen = chess.STARTING_BOARD_FEN
        # http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm
        self.pgn = None
        self.headers = {}
        self.headers["Date"] = strftime("%Y-%m-%d %H:%M:%S")
        self.locked = False
        self.moveIndex = 0

    # def __getstate__(self):
    #    state={}
    #    state["gameid"]=self.gameid
    #    state["pgn"]=self.pgn
    #    state["locked"]=self.locked
    #    state["moveIndex"]=self.moveIndex
    #    return state

    # def __setstate__(self, state):
    #    self.gameid=state["gameid"]
    #   self.pgn=state["pgn"]
    #    self.locked=state["locked"]
    #    self.moveIndex=state["moveIndex"]
    def updateHeaders(self, headers):
        for key, header in self.headers.items():
            headers[key] = header

    def update(self, board):
        try:
            game = chess.pgn.Game.from_board(board.chessboard)
            self.updateHeaders(game.headers)
            self.pgn = str(game)
        except BaseException as e:
            print("pgn error: %s", str(e))

    def move(self, board):
        self.moveIndex += 1
        self.update(board)

    @staticmethod
    def gameId():
        gameid = strftime("game_%Y-%m-%d_%H%M%S")
        return gameid

    def showDebug(self):
        print("fen: %s" % (self.fen))
        print("pgn: %s" % (self.pgn))
        print("moveIndex: %d" % (self.moveIndex))


class WebCamGame(Game):
    """keeps track of a webcam games state"""

    def __init__(self, gameid):
        super(WebCamGame, self).__init__(gameid)
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
        self.writeJson(gameJsonFile)

        if self.locked is not None and not self.locked:
            if self.fen is not None:
                fenFile = savedir + "/" + self.gameid + ".fen"
                print(self.fen, file=open(fenFile, "w"))
            if self.pgn is not None:
                pgnFile = savedir + "/" + self.gameid + ".pgn"
                # see https://python-chess.readthedocs.io/en/latest/pgn.html
                print(self.pgn, file=open(pgnFile, "w"), end="\n\n")
        return savedir

    @staticmethod
    def createNewGame():
        return WebCamGame(Game.gameId())

    @staticmethod
    def fromArgs(args):
        env = Environment()
        if args is None or args.game is None:
            webCamGame = WebCamGame.createNewGame()
        else:
            gamepath = args.game
            if not gamepath.startswith("/"):
                gamepath = env.games + "/" + gamepath
            webCamGame = WebCamGame.readJson(gamepath)
            if webCamGame is None:
                # self.videoAnalyzer.log("could not read %s " % (gamepath))
                webCamGame = webCamGame.createNewGame()
        webCamGame.checkEnvironment(env)
        if args is not None:
            if args.event is not None:
                webCamGame.headers["Event"] = args.event
            if args.site is not None:
                webCamGame.headers["Site"] = args.site
            if args.round is not None:
                webCamGame.headers["Round"] = args.round
            if args.white is not None:
                webCamGame.headers["White"] = args.white
            if args.black is not None:
                webCamGame.headers["Black"] = args.black

        return webCamGame

    @staticmethod
    def getWebCamGames(path):
        webCamGames = {}
        for file in os.listdir(path):
            if file.endswith(".json"):
                filePath = os.path.join(path, file)
                webCamGame = WebCamGame.readJson(filePath, "")
                if isinstance(webCamGame, WebCamGame):
                    webCamGames[webCamGame.gameid] = webCamGame
                else:
                    raise Exception("invalid json file %s" % filePath)
        return webCamGames
