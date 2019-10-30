#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
from flask import Flask, request
from flask_autoindex import AutoIndex
from flask_restful import Api
import ast
import logging
import sys
import platform
import os.path
import argparse
from WebApp import WebApp

thisscriptFolder = os.path.dirname(os.path.abspath(__file__))

# prepare the RESTful application
# prepare static webserver
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='',
            static_folder=thisscriptFolder + '/../web')
files_index=AutoIndex(app, browse_root=thisscriptFolder+'/../games',add_url_rules=False)
api = Api(app)
# app.logger.addHandler(logging.StreamHandler(STDOUT))
app.logger.setLevel(logging.INFO)
if WebApp.debug:
    app.logger.setLevel(logging.DEBUG)

app.logger.info("python src folder is %s" % (thisscriptFolder))
# check if we are running on a raspberry PI
app.logger.info("Running on %s" % (platform.system()))
# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
if platform.system() == 'Linux' and os.path.exists('/sys/firmware/devicetree/base/model'):
    app.logger.info("Running on Raspberry PI")


@app.route("/")
def root():
    return webApp.home()

# https://stackoverflow.com/a/41527903/1497139
@app.route('/games')
@app.route('/games/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path)

@app.route('/video')
def video_feed():
    return webApp.videoFeed()


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return webApp.download(thisscriptFolder + '/../web/webcamchess/', filename)


@app.route("/chess/debug", methods=['GET'])
def chessDebug():
    return webApp.chessDebug()


@app.route("/chess/rotatevideo90", methods=['GET'])
def videoRotate90():
    return webApp.videoRotate90()


@app.route("/chess/pausevideo", methods=['GET'])
def video_pause():
    return webApp.videoPause()


@app.route("/chess/save", methods=['GET'])
def chessSave():
    return webApp.chessSave()

@app.route("/chess/takeback", methods=['GET'])
def chessTakeback():
    return webApp.chessTakeback()


@app.route("/chess/forward", methods=['GET'])
def chessForward():
    return webApp.chessForward()


@app.route("/chess/pgn", methods=['GET'])
def chessPgn():
    """ set game status from the given pgn"""
    updateGame = request.args.get('updateGame')
    updateFEN = request.args.get('updateFEN')
    pgn = request.args.get('pgn')
    fen = request.args.get('fen')
    if updateFEN is not None:
        return webApp.chessFEN(fen)
    elif updateGame is not None:
        return webApp.chessPgn(pgn)
    else:
        return webApp.index("expected updateGame or updateFEN but no such request found")


@app.route("/chess/chesswebcamclick/<width>/<height>", methods=['GET'])
def chessWebCamClick(width, height):
    # click info is in an unnamed query parameter
    args = request.args.to_dict()
    click = next(iter(args)).split(',')
    x, y = click
    w = int(width)
    h = int(height)
    return webApp.chessWebCamClick(int(x), int(y), w, h)


@app.route("/chess/move/<move>", methods=['GET'])
def chessMove(move):
    return webApp.chessMove(move)


# capture a single still image
@app.route("/chess/photo", methods=['GET'])
def photo():
    return webApp.photo(thisscriptFolder + '/../web/webcamchess/')


# home
@app.route("/chess/home", methods=['GET'])
def home():
    return webApp.home()

# default arguments for Web Chess Camera


class WebChessCamArgs:
    """This class parses command line arguments and generates a usage."""

    def __init__(self, argv):
        self.parser = argparse.ArgumentParser(description='WebChessCam')
        self.parser.add_argument('--port',
                                 type=int,
                                 default="5003",
                                 help="port to run server at")

        self.parser.add_argument('--input',
                                 default="0",
                                 help="Manually set the input device.")

        self.parser.add_argument('--host',
                                 default="0.0.0.0",
                                 help="host to allow access for")
        
        self.parser.add_argument('--game',
                                 default=None,
                                 help="game to initialize with")

        self.parser.add_argument('--debug',
                                 action='store_true',
                                 help="show debug output")

        self.parser.add_argument('--rotation',
                                 type=int,
                                 default=0,
                                 help="rotation of chessboard")

        self.parser.add_argument('--warp',
                                 default="[]",
                                 help="warp points")

        self.args = self.parser.parse_args(argv)
        self.args.warpPointList = ast.literal_eval(self.args.warp)


if __name__ == '__main__':
    args = WebChessCamArgs(sys.argv[1:]).args
    webApp = WebApp(args, app.logger)
    app.run(port='%d' % (args.port), host=args.host)
