# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video

# test reading an example video
def test_ReadVideo():
    video=Video()
    video.open('testMedia/emptyBoard001.avi')
    video.play()
    print ("played %d frames" % (video.frames))
    assert video.frames == 52

# create a blank image
def test_CreateBlank():
    video=Video()
    width=400
    height=400
    image=video.createBlank(width,height)
    iheight, iwidth, channels = image.shape
    print ("created blank %dx%d image with %d channels" % (iwidth,iheight,channels))
    assert height==iheight
    assert width==iwidth
    assert channels==3

def test_getSubRect():
    video=Video()
    image=video.readImage("testMedia/chessBoard001.jpg")
    subImage=video.getSubRect(image,(0,0,200,200))
    iheight, iwidth, channels = subImage.shape
    assert iheight==200
    assert iwidth==200
    assert channels==3


test_ReadVideo()
test_getSubRect()
test_CreateBlank()
