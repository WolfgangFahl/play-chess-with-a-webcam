'''
Created on 2019-12-21

@author: wf
'''
from pcwawc.lichess import Lichess
from pcwawc.lichess import Game as LichessGame
import getpass
import lichess.api

debug=True
def test_lichess():
    lichess=Lichess()
    if lichess.client is not None:
        account=lichess.getAccount()
        if debug:
            print(account)
        #print(account.adict)
        pgn="""[Event "Play Chess With a WebCam"]
[Site "Willich, Germany"]
[Date "2019-12-21 12:46:49"]
[Round "1"]
[White "Wolfgang"]
[Black "Maria"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0"""
        lichess.pgnImport(pgn)
    pass

def test_game():
    game_id="cpOszEMY"
    lichess=Lichess()
    game=lichess.game(game_id)
    assert game["id"]==game_id
    assert game["moves"]=="e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#"
    
class MoveHandler():
    def __init__(self,lichess,game,movesToPlay):
        self.lichess=lichess
        self.account=lichess.getAccount()
        self.game=game
        self.movesToPlay=movesToPlay
        pass
    
    def myTurn(self,moveIndex):
        iAmWhite=self.game.white.username==self.account.username
        myTurnIndex=0 if iAmWhite else 1
        return moveIndex%2 == myTurnIndex
    
    def onState(self,event):
        state=event.state 
        # next moveIndex
        moveIndex=state.moveIndex+1
        if self.myTurn(moveIndex):  
            print ("%3d moves played: %s" % (moveIndex,state.moves))
            if moveIndex<len(self.movesToPlay):
                self.game.move(self.movesToPlay[moveIndex])
        
def test_OTB_stream1():
    # test letting a bot play against himself
    if getpass.getuser()=="wf":
        lichess=Lichess(debug=True)
        # challenge my self
        lichess.challenge(lichess.getAccount().username)
        game_id=lichess.waitForChallenge()
        game=LichessGame(lichess,game_id,debug=True)
        moveHandler=MoveHandler(game,["e2e4","e7e5","f1c4","b8c6"])
        game.subscribe(moveHandler.onState)
        game.start()
        #game.move('e2e4')
        #game.move('e7e5')  
        #game.move('f1c4')
        #game.move('b8c6')
        #game.abort()
        # game.move('b8c6')
        #game.resign()
        #game.stop()
        
def test_OTB_stream2():
    # test letting a bot play against anotherbot
    if getpass.getuser()=="wf":
        lichessMe=Lichess(debug=True)
        lichessOther=Lichess(debug=True,tokenName="token2")   
        game_id=lichessMe.waitForChallenge()
        lichessOther.challenge(lichessMe.getAccount().username)
        gameMe=LichessGame(lichessMe,game_id,debug=True)
        gameOther=LichessGame(lichessOther,game_id,debug=True)
        moveList=["e2e4","e7e5","f1c4","b8c6","d1h5","g8f6","h5f7"]
        moveHandlerMe=MoveHandler(lichessMe,gameMe,moveList)
        moveHandlerOther=MoveHandler(lichessOther,gameOther,moveList)
        gameMe.subscribe(moveHandlerMe.onState)
        gameOther.subscribe(moveHandlerOther.onState)
        gameMe.start()
        gameOther.start()
        
       
def test_rating():
    user = lichess.api.user('thibault')
    rating=user['perfs']['blitz']['rating']
    assert rating>1000   

#test_rating()    
#test_lichess()
#test_game()
#test_OTB_stream1()
test_OTB_stream2()
