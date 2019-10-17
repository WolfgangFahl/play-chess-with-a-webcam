# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from BoardFinder import BoardFinder
def test_findBoard():
    video=Video()
    filename="testMedia/chessBoard001.jpg"
    image=video.readImage(filename)
    height, width = image.shape[:2]
    print ("read image %s: %dx%d" % (filename,width,height))
    finder=BoardFinder(image)

test_findBoard()
