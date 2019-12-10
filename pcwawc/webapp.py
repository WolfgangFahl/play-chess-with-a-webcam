#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.board import Board
from pcwawc.videoanalyze import VideoAnalyzer
from pcwawc.boarddetector import BoardDetector
from pcwawc.environment import Environment
from pcwawc.video import Video
from pcwawc.game import WebCamGame
from flask import render_template, send_from_directory, Response, jsonify
from datetime import datetime

class WebApp:
    """ actual Play Chess with a WebCam Application - Flask calls are routed here """
    debug = False

    # construct me with the given settings
    def __init__(self, args, logger=None):
        """ construct me """
        self.args = args
        self.video = Video()
       
        
        self.videoStream = None
        self.board = Board()
        self.boardDetector = BoardDetector(self.board, self.video,args.speedup)
        self.videoAnalyzer=VideoAnalyzer(args,video=self.video,logger=logger,analyzers={self.boardDetector})
        self.setDebug(args.debug)
        self.env = Environment()
        if args.game is None:
            self.webCamGame = self.createNewCame()
        else:
            gamepath = args.game
            if not gamepath.startswith("/"):
                gamepath = self.env.games + "/" + gamepath
            self.webCamGame = WebCamGame.readJson(gamepath)
            if self.webCamGame is None:
                self.videoAnalyzer.log("could not read %s " % (gamepath))
                self.webCamGame = self.createNewCame() 
        self.webCamGame.checkEnvironment(self.env)        
        self.game = self.webCamGame.game
  
    def createNewCame(self):
        return WebCamGame("game" + self.video.fileTimeStamp())
        
    def log(self, msg):
        self.videoAnalyzer.log(msg)

    # return the index.html template content with the given message
    def index(self, msg):
        self.log(msg)
        self.webCamGame.warp = self.videoAnalyzer.warp
        self.webCamGame.save()
        gameid = self.webCamGame.gameid
        return render_template('index.html', message=msg, timeStamp=self.video.timeStamp(), gameid=gameid)

    def home(self):
        self.videoAnalyzer.video = Video()
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
        if self.videoAnalyzer.hasImage():
            try: 
                corners=self.videoAnalyzer.findChessBoard()
                msg="%dx%d found" % (corners.rows,corners.cols)
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
        px = x * self.videoAnalyzer.video.width // w
        py = y * self.videoAnalyzer.video.height // h
        colorInfo=""
        if self.videoAnalyzer.hasImage() is not None:
            b, g, r = self.videoAnalyzer.video.frame[py, px]
            colorInfo="r:%x g:%x b:%x" % (r,g,b)
        warp=self.videoAnalyzer.warp
        warp.addPoint(px, py)
        msg = "clicked warppoint %d pixel %d,%d %s mouseclick %d,%d in image %d x %d" % (len(warp.pointList), px, py, colorInfo, x, y, w, h)
        return self.index(msg)

    def photo(self, path):
        try:
            self.videoAnalyzer.open()
            video=self.videoAnalyzer.video
            filename = 'chessboard_%s.jpg' % (video.fileTimeStamp())
            # make sure the path exists
            Environment.checkDir(path)
            video.still2File(path + filename, postProcess=self.videoAnalyzer.warpAndRotate, close=False)
            msg = "still image <a href='/photo/%s'>%s</a> taken from input %s" % (filename, filename, self.args.input)
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)
    
    def videoRecord(self,path):
        if not self.videoAnalyzer.isRecording():
            video=self.videoAnalyzer.video
            filename=self.videoAnalyzer.startVideoRecording(path,'chessgame_%s.avi' % (video.fileTimeStamp()))
            msg="started recording %s" % (filename)
        else:
            filename=self.videoAnalyzer.stopVideoRecording()  
            msg="finished recording "+filename
        return self.index(msg)   

    def videoRotate90(self):
        try:
            warp=self.videoAnalyzer.warp
            warp.rotate(90)
            msg = "rotation: %d°" % (warp.rotation)
            return self.index(msg)
        except BaseException as e:
            return self.indexException(e)

    def videoPause(self):
        ispaused=self.videoAnalyzer.videoPause()
        msg = "video " + ('paused' if ispaused else 'running')
        return self.index(msg)

    def videoFeed(self):
        self.videoAnalyzer.open()
        # return the response generated along with the specific media
        # type (mime type)
        video=self.videoAnalyzer.video
        return Response(self.genVideo(video),
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

    

    # video generator
    def genVideo(self, video):
        while True:
            # postProcess=video.addTimeStamp
            postProcess = self.videoAnalyzer.warpAndRotate
            ret, encodedImage, quitWanted = video.readJpgImage(show=False, postProcess=postProcess)
            # ensure we got a valid image
            if not ret:
                continue
            if quitWanted:
                break
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                           bytearray(encodedImage) + b'\r\n')
