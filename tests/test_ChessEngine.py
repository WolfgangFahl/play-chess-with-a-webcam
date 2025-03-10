"""
Created on 2019-12-26

@author: wf
"""

import asyncio
import os
import threading
import time
from datetime import datetime
from unittest import TestCase

import chess.pgn

from pcwawc.chessengine import Engine

debug = True


class ChessEngineTest(TestCase):

    def fix_path(self):
        """fixes PATH issues e.g. on MacOS macports environment - adopt to your needs as you see fit"""
        home = os.environ["HOME"]
        homebin = home + "/bin"
        # is a home/bin and/or /usr/games directory available?
        # priority is last in list as higher priority
        for path in ["/opt/local/bin", "/usr/games", homebin]:
            # if the path is available
            if os.path.isdir(path):
                if debug:
                    print("found %s - prepending it to PATH" % path)
                os.environ["PATH"] = "%s:%s" % (path, os.environ["PATH"])

    def findEngines(self):
        """
        find the available chess engines on this computer
        """
        self.fix_path()
        Engine.debug = debug
        engineConfigs = Engine.findEngines()
        return engineConfigs

    # http://julien.marcel.free.fr/macchess/Chess_on_Mac/Engines.html
    def test_engines(self):
        engineConfigs = self.findEngines()
        for key, engineConfig in engineConfigs.items():
            chessEngine = Engine(engineConfig)
            print(chessEngine)
            try:
                engine = chessEngine.open()
            except Exception as e:
                print("opening %s failed with " % (engine.name, str(e)))
            # pytest.fail(str(e))
            chessEngine.close()

    def test_play(self):
        """
        test playing
        """
        engineConfigs = self.findEngines()
        engineCmds = ["gnuchess", "stockfish"]
        for engineCmd in engineCmds:
            if engineCmd not in engineConfigs:
                print(f"{engineCmd} not found can not test playing")
                break
            chessEngine = Engine(engineConfigs[engineCmd])
            engine = chessEngine.open()
            if engine is None:
                raise Exception(
                    "Could not open %s engine: %s"
                    % (chessEngine.name, str(chessEngine.error))
                )
            board = chess.Board()
            game = chess.pgn.Game()
            game.headers["Event"] = "test_chessengine %s" % (chessEngine.name)
            game.headers["Site"] = (
                "http://wiki.bitplan.com/index.php/PlayChessWithAWebCam"
            )
            game.headers["White"] = "%s" % (chessEngine.name)
            game.headers["Black"] = "%s" % (chessEngine.name)
            game.headers["Date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            moveIndex = 0
            node = None
            while not board.is_game_over():
                result = engine.play(board, chess.engine.Limit(time=0.1))
                move = str(result.move)
                board.push(result.move)
                print(
                    "%d-%s: %s"
                    % (
                        moveIndex // 2 + 1,
                        "white" if moveIndex % 2 == 0 else "black",
                        move,
                    )
                )
                print(board.unicode())
                if moveIndex == 0:
                    node = game.add_variation(chess.Move.from_uci(move))
                else:
                    node = node.add_variation(chess.Move.from_uci(move))
                moveIndex += 1

            engine.quit()
            print(game)
            # try pasting resulting pgn to
            # https://lichess.org/paste

    @classmethod
    def tearDownClass(cls):
        time.sleep(5)
        print("trying to cancel all threads and tasks")
        for thread in threading.enumerate():
            print("%s" % (thread.name))
        loop = asyncio.get_event_loop()
        if loop is not None:
            for task in asyncio.all_tasks(loop):
                print("cancelling %s" % (str(task)))
                task.cancel()
