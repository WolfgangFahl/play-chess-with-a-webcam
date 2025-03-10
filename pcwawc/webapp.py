#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import time
from datetime import datetime

from flask import Response, jsonify, render_template, send_from_directory

from pcwawc.detectorfactory import MoveDetectorFactory
from pcwawc.environment import Environment
from pcwawc.video import Video
from pcwawc.videoanalyze import VideoAnalyzer


class WebApp:
    """actual Play Chess with a WebCam Application - Flask calls are routed here"""

    debug = False

    # construct me with the given settings
    def __init__(self, args, logger=None):
        """construct me"""
        self.args = args
        self.videoStream = None
        self.videoAnalyzer = VideoAnalyzer(args, logger=logger)
        self.videoAnalyzer.setUpDetector()
        self.board = self.videoAnalyzer.vision.board
        self.setDebug(args.debug)
        self.env = Environment()

    def log(self, msg):
        self.videoAnalyzer.log(msg)

    # return the index.html template content with the given message
    def index(self, msg):
        self.log(msg)
        game = self.board.game
        game.warp = self.videoAnalyzer.vision.warp
        game.save()
        gameid = game.gameid
        return render_template(
            "index.html",
            detector=self.videoAnalyzer.moveDetector,
            detectors=MoveDetectorFactory.detectors,
            message=msg,
            timeStamp=self.videoAnalyzer.vision.video.timeStamp(),
            gameid=gameid,
        )

    def home(self):
        self.videoAnalyzer.vision.video = Video()
        return self.index("Home")

    def photoDownload(self, path, filename):
        #  https://stackoverflow.com/a/24578372/1497139
        return send_from_directory(directory=path, filename=filename)

    def setDebug(self, debug):
        WebApp.debug = debug
        self.videoAnalyzer.setDebug(debug)

    # toggle the debug flag
    def chessDebug(self):
        self.setDebug(not WebApp.debug)
        msg = "debug " + ("on" if WebApp.debug else "off")
        return self.index(msg)

    # automatically find the chess board
    def chessFindBoard(self):
        if self.videoAnalyzer.hasImage():
            try:
                corners = self.videoAnalyzer.findChessBoard()
                msg = "%dx%d found" % (corners.rows, corners.cols)
            except Exception as e:
                msg = str(e)
        else:
            msg = "can't find chess board - video is not active"
        return self.index(msg)

    def chessTakeback(self):
        try:
            msg = "take back"
            if not self.board.takeback():
                msg = "can not take back any more moves"
            if WebApp.debug:
                self.game.showDebug()
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def chessSave(self):
        gameid = self.board.lockGame()
        msg = "chess game <a href='/chess/games/%s'>%s</a> saved(locked)" % (
            gameid,
            gameid,
        )
        return self.index(msg)

    def chessGameColors(self):
        msg = "color update in progress"
        return self.index(msg)

    def chessForward(self):
        msg = "forward"
        return self.index(msg)

    def indexException(self, e):
        msg = "<span style='color:red'>%s</span>" % str(e)
        return self.index(msg)

    def chessMove(self, move):
        try:
            if "-" in move:
                move = move.replace("-", "")
            self.board.ucimove(move)
            msg = "move %s -> fen= %s" % (move, self.board.fen)
            if WebApp.debug:
                self.game.showDebug()
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def timeStamp(self):
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    def chessGameState(self, gameid):
        fen = self.board.fen
        pgn = self.board.game.pgn
        gameStateJson = jsonify(
            fen=fen,
            pgn=pgn,
            gameid=gameid,
            debug=WebApp.debug,
            timestamp=self.timeStamp(),
        )
        # if WebApp.debug:
        #    self.log(gameStateJson)
        return gameStateJson

    def chessSettings(self, args):
        msg = "settings"
        if "detector" in args:
            newDetectorName = args["detector"]
            newDetector = MoveDetectorFactory.create(
                newDetectorName, self.videoAnalyzer.vision
            )
            self.videoAnalyzer.changeDetector(newDetector)
            msg = "changing detector to %s" % (newDetectorName)
        return self.index(msg)

    def chessFEN(self, fen):
        msg = fen
        try:
            self.board.updatePieces(fen)
            msg = "game update from fen %s" % (fen)
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def chessPgn(self, pgn):
        try:
            self.board.setPgn(pgn)
            msg = "game updated from pgn"
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    # picture has been clicked
    def chessWebCamClick(self, x, y, w, h):
        video = self.videoAnalyzer.vision.video
        if not self.videoAnalyzer.hasImage():
            msg = "no video available"
        else:
            px = x * video.width // w
            py = y * video.height // h
            b, g, r = video.frame[py, px]
            colorInfo = "r:%x g:%x b:%x" % (r, g, b)
            warp = self.videoAnalyzer.vision.warp
            warp.addPoint(px, py)
            msg = (
                "clicked warppoint %d pixel %d,%d %s mouseclick %d,%d in image %d x %d"
                % (len(warp.pointList), px, py, colorInfo, x, y, w, h)
            )
            return self.index(msg)

    def photo(self, path):
        try:
            if self.videoAnalyzer.hasImageSet():
                # make sure the path exists
                Environment.checkDir(path)
                video = self.videoAnalyzer.vision.video
                filename = "chessboard_%s.jpg" % (video.fileTimeStamp())
                video.writeImage(
                    self.videoAnalyzer.cbImageSet.cbGUI.image, path + filename
                )
                msg = "still image <a href='/photo/%s'>%s</a> taken from input %s" % (
                    filename,
                    filename,
                    self.args.input,
                )
            else:
                msg = "no imageset for photo available"
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def videoRecord(self, path):
        if not self.videoAnalyzer.isRecording():
            video = self.videoAnalyzer.vision.video
            filename = self.videoAnalyzer.startVideoRecording(
                path, "chessgame_%s.avi" % (video.fileTimeStamp())
            )
            msg = "started recording %s" % (filename)
        else:
            filename = self.videoAnalyzer.stopVideoRecording()
            msg = "finished recording " + filename
        return self.index(msg)

    def videoRotate90(self):
        try:
            warp = self.videoAnalyzer.vision.warp
            warp.rotate(90)
            msg = "rotation: %d°" % (warp.rotation)
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def videoPause(self):
        ispaused = self.videoAnalyzer.videoPause()
        msg = "video " + ("paused" if ispaused else "running")
        return self.index(msg)

    def videoFeed(self):
        self.videoAnalyzer.open()
        # return the response generated along with the specific media
        # type (mime type)
        return Response(
            self.genVideo(self.videoAnalyzer),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    # https://html.spec.whatwg.org/multipage/server-sent-events.html
    # https://stackoverflow.com/a/51969441/1497139
    def getEvent(self):
        """this could be any function that blocks until data is ready"""
        time.sleep(1.0)
        s = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return s

    def eventFeed(self):
        return Response(self.genEventStream(), mimetype="text/event-stream")

    def genEventStream(self):
        while True:
            # wait for source data to be available, then push it
            yield "data: {}\n\n".format(self.getEvent())

    # streamed video generator
    # @TODO fix this non working code
    # def genVideoStreamed(self, video):
    #    if self.videoStream is None:
    #        self.videoStream = VideoStream(self.video, show=True, postProcess=self.video.addTimeStamp)
    #        self.videoStream.start()
    #    while True:
    #        frame = self.videoStream.read()
    #        if frame is not None:
    #            flag, encodedImage = self.video.imencode(frame)
    #            # ensure we got a valid image
    #            if not flag:
    #                continue
    #            # yield the output frame in the byte format
    #            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
    #                  bytearray(encodedImage) + b'\r\n')

    # video generator
    def genVideo(self, analyzer):
        if self.args.autowarp:
            analyzer.autoWarp()
        while True:
            cbImageSet = analyzer.nextImageSet()
            if cbImageSet is None:
                break
            guiImage = cbImageSet.cbGUI.image
            if guiImage is not None:
                (flag, encodedImage) = analyzer.vision.video.imencode(guiImage)
                if not flag:
                    self.log("encoding failed")
                else:
                    # yield the output frame in the byte format
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + bytearray(encodedImage)
                        + b"\r\n"
                    )
