# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from BoardFinder import BoardFinder

def getImage(num):
    video=Video()
    filename="testMedia/chessBoard%03d.jpg" % (num)
    image=video.readImage(filename)
    height, width = image.shape[:2]
    print ("read image %s: %dx%d" % (filename,width,height))
    return image

# test finding a chess board
def test_findBoard():
    image=getImage(1)
    finder=BoardFinder(image)
    #finder.setup()

def test_getBlackMaxSide():
    for index in range(0,5):
        image=getImage(index+1)
        finder=BoardFinder(image)
        side=finder.getBlackMaxSide(image)
        print ("black is at %d" % (side))

# test hough transformation
def test_houghTransform():
    expected=[98,46,24,20,36]
    for index in range(0,5):
        video=Video()
        image=getImage(index+1)
        lines=video.houghTransform(image)
        print ("found %d lines in chessBoard%03d" % (lines.size,index+1))
        assert expected[index]==lines.size
        video.drawLines(image,lines)
        video.showImage(image,"hough lines",True,1000)

test_getBlackMaxSide()
test_houghTransform()
test_findBoard()
