#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pathlib import Path

class Environment:
    """ Runtime Environment """

    def __init__(self):
        """ get the directory in which the testMedia resides """
        self.scriptPath = Path(__file__).parent
        self.projectPath = self.scriptPath.parent
        self.testMediaPath = Path(self.projectPath, 'testMedia')
        self.testMedia = str(self.testMediaPath.absolute()) + "/"
        self.games = str(self.projectPath) + "/games"
