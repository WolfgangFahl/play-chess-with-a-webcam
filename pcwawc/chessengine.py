"""
Created on 2019-12-16

@author: wf
"""

import concurrent.futures
import shutil

# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import chess.engine


class Engine:
    """Chess Engines support e.g. Universal Chess Interface see https://chessprogramming.wikispaces.com/UCI"""

    # shall we output debug information?
    debug = False

    # list of engines to search for
    engineConfigs = [
        {
            "name": "Crafty Computer Chess",
            "command": "crafty",
            "url": "http://www.craftychess.com/",
            "protocol": "?",
        },
        {
            "name": "GNU Chess",
            "command": "gnuchess",
            "url": "https://www.gnu.org/software/chess/",
            "options": "--uci",
            "protocol": "uci",
        },
        {
            "name": "Stockfish Chess",
            "command": "stockfish",
            "url": "https://stockfishchess.org/",
            "protocol": "uci",
        },
        {
            "name": "XBoard",
            "command": "xboard",
            "url": "https://www.gnu.org/software/xboard/manual/xboard.html",
            "protocol": "xboard",
        },
    ]

    def __init__(self, engineConfig, timeout=5):
        """
        construct me with the given engineConfiguration and timeout

        Args:
            engineConfig(dict): the engine configuration to use
            timeout(float): the number of seconds to wait of the given engine
        """
        self.engineCmd = engineConfig["command"]
        self.enginePath = engineConfig["path"]
        self.name = engineConfig["name"]
        self.url = engineConfig["url"]
        self.protocolName = engineConfig["protocol"]
        self.options = engineConfig["options"] if "options" in engineConfig else None
        if self.protocolName == "uci":
            self.protocol = chess.engine.UciProtocol
        elif self.protocolName == "xboard":
            self.protocol = chess.engine.XBoardProtocol
        else:
            self.protocol = None
        self.timeout = timeout
        # asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
        # https://python-chess.readthedocs.io/en/latest/engine.html
        self.error = None

    def open(self):
        """
        open this chess engine
        """
        self.engine = None
        self.error = None
        if self.protocol is None:
            self.error = Exception("unknown protocol for %s" % self.name)
        else:
            try:
                cmd = [self.engineCmd]
                if self.options:
                    cmd.append(self.options)
                self.engine = chess.engine.SimpleEngine.popen(
                    self.protocol, cmd, timeout=self.timeout, debug=Engine.debug
                )
            except Exception as te:
                self.error = te
                pass
        return self.engine

    def close(self):
        """
        close the given engine
        """
        if self.engine is not None:
            try:
                self.engine.quit()
            except concurrent.futures._base.TimeoutError:
                # so what?
                if self.debug:
                    print(
                        "timeout after %1.f secs for %s on close forcing close now ..."
                        % (self.timeout, self.name)
                    )
                self.engine.close()
                pass

    def __str__(self):
        text = "chess engine %s called via %s at %s" % (
            self.name,
            self.engineCmd,
            self.enginePath,
        )
        return text

    @staticmethod
    def findEngines():
        """
        check which engines from the Engine configurations are installed
        on this computer and return a dict of these

        Returns:
            dict: map of Engines by Command e.g. "gnuchess" or "stockfish"
        """
        engineDict = {}
        for engineConfig in Engine.engineConfigs:
            engineCmd = engineConfig["command"]
            enginePath = shutil.which(engineCmd)
            if enginePath is not None:
                if Engine.debug:
                    print("found %s engine at %s" % (engineCmd, enginePath))
                engineConfig["path"] = enginePath
                engineDict[engineCmd] = engineConfig
        return engineDict
