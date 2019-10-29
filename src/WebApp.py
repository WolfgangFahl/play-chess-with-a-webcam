#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video, VideoStream
from Board import Board
from BoardDetector import BoardDetector
from flask import Flask, request, render_template, send_from_directory, Response
import numpy as np
from YamlAbleMixin import YamlAbleMixin
from JsonAbleMixin import JsonAbleMixin


class Warp(YamlAbleMixin, JsonAbleMixin):
    """ holds the trapezoid points to be use for warping an image take from a peculiar angle """

    # construct me from the given setting
    def __init__(self, pointList=[], rotation=0, bgrColor=(0, 255, 0)):
       self.rotation = rotation
       self.bgrColor = bgrColor
       self.pointList = pointList
       self.updatePoints()

    def rotate(self, angle):
       self.rotation = self.rotation + angle
       if self.rotation >= 360:
         self.rotation = self.rotation % 360

    def updatePoints(self):
      pointLen = len(self.pointList)
      if pointLen == 0:
        self.points = None
      else:
        self.points = np.array(self.pointList)
      self.warping = pointLen == 4

    def addPoint(self, px, py):
        """ add a point with the given px,py coordinate
        to the warp points make sure we have a maximum of 4 warpPoints if warppoints are complete when adding reset them
        this allows to support click UIs that need an unwarped image before setting new warp points.
        px,py is irrelevant for reset """
        if len(self.pointList) >= 4:
          self.pointList = []
        else:
          self.pointList.append([px, py])
        self.updatePoints()


class WebApp:
    """ actual Play Chess with a WebCam Application - Flask calls are routed here """
    debug = False

    # construct me with the given settings
    def __init__(self, args, logger=None, warpPointBGRColor=(0, 255, 0)):
        """ construct me """
        self.args = args
        self.logger = logger
        self.setDebug(args.debug)
        self.video = Video()
        self.videoStream = None
        self.board = Board()
        self.log("Warp: %s" % (args.warpPointList))
        self.warp = Warp(args.warpPointList)
        self.warp.rotation = args.rotation

    def log(self, msg):
        if WebApp.debug and self.logger is not None:
            self.logger.info(msg)
               
    # return the index.html template content with the given message
    def index(self, msg):
        return render_template('index.html', message=msg, timeStamp=self.video.timeStamp())

    def home(self):
        self.video = Video()
        return self.index("Home")

    def download(self, path, filename):
        #  https://stackoverflow.com/a/24578372/1497139
        return send_from_directory(directory=path, filename=filename)

    def setDebug(self, debug):
        WebApp.debug = debug
        BoardDetector.debug = WebApp.debug

    # toggle the debug flag
    def chessDebug(self):
        self.setDebug(not WebApp.debug)
        msg = "debug " + ('on' if WebApp.debug else 'off')
        return self.index(msg)

    def chessTakeback(self):
        msg = "take back"
        return self.index(msg)

    def chessForward(self):
        msg = "forward"
        return self.index(msg)
    
    def chessMove(self, move):
        self.board.performMove(move)
        msg = "move %s -> fen= %s" % (move, self.board.fen())
        return self.index(msg, cmd="fen", value=self.board.fen())

    def chessFEN(self, fen):
        msg = fen
        try:
            self.board.setFEN(fen)
            msg = "game update from fen %s" % (fen)
        except ValueError as ve:
            msg = str(ve)
        return self.index(msg)

    def chessPgn(self, pgn):
        self.board.setPgn(pgn)
        msg = "game updated from pgn"
        return self.index(msg)

    def chessWebCamClick(self, x, y, w, h):
        px = x * self.video.width // w
        py = y * self.video.height // h
        self.warp.addPoint(px, py)
        msg = "clicked warppoint %d pixel %d,%d mouseclick %d,%d in image %d x %d" % (len(self.warp.pointList), px, py, x, y, w, h)
        return self.index(msg)

    def photo(self, path):
        # todo select input device
        self.video.capture(self.args.input)
        filename = 'chessboard_%s.jpg' % (self.video.fileTimeStamp())
        self.video.still2File(path + filename, postProcess=self.warpAndRotate, close=False)
        msg = "still image <a href='/download/%s'>%s</a> taken from input %s" % (filename, filename, self.args.input)
        return self.index(msg)

    def videoRotate90(self):
        self.warp.rotate(90)
        msg = "rotation: %d°" % (self.warp.rotation)
        return self.index(msg)

    def videoPause(self):
        ispaused = not self.video.paused()
        self.video.pause(ispaused)
        msg = "video " + ('paused' if ispaused else 'running')
        return self.index(msg)

    def videoFeed(self):
        if self.video.frames == 0:
            # capture from the given video device
            self.video.capture(self.args.input)
        # return the response generated along with the specific media
        # type (mime type)
        return Response(self.genVideo(self.video),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    # streamed video generator
    # @TODO fix this non working code
    def genVideoStreamed(self, video):
        if self.videoStream is None:
            self.videoStream = VideoStream(self.video, show=True, postProcess=self.video.addTimeStamp)
            self.videoStream.start()
        while True:
            frame = self.videoStream.read()
            if frame is not None:
                flag, encodedImage = self.video.imencode(frame)
                # ensure we got a valid image
                if not flag:
                    continue
                # yield the output frame in the byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                      bytearray(encodedImage) + b'\r\n')

    def warpAndRotate(self, image):
        """ warp and rotate the image as necessary - add timestamp if in debug mode """
        if self.warp.points is None:
            warped = image
        else:
            if len(self.warp.points) < 4:
                self.video.drawTrapezoid(image, self.warp.points, self.warp.bgrColor)
                warped = image
            else:
                warped = self.video.warp(image, self.warp.points)
        if self.warp.rotation > 0:
            warped = self.video.rotate(warped, self.warp.rotation)
        # analyze the board if warping is active
        if self.warp.warping:
            boardDetector = BoardDetector(self.board, self.video)
            # @TODO make configurable via settings
            distance = 5
            step = 3
            warped = boardDetector.analyze(warped, self.video.frames, distance, step)
        if WebApp.debug:
            self.video.addTimeStamp(warped)
        return warped

    # video generator
    def genVideo(self, video):
         while True:
             # postProcess=video.addTimeStamp
             postProcess = self.warpAndRotate
             ret, encodedImage, quit = video.readJpgImage(show=False, postProcess=postProcess)
             # ensure we got a valid image
             if not ret:
                 continue
             if quit:
                 break
             # yield the output frame in the byte format
             yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                           bytearray(encodedImage) + b'\r\n')
