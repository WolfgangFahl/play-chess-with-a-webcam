#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# workaround for https://github.com/jarus/flask-testing/issues/143
import werkzeug
from flask import Flask, request

# Global imports
from pcwawc.args import Args
from pcwawc.environment import Environment
from pcwawc.webapp import WebApp

werkzeug.cached_property = werkzeug.utils.cached_property
import logging
import os.path
import platform
import sys

from flask_autoindex import AutoIndex
from flask_restful import Api

env = Environment()

# prepare the RESTful application
# prepare static webserver
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path="", static_folder=str(env.projectPath) + "/web")
files_index = AutoIndex(app, browse_root=env.games, add_url_rules=False)
api = Api(app)
# app.logger.addHandler(logging.StreamHandler(STDOUT))
app.logger.setLevel(logging.INFO)
if WebApp.debug:
    app.logger.setLevel(logging.DEBUG)

app.logger.info("python src folder is %s" % (env.scriptPath))
# check if we are running on a raspberry PI
app.logger.info("Running on %s" % (platform.system()))
# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
if platform.system() == "Linux" and os.path.exists(
    "/sys/firmware/devicetree/base/model"
):
    app.logger.info("Running on Raspberry PI")


@app.route("/")
def root():
    return webApp.home()


# https://stackoverflow.com/a/41527903/1497139
@app.route("/chess/games/")
@app.route("/chess/games/<path:path>")
def autoindex(path="."):
    return files_index.render_autoindex(path)


@app.route("/chess/recordvideo")
def video_record():
    return webApp.videoRecord(env.games + "/videos/")


@app.route("/video")
def video_feed():
    return webApp.videoFeed()


@app.route("/eventstream")
def eventstream():
    return webApp.eventFeed()


@app.route("/photo/<path:filename>", methods=["GET", "POST"])
def photoDownload(filename):
    return webApp.photoDownload(env.games + "/photos/", filename)


@app.route("/chess/debug", methods=["GET"])
def chessDebug():
    return webApp.chessDebug()


@app.route("/chess/findboard", methods=["GET"])
def chessFindBoard():
    return webApp.chessFindBoard()


@app.route("/chess/rotatevideo90", methods=["GET"])
def videoRotate90():
    return webApp.videoRotate90()


@app.route("/chess/pausevideo", methods=["GET"])
def video_pause():
    return webApp.videoPause()


@app.route("/chess/save", methods=["GET"])
def chessSave():
    return webApp.chessSave()


@app.route("/chess/takeback", methods=["GET"])
def chessTakeback():
    return webApp.chessTakeback()


@app.route("/chess/forward", methods=["GET"])
def chessForward():
    return webApp.chessForward()


@app.route("/chess/<gameid>/state", methods=["GET"])
def chessGameState(gameid):
    return webApp.chessGameState(gameid)


@app.route("/chess/settings", methods=["GET"])
def chessSettings():
    args = request.args.to_dict()
    return webApp.chessSettings(args)


@app.route("/chess/gamecolors", methods=["GET"])
def chessGameColors():
    return webApp.chessGameColors()


@app.route("/chess/update", methods=["GET"])
def chessUpdate():
    """set game status from the given pgn, fen or move"""
    updateGame = request.args.get("updateGame")
    updateFEN = request.args.get("updateFEN")
    updateMove = request.args.get("updateMove")
    pgn = request.args.get("pgn")
    fen = request.args.get("fen")
    move = request.args.get("move")
    if updateFEN is not None:
        return webApp.chessFEN(fen)
    elif updateGame is not None:
        return webApp.chessPgn(pgn)
    elif updateMove is not None:
        return webApp.chessMove(move)
    else:
        return webApp.index(
            "expected updateGame,updateFEN or updateMove but no such request found"
        )


@app.route("/chess/chesswebcamclick/<width>/<height>", methods=["GET"])
def chessWebCamClick(width, height):
    # click info is in an unnamed query parameter
    args = request.args.to_dict()
    click = next(iter(args)).split(",")
    x, y = click
    w = int(width)
    h = int(height)
    return webApp.chessWebCamClick(int(x), int(y), w, h)


@app.route("/chess/move/<move>", methods=["GET"])
def chessMove(move):
    return webApp.chessMove(move)


# capture a single still image
@app.route("/chess/photo", methods=["GET"])
def photo():
    return webApp.photo(env.games + "/photos/")


# home
@app.route("/chess/home", methods=["GET"])
def home():
    return webApp.home()


# default arguments for Web Chess Camera
class WebChessCamArgs(Args):
    """This class parses command line arguments and generates a usage."""

    def __init__(self, argv):
        super().__init__(description="WebChessCam")
        self.parser.add_argument(
            "--port", type=int, default="5003", help="port to run server at"
        )

        self.parser.add_argument(
            "--host", default="0.0.0.0", help="host to allow access for"
        )

        self.args = self.parse(argv)


if __name__ == "__main__":
    args = WebChessCamArgs(sys.argv[1:]).args
    webApp = WebApp(args, app.logger)
    app.run(port="%d" % (args.port), host=args.host, threaded=True)
