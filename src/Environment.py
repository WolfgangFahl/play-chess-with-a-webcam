#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from pathlib import Path
import os
    
class Environment:
    """ Runtime Environment """

    def __init__(self):
        """ get the directory in which the testMedia resides """
        self.scriptPath = Path(__file__).parent
        self.projectPath = self.scriptPath.parent
        self.testMediaPath = Path(self.projectPath, 'testMedia')
        self.testMedia = str(self.testMediaPath.absolute()) + "/"
        self.games = str(self.projectPath) + "/games"
    
class TestEnvironment(Environment):
    warpPointList=[
        ([427,180],[ 962,180],[ 952, 688],[430, 691]),
        ([288, 76],[1057, 93],[1050, 870],[262, 866]),
        ([132, 89],[ 492, 90],[ 497, 451],[122, 462]),
        ([143, 18],[ 511, 13],[ 511, 387],[147, 386]),
        ([260,101],[ 962,133],[ 950, 815],[250, 819]),
        ([250,108],[ 960,135],[ 947, 819],[242, 828]),
        ([277,106],[ 972,129],[ 957, 808],[270, 800]),
        ([278, 88],[ 999, 88],[1072, 808],[124, 786]),
        ([360,238],[2380,224],[2385,2251],[407,2256]),
        ([483,132],[1338,124],[1541, 936],[255, 953]),
        ([  8,  1],[ 813,  1],[ 817, 812],[  3, 809])
        ]
    rotations=[0,0,0,0,270,270,270,0,0,0,0]
    
    """ Test Environment """
    def __init__(self):
        super().__init__()
        rlen=len(TestEnvironment.rotations)
        wlen=len(TestEnvironment.warpPointList)
        if rlen != wlen:
            raise Exception("%d rotations for %d warpPoints" %(rlen,wlen))
        self.imageInfos=[]
        for num in range(1,1000):
            filename = self.testMedia + "chessBoard%03d.jpg" % (num)
            if not os.path.isfile(filename):
                break
            if num-1>=len(TestEnvironment.rotations):
                raise Exception("%d test files for %d warpPoints/rotations" %(num,wlen))
            imageInfo={'index': num,
                       'title': "image%03d" % (num),
                       'filename': filename,
                       'rotation': TestEnvironment.rotations[num-1],
                       'warpPoints': TestEnvironment.warpPointList[num-1]}
            self.imageInfos.append(imageInfo)
        
    # get image with the given number
    def getImage(self, num):
        image,video=self.getImageWithVideo(num)
        if video is None:
            pass
        return image
        
    # get image with the given number
    def getImageWithVideo(self, num):   
        video = Video()
        filename = self.testMedia + "chessBoard%03d.jpg" % (num)
        image = video.readImage(filename)
        height, width = image.shape[:2]
        print ("read image %s: %dx%d" % (filename, width, height))
        return image,video
