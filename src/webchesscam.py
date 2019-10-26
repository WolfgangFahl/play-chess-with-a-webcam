#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
from flask import Flask, request, render_template, send_from_directory, abort, Response
from flask_restful import Resource, Api
import json
import logging
import sys
import time
import yaml
import platform
import os.path
from subprocess import STDOUT
import argparse
from WebApp import WebApp

thisscriptFolder = os.path.dirname(os.path.abspath(__file__))

# prepare the RESTful application
# prepare static webserver
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='',
            static_folder=thisscriptFolder + '/../web')
api = Api(app)
#app.logger.addHandler(logging.StreamHandler(STDOUT))
app.logger.setLevel(logging.INFO)
app.logger.info("python src folder is %s" % (thisscriptFolder))
# check if we are running on a raspberry PI
app.logger.info("Running on %s" % (platform.system()))
# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
if platform.system() == 'Linux' and os.path.exists('/sys/firmware/devicetree/base/model'):
    app.logger.info("Running on Raspberry PI")

@app.route("/")
def root():
    return webApp.home()

@app.route('/video')
def video_feed():
    return webApp.videoFeed()

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return webApp.download(thisscriptFolder + '/../web/webcamchess/',filename)

@app.route("/chess/debug", methods=['GET'])
def chessDebug():
    return webApp.chessDebug()

@app.route("/chess/rotatevideo90", methods=['GET'])
def videoRotate90():
    return webApp.videoRotate90()

@app.route("/chess/pausevideo", methods=['GET'])
def video_pause():
    return webApp.videoPause()

@app.route("/chess/takeback", methods=['GET'])
def chessTakeback():
    return webApp.chessTakeback()

@app.route("/chess/forward", methods=['GET'])
def chessForward():
    return webApp.chessForward()

@app.route("/chess/pgn", methods=['GET'])
def chessPgn():
    """ set game status from the given pgn"""
    pgn = request.args.get('pgn')
    fen = request.args.get('fen')
    return webApp.chessPgn(pgn,fen)

@app.route("/chess/chesswebcamclick/<width>/<height>", methods=['GET'])
def chessWebCamClick(width,height):
    # click info is in an unnamed query parameter
    args = request.args.to_dict()
    click=next(iter(args)).split(',')
    x,y=click
    w=int(width)
    h=int(height)
    return webApp.chessWebCamClick(int(x),int(y),w,h)

@app.route("/chess/move/<move>", methods=['GET'])
def chessMove(move):
    board.performMove(move)
    msg = "move %s -> fen= %s" % (move, board.fen())
    return index(msg, cmd="fen", value=board.fen())

# capture a single still image
@app.route("/chess/photo", methods=['GET'])
def photo():
    return webApp.photo(thisscriptFolder + '/../web/webcamchess/')

# home
@app.route("/chess/home", methods=['GET'])
def home():
    return webApp.home()

# default arguments for Chess Cam


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
        self.parser.add_argument('--debug',
                                 action='store_true',
                                 help="show debug output")
        self.args = self.parser.parse_args(argv)


if __name__ == '__main__':
    args = WebChessCamArgs(sys.argv[1:]).args
    webApp=WebApp(args)
    app.run(port='%d' % (args.port), host=args.host)
