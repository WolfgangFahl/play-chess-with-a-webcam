#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-10-10

@author: wf
see e.g. https://www.fide.com/FIDE/handbook/LawsOfChess.pdf
'''

from zope.interface import Interface
from zope.interface import Attribute
from enum import IntEnum

class FieldState(IntEnum):
    """ the state of a field is a combination of the field color with a piece color + two empty field color options"""
    WHITE_EMPTY = 0
    WHITE_WHITE = 1
    WHITE_BLACK = 2
    BLACK_EMPTY = 3
    BLACK_WHITE = 4
    BLACK_BLACK = 5    
    
    def title(self,titles=["white empty", "white on white", "black on white","black empty","white on black","black on black"]):
        return titles[self]

class IGame(Interface):
    pgn=Attribute("Portable game notation")
    
class IChessboard(Interface):
    """ chessboard """
    fen=Attribute("Forsyth–Edwards Notation")
    
class ISquare(Interface):
    """ one of the 64 square fields of a chessboard """
    an=Attribute("algebraic notation")
    fieldColor=Attribute("color of the empty square")
    piece=Attribute("chess piece currently on the square - may be None")
    
class IPiece(Interface):
    """ a chess piece King,Queen,Bishop,Knight,Rook or Pawn"""   
    color=Attribute("color of the piece")
    
class IChessBoardVision(Interface):
    title=Attribute("name/title of the chessboard observation")
    """ visual observer of a chessboard e.g. with a camera - a video or still image"""
    def open(self,device):
        """ open the access to the chessboard images via the given device e.g. device number or filepath"""
        pass
    
    def readChessBoardImage(self):
        """ read a chessboard Image and return it"""
        pass
        
    def close(self):
        """ close the access to the chessbaord images"""
        pass
    
class IChessBoardImageSet(Interface):
    frameIndex=Attribute("index of image in a sequence")
    timeStamp=Attribute("time")    
    image=Attribute("original image")
    warped=Attribute("image warped to square size")
        
    
class IChessBoardImage(Interface):
    """ a single image of a chessboard"""
    image=Attribute("original trapezoid image")
    width=Attribute("width of the original image")
    height=Attribute("width of the original image")
    
class IMoveDetector(Interface):
    """ a detector for moves on a chessboard image"""
    def analyzeChessBoardImage(self,image,video,args):
        pass    