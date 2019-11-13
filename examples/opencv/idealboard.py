#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# Ideal Board
import cv2  # Not actually necessary if you just want to create an image.
import numpy as np
from timeit import default_timer as timer
from Environment import Environment
import matplotlib.pyplot as plt
from enum import IntEnum
from chess import square

class SquareKind(IntEnum):
    """ kind of Square """
    FIELD_WHITE = 0
    FIELD_BLACK = 1
    PIECE_WHITE = 2
    PIECE_BLACK = 3
    
    def title(self,titles=["white field", "black field", "white piece","black piece"]):
        return titles[self]
    
class Channel(IntEnum):
    GREEN=0
    BLUE=1
    RED=2
    
    def title(self,titles=["green", "blue", "red"]):
        return titles[self]
        
 
class IdealBoard:
    windowName='Ideal Chessboard'
    rows=8
    cols=8
    debug=True
    fieldWhite=(255,255,255)
    fieldBlack=(0,0,0)
    pieceWhite=(169,169,169)
    pieceBlack=(86,86,86)
        
    
    def __init__(self,width,height,fieldWhite=None,fieldBlack=None,pieceWhite=None, pieceBlack=None):
        self.width=width
        self.height=height
        if fieldWhite is None: fieldWhite=IdealBoard.fieldWhite
        if fieldBlack is None: fieldBlack=IdealBoard.fieldBlack
        if pieceWhite is None: pieceWhite=IdealBoard.pieceWhite
        if pieceBlack is None: pieceBlack=IdealBoard.pieceBlack
        self.pieceWhite=pieceWhite
        self.pieceBlack=pieceBlack
        self.fieldWhite=fieldWhite
        self.fieldBlack=fieldBlack
        self.image = np.zeros((height,width,3), np.uint8)
        self.diffSumValue=1000*1000*1000
        for col in range(IdealBoard.cols):
            for row in range(IdealBoard.rows):
                self.colorField(col,row,white=fieldWhite,black=fieldBlack)
                self.colorPiece(col,row,white=pieceWhite,black=pieceBlack)
                
    @staticmethod
    def createIdeal(width,height):
        return IdealBoard(width,height,fieldWhite=IdealBoard.fieldWhite)            
    
    def colorPiece(self,col,row,white,black):   
        filled=-1   
        color=black if row<2 else white if row>5 else None
        # uncomment to simulate e2-e4
        #if row==6 and col==4: color=None
        #if row==4 and col==4: color=white
        
        if color is not None:
            radius=self.width//IdealBoard.cols//3
            center=int(self.width*(col+0.5)/IdealBoard.cols),int(self.height*(row+0.5)/IdealBoard.rows)
            cv2.circle(self.image, center, radius, color=color, thickness=filled)        
                
    def colorField(self,col,row,white,black):
        filled=-1           
        # https://gamedev.stackexchange.com/a/44998/133453
        color=white if (col+row) % 2 == 0 else black        
        pt1=(self.width*(col+0)//IdealBoard.cols,self.height*(row+0)//IdealBoard.rows)
        pt2=(self.width*(col+1)//IdealBoard.cols,self.height*(row+1)//IdealBoard.rows)
        cv2.rectangle(self.image, pt1, pt2, color,thickness=filled)
        
    def diff(self,other):
        return cv2.absdiff(self.image,other)   
        
    def diffSum(self,other):
        #diffImage=self.diff(other) 
        #return diffImage.sum()   
        # https://stackoverflow.com/questions/17829092/opencv-cv2-absdiffimg1-img2-sum-without-temporary-img
        self.diffSumValue=cv2.norm(self.image,other,cv2.NORM_L1)
        return self.diffSumValue
    
    def adjust(self,channel,squareKind,squareKindToAdjust,color,value):
        g,b,r=color
        if not squareKind==squareKindToAdjust:
            return color
        elif channel==Channel.GREEN:
            return value,b,r
        elif channel==Channel.BLUE:
            return g,value,r
        elif channel==Channel.RED:
            return g,b,value
        else:
           raise Exception("invalid channel %d",channel)
    
    def optimize(self,chessboardImage,channel,squareKind,fromValue=255,toValue=0,step=-1):
        h, w = chessboardImage.shape[:2]
        values=np.array([])
        diffSums=np.array([])
        # assume we are the best ideal board so far
        minBoard=self
        minSum=self.diffSumValue
        minValue=-1
        for value in range(fromValue,toValue,step):
            values=np.append(values,value)
            fieldWhite=self.adjust(channel,squareKind,SquareKind.FIELD_WHITE,self.fieldWhite,value)
            fieldBlack=self.adjust(channel,squareKind,SquareKind.FIELD_BLACK,self.fieldBlack,value)
            pieceWhite=self.adjust(channel,squareKind,SquareKind.PIECE_WHITE,self.pieceWhite,value)
            pieceBlack=self.adjust(channel,squareKind,SquareKind.PIECE_BLACK,self.pieceBlack,value)
            idealBoard=IdealBoard(w,h,fieldWhite=fieldWhite,fieldBlack=fieldBlack,pieceWhite=pieceWhite,pieceBlack=pieceBlack)
            diffSum=idealBoard.diffSum(chessboardImage)
            if diffSum<minBoard.diffSumValue:
                minBoard=idealBoard
                minValue=value
            diffSums=np.append(diffSums,diffSum)
            print ("%s %s  value: %3d -> %d / %d" % (squareKind.title(),channel.title(),value,diffSum, minBoard.diffSumValue))
        if IdealBoard.debug:
            title="%s %s %d" % (squareKind.title(),channel.title(),minValue)
            IdealBoard.showImage(minBoard.image, title, waitTime=1)
            plt.title(title)
            plt.plot(values,diffSums)
            # https://stackoverflow.com/questions/30364770/how-to-set-timeout-to-pyplot-show-in-matplotlib
            plt.show()
        return minBoard    
        
    @staticmethod   
    def optimizeIdeal(chessboardImage):
        h, w = chessboardImage.shape[:2]
        minBoard=IdealBoard.createIdeal(w,h)
        # loop over fieldwhite, fieldblack, piecewhite, pieceblack
        for squareKind in SquareKind:
            # loop over b,g,r
            for channel in Channel:
                minBoard=minBoard.optimize(chessboardImage,channel,squareKind)               
        return minBoard

    def save(self,filepath):
        cv2.imwrite(filepath, self.image)
          
    @staticmethod
    def showImage(image=None,title="idealboard",waitTime=86400*1000):     
        if image is not None:
            cv2.imshow(title,image)   
            cv2.imwrite("/tmp/"+title+".jpg",image)     
        cv2.waitKey(waitTime)
        
    def show(self,title="idealboard",waitTime=86400*1000):
        IdealBoard.showImage(self.image,title,waitTime) 
      
shortTime=500      
IdealBoard.debug=False
env=Environment()
chessboard12Path=env.testMedia+'chessboard012.jpg'
chessboard12=cv2.imread(chessboard12Path)
IdealBoard.showImage(chessboard12,title="original",waitTime=shortTime)
start=timer()      
board=IdealBoard.createIdeal(527,527)
end=timer()
print('ideal board created in %.3fs' % (end-start))
board.show(waitTime=shortTime)
start=timer()  
diffImage=board.diff(chessboard12)
end=timer()
print('diff created in %.3fs' % (end-start))
IdealBoard.showImage(diffImage,title="diff",waitTime=shortTime)   
start=timer()
optimized=IdealBoard.optimizeIdeal(chessboard12)
end=timer()
print('optimized in %.3fs' % (end-start))
IdealBoard.showImage(image=optimized.image,title="optimized",waitTime=shortTime)
IdealBoard.showImage(image=optimized.diff(chessboard12),title="optimizedDiff")
board.save("/tmp/idealchessboard.jpg")
