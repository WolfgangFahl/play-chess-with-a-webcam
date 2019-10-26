#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
import chess
import chess.pgn
import io
from chess import Move
from Field import Field

class RejectedMove(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Board(object):
    """This class is used to hold the state of a chessboard with pieces positions and the current player's color which player needs to play. It uses the python-chess library by default"""
    debug=True

    C = {'w': 0, 'b': 1}
    # initialize the board with a default dominator next cell to the right
    def __init__(self, dominatorOffset=(0,-1)):
        self.board = chess.Board()
        self.toPlay = Board.C['w']
        self.dominator = dominatorOffset
        self.fieldsByAn={}

        self.fields = [[0 for x in range(Field.rows)] for y in range(Field.cols)]
        for row in range(Field.rows):
            for col in range(Field.cols):
                field=Field(row,col)
                self.fieldsByAn[field.an]=field
                self.fields[row][col]=field

    def GetCellName(self,col, row):
        """Returns the cell name string given 0-based column and row"""
        field=self.fields[row][col]
        return  field.an.upper()

    # perform the given move
    def performMove(self, move):
        fromCell=move[0].lower()
        toCell=move[1].lower()
        if Board.debug:
            print ("move %s-%s" % (fromCell,toCell))
            print ("%s" % (self.unicode()))
        move=Move.from_uci(fromCell+toCell)
        san=self.board.san(move)
        self.board.push(move)
        return san

    # get my pgn description
    def pgn(self):
        game=chess.pgn.Game.from_board(self.board)
        return game

    # set my board and game from the given pgn
    def setPgn(self,pgn):
        pgnIo=io.StringIO(pgn)
        game=chess.pgn.read_game(pgnIo)
        self.board=game.board()
        for move in game.mainline_moves():
          self.board.push(move)

    #get my fen description
    def fen(self):
        fen=self.board.board_fen()
        return fen

    # get my unicode representation
    def unicode(self):
        unicode=self.board.unicode()
        return unicode
