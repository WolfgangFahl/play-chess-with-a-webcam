#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
import sys
from collections import defaultdict
from chessUtils import GetColumnFromName, GetRowFromName, GetCellName, GetDominator, GetDominated, SplitDomination, isInList
from chessUtils import isPossibleMoveWhitePawn, isPossibleMoveBlackPawn, isPossibleMoveRook, isPossibleMoveBishop, isPossibleMoveQueen, isPossibleMoveKing, isPossibleMoveKnight

C = {'w':0, 'b':1}
P = {'r':0, 'n':1, 'b':2, 'q':3, 'k':4, 'p':5}
Pi = {0:'r',
     1:'n',
     2:'b',
     3:'q',
     4:'k',
     5:'p',
     'bp':'bp',}
RESULT = {'SUCCESS':True, 'FAIL':False}
ISVALID = {'bp':isPossibleMoveBlackPawn,
           'p':isPossibleMoveWhitePawn,
           'r':isPossibleMoveRook,
           'n':isPossibleMoveKnight,
           'b':isPossibleMoveBishop,
           'q':isPossibleMoveQueen,
           'k':isPossibleMoveKing,
           }

COLOR = 0
PIECE = 1

class RejectedMove(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class State(object):
    """This class is used to remember the pieces positions and the current player's color which player needs to play)."""
    
    def __init__(self, dominatorOffset):
        self.board = self._initBoard()
        self.toPlay = C['w']
        self.dominator = dominatorOffset
        
        
    def moveCam(self, move):
        """This method call the public method to update internals of State class
        move is a list of cells with detected motion
        return the move or raise RejectedMove
        Warning. There are two ambiguous move lists that cause this class to make an assumption.
            In the same line, all neighbors, all in move : Player-Space-Space       : Assume the player goes to last space
            In the same line, all neighbors, all in move : Player-Space-Opponent    : Assume the player eats the opponent
        The ambiguity comes from the fact that cells can be "dominated" due to angular camera"""
        stepOut, stepIn = self._partMoves(move)
        move = ""
        if len(stepOut) == 2 and len(stepIn) == 1:
            move = self._eat(stepOut,stepIn)
        
        elif len(stepOut) == 2 and len(stepIn) == 2:
            move = self._castle(stepOut,stepIn)
        
        else:
            move = self._move(stepOut,stepIn)
        
        self._switchTurn()
        return move
    
    
    def _move(self, fromCell, toCell):
        """Method to be called if there is a simple move to be done. 
            In case of a mistaken move that should be an eatin action, the method will succeed only if the ending position is not already occupied by the moving player.
            fromCell must be of lenght == 1
            toCell must be of lenght == 1
            parameters must contains string(2 char) adresses
            returns False if movement Failed, true otherwise"""
        if len(fromCell) != 1 or len(toCell) != 1 or self._emptyCell(fromCell[0]) or (self.board[fromCell[0]][COLOR] != self.toPlay) or self._sameColor(fromCell[0], toCell[0]):
            raise RejectedMove("During move: Not a regular move, or fromCell is empty, or moving with opponent's piece, or eating it's own piece")
            
        
        self._validateMove(fromCell[0],toCell[0])
        
        self.board[toCell[0]] = self.board[fromCell[0]]
        self.board[fromCell[0]] = None
        
        lastMove = fromCell[0] + toCell[0]
        if self._tryToPromote(toCell[0]) == RESULT['SUCCESS']: #Promote the pawn to a queen if it gets to the last row
            lastMove = lastMove + "q"
        
        return lastMove
        
        
    def _eat(self, fromCell, toCell):
        """Regular eating method. Should be called if there are 2 detected cells with a removed piece
        fromCell must be of lenght == 2
        toCell must be of lenght == 1
        a player cannot eat himself
        parameters must contains string(2 char) adresses
        the method is tolerant to "En Passant".
        returns False if movement Failed, true otherwise"""
        if len(fromCell) != 2 or len(toCell) != 1 or self._sameColor(fromCell[0], fromCell[1]):
            raise RejectedMove("During eat: fromCell or toCell size not fit, or eating it's own piece")
        
        i = 0 #Get the id of the eating piece
        if self.board[fromCell[i]][COLOR] != self.toPlay:
            i += 1
        
        self._validateMove(fromCell[i],toCell[0])
        
        self.board[fromCell[(i+1)%2]] = None #"En passant": The eaten piece is not where the eating piece will go
        
        self.board[toCell[0]] = self.board[fromCell[i]]
        self.board[fromCell[i]] = None
        
        lastMove = fromCell[i] + toCell[0]
        if self._tryToPromote(toCell[0]) == RESULT['SUCCESS']: #Promote the pawn to a queen if it gets to the last row
            lastMove = lastMove + "q"
        
        return lastMove
        
    
    def _castle(self, fromCell, toCell):
        """Castling method. CAUTION: The method only validates if king and rook is in position and that ending cells are empty. 
        The method is not robust to the rules of the castle move (k and r have not been moved, k in not checked and will not be in any cell where it will end or go through).
        fromCells must be the king and rook of same color at starting position
        toCells must be the good ending positions and need to be empty
        parameters must contains string(2 char) adresses
        returns False if movement Failed, true otherwise"""

        if len(fromCell) != 2 or len(toCell) != 2:
            raise RejectedMove("During Castle: fromCell or toCell size not fit")
            
        if not self._emptyCell(toCell[0]) or not self._emptyCell(toCell[1]) or not self._sameColor(fromCell[0], fromCell[1]) or (self.board[fromCell[0]][COLOR] != self.toPlay):
            raise RejectedMove("During Castle: destination cells not available, or not trying to casle with own team")
            
        if (not (self.board[fromCell[0]][PIECE] == P['r'] or self.board[fromCell[0]][PIECE] == P['k']) or 
            not (self.board[fromCell[1]][PIECE] == P['k'] or self.board[fromCell[1]][PIECE] == P['r'])) : 
            raise RejectedMove("During Castle: trying to castle without king or without rook")
        
        #Get the adress of the king
        kingId = 0
        if self.board[fromCell[kingId]][PIECE] != P['k']:
            kingId += 1
        king = fromCell[kingId]
        rook = fromCell[(kingId +1)%2]
            
        #get the toCells identified by left right
        left = toCell[0]
        right = toCell[1]
        if(GetColumnFromName(toCell[0]) - GetColumnFromName(toCell[1]) > 0):
            left = toCell[1]
            right = toCell[0]        
        
        #fromCell and toCell are in good starting positions
        goodPositions = False
        arrivalKing = left
        arrivalRook = right
        if self.toPlay == C['w'] and king == "E1":
            if (rook == "A1" and left == "C1" and right == "D1"):
                goodPositions = True
                
            elif (rook == "H1" and left == "F1" and right == "G1"):
                goodPositions = True
                arrivalKing = right
                arrivalRook = left
                
        elif self.toPlay == C['b'] and king == "E8":
            if (rook == "A8" and left == "C8" and right == "D8"):
                goodPositions = True
                
            elif (rook == "H8" and left == "F8" and right == "G8"):
                goodPositions = True
                arrivalKing = right
                arrivalRook = left

        if not goodPositions:
            raise RejectedMove("Positions for castling are erroneous")
                
        #Make the move
        self.board[arrivalKing] = self.board[king]
        self.board[king] = None
        
        self.board[arrivalRook] = self.board[rook]
        self.board[rook] = None
        
        lastMove = king + arrivalKing
        return lastMove
    
    def _tryToPromote(self, c):
        """Promote the pawn to a queen if it gets to the last row.
            Returns Success if a pawn promoted, Fail otherwise
            TODO: For the moment, we just can't promote to knight. Here's the algorithm that should be used
                1 - If knight gives a checkmate - promote to knight
                2 - Queen by default unless gives a pat. then
                3 - Rook unless gives a pat. then
                4 - if endgame (not ?to many? pieces) try bishop unless gives a pat.
                5 - else or if beginning of a game, promote to knight"""
            
        if(self.board[c][COLOR] == C['w'] and self.board[c][PIECE] == P['p'] and GetRowFromName(c) == 8):
            self.board[c] = (C['w'],P['q'])
            return RESULT['SUCCESS']
            
        elif(self.board[c][COLOR] == C['b'] and self.board[c][PIECE] == P['p'] and GetRowFromName(c) == 1):
            self.board[c] = (C['b'],P['q'])
            return RESULT['SUCCESS']
            
        return RESULT['FAIL']
        
    def _switchTurn(self):
        self.toPlay = (self.toPlay + 1) % 2
        
    def _sameColor(self, c1, c2):
        return not(self.board[c1] is None or self.board[c2] is None) and self.board[c1][COLOR] == self.board[c2][COLOR]
        
    def _emptyCell(self, c):
        return self.board[c] is None
    
    def _validateMove(self, fromCell, toCell):
        """Redirects to chessUtils in order to confirm that the move is possible, according to the moving piece
           Raises RejectedMove if move is invalid for the moving piece"""
        piece = self.board[fromCell][PIECE]
        if self.board[fromCell][COLOR] == C['b'] and piece == P['p']:
            piece = 'bp' # Special case of the ISVALID dictionnary
        
        if not ISVALID[Pi[piece]](fromCell, toCell):
            raise RejectedMove("Move violation : The current piece cannot move that way!")
    
    def _initBoard(self):
        board = {}
        
        #Init every cells to None before setting the pieces
        for col in range(0,8):
            for row in range (0,8):
                board[GetCellName(col,row)] = None
        
        #White major row
        board[GetCellName(0,0)] = (C['w'],P['r']) 
        board[GetCellName(1,0)] = (C['w'],P['n']) 
        board[GetCellName(2,0)] = (C['w'],P['b'])
        board[GetCellName(3,0)] = (C['w'],P['q'])
        board[GetCellName(4,0)] = (C['w'],P['k'])
        board[GetCellName(5,0)] = (C['w'],P['b'])
        board[GetCellName(6,0)] = (C['w'],P['n'])
        board[GetCellName(7,0)] = (C['w'],P['r'])
        
        #White pawn row
        board[GetCellName(0,1)] = (C['w'],P['p'])
        board[GetCellName(1,1)] = (C['w'],P['p'])
        board[GetCellName(2,1)] = (C['w'],P['p'])
        board[GetCellName(3,1)] = (C['w'],P['p'])
        board[GetCellName(4,1)] = (C['w'],P['p'])
        board[GetCellName(5,1)] = (C['w'],P['p'])
        board[GetCellName(6,1)] = (C['w'],P['p'])
        board[GetCellName(7,1)] = (C['w'],P['p'])
        
        #Black pawn row
        board[GetCellName(0,6)] = (C['b'],P['p'])
        board[GetCellName(1,6)] = (C['b'],P['p'])
        board[GetCellName(2,6)] = (C['b'],P['p'])
        board[GetCellName(3,6)] = (C['b'],P['p'])
        board[GetCellName(4,6)] = (C['b'],P['p'])
        board[GetCellName(5,6)] = (C['b'],P['p'])
        board[GetCellName(6,6)] = (C['b'],P['p'])
        board[GetCellName(7,6)] = (C['b'],P['p'])
        
        #Black major row
        board[GetCellName(0,7)] = (C['b'],P['r'])
        board[GetCellName(1,7)] = (C['b'],P['n'])
        board[GetCellName(2,7)] = (C['b'],P['b'])
        board[GetCellName(3,7)] = (C['b'],P['q'])
        board[GetCellName(4,7)] = (C['b'],P['k'])
        board[GetCellName(5,7)] = (C['b'],P['b'])
        board[GetCellName(6,7)] = (C['b'],P['n'])
        board[GetCellName(7,7)] = (C['b'],P['r'])
        
        return board
        
    def _partMoves(self, move):
        """The ugliest method of all : It tries to split the detected moving cells into two lists for further move analytics by State class.
        Throws an error if format seems to be invalid.
        returns the tuple: stepOut, stepIn
        stepOut (pieces removed from cells in that list) 
        stepIn (pieces appeared on the cells in that list)
        WARNING : THERE ARE TWO AMBIGUOUS SITUATIONS AT THE END OF THIS FUNCTION"""
        stepOut = []
        stepIn = []
        
        #Maybe it's a castling move check that first
        if(isInList("E1",move) and isInList("H1",move) and not self._emptyCell("E1") and self.board["E1"][PIECE] == P['k'] and self._emptyCell("F1")):
            stepOut = ["E1","H1"]
            stepIn = ["F1","G1"]
            return stepOut, stepIn
        elif(isInList("E1",move) and isInList("A1",move) and not self._emptyCell("E1") and self.board["E1"][PIECE] == P['k'] and self._emptyCell("D1")):
            stepOut = ["E1","A1"]
            stepIn = ["C1","D1"]
            return stepOut, stepIn
        elif(isInList("E8",move) and isInList("H8",move) and not self._emptyCell("E8") and self.board["E8"][PIECE] == P['k'] and self._emptyCell("F8")):
            stepOut = ["E8","H8"]
            stepIn = ["F8","G8"]
            return stepOut, stepIn
        elif(isInList("E8",move) and isInList("A8",move) and not self._emptyCell("E8") and self.board["E8"][PIECE] == P['k'] and self._emptyCell("D8")):
            stepOut = ["E8","A8"]
            stepIn = ["C8","D8"]
            return stepOut, stepIn
        
        #From there there could only be less than 5 keys in move, else this is an error
        if len(move) > 5 or len(move) < 2:
            raise RejectedMove("To many movement: " + str(len(move)))
            
        #For most moves, only two cells will be detected
        if len(move) == 2:
            if self.board[move[0]] == None:
                stepIn.append(move[0])
                stepOut.append(move[1])
            else:
                if self.board[move[0]][COLOR] == self.toPlay:
                    stepIn.append(move[1])
                    stepOut.append(move[0])
                else:
                    stepIn.append(move[0])
                    stepOut.append(move[1])
                    
            return stepOut, stepIn
                
        #Len 3 or len 4 (or len 5 only for EnPassant)
        dominator, dominated = SplitDomination(move, self.dominator)
        empty = []
        player = []
        opponent = []
        for key in move:
            if self._emptyCell(key):
                empty.append(key)
            elif self.board[key][COLOR] == self.toPlay:
                player.append(key)
            elif self.board[key][COLOR] != self.toPlay:
                opponent.append(key)
        
        #Find the moving player's piece
        if len(player) == 0:
            raise RejectedMove("Player have not moved")
        elif len(player) == 1:
            stepOut.append(player[0])
        else: #more than 1 player's piece : One is more dominant than the others
            for key in player:
                if isInList(key, dominator):
                    stepOut.append(key)
                    break
        
        #Find a dominant empty space
        if len(empty) > 0:
            for key in empty:
                if isInList(key, dominator) and not isInList(key,dominated):
                    stepIn.append(key)
                    break
                    
        if len(stepIn) == 1: #It is the ending position, for sure
            #It still can be EnPassant
            if self.board[stepOut[0]][PIECE] == P['p']:
                pos = stepIn[0][0] + stepOut[0][1] #position where opponent pawn may be
                if isInList(pos,opponent) and self.board[pos][PIECE] == P['p'] :
                    stepOut.append(pos)
                    
            return stepOut, stepIn
        
        #Eating a dominant opponent's piece
        if len(opponent) > 0 :
            for key in opponent:
                if isInList(key, dominator) and not isInList(key, dominated) :
                    #it still can be EnPassant
                    stepOut.append(key)
                    if GetRowFromName(key) == GetRowFromName(stepOut[0]) and self.board[stepOut[0]][PIECE] == P['p']: 
                        #pawn is eating in same row, so it's an EnPassant move
                        if self.board[key][COLOR] == C['w'] :
                            stepIn.append(key[0] + "3")
                        else:
                            stepIn.append(key[0] + "6")
                    else:
                        stepIn.append(key)
                    return stepOut, stepIn
        
        #Short movement in a straight line... hope I have not forgotten other possible moves!
        nextCell0 = GetDominated(stepOut[0], self.dominator)
        if isInList(nextCell0, opponent): #1: eat the opponent on the played's dominated cell
            stepIn.append(nextCell0)
        elif isInList(nextCell0, empty): 
            nextCell1 = GetDominated(nextCell0, self.dominator) 
            if isInList(nextCell1, opponent): #2: player-space-opponent : AMBIGUOUS, we assume player dont eat opponent's piece and that it steps in empty space
                stepIn.append(nextCell0)
            elif isInList(nextCell1, empty): 
                nextCell2 = GetDominated(nextCell1, self.dominator)
                if isInList(nextCell2, opponent): #3: player-space-space-opponent : player do not eat opponent's piece. it steps on last empty square
                    stepIn.append(nextCell1)
                elif isInList(nextCell2, empty): #4 : player-space-space-space : player stand in the space of the middle
                    stepIn.append(nextCell1)
                else: #5 : player-space-space : AMBIGUOUS, we assume player moves on the space in between
                    stepIn.append(nextCell0)
        else:
            raise RejectedMove("Unknown move")
        
        return stepOut, stepIn
        
if __name__ == "__main__":
    dominatorOffset = (0,-1) # Dominator is on the next cell to the right
    state = State(dominatorOffset)
    #try: #Easy mode
    #    print state.moveCam(['D2', 'D4'])             #d4
    #    print state.moveCam(['G8','F6'])              #Nf6
    #    print state.moveCam(['C2','C4'])              #c4
    #    print state.moveCam(['E7','E6'])              #e6
    #    print state.moveCam(['C4','C5'])              #c5
    #    print state.moveCam(['F8','D6'])              #Bd6
    #    print state.moveCam(['D1','A4'])              #Qa4
    #    print state.moveCam(['B7','B5'])              #b5
    #    print state.moveCam(['B5','C5','B6'])   #cxb6, En Passant
    #    print state.moveCam(['H8','E8','G8','F8'])    #0-0
    #    print state.moveCam(['B6','C7'])              #bxc7, Hidden eat
    try: #Hard mode
        print state.moveCam(['D2','D3','D4','D5'])        #d4
        print state.moveCam(['G8','F7','F6'])              #Nf6
        print state.moveCam(['C2','C3','C4'])              #c4
        print state.moveCam(['E8','E7','E6'])              #e6
        print state.moveCam(['C4','C5'])              #c5 (putting C6 is an ambiguous move)
        print state.moveCam(['F8','D6', 'D7'])              #Bd6
        print state.moveCam(['D1', 'D2','A4','A5'])              #Qa4
        print state.moveCam(['B7','B5', 'B8','B6'])              #b5
        print state.moveCam(['B5','C5','B6', 'B7', 'C6'])   #cxb6, En Passant
        print state.moveCam(['H8','E8','G8','F8','H7','E7','G7','F7'])    #0-0
        print state.moveCam(['B6','C7','B7','C8'])              #bxc7, Hidden eat
    except RejectedMove as e:
        print e
        pass
    print "---Final positions---"
    it = iter(sorted(state.board.items()))
    for i in range(0,64):
        data = it.next() 
        str = data[0]
        
        if data[1] == None:
            str += ": Empty"
        elif data[1][0] == 1:
            str += ": Black "
        else:
            str += ": White "
        
        if data[1] != None:
            if data[1][1] == P['r']:
                str += "rook"        
            elif data[1][1] == P['n']:
                str += "knight"
            elif data[1][1] == P['b']:
                str += "bishop"
            elif data[1][1] == P['q']:
                str += "queen"
            elif data[1][1] == P['k']:
                str += "king"
            else:
                str += "pawn"
        
        print str
