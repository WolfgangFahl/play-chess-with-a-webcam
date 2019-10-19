#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import argparse

# default arguments for Chess Cam
class Args:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='ChessCam Argument Parser')
        self.parser.add_argument('--nouci',
                            action='store_true',
                            help="Don't use the UCI interface.")
        self.parser.add_argument('--input',
                            type=int,
                            default=0,
                            help="Manually set the input device.")
        self.parser.add_argument('--debug',
                            action='store_true',
                            help="show debug output")
        self.parser.add_argument('--cornermarker',default=None,help="filepath for an image of the cornermarker being used")                             
        self.parser.add_argument('--fullScreen',
                            action='store_true',
                            help="Display output in fullScreen mode")
        self.args = self.parser.parse_args()
