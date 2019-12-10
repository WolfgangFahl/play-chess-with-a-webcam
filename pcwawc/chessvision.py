#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-10-10

@author: wf
see https://www.fide.com/FIDE/handbook/LawsOfChess.pdf
'''

from zope.interface import Interface
from zope.interface import Attribute

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