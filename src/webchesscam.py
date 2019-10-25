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
from Video import Video
from Board import Board

thisscriptFolder=os.path.dirname(os.path.abspath(__file__))

# prepare the RESTful application
# prepare static webserver
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='', static_folder=thisscriptFolder+'/../web')
api = Api(app)
app.logger.addHandler(logging.StreamHandler(STDOUT))
app.logger.info("python src folder is %s" % (thisscriptFolder))
# check if we are running on a raspberry PI
app.logger.info("Running on %s" % (platform.system()))
# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
if platform.system() == 'Linux' and os.path.exists('/sys/firmware/devicetree/base/model'):
    app.logger.info("Running on Raspberry PI")

# return the index.html template content with the given message
def index(msg,cmd=None):
    return render_template('index.html',cmd=None, message=msg, timeStamp=video.timeStamp())

@app.route("/")
def root():
    return index("Ready")

def gen(video):
    while True:
        ret,encodedImage,quit=video.readJpgImage()
        # ensure we got a valid image
        if not ret:
            continue
        if quit:
            break
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
			bytearray(encodedImage) + b'\r\n')

@app.route('/video')
def video_feed():
    # capture from the given video device
    video.capture(args.input)
    # return the response generated along with the specific media
	# type (mime type)
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/chess/move/<move>", methods=['GET'])
def chessMove(move):
    board.performMove(move)
    msg="move %s -> fen= %s" % (move,board.fen())
    return index(msg,cmd=("fen",board.fen()))

# capture a single still image
@app.route("/chess/photo", methods=['GET'])
def photo():
    # todo select input device
    video.capture(args.input)
    video.still2File(thisscriptFolder+'/../web/webcamchess/chessboard.jpg')
    return index("still image taken from input %s" % (args.input))

# home
@app.route("/chess/home", methods=['GET'])
def home():
    return index("Home")

# default arguments for Chess Cam
class WebChessCamArgs:
    """This class parses command line arguments and generates a usage."""

    def __init__(self,argv):
        self.parser=argparse.ArgumentParser(description='WebChessCam')
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
    args=WebChessCamArgs(sys.argv[1:]).args
    video=Video()
    board=Board()
    app.run(port='%d' % (args.port), host=args.host)
