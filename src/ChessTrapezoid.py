#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import numpy as np
import cv2
import chess

class ChessTrapezoid:
    rows=8
    cols=8
    
    """ Chess Trapezoid as seen via a webcam """
    def __init__(self,topLeft,topRight,bottomRight,bottomLeft):
        self.tl,self.tr,self.br,self.br=topLeft,topRight,bottomRight,bottomLeft
        self.poly=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
        self.rotation=0
        # trapezoid representation of squares
        self.tsquares={}
        for square in chess.SQUARES:
            tsquare=self.getSquare(square)
            print(tsquare)
            self.tsquares[square]=tsquare
        
    def getSquare(self,square):
        tsquare={}
        col=chess.square_file(square)
        row=chess.square_rank(square)
        tsquare['square']=square        
        tsquare['an']=chess.SQUARE_NAMES[square]
        #tsquare['poly']=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
        return tsquare         
            
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
    
    