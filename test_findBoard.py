# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from BoardFinder import BoardFinder

def getImage():
    video=Video()
    filename="testMedia/chessBoard001.jpg"
    image=video.readImage(filename)
    height, width = image.shape[:2]
    print ("read image %s: %dx%d" % (filename,width,height))
    return image

# test finding a chess board
def test_findBoard():
    image=getImage()
    #finder=BoardFinder(image)

# test hough transformation
def test_houghTransform():
    video=Video()
    image=getImage()
    lines=video.houghTransform(image)
    print ("found %d lines" % (lines.size))
    assert 98==lines.size

test_findBoard()
test_houghTransform()
