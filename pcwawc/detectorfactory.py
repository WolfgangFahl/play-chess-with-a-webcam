'''
Created on 2019-12-14

@author: wf
'''
from pcwawc.boarddetector import BoardDetector

class MoveDetectorFactory:
    @staticmethod
    def create(detectorname,board,video,args):
        if detectorname=="luminance":
            moveDetector = BoardDetector(board, video,args.speedup)
        if moveDetector is None:
            raise Exception("MoveDetectorFactory create: unknown detectorname %s" % (detectorname))   
        return moveDetector
