#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-12-08

@author: wf
'''
from pcwawc.args import Args
import sys

class VideoAnalyzer():
    def __init__(self,args):
        self.args=args
        
    def analyze(self):
        pass

if __name__ == '__main__':
    cmdLineArgs = Args("Chessboard Video analyzer")
    args = cmdLineArgs.parse(sys.argv[1:])
    videoAnalyzer=VideoAnalyzer(args)
    videoAnalyzer.analyze()