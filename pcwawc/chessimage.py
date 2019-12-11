'''
Created on 2019-12-10

@author: wf
'''
from pcwawc.chessvision import IChessBoardImage, IChessBoardVision
from pcwawc.video import Video
from zope.interface import implementer
from timeit import default_timer as timer

@implementer(IChessBoardVision) 
class ChessBoardVision:
    debug=False
    
    """ implements access to chessboard images"""
    def __init__(self,title="chessboard"):
        self.title=title
        self.video=Video(title)
        self.showDebug=ChessBoardVision.debug
        self.start=None
        self.quitWanted=False
        self.hasImage=False
        pass
    
    def open(self,device):
        self.video.capture(device)
        
    def readChessBoardImage(self):
        self.hasImage, image, self.quitWanted = self.video.readFrame(self.showDebug)
        if self.video.frames==1:
            self.start=timer()
        self.chessBoardImage=ChessBoardImage(self,image,self.video.frames,timer()-self.start)
        return self.chessBoardImage
        
    def close(self):
        self.video.close()    

@implementer(IChessBoardImage)     
class ChessBoardImage:
    """ a chessboard image and it's transformations"""
    def __init__(self,vision,image,frameIndex,timeStamp):
        self.vision=vision
        self.frameIndex=frameIndex
        self.image=image
        self.height,self.width = image.shape[:2]
  
        # see https://stackoverflow.com/questions/47743246/getting-timestamp-of-each-frame-in-a-video
        self.timeStamp=timeStamp
        
