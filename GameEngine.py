#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
from math import sin, cos, sqrt, pi, atan2
import sys
import numpy as np
from collections import defaultdict
import argparse

# Local imports
from state import State, RejectedMove
from uci import Uci, ArenaQuit
from ChessCam import ChessCam, UserExit

class GameEngine(object):
    """This class is used to change the game state using StateClass. 
    It also communicates moves with the chess ai facade and an observer to detect 
    if a move have been played by an ai."""
    
    def __init__(self, uci=True):
        self.uci = Uci()
        self.cam = ChessCam()
        self.state = State(self.cam.getDominatorOffset())
        self.useUCI = uci
    
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
                    move = self.state.moveCam(moveFromCamera)
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
                    self.state.moveCam(moveFromCamera) # We accept the move by default, the user is gentle with us!
                except RejectedMove as e:
                    sys.stderr.write(str(e))
                    continue
                # move = self.state.getLastMoveUCI() # ?
                move = ""
                camToPlay = True
            
            else: #It's the opponent's turn
                #Receive a counter move
                move = self.uci.getResponse()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ChessCam Argument Parser')
    parser.add_argument('--nouci',
                        action='store_true',
                        help="Don't use the UCI interface.")
    parser.add_argument('--input',
                        type=int,
                        default=0,
                        help="Manually set the input device.")
    args = parser.parse_args()

    thisInstance = GameEngine(uci=not args.nouci)
    thisInstance.play()