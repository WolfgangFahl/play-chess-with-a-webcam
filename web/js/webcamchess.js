// 2019-10-22
// Webcam Chess JavaScript code
// https://chessboardjs.com/examples#5003
// NOTE: this example uses the chess.js library:
// https://github.com/jhlywa/chess.js

var board = null
var game = new Chess()
var whiteSquareGrey = '#a9a9a9'
var blackSquareGrey = '#696969'

// execute the given command in the URL parameters
function handleQuery() {
  var url=new URL(window.location.href)
  var searchParams = new URLSearchParams(url.search);
  var pgn=searchParams.get('pgn')
  var fen=searchParams.get('fen')
  var updateGame=searchParams.get('updateGame')
  var updateFEN=searchParams.get('updateFEN')
  if (pgn && updateGame ){
    game.load_pgn(pgn);
    board.position(game.fen());
    showPgn(false);
  }
  if (fen && updateFEN) {
    game=new Chess(fen)
    board.position(game.fen());
    showPgn(false);
  }
}

// add  a click hander for the webcam
function addChessWebCamClickHandler() {
  // https://stackoverflow.com/questions/34867066/javascript-mouse-click-coordinates-for-image
  document.getElementById('chesswebcam').addEventListener('click', function (event) {
    // https://stackoverflow.com/a/288731/1497139
    bounds=this.getBoundingClientRect();
    var left=bounds.left;
    var top=bounds.top;
    var x = event.pageX - left;
    var y = event.pageY - top;
    var cw=this.clientWidth
    var ch=this.clientHeight
    var iw=this.naturalWidth
    var ih=this.naturalHeight
    var px=x/cw*iw
    var py=y/ch*ih
    alert("click on "+this.tagName+" at pixel ("+px+","+py+") mouse pos ("+x+"," + y+ ") relative to boundingClientRect at ("+left+","+top+") client image size: "+cw+" x "+ch+" natural image size: "+iw+" x "+ih );
  });
}

function removeGreySquares () {
  $('#chessboard .square-55d63').css('background', '')
}

function greySquare (square) {
  var $square = $('#chessboard .square-' + square)

  var background = whiteSquareGrey
  if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
  }

  $square.css('background', background)
}

function onDragStart (source, piece) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false

  // or if it's not that side's turn
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false
  }
}

// show the pgn notation of the game
function showPgn(doClick) {
  var pgn=game.pgn();
  // textarea
  document.getElementById("pgn").innerHTML = pgn;
  // input
  var fen=board.fen();
  document.getElementById("fen").innerHTML = fen;
  if (doClick)
     document.getElementById('updateGame').click();
}

function onDrop (source, target) {
  removeGreySquares()

  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })

  // illegal move
  if (move === null)
    return 'snapback'
  else {
    showPgn(true);
  }
}

function onMouseoverSquare (square, piece) {
  // get list of possible moves for this square
  var moves = game.moves({
    square: square,
    verbose: true
  })

  // exit if there are no moves available for this square
  if (moves.length === 0) return

  // highlight the square they moused over
  greySquare(square)

  // highlight the possible squares for this piece
  for (var i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }
}

function onMouseoutSquare (square, piece) {
  removeGreySquares()
}

function onSnapEnd () {
  board.position(game.fen())
}

var config = {
  draggable: true,
  pieceTheme: '/img/chesspieces/wikipedia/{piece}.png',
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onMouseoutSquare: onMouseoutSquare,
  onMouseoverSquare: onMouseoverSquare,
  onSnapEnd: onSnapEnd
}
// addChessWebCamClickHandler()
board = Chessboard('chessboard', config)
