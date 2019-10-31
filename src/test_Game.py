# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Game import Game, WebCamGame
from Environment import Environment
from WebApp import WebApp
from webchesscam import WebChessCamArgs
from unittest.mock import Mock

debug = True


def test_Game001():
    game = Game('test001')
    game.fen = "8/8/8/8/8/8/8/8 w - -"
    json = game.asJson()
    if debug:
        print (json)
    assert  '"fen": "8/8/8/8/8/8/8/8 w - -"' in json  

    
def test_WebCamGame():
    webCamGame = WebCamGame("chessBoard001")    
    webCamGame.game.fen = "8/8/8/8/8/8/8/8 w - -"
    json = webCamGame.asJson()
    if debug:
        print (json)
    assert '"fen": "8/8/8/8/8/8/8/8 w - -"' in json      
    assert "chessBoard001" in json

    
def test_WebCamGames():
    # get the testEnvironment    
    testEnv = Environment()
    for webCamGame in WebCamGame.getWebCamGames(testEnv.testMediaPath).values():
        if debug:
            print (webCamGame.asJson())
        webCamGame.save("testGames")        

        
def test_WebApp():
    webApp = WebApp(WebChessCamArgs(["--debug"]).args)
    WebApp.index = Mock(return_value="")
    game = webApp.game
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
    webApp.chessFEN(fen)
    assert game.fen == fen
    assert game.moveIndex == 0
    webApp.chessMove("e2e4")
    assert game.moveIndex == 1
    webApp.chessMove("e7e5")
    assert game.moveIndex == 2
    webApp.chessMove("d2d3")
    assert game.moveIndex == 3
    webApp.chessTakeback()
    assert game.moveIndex == 2
    webApp.chessSave()
  

test_Game001()
test_WebCamGame()
test_WebCamGames()
test_WebApp()
