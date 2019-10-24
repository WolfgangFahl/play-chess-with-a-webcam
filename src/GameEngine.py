#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
from Args import Args
from math import sin, cos, sqrt, pi, atan2
import sys
import numpy as np
from collections import defaultdict

# Local imports
from Board import Board, RejectedMove
from uci import Uci, ArenaQuit
from ChessCam import ChessCam, UserExit

class GameEngine(object):
    """This class is used to change the game state using StateClass.
    It also communicates moves with the chess ai facade and an observer to detect
    if a move have been played by an ai."""

    def __init__(self, argv):
        self.uci = Uci()
        self.cam = ChessCam()
        self.cam.prepare(argv)
        self.board = Board(self.cam.getDominatorOffset())
        self.useUCI = not self.cam.args.nouci

    def play(self):
        """This method plays the main loop of the ChessCam project until ArenaQuit or UserExit is received."""
        try:
            self.mainLoop()
        except ArenaQuit:
            pass
        except UserExit:
            pass

    def mainLoop(self):
        #Synchronize with Arena by knowing if opponent plays first.
        move = ""
        camToPlay = True
        if self.useUCI:
            move = self.uci.getResponse()
            camToPlay = (len(move) == 0)
        if move == "STARTPOS":
            camToPlay = True

        while True:
            if camToPlay:
                #Get a move from the camera and validate that move
                with open('output.txt', 'a') as f:
                    f.write("camToPlay: Waiting for out move...\n")
                moveFromCamera = self.cam.getNextMove()
                try:
                    move = self.board.performMove(moveFromCamera)
                except RejectedMove as e:
                    # Handle Undo
                    sys.stderr.write(str(e))
                    sys.stderr.write(str(moveFromCamera))
                    with open('output.txt', 'a') as f:
                        f.write("camToPlay: Awaiting Undo...\n")
                    self.cam.getNextMove()
                    sys.stderr.write("Undo OK")
                    continue

                #Inform arena of that move
                with open('output.txt', 'a') as f:
                    f.write("camToPlay: sendMove: {0}.\n".format(move))
                self.uci.sendMove(move)
                move = ""
                # Keep to True when not on uci mode
                if self.useUCI:
                    camToPlay = False

            elif move != "": #a move needs to be played by the cam to synchronize with Arena
                with open('output.txt', 'a') as f:
                    f.write("remotePlay: Do the showed move...\n")
                moveFromCamera = self.cam.getNextMove()
                try:
                    self.board.performMove(moveFromCamera) # We accept the move by default, the user is gentle with us!
                except RejectedMove as e:
                    sys.stderr.write(str(e))
                    continue
                # move = self.board.getLastMoveUCI() # ?
                move = ""
                camToPlay = True

            else: #It's the opponent's turn
                #Receive a counter move
                move = self.uci.getResponse()


if __name__ == "__main__":
    gameEngine = GameEngine(sys.argv[1:])
    gameEngine.play()
