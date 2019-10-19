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
    image=getImage(6)
    finder=BoardFinder(image)
    finder.prepare()

def test_getBlackMaxSide():
    # fixme - this is not really the expected result
    expected=[0,0,2,2,0]
    for index in range(0,5):
        image=getImage(index+1)
        finder=BoardFinder(image)
        side=finder.getBlackMaxSide(image)
        print ("black is at %d" % (side))
        assert expected[index]==side

# test hough transformation
def test_houghTransform():
    expected=[98,46,26,20,36,38]
    for index in range(0,6):
        video=Video()
        image=getImage(index+1)
        lines=video.houghTransform(image)
        print ("found %d lines in chessBoard%03d" % (lines.size,index+1))
        assert expected[index]==lines.size
        video.drawLines(image,lines)
        video.showImage(image,"hough lines",True,500)

test_findBoard()
test_getBlackMaxSide()
test_houghTransform()
