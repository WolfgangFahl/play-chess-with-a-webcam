# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Game import Game, WebCamGame
from HelpTesting import TheTestEnv

def test_Game001():
    game=Game('test001')
    game.fen="8/8/8/8/8/8/8/8 w - -"
    json=game.asJson()
    print (json)
    assert json=='{"fen": "8/8/8/8/8/8/8/8 w - -", "name": "test001", "py/object": "Game.Game"}'
    

def test_WebCamGame():
    webCamGame=WebCamGame("chessBoard001")    
    webCamGame.game.fen="8/8/8/8/8/8/8/8 w - -"
    json=webCamGame.asJson()
    print (json)
    
def test_WebCamGames():
    # get the testEnvironment    
    testEnv=TheTestEnv()
    for webCamGame in testEnv.getWebCamGames().values():
        print (webCamGame.asJson())

test_Game001()
test_WebCamGame()
test_WebCamGames()
