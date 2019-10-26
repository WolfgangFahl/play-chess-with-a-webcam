#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video, VideoStream
from Board import Board
from flask import Flask, request, render_template, send_from_directory, abort, Response
import numpy as np

class WebApp:
    """ actual Web Application - Flask calls are routed here """
    # construct me with no parameters
    debug=False

    def __init__(self,args,warpPointBGRColor=(0, 255, 0)):
       self.args=args
       self.warpPointColor= warpPointBGRColor
       self.video = Video()
       self.videoStream = None
       self.board = Board()
       self.warpPointList = []
       self.warpPoints=None

    # return the index.html template content with the given message
    def index(self,msg):
         return render_template('index.html', message=msg, timeStamp=self.video.timeStamp())

    def home(self):
        return self.index("Home")

    def chessDebug(self):
        WebApp.debug=not WebApp.debug
        msg = "debug " + ( 'on' if WebApp.debug else 'off' )
        return self.index(msg)

    def chessTakeback(self):
        msg="take back"
        return self.index(msg)

    def chessForward(self):
        msg="forward"
        return self.index(msg)

    def chessPgn(self,pgn,fen):
        self.board.setPgn(pgn)
        msg=fen
        return self.index(msg)

    def addWarpPoint(self,px,py):
        # make sure we have a maximum of 4 warpPoints
        # if warppoints are complete when adding reset them
        # px,py is irrelevant for reset
        if len(self.warpPointList)>=4:
          self.warpPointList=[]
          self.warpPoints=None
        else:
           self.warpPointList.append([px,py])
           self.warpPoints=np.array(self.warpPointList)

    def chessWebCamClick(self,x,y,w,h):
        px=x*self.video.width//w
        py=y*self.video.height//h
        self.addWarpPoint(px,py)
        msg="clicked warppoint %d pixel %d,%d mouseclick %d,%d in image %d x %d" % (len(self.warpPointList),px,py,x,y,w,h)
        return self.index(msg)

    def photo(self,path):
        # todo select input device
        self.video.capture(self.args.input)
        filename='chessboard_%s.jpg' % (self.video.fileTimeStamp())
        self.video.still2File(path+filename)
        # @TODO allow download of the given file from path
        return self.index("still image %s taken from input %s" % (filename,self.args.input))

    def videoPause(self):
        ispaused=not self.video.paused()
        self.video.pause(ispaused)
        msg = "video " + ( 'paused' if ispaused else 'running' )
        return self.index(msg)

    def videoFeed(self):
        if self.video.frames==0:
            # capture from the given video device
            self.video.capture(self.args.input)
        # return the response generated along with the specific media
        # type (mime type)
        return Response(self.genVideo(self.video),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    # streamed video generator
    # @TODO fix this non working code
    def genVideoStreamed(self,video):
        if self.videoStream is None:
           self.videoStream=VideoStream(self.video,show=True,postProcess=self.video.addTimeStamp)
           self.videoStream.start()
        while True:
            frame=self.videoStream.read()
            if frame is not None:
                flag,encodedImage=self.video.imencode(frame)
                # ensure we got a valid image
                if not flag:
                    continue
                # yield the output frame in the byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                      bytearray(encodedImage) + b'\r\n')

    def warp(self,image):
        if self.warpPoints is None:
            warped=image
        else:
            if len(self.warpPoints) < 4:
                self.video.drawTrapezoid(image,self.warpPoints,self.warpPointColor)
                warped=image
            else:
              warped=self.video.warp(image,self.warpPoints)
        if WebApp.debug:
           self.video.addTimeStamp(warped)
        return warped

    # video generator
    def genVideo(self,video):
       while True:
          # postProcess=video.addTimeStamp
          postProcess=self.warp
          ret,encodedImage,quit=video.readJpgImage(show=False,postProcess=postProcess)
          # ensure we got a valid image
          if not ret:
             continue
          if quit:
             break
          # yield the output frame in the byte format
          yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                           bytearray(encodedImage) + b'\r\n')
