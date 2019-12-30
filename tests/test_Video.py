# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.video import Video
from pcwawc.environment4test import Environment4Test
from unittest import TestCase

testenv=Environment4Test()
class VideoTest(TestCase):
    
    # test reading an example video
    def test_ReadVideo(self):
        video = Video()
        video.open(testenv.testMedia+'emptyBoard001.avi')
        video.play()
        print ("played %d frames" % (video.frames))
        assert video.frames == 52
    
    def test_ReadVideoWithPostProcess(self):
        video = Video()
        video.open(testenv.testMedia+'emptyBoard001.avi')
        for frame in range(0, 52):
            ret, jpgImage, quit = video.readFrame(show=True, postProcess=video.addTimeStamp)
    
    # test pausing the video
    def test_ReadVideoWithPause(self):
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
    def test_ReadJpg(self):
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
    def test_CreateBlank(self):
        video = Video()
        width = 400
        height = 400
        image = video.createBlank(width, height)
        iheight, iwidth, channels = image.shape
        print ("created blank %dx%d image with %d channels" % (iwidth, iheight, channels))
        assert height == iheight
        assert width == iwidth
        assert channels == 3
    
    
    def test_getSubRect(self):
        video = Video()
        image = video.readImage(testenv.testMedia+"chessBoard001.jpg")
        subImage = Video.getSubRect(image, (0, 0, 200, 200))
        iheight, iwidth, channels = subImage.shape
        assert iheight == 200
        assert iwidth == 200
        assert channels == 3
    
    def test_device(self):
        assert Video.is_int("0")
        v0 = int("0")
        assert v0 == 0
        
    def test_Concatenate(self):
        video=Video()
        w=400
        h=400
        #https://stackoverflow.com/a/21170291/1497139
        image1=video.createBlank(w, h, (192,192,192))
        image2=video.createBlank(w, h, (255,128,0))
        image3=video.createBlank(w, h, (255//3,255//3,255/3))
        image4=video.createBlank(w, h, (0,0,255))
        combined=video.as2x2(image1,image2,image3,image4,downScale=1)
        hc, wc= combined.shape[:2]
        assert hc==2*h
        assert wc==2*w    
        video.showImage(combined, "combined",keyWait=1000)
