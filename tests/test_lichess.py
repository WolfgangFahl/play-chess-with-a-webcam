"""
Created on 2019-12-21

@author: wf
"""

import getpass
from unittest import TestCase

import lichess.api

from pcwawc.lichessbridge import Game as LichessGame
from pcwawc.lichessbridge import Lichess

debug = True


class MoveHandler:
    """example move handler"""

    def __init__(self, lichess, game, movesToPlay):
        self.lichess = lichess
        self.account = lichess.getAccount()
        self.game = game
        self.movesToPlay = movesToPlay
        pass

    def myTurn(self, moveIndex):
        iAmWhite = self.game.white.username == self.account.username
        myTurnIndex = 0 if iAmWhite else 1
        return moveIndex % 2 == myTurnIndex

    def onState(self, event):
        state = event.state
        # next moveIndex
        moveIndex = state.moveIndex + 1
        if self.myTurn(moveIndex):
            print("%3d moves played: %s" % (moveIndex, state.moves))
            if moveIndex < len(self.movesToPlay):
                self.game.move(self.movesToPlay[moveIndex])


class LichessTest(TestCase):

    def test_lichess(self):
        lichess = Lichess()
        if lichess.client is not None:
            account = lichess.getAccount()
            if debug:
                print(account)
            # print(account.adict)
            pgn = """[Event "Play Chess With a WebCam"]
    [Site "Willich, Germany"]
    [Date "2019-12-21 12:46:49"]
    [Round "1"]
    [White "Wolfgang"]
    [Black "Maria"]
    [Result "1-0"]
    
    1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0"""
            lichess.pgnImport(pgn)
        pass

    def test_game(self):
        game_id = "cpOszEMY"
        lichess = Lichess()
        game = lichess.game(game_id)
        assert game["id"] == game_id
        assert game["moves"] == "e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#"

    # def test_OTB_stream1():
    # test letting a bot play against himself
    #    if getpass.getuser()=="wf":
    #        lichess=Lichess(debug=True)
    # challenge my self
    #        lichess.challenge(lichess.getAccount().username)
    #       game_id=lichess.waitForChallenge()
    #       game=LichessGame(lichess,game_id,debug=True)
    #       moveHandler=MoveHandler(lichess,game,["e2e4","e7e5","f1c4","b8c6"])
    #       game.subscribe(moveHandler.onState)
    #       game.start()
    # game.move('e2e4')
    # game.move('e7e5')
    # game.move('f1c4')
    # game.move('b8c6')
    # game.abort()
    # game.move('b8c6')
    # game.resign()
    # game.stop()

    def test_Botplay(self, tokenName1="token", tokenName2="token2"):
        lichessMe = Lichess(debug=True, tokenName=tokenName1)
        lichessOther = Lichess(debug=True, tokenName=tokenName2)
        if lichessMe.client is not None and lichessOther.client is not None:
            game_id = lichessMe.waitForChallenge()
            lichessOther.challenge(lichessMe.getAccount().username)
            gameMe = LichessGame(lichessMe, game_id, debug=True)
            gameOther = LichessGame(lichessOther, game_id, debug=True)
            moveList = ["e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7"]
            moveHandlerMe = MoveHandler(lichessMe, gameMe, moveList)
            moveHandlerOther = MoveHandler(lichessOther, gameOther, moveList)
            gameMe.subscribe(moveHandlerMe.onState)
            gameOther.subscribe(moveHandlerOther.onState)
            gameMe.start()
            gameOther.start()

    def test_OTB_stream(self):
        # test letting a bot play against anotherbot
        if not getpass.getuser() == "travis":
            self.test_Botplay()
            # test_Botplay("token","token")

    def test_rating(self):
        user = lichess.api.user("thibault")
        rating = user["perfs"]["blitz"]["rating"]
        assert rating > 1000

    def test_broadcast(self):
        pass
