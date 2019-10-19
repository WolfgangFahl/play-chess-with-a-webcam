# Play Chess With a Webcam by Olivier Dugas
[![Travis (.org)](https://img.shields.io/travis/WolfgangFahl/play-chess-with-a-webcam.svg)](https://travis-ci.org/WolfgangFahl/play-chess-with-a-webcam)
[![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/play-chess-with-a-webcam.svg)](https://github.com/WolfgangFahl/play-chess-with-a-webcam/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/WolfgangFahl/play-chess-with-a-webcam.svg)](https://github.com/WolfgangFahl/play-chess-with-a-webcam/issues/?q=is%3Aissue+is%3Aclosed)
[![GitHub](https://img.shields.io/github/license/WolfgangFahl/play-chess-with-a-webcam.svg)](https://www.apache.org/licenses/LICENSE-2.0)

[![chessboard](http://blogdugas.net/images/posts/chessboard.png)](http://blogdugas.net/blog/2015/05/18/play-chess-with-a-webcam/)

### Documentation
* [blogdugas.net](http://blogdugas.net/blog/2015/05/18/play-chess-with-a-webcam/)
* [Raspberry PI Chessboard Camera](http://wiki.bitplan.com/index.php/Raspberry_PI_Chessboard_Camera)


### Installation
Prerequisites: python2

```
./install
```

### Testing
```
./test
```


### Starting
```
./run
```
### Usage
```
/run -h
usage: ChessCam.py [-h] [--nouci] [--input INPUT] [--debug] [--fullScreen]

ChessCam Argument Parser

optional arguments:
  -h, --help     show this help message and exit
  --nouci        Don't use the UCI interface.
  --input INPUT  Manually set the input device.
  --debug        show debug output
  --fullScreen   Display output in fullScreen mode
```
  
### Recording Chess Games via webcam
```
./record
```

### Getting a still image of a Chess Games via webcam
```
./still
```
