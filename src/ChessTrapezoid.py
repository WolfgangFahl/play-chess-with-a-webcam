#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import numpy as np
import cv2
import chess

class ChessTSquare:
    """ a chess square in it's trapezoidal perspective """
    def __init__(self,square):
        self.square=square
        self.an=chess.SQUARE_NAMES[square]
        self.row=ChessTrapezoid.rows-1-chess.square_rank(square)
        self.col=chess.square_file(square)
        # https://gamedev.stackexchange.com/a/44998/133453
        self.fieldColor=chess.WHITE if (self.col+self.row) % 2 == 0 else chess.BLACK   
        self.piece=None
        #tsquare['poly']=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
            
class ChessTrapezoid:
    """ Chess board Trapezoid (UK) / Trapezium (US) / Trapez (DE)  as seen via a webcam image """
    
    debug=False
    rows=8
    cols=8
    
    def __init__(self,topLeft,topRight,bottomRight,bottomLeft):
        """ construct me from the given corner points"""
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
            tsquare=ChessTSquare(square)
            if ChessTrapezoid.debug:
                print(tsquare)
            self.tsquares[square]=tsquare
            
    def relativeXY(self,rx,ry):
        """ convert a relative 0-1 based coordinate to a coordinate in the trapez"""
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
        """ get the trapezoid chessboard square for the given row and column"""
        row,col=self.rotateIndices(row, col)
        squareIndex = (ChessTrapezoid.rows-1-row) * ChessTrapezoid.cols + col;
        square = chess.SQUARES[squareIndex]
        return self.tsquares[square]
    
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
    
    def maskFEN(self,fen):
        self.board=chess.Board(fen)
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            tsquare=self.tsquares[square]
            tsquare.piece=piece
    
    