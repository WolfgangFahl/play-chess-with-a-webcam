#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import colorsys
# from colormath.color_objects import sRGBColor, LabColor
# from colormath.color_conversions import convert_color
# from colormath.color_diff import delta_e_cie2000
from RunningStats import ColorStats
import chess
from enum import IntEnum


class FieldState(IntEnum):
    WHITE_EMPTY = 0
    WHITE_WHITE = 1
    WHITE_BLACK = 2
    BLACK_EMPTY = 3
    BLACK_WHITE = 4
    BLACK_BLACK = 5


class Field:
    """ a single Field of a chess board as observed from a WebCam"""
    rows = 8
    cols = 8
    # bgr colors
    white = (255, 255, 255)
    lightGrey = (64, 64, 64)
    darkGrey = (192, 192, 192)
    green = (0, 255, 0)
    red = (0, 0, 255)
    black = (0, 0, 0)

    @staticmethod
    def hsv_to_rgb(h, s, v):
        return colorsys.hsv_to_rgb(h, s, v)

    @staticmethod
    def hsv255_to_rgb255(h, s, v):
        r, g, b = Field.hsv_to_rgb(h / 255, s / 255, v / 255)
        return (int(r * 255), int(g * 255), int(b * 255))

    # construct me
    def __init__(self, board, row, col):
        self.board = board
        # row and column indices from 0-7
        self.row = row
        self.col = col
        self.squareIndex = row * 8 + col;
        self.square = chess.SQUARES[self.squareIndex]
        # https://python-chess.readthedocs.io/en/latest/core.html - chess.WHITE=True, chess.BLACK=False
        # https://gamedev.stackexchange.com/a/44998/133453
        # A1 at 0,0 is black moving an odd number of steps horizontally and vertically will end up on a white
        self.fieldColor = (self.col + self.row) % 2 == 1
        # algebraic notation of field
        # A1 to H8
        self.an = chess.SQUARE_NAMES[self.squareIndex]
        # center pixel position of field
        self.pcx = None
        self.pcy = None
        self.distance = None
        self.step = None
        self.hsvStats = None
        self.rgbStats = None
        self.luminance = None
        self.rgbColorKey = None
        self.colorKey = None

    def getPiece(self):
        if self.board  is None:
            raise Exception("Board not set for %s" % (self.an))
        if self.board.chessboard  is None:
            raise Exception("board.chessboard not set for %s" % (self.an))
        piece = self.board.chessboard.piece_at(self.square)
        return piece

    def getFieldState(self):
        piece = self.getPiece()
        if piece is None:
            if self.fieldColor == chess.WHITE:
                return FieldState.WHITE_EMPTY
            else:
                return FieldState.BLACK_EMPTY
        elif piece.color == chess.WHITE:
            if self.fieldColor == chess.WHITE:
                return FieldState.WHITE_WHITE
            else:
                return FieldState.BLACK_WHITE
        else:
            if self.fieldColor == chess.WHITE:
                return FieldState.WHITE_BLACK
            else:
                return FieldState.BLACK_BLACK
        # this can't happen
        return None

    # analyze the color arround my center pixel to the given
    # distance
    def analyzeColor(self, image, hsv, distance=1, step=1):
        self.distance = distance
        self.step = step
        self.hsvStats = ColorStats()
        self.rgbStats = ColorStats()
        for dx in range(-distance * step, distance * step + 1, step):
            for dy in range(-distance * step, distance * step + 1, step):
                ph, ps, pv = hsv[self.pcy + dy, self.pcx + dx]
                b, g, r = image[self.pcy + dy, self.pcx + dx]
                # print ("(%3d,%3d)=(%3d,%3d,%3d)" % (self.pcx+dx,self.pcy+dy,ph,ps,pv))
                self.hsvStats.push(ph, ps, pv)
                self.rgbStats.push(r, g, b)
        self.luminance = self.hsvStats.c3Stats
        self.rgbColorKey = self.rgbStats.rgbColorKey()
        self.colorKey = self.hsvStats.colorKey()

    def getColor(self):
        h, s, v = self.hsvStats.mean()
        r, g, b = Field.hsv255_to_rgb255(h, s, v)
        bgr = (b, g, r)
        # print("(%3d,%3d)=(%3d,%3d,%3d) (%3d,%3d,%3d)" % (self.pcx,self.pcy,h,s,v,r,g,b))
        return bgr

    def drawDebug(self, video, image, detectedFieldState):
        pcx = self.pcx
        pcy = self.pcy
        distance = self.distance
        step = self.step
        fieldState = self.getFieldState()
        detectColor = Field.black #Field.green if fieldState == detectedFieldState else Field.red
        fieldColor = self.getColor()
        x1, y1, x2, y2 = pcx - distance * step, pcy - distance * step, pcx + distance * step, pcy + distance * step
        # outer thickness for displaying detect state: green ok red - there is an issue
        ot = 2
        # inner thickness for displaying the field color
        it = 3
        video.drawRectangle(image, (x1 - ot, y1 - ot), (x2 + ot, y2 + ot), thickness=ot, color=detectColor)
        video.drawRectangle(image, (x1   , y1), (x2   , y2), thickness=it, color=fieldColor)
        piece = self.getPiece()
        if piece is None:
            emptyFieldColor = Field.white if fieldState == FieldState.WHITE_EMPTY else Field.black
            video.drawRectangle(image, (x1 + it, y1 + it), (x2 - it, y2 - it), thickness=-1, color=emptyFieldColor)
        else:
            symbol=piece.symbol()#piece.unicode_symbol()
            video.drawCenteredText(image,symbol,pcx,pcy)
                
