# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from BoardFinder import BoardFinder
from mathUtils import getIndexRange

def getImage(num):
    video=Video()
    filename="testMedia/chessBoard%03d.jpg" % (num)
    image=video.readImage(filename)
    height, width = image.shape[:2]
    print ("read image %s: %dx%d" % (filename,width,height))
    return image

# test finding a chess board
def test_findBoard():
    #for index in range(5,8):
      image=getImage(7)
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

def test_Dot():
    video=Video()
    dotImage=video.readImage("testMedia/greendot.jpg")
    image=getImage(7)
    finder=BoardFinder(image)
    dotHSVRanges=finder.calibrateCornerMarker(dotImage)
    assert dotHSVRanges==[(61, 91), (81, 108), (34, 60)]

def test_histRange():
    hist=[0,0,0,1,2,4,2,1,0,0,0,0]
    indexRange=getIndexRange(hist,1,10)
    print (indexRange)
    assert indexRange==(3, 7)

test_histRange()
test_Dot()
test_findBoard()
test_getBlackMaxSide()
test_houghTransform()
