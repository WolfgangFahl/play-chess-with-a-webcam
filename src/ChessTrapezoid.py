#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import numpy as np
import cv2
import chess

class ChessTrapezoid:
    debug=False
    rows=8
    cols=8
    
    """ Chess Trapezoid as seen via a webcam """
    def __init__(self,topLeft,topRight,bottomRight,bottomLeft):
        self.tl,self.tr,self.br,self.bl=topLeft,topRight,bottomRight,bottomLeft
        self.poly=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
        # prepare the perspective transformation
        # https://stackoverflow.com/questions/27585355/python-open-cv-perspectivetransform
        # https://stackoverflow.com/a/41768610/1497139
        # the destination 
        pts_dst = np.asarray([topLeft,topRight,bottomRight,bottomLeft],dtype=np.float32)
        # the normed square described as a polygon in clockwise direction with an origin at top left
        self.pts_normedSquare = np.asarray([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],dtype=np.float32)
        self.transform=cv2.getPerspectiveTransform(self.pts_normedSquare,pts_dst)
        self.rotation=0
        # trapezoid representation of squares
        self.tsquares={}
        for square in chess.SQUARES:
            tsquare=self.getSquare(square)
            if ChessTrapezoid.debug:
                print(tsquare)
            self.tsquares[square]=tsquare
            
    def relativeXY(self,rx,ry):
        # see https://math.stackexchange.com/questions/2084647/obtain-two-dimensional-linear-space-on-trapezoid-shape
        # https://stackoverflow.com/a/33303869/1497139
        rxry = np.asarray([[rx, ry]],dtype=np.float32)
        # target array - values are irrelevant because the will be overridden
        xya=cv2.perspectiveTransform(np.array([rxry]),self.transform)
        # example result:
        # ndarray: [[[20. 40.]]]
        xy=xya[0][0]
        x,y=xy[0],xy[1]
        return x,y
            
    def tSquareAt(self,row,col):
        row,col=self.rotateIndices(row, col)
        squareIndex = (ChessTrapezoid.rows-1-row) * ChessTrapezoid.cols + col;
        square = chess.SQUARES[squareIndex]
        return self.tsquares[square]
        
    def getSquare(self,square):
        tsquare={}
        tsquare['square']=square        
        tsquare['an']=chess.SQUARE_NAMES[square]
        tsquare['row']=ChessTrapezoid.rows-1-chess.square_rank(square)
        tsquare['col']=chess.square_file(square)
        #tsquare['poly']=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
        return tsquare         
    
    def rotateIndices(self,row,col):
        if self.rotation==0:
            return row,col
        elif self.rotation==90:
            return ChessTrapezoid.cols-1-col,row
        elif self.rotation==180:
            return ChessTrapezoid.rows-1-row,ChessTrapezoid.cols-1-col
        elif self.rotation==270:
            return col,ChessTrapezoid.rows-1-row
        else:
            raise Exception("invalid rotation %d for rotateIndices" % self.rotation)
            
    def prepareMask(self,image):    
        """ prepare a trapezoid/polygon mask to focus on the square chess field seen as a trapezoid"""
        h, w = image.shape[:2]    
        self.mask = np.zeros((h,w,1), np.uint8)  
        color=(128)
        cv2.fillConvexPoly(self.mask,self.poly,color)
        
    def maskImage(self,image):
        """ return the masked image that filters the trapezoid view"""
        masked=cv2.bitwise_and(image,image,mask=self.mask)
        return masked
    
    def maskFen(self,fen):
        self.board=chess.Board(fen)
    
    