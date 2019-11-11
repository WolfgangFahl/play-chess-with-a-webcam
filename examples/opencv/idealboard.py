#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# Ideal Board
import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

class IdealBoard:
    windowName='Ideal Chessboard'
    rows=8
    cols=8
    
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.image = np.zeros((height,width,3), np.uint8)
        for col in range(IdealBoard.cols):
            for row in range(IdealBoard.rows):
                self.colorField(col,row)
                self.colorPiece(col,row)
    
    def colorPiece(self,col,row,white=(169,169,169),black=(86,86,86)):   
        filled=-1   
        color=black if row<2 else white if row>5 else None
        # uncomment to simulate e2-e4
        #if row==6 and col==4: color=None
        #if row==4 and col==4: color=white
        
        if color is not None:
            radius=self.width//IdealBoard.cols//3
            center=int(self.width*(col+0.5)/IdealBoard.cols),int(self.height*(row+0.5)/IdealBoard.rows)
            cv2.circle(self.image, center, radius, color=color, thickness=filled)        
                
    def colorField(self,col,row,white=(255,255,255),black=(0,0,0)):
        filled=-1           
        # https://gamedev.stackexchange.com/a/44998/133453
        color=white if (col+row) % 2 == 0 else black        
        pt1=(self.width*(col+0)//IdealBoard.cols,self.height*(row+0)//IdealBoard.rows)
        pt2=(self.width*(col+1)//IdealBoard.cols,self.height*(row+1)//IdealBoard.rows)
        cv2.rectangle(self.image, pt1, pt2, color,thickness=filled)

    def save(self,filepath):
         cv2.imwrite(filepath, self.image)
          
    def show(self):     
        cv2.imshow(IdealBoard.windowName, self.image)     
        cv2.waitKey()
      
board=IdealBoard(800,800)   
board.save("/tmp/idealchessboard.jpg")
board.show()   