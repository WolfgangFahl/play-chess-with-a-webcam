#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

import io

# Global imports
import chess.pgn
from chess import Move
from zope.interface import implementer

from pcwawc.chessvision import IChessBoard
from pcwawc.field import Field
from pcwawc.game import WebCamGame


@implementer(IChessBoard)
class Board(object):
    """This class is used to hold the state of a chessboard with pieces positions and the current player's color which player needs to play. It uses the python-chess library by default"""

    debug = False
    EMPTY_FEN = "8/8/8/8/8/8/8/8 w - -"
    START_FEN = chess.STARTING_BOARD_FEN

    # initialize the board
    def __init__(self, args=None):
        self.chessboard = chess.Board()
        self.fieldsByAn = {}
        self.args = args
        self.debug = self.args is not None and self.args.debug
        self.game = WebCamGame.fromArgs(args)
        self.updateFen()
        self.game.update(self)

        self.fields = [[0 for x in range(Field.rows)] for y in range(Field.cols)]
        for row in range(Field.rows):
            for col in range(Field.cols):
                field = Field(self, row, col)
                self.fieldsByAn[field.an] = field
                self.fields[col][row] = field

    def fieldAt(self, row, col):
        return self.fields[col][row]

    def genSquares(self):
        for field in self.fieldsByAn.values():
            yield field

    def divideInSquares(self, width, height):
        # interpolate the centers of the 8x8 fields from a squared image
        fieldHeight = height / Field.rows
        fieldWidth = width / Field.cols
        for field in self.genSquares():
            field.setRect(width, height, fieldWidth, fieldHeight)

    def fieldStateCounts(self):
        # there are 6 different FieldStats
        counts = [0, 0, 0, 0, 0, 0]
        for field in self.fieldsByAn.values():
            fieldState = field.getFieldState()
            counts[fieldState] = counts[fieldState] + 1
        return counts

    def piecesOfColor(self, color):
        count = 0
        for field in self.fieldsByAn.values():
            piece = field.getPiece()
            if piece is not None and piece.color == color:
                count = count + 1
        return count

    # perform the given move
    def performMove(self, move):
        fromCell, toCell = move
        return self.ucimove(fromCell + toCell)

    def ucimove(self, ucimove):
        move = Move.from_uci(ucimove.lower())
        return self.move(move)

    def move(self, move):
        """perform the given move"""
        try:
            if self.debug:
                print("trying to perform move %s on" % (str(move)))
                print("%s" % (self.unicode()))
            san = self.chessboard.san(move)
        except Exception as e:
            if self.debug:
                print("failed with error: %s" % (str(e)))
            return None

        self.chessboard.push(move)
        self.game.move(self)
        self.updateFen()
        if self.args is not None and not self.args.nomoves:
            print("move %s" % (san))
            print("%s" % (self.unicode()))
        return san

    def takeback(self):
        if self.game.moveIndex > 0:
            self.game.moveIndex = self.game.moveIndex - 1
            self.chessboard.pop()
            self.updateFen()
            return True
        else:
            return False

    def lockGame(self):
        # @TODO implement locking of a saved game to make it immutable
        gameid = self.game.gameid
        self.game.locked = True
        return gameid

    # set my board and game from the given pgn
    def setPgn(self, pgn):
        self.game.pgn = pgn
        pgnIo = io.StringIO(pgn)
        game = chess.pgn.read_game(pgnIo)
        if game is None:
            # TODO log a warning
            return
        self.chessboard = game.board()
        for move in game.mainline_moves():
            self.chessboard.push(move)
        self.updateFen()

    def updatePieces(self, fen):
        self.chessboard = chess.Board(fen)
        self.updateFen()

    # get my fen description
    def updateFen(self):
        self.fen = self.chessboard.board_fen()
        self.game.fen = self.fen
        return self.fen

    # get my unicode representation
    def unicode(self):
        unicode = self.chessboard.unicode()
        return unicode

    def changeToMove(self, change):
        sq1, sq2 = change
        """ convert the given change in the physical board to a move """
        for move in self.chessboard.legal_moves:
            movestr = str(move)
            if sq1 + sq2 == movestr or sq2 + sq1 == movestr:
                return move
        return None
