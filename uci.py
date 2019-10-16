#!/usr/bin/python
# -*- encoding: utf-8 -*-
from __future__ import print_function

# Global imports
import sys


class ArenaQuit(Exception):
    pass


class Uci(object):
    """This class interacts with stdin and stdout with Arena in the UCI
    convention in order to communicate chess moves"""
    STARTFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    def sendMove(self, move):
        """This method prints the move in a uci manner"""
        move = move.lower()
        with open('output.txt', 'a') as f:
            f.write("SENT:bestmove {0}\n".format(move))
        sys.stdout.write("bestmove {0}\n".format(move)) #+ " ponder " + "a8a6"
        sys.stdout.flush()
    
    def getResponse(self):
        """Enter a loop that waits until Arena respond with a 'position'
        [and\or] gives a 'go'.

        Returns a move of the following format: 
        A1A2, 
        E1G1 (for small white castling), 
        D1D7 (queen eats pawn), 
        B7B8q (for promotion)
        or an empty string if it's our turn to move, it's not our opponent's
        turn (might occur when a game begins)"""
        
        token = ""
        move = ""
        while (token != "quit" and token != "go"):
            tokens = sys.stdin.readline().lstrip().split()
            with open('output.txt', 'a') as f:
                f.write(" ".join(tokens) + '\n')
            for token in tokens:
                if token == "isready":
                    print("readyok")
                elif token == "position":
                    move = self._setPosition(tokens);
                elif token == "uci":
                    print("id name {0}\n"
                          "id author {1}\n"
                          "uciok".format("ChessCam",
                                         "Olivier Dugas and "
                                         "Yannick Hold-Geoffroy"))
                elif token == "go":
                    break
        
        if token == "quit":
            raise ArenaQuit("Quit command received.")
            
        return move
    
    def _setPosition(self, tokens):
        """Our version of chessCam won't be tolerant to undo, nor will it be to
        chess960."""
        
        move = tokens[-1].upper()
        if len(move) == 5: #Ensure that the promotion piece is lowercase
            move = move[:-1] + move[-1].lower()
        with open('output.txt', 'a') as f:
            f.write("Move received: {0}\n".format(move))
        return move
  

if __name__ == '__main__':
    # Test our UCI protocol
    ourUCI = Uci()
    while True:
        # Get Interface move
        try:
            move = ourUCI.getResponse()
        except ArenaQuit:
            sys.exit(0)
        # Writes the same move back
        ourUCI.sendMove(move)