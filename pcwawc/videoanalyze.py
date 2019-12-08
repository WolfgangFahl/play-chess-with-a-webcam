#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-12-08

@author: wf
'''
from pcwawc.args import Args
import sys
from pcwawc.boardfinder import BoardFinder, Corners

class VideoAnalyzer():
    """ analyzer for chessboard videos - may be used from command line or web app"""
    def __init__(self,args):
        self.args=args
        self.debug=False
        
    def analyze(self):
        pass
    
    def findChessBoard(self,image,video):
        finder = BoardFinder(image,video=video)
        corners=finder.findOuterCorners()
        # @FIXME - use propert title and frame count instead
        title = 'corners_%s.jpg' % (video.fileTimeStamp())
        histograms=finder.getHistograms(image, title, corners)    
        finder.expand(image,title,histograms,corners)
        if self.debug:
            corners.showDebug(image,title)
            finder.showPolygonDebug(image,title,corners)
            finder.showHistogramDebug(histograms,title,corners)
        return corners
    
    def setDebug(self, debug):
        self.debug=debug
        BoardFinder.debug=debug
        Corners.debug=debug


if __name__ == '__main__':
    cmdLineArgs = Args("Chessboard Video analyzer")
    args = cmdLineArgs.parse(sys.argv[1:])
    videoAnalyzer=VideoAnalyzer(args)
    videoAnalyzer.analyze()