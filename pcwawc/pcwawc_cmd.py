'''
Created on 2025-03-12

@author: wf
'''
import sys
from argparse import ArgumentParser

from ngwidgets.cmd import WebserverCmd
from pcwawc.webserver import WebServer

class PlayChessWithAWebCamCmd(WebserverCmd):
    """
    play chess with a Webcam command line handling
    """

    def __init__(self):
        """
        constructor
        """
        config = WebServer.get_config()
        WebserverCmd.__init__(self, config, WebServer)
        pass

    def getArgParser(self, description: str, version_msg) -> ArgumentParser:
        """
        override the default argparser call
        """
        parser = super().getArgParser(description, version_msg)
        return parser

def main(argv: list = None):
    """
    main call
    """
    cmd = PlayChessWithAWebCamCmd()
    exit_code = cmd.cmd_main(argv)
    return exit_code



if __name__ == "__main__":
    exit_code=main()
    sys.exit(exit_code)


