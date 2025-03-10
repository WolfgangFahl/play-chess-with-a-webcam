#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
"""
Created on 2019-12-08

@author: wf
"""
import argparse
import ast


class Args:
    """Command Line argument handling"""

    def __init__(self, description):
        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument(
            "--input", default="0", help="Manually set the input device."
        )
        self.parser.add_argument(
            "--autowarp",
            action="store_true",
            help="automatically find and warp chessboard",
        )

        self.parser.add_argument("--black", default=None, help="PGN Black header")

        self.parser.add_argument(
            "--debug", action="store_true", help="show debug output"
        )

        self.parser.add_argument(
            "--detector", default="simple8x8", help="move detector to be used"
        )

        self.parser.add_argument("--event", default=None, help="PGN Event header")

        self.parser.add_argument(
            "--fen", default=None, help="Forsyth–Edwards Notation to start with"
        )

        self.parser.add_argument("--game", default=None, help="game to initialize with")

        self.parser.add_argument(
            "--lichess", action="store_true", help="activate lichess integration"
        )

        self.parser.add_argument(
            "--nomoves", action="store_true", help="do not show each individual move"
        )

        self.parser.add_argument(
            "--nowarp",
            action="store_true",
            help="chessboard vision is already squared e.g. recorded that way",
        )

        self.parser.add_argument("--round", default=None, help="PGN Round header")

        self.parser.add_argument(
            "--rotation",
            type=int,
            default=0,
            help="rotation of chessboard 0,90,180 or 270",
        )

        self.parser.add_argument("--site", default=None, help="PGN Site header")

        self.parser.add_argument(
            "--startframe",
            type=int,
            default=0,
            help="video frame at which to start detection",
        )

        self.parser.add_argument(
            "--speedup",
            type=int,
            default=1,
            help="detection speedup - higher speedup means less precision",
        )

        self.parser.add_argument("--white", default=None, help="PGN White header")

        self.parser.add_argument("--warp", default="[]", help="warp points")

        self.parser.add_argument(
            "--distance",
            type=int,
            default=5,
            help="detection pixel distance - number of pixels analyzed i square of this",
        )

        self.parser.add_argument(
            "--step",
            type=int,
            default=3,
            help="detection pixel steps - distance*step is the grid size being analyzed",
        )

        pass

    def parse(self, argv):
        self.args = self.parser.parse_args(argv)
        self.args.warpPointList = ast.literal_eval(self.args.warp)
        return self.args
