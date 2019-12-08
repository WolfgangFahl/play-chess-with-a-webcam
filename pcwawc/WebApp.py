#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.Board import Board
from pcwawc.videoanalyze import VideoAnalyzer
from pcwawc.BoardDetector import BoardDetector
from pcwawc.Environment import Environment
from pcwawc.Video import Video
from pcwawc.game import WebCamGame, Warp
from flask import render_template, send_from_directory, Response, jsonify
from datetime import datetime

class WebApp:
    """ actual Play Chess with a WebCam Application - Flask calls are routed here """
    debug = False

    # construct me with the given settings
    def __init__(self, args, logger=None):
        """ construct me """
        self.args = args
        self.logger = logger
        self.videoAnalyzer=VideoAnalyzer(args)
        self.setDebug(args.debug)
        self.video = Video()
        self.videoStream = None
        self.board = Board()
        self.boardDetector = BoardDetector(self.board, self.video,args.speedup)
        self.env = Environment()
        # not recording
        self.videopath=None
        self.videoout=None
        if args.game is None:
            self.webCamGame = self.createNewCame()
        else:
            gamepath = args.game
            if not gamepath.startswith("/"):
                gamepath = self.env.games + "/" + gamepath
            self.webCamGame = WebCamGame.readJson(gamepath)
            if self.webCamGame is None:
                self.log("could not read %s " % (gamepath))
                self.webCamGame = self.createNewCame() 
        self.webCamGame.checkEnvironment(self.env)        
        self.game = self.webCamGame.game    
        self.log("Warp: %s" % (args.warpPointList))
        self.warp = Warp(args.warpPointList)
        self.warp.rotation = args.rotation
  
    def createNewCame(self):
        return WebCamGame("game" + self.video.fileTimeStamp())
        
    def log(self, msg):
        if WebApp.debug and self.logger is not None:
            self.logger.info(msg)

    # return the index.html template content with the given message
    def index(self, msg):
        self.log(msg)
        self.webCamGame.warp = self.warp
        self.webCamGame.save()
        gameid = self.webCamGame.gameid
        return render_template('index.html', message=msg, timeStamp=self.video.timeStamp(), gameid=gameid)

    def home(self):
        self.video = Video()
        return self.index("Home")

    def photoDownload(self, path, filename):
        #  https://stackoverflow.com/a/24578372/1497139
        return send_from_directory(directory=path, filename=filename)

    def setDebug(self, debug):
        WebApp.debug = debug
        BoardDetector.debug = WebApp.debug
        self.videoAnalyzer.setDebug(debug)
 
    # toggle the debug flag
    def chessDebug(self):
        self.setDebug(not WebApp.debug)
        msg = "debug " + ('on' if WebApp.debug else 'off')
        return self.index(msg)
    
    # automatically find the chess board
    def chessFindBoard(self):
        if self.video.frame is not None:
            try: 
                corners=self.videoAnalyzer.findChessBoard(self.video.frame, self.video)
                msg="%dx%d found" % (corners.rows,corners.cols)
                trapez=corners.trapez8x8
                self.warp.pointList=trapez
                self.warp.updatePoints()
            except Exception as e:
                msg=str(e)  
        else: 
            msg ="can't find chess board - video is not active"
        return self.index(msg)

    def chessTakeback(self):
        try:
            msg = "take back"
            self.board.takeback()
            if self.game.moveIndex > 0:
                self.game.moveIndex = self.game.moveIndex - 1
            else:
                msg = "can not take back any more moves"    
            if WebApp.debug:
                self.game.showDebug()
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)
    
    def chessSave(self): 
        # @TODO implement locking of a saved game to make it immutable
        gameid = self.webCamGame.gameid
        self.game.locked = True
        msg = "chess game <a href='/chess/games/%s'>%s</a> saved(locked)" % (gameid, gameid)
        return self.index(msg)
    
    def chessGameColors(self):
        msg = "color update in progress"
        return self.index(msg)

    def chessForward(self):
        msg = "forward"
        return self.index(msg)
    
    def indexException(self, e):
        msg = ("<span style='color:red'>%s</span>" % str(e))
        return self.index(msg)

    def chessMove(self, move):
        try:
            if "-" in move:
                move = move.replace('-', '')
            self.board.move(move)
            self.game.moveIndex = self.game.moveIndex + 1
            self.game.fen = self.board.fen()
            self.game.pgn = self.board.getPgn()
            msg = "move %s -> fen= %s" % (move, self.game.fen)
            if WebApp.debug:
                self.game.showDebug()
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def timeStamp(self):
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                        
    def chessGameState(self, gameid):
        fen = self.board.fen()
        pgn = self.board.getPgn()
        return jsonify(fen=fen, pgn=pgn, gameid=gameid, debug=WebApp.debug, timestamp=self.timeStamp())
    
    def chessFEN(self, fen):
        msg = fen
        try:
            self.board.setFEN(fen)
            msg = "game update from fen %s" % (fen)
            self.game.fen = fen
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
        px = x * self.video.width // w
        py = y * self.video.height // h
        colorInfo=""
        if self.video.frame is not None:
            b, g, r = self.video.frame[py, px]
            colorInfo="r:%x g:%x b:%x" % (r,g,b)
        self.warp.addPoint(px, py)
        msg = "clicked warppoint %d pixel %d,%d %s mouseclick %d,%d in image %d x %d" % (len(self.warp.pointList), px, py, colorInfo, x, y, w, h)
        return self.index(msg)

    def photo(self, path):
        try:
            # todo select input device
            if self.video.frames == 0:
                self.video.capture(self.args.input)
            filename = 'chessboard_%s.jpg' % (self.video.fileTimeStamp())
            # make sure the path exists
            Environment.checkDir(path)
            self.video.still2File(path + filename, postProcess=self.warpAndRotate, close=False)
            msg = "still image <a href='/photo/%s'>%s</a> taken from input %s" % (filename, filename, self.args.input)
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)
    
    def videoRecord(self,path):
        if self.videoout is None:
            if self.video.frames == 0:
                self.video.capture(self.args.input)
            self.videofilename = 'chessgame_%s.avi' % (self.video.fileTimeStamp())
            # make sure the path exists
            Environment.checkDir(path)
            self.videopath=path+self.videofilename
            msg="started recording"
        else:
            self.videoout.release()
            self.videopath=None
            self.videoout=None    
            msg="finished recording "+self.videofilename
        return self.index(msg)   

    def videoRotate90(self):
        try:
            self.warp.rotate(90)
            msg = "rotation: %d°" % (self.warp.rotation)
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

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
            warped = self.boardDetector.analyze(warped, self.video.frames, self.args.distance, self.args.step)
        if WebApp.debug:
            warped = self.video.addTimeStamp(warped)
        # do we need to record?
        if self.videopath is not None:
            # is the output open?
            if self.videoout is None:
                # create correctly sized output
                h, w = warped.shape[:2]
                self.videoout=self.video.prepareRecording(self.videopath,w,h)
         
            self.videoout.write(warped)   
            self.log("wrote frame %d to recording " % (self.video.frames)) 
        return warped

    # video generator
    def genVideo(self, video):
        while True:
            # postProcess=video.addTimeStamp
            postProcess = self.warpAndRotate
            ret, encodedImage, quitWanted = video.readJpgImage(show=False, postProcess=postProcess)
            # ensure we got a valid image
            if not ret:
                continue
            if quitWanted:
                break
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                           bytearray(encodedImage) + b'\r\n')
