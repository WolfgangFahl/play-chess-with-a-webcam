#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
import chess
from chess import Move

class RejectedMove(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Board(object):
    """This class is used to hold the state of a chessboard with pieces positions and the current player's color which player needs to play. It uses the python-chess library by default"""
    debug=True

    C = {'w': 0, 'b': 1}
    COLUMN_LETTER = {0: 'A', 1: 'B', 2: 'C',
        3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'}
    ROW_NUMBER = {0: str(1), 1: str(2), 2: str(3), 3: str(
        4), 4: str(5), 5: str(6), 6: str(7), 7: str(8)}

    # initialize the board with a default dominator next cell to the right
    def __init__(self, dominatorOffset=(0,-1)):
        self.board = chess.Board()
        self.toPlay = Board.C['w']
        self.dominator = dominatorOffset

    @staticmethod
    def GetCellName(column, row):
        """Returns the cell name string given 0-based column and row"""
        # @TODO deprecated use python-chess instead
        return ''.join([Board.COLUMN_LETTER[column], Board.ROW_NUMBER[row]])

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

    #get my fen description
    def fen(self):
        fen=self.board.board_fen()
        return fen

    # get my unicode representation
    def unicode(self):
        unicode=self.board.unicode()
        return unicode
