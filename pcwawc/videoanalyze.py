#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-12-08

@author: wf
'''
from pcwawc.args import Args
from pcwawc.Video import Video
from pcwawc.Environment import Environment
from pcwawc.boardfinder import BoardFinder, Corners
from pcwawc.game import Warp
import sys

class VideoAnalyzer():
    """ analyzer for chessboard videos - may be used from command line or web app"""
    def __init__(self,args,video=None,logger=None,analyzers=None):
        if video is None:
            self.video = Video()
        else:
            self.video=video;
        self.logger=logger    
        self.args=args
        self.debug=args.debug
        if self.debug:
            self.log("Warp: %s" % (args.warpPointList))
        if analyzers is None:
            self.analyzers={}
        else:
            self.analyzers=analyzers    
        self.warp = Warp(args.warpPointList)
        self.warp.rotation = args.rotation
        # not recording
        self.videopath=None
        self.videoout=None
        
    def open(self):
        if self.video.frames == 0:
            self.video.capture(self.args.input)
           
    def hasImage(self):
        return self.video.frame is not None    
            
    def isRecording(self):
        return self.videoout is not None        
        
    def startVideoRecording(self,path,filename):
        self.open()
        self.videofilename = filename
        # make sure the path exists
        Environment.checkDir(path)
        self.videopath=path+self.videofilename
        return filename
    
    def stopVideoRecording(self):
        self.videoout.release()
        self.videopath=None
        self.videoout=None  
        return self.videofilename
    
    def videoPause(self):
        ispaused = not self.video.paused()
        self.video.pause(ispaused)
        return ispaused
   
        
    def analyze(self):
        pass
    
    def findChessBoard(self):
        return self.findTheChessBoard(self.video.frame,self.video)
    
    def findTheChessBoard(self,image,video):
        finder = BoardFinder(image,video=video)
        corners=finder.findOuterCorners()
        # @FIXME - use property title and frame count instead
        title = 'corners_%s.jpg' % (video.fileTimeStamp())
        histograms=finder.getHistograms(image, title, corners)    
        finder.expand(image,title,histograms,corners)
        if self.debug:
            corners.showDebug(image,title)
            finder.showPolygonDebug(image,title,corners)
            finder.showHistogramDebug(histograms,title,corners)
        trapez=corners.trapez8x8
        self.warp.pointList=trapez
        self.warp.updatePoints()    
        return corners
    
    def warpAndRotate(self, image):
        """ warp and rotate the image as necessary - add timestamp if in debug mode """
        if self.warp.points is None:
            warped = image
        else:
            if len(self.warp.points) < 4:
                self.video.drawTrapezoid(image, self.warp.points, self.warp.bgrColor)
                warped = image
            else:
                warped = self.video.warp(image, self.warp.points)
        if self.warp.rotation > 0:
            warped = self.video.rotate(warped, self.warp.rotation)
        # analyze the board if warping is active
        if self.warp.warping:
            for analyzer in self.analyzers:
                warped = analyzer.analyze(self.video,self.args)
        if self.debug:
            warped = self.video.addTimeStamp(warped)
        # do we need to record?
        if self.videopath is not None:
            # is the output open?
            if self.videoout is None:
                # create correctly sized output
                h, w = warped.shape[:2]
                self.videoout=self.video.prepareRecording(self.videopath,w,h)
         
            self.videoout.write(warped)   
            self.log("wrote frame %d to recording " % (self.video.frames)) 
        return warped
    
    def log(self, msg):
        if self.debug and self.logger is not None:
            self.logger.info(msg)
    
    def setDebug(self, debug):
        self.debug=debug
        BoardFinder.debug=debug
        Corners.debug=debug


if __name__ == '__main__':
    cmdLineArgs = Args("Chessboard Video analyzer")
    args = cmdLineArgs.parse(sys.argv[1:])
    videoAnalyzer=VideoAnalyzer(args)
    videoAnalyzer.analyze()