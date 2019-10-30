# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Game import Game, WebCamGame
from Environment import Environment


def test_Game001():
    game = Game('test001')
    game.fen = "8/8/8/8/8/8/8/8 w - -"
    json = game.asJson()
    print (json)
    assert json == '{"fen": "8/8/8/8/8/8/8/8 w - -", "name": "test001", "py/object": "Game.Game"}'
    

def test_WebCamGame():
    webCamGame = WebCamGame("chessBoard001")    
    webCamGame.game.fen = "8/8/8/8/8/8/8/8 w - -"
    json = webCamGame.asJson()
    print (json)

    
def test_WebCamGames():
    # get the testEnvironment    
    testEnv = Environment()
    for webCamGame in WebCamGame.getWebCamGames(testEnv.testMediaPath).values():
        print (webCamGame.asJson())
        webCamGame.save("testGames")


test_Game001()
test_WebCamGame()
test_WebCamGames()
