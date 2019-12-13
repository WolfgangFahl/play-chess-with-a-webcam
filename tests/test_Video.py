# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.video import Video
from pcwawc.environment4test import Environment4Test

testenv=Environment4Test()

# test reading an example video
def test_ReadVideo():
    video = Video()
    video.open(testenv.testMedia+'emptyBoard001.avi')
    video.play()
    print ("played %d frames" % (video.frames))
    assert video.frames == 52


def test_ReadVideoWithPostProcess():
    video = Video()
    video.open(testenv.testMedia+'emptyBoard001.avi')
    for frame in range(0, 52):
        ret, jpgImage, quit = video.readFrame(show=True, postProcess=video.addTimeStamp)


# test pausing the video
def test_ReadVideoWithPause():
    video = Video()
    video.open(testenv.testMedia+'emptyBoard001.avi')
    for frame in range(0, 62):
        if frame >= 10 and frame < 20:
            video.pause(True)
        else:
            video.pause(False)
        ret, jpgImage, quit = video.readFrame(show=True)
        # print (video.frames)
        assert ret
        assert jpgImage is not None
        height, width = jpgImage.shape[:2]
        # print ("%d: %d x %d" % (frame,width,height))
        assert (width, height) == (640, 480)
    assert video.frames == 52


# test reading video as jpg frames
def test_ReadJpg():
    video = Video()
    video.open(testenv.testMedia+'emptyBoard001.avi')
    for frame in range(0, 52):
        ret, jpgImage, quit = video.readFrame(show=True)
        assert ret
        assert jpgImage is not None
        height, width = jpgImage.shape[:2]
        # print ("%d: %d x %d" % (frame,width,height))
        assert (width, height) == (640, 480)
    assert video.frames == 52


# create a blank image
def test_CreateBlank():
    video = Video()
    width = 400
    height = 400
    image = video.createBlank(width, height)
    iheight, iwidth, channels = image.shape
    print ("created blank %dx%d image with %d channels" % (iwidth, iheight, channels))
    assert height == iheight
    assert width == iwidth
    assert channels == 3


def test_getSubRect():
    video = Video()
    image = video.readImage(testenv.testMedia+"chessBoard001.jpg")
    subImage = Video.getSubRect(image, (0, 0, 200, 200))
    iheight, iwidth, channels = subImage.shape
    assert iheight == 200
    assert iwidth == 200
    assert channels == 3


def test_device():
    assert Video.is_int("0")
    v0 = int("0")
    assert v0 == 0

test_device()
test_ReadVideoWithPostProcess()
test_ReadVideoWithPause()
test_ReadJpg()
test_ReadVideo()
test_getSubRect()
test_CreateBlank()
