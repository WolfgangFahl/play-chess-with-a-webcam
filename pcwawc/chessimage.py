'''
Created on 2019-12-10

@author: wf
'''
from pcwawc.chessvision import IChessBoardImageSet, IChessBoardImage, IChessBoardVision
from pcwawc.environment import Environment
from pcwawc.jsonablemixin import JsonAbleMixin
from pcwawc.video import Video
from zope.interface import implementer
from timeit import default_timer as timer
import os


@implementer(IChessBoardVision) 
class ChessBoardVision(JsonAbleMixin):   
    """ implements access to chessboard images"""
    
    debug=False
 
    def __init__(self,title="chessboard"):
        self.title=title
        self.video=Video(title)
        self.showDebug=ChessBoardVision.debug
        self.start=None
        self.quitWanted=False
        self.hasImage=False
        self.device=None
        self.timestamps=[]
        pass
    
    def open(self,device):
        self.video.capture(device)
        self.device=device
        
    def readChessBoardImage(self):
        self.hasImage, image, self.quitWanted = self.video.readFrame(self.showDebug)
        if self.video.frames==1:
            self.start=timer()
        timestamp=timer()-self.start
        frameIndex=self.video.frames
        self.chessBoardImageSet=ChessBoardImageSet(self,image,frameIndex,timestamp)
        self.timestamps.append(timestamp)
        return self.chessBoardImageSet
        
    def close(self):
        self.video.close()    
        
    def __getstate__(self):
        state={}
        state["title"]=self.title
        device=self.device
        if not Video.is_int(device):
            cwd=os.getcwd()
            devicepath=os.path.dirname(device)
            root=os.path.commonpath([cwd,devicepath])
            device=os.path.relpath(devicepath,root)+'/'+os.path.basename(device)
        state["device"]=device
        state["timestamps"]=self.timestamps
        return state
        
    def __setstate__(self, state):
        self.title=state["title"]
        self.device=state["device"]
        self.timestamps=state["timestamps"]  
        
    def save(self,path="games/videos"):
        env = Environment()
        savepath = str(env.projectPath) + "/" + path
        Environment.checkDir(savepath)
        jsonFile = savepath + "/" + self.title 
        self.writeJson(jsonFile)    

@implementer(IChessBoardImageSet)     
class ChessBoardImageSet:
    """ a set of images of the current chess board"""
    def __init__(self,vision,image,frameIndex,timeStamp):
        self.vision=vision
        self.frameIndex=frameIndex
        # see https://stackoverflow.com/questions/47743246/getting-timestamp-of-each-frame-in-a-video
        self.timeStamp=timeStamp
        self.cbImage=ChessBoardImage(image)
        self.warped=None
  
@implementer(IChessBoardImage)     
class ChessBoardImage:
    """ a chessboard image and it's transformations"""
    def __init__(self,image):
        self.image=image
        self.height,self.width = image.shape[:2]
