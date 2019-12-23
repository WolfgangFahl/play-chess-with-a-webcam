'''
Created on 2019-12-21

@author: wf
'''
from pcwawc.lichess import Lichess

def test_lichess():
    lichess=Lichess()
    if lichess.client is not None:
        account=lichess.getAccount()
        #print(account)
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
    gameid="cpOszEMY"
    lichess=Lichess()
    game=lichess.game(gameid)
    assert game["id"]==gameid
    assert game["moves"]=="e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#"
    
test_lichess()
test_game()
