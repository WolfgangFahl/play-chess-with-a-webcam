#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
"""
Created on 2019-10-10

@author: wf
see e.g. https://www.fide.com/FIDE/handbook/LawsOfChess.pdf
"""
# <uml>
# IChessBoardVision "1" ..> "n" IChessBoardImageSet
# IMoveDetector "1" ..> "n" IChessBoardImageSet
# IChessBoardVision "1" -- "1" IChessBoard
# IChessBoardVision "1" -- "1" IWarp
# IGame "1" -- "1" IChessBoard
# IChessBoardImageSet "1" -- "n" IChessBoardImage
# IChessBoard "1" -- "64" ISquare
# ISquare "1" -- "1" IPiece
# ISquare "1" -- "1" FieldState
# </uml>

from enum import IntEnum

from zope.interface import Attribute, Interface


class FieldState(IntEnum):
    """the state of a field is a combination of the field color with a piece color + two empty field color options"""

    WHITE_EMPTY = 0
    WHITE_WHITE = 1
    WHITE_BLACK = 2
    BLACK_EMPTY = 3
    BLACK_WHITE = 4
    BLACK_BLACK = 5

    def title(
        self,
        titles=[
            "white empty",
            "white on white",
            "black on white",
            "black empty",
            "white on black",
            "black on black",
        ],
    ):
        return titles[self]


class IGame(Interface):
    """a chess game"""

    pgn = Attribute("Portable game notation")


class IChessBoard(Interface):
    """chessboard"""

    fen = Attribute("Forsyth–Edwards Notation")

    def divideInSquares(self, width, height):
        """divide the board in squares based on the given width and height"""
        pass

    def genSquares(self):
        """generate all my squares"""
        pass

    def updatePieces(self, fen):
        """update the piece positions according to the given FEN"""
        pass


class ISquare(Interface):
    """one of the 64 square fields of a chessboard"""

    board = Attribute("the chessboard this square belongs to")
    an = Attribute("algebraic notation")
    fieldColor = Attribute("color of the empty square")
    piece = Attribute("chess piece currently on the square - may be None")

    def getSquareImage(self, cbImage):
        """get the 1/64 subimage of this square for the given chessboard image"""
        pass


class IPiece(Interface):
    """a chess piece King,Queen,Bishop,Knight,Rook or Pawn"""

    color = Attribute("color of the piece")


class IChessBoardVision(Interface):
    title = Attribute("name/title of the chessboard observation")
    warp = Attribute("the trapzeoid coordinates for warping to a square image")
    args = Attribute("the command line arguments/settings")
    debug = Attribute("true for debugging")
    """ visual observer of a chessboard e.g. with a camera - a video or still image"""

    def open(self, device):
        """open the access to the chessboard images via the given device e.g. device number or filepath"""
        pass

    def readChessBoardImage(self):
        """read a chessboard Image and return it"""
        pass

    def close(self):
        """close the access to the chessboard images"""
        pass


class IWarp(Interface):
    """trapez to square warp point handling"""

    def rotate(self, angle):
        """rotate me with the given angle"""
        pass

    def updatePoints(self):
        """update the points"""

    def addPoint(self, px, py):
        """add the given point to the warp point list"""
        pass


class IChessBoardImageSet(Interface):
    """a set of Images"""

    frameIndex = Attribute("index of image in a sequence")
    timeStamp = Attribute("time")
    cbImage = Attribute("original chessboard image")
    cbGUI = Attribute("the chessboard image to be displayed in the GUI")
    cbWarped = Attribute("chessboard image warped to square size")
    cbIdeal = Attribute("ideal chessboard image constructed from parameters")
    cbPreMove = Attribute("chessboard image before move")
    cbDiff = Attribute("chessboard image difference to premove state")

    def warpAndRotate(self):
        """warp and rotate the original image"""

    def prepareGUI(self):
        """prepare the gui output e.g. for debugging"""
        pass


class IChessBoardImage(Interface):
    """a single image of a chessboard"""

    image = Attribute("the chessboard image")
    width = Attribute("width of the image")
    height = Attribute("height of the image")
    pixels = Attribute("number of pixels of image = widthxheight")
    title = Attribute("title of the image")

    def diffBoardImage(self, cbOther):
        """get the difference image between me an the other chessboard image"""
        pass


class IMoveDetector(Interface):
    """a detector for moves on a chessboard image"""

    name = Attribute("name of the detector")
    debug = Attribute("true for debugging")

    def setup(self, name, board, video, args):
        """setup the detector with the given board, video and arguments"""

    def onChessBoardImage(self, imageEvent):
        """event handler for image events"""
        pass
