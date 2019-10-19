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

============================== test session starts ==============================
platform darwin -- Python 3.7.4, pytest-5.2.1, py-1.8.0, pluggy-0.12.0
rootdir: /Users/wf/source/python/play-chess-with-a-webcam
plugins: cov-2.8.1
collected 9 items                                                               

test_OpenCV_version.py .                                                  [ 11%]
test_Video.py ...                                                         [ 44%]
test_findBoard.py .....                                                   [100%]

---------- coverage: platform darwin, python 3.7.4-final-0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
Args.py                     10     10     0%
BoardFinder.py             206     32    84%
Cell.py                     10      4    60%
ChessCam.py                 72     72     0%
GameEngine.py               66     66     0%
InputManager.py             43     43     0%
MovementDetector.py         53     38    28%
StateDetector.py            93     75    19%
Video.py                   123     52    58%
chessUtils.py               78     55    29%
mathUtils.py                49     25    49%
state.py                   283    283     0%
test_OpenCV_version.py       6      0   100%
test_Video.py               28      0   100%
test_findBoard.py           49      0   100%
uci.py                      45     45     0%
--------------------------------------------
TOTAL                     1214    800    34%


============================== 9 passed in 24.07s ===============================
```

### Starting
```
./run
```
### Usage
```
/run -h
usage:  ChessCam.py [-h] [--nouci] [--input INPUT] [--debug]
                   [--cornermarker CORNERMARKER] [--fullScreen]

ChessCam Argument Parser

optional arguments:
  -h, --help            show this help message and exit
  --nouci               Don't use the UCI interface.
  --input INPUT         Manually set the input device.
  --debug               show debug output
  --cornermarker CORNERMARKER
                        filepath for an image of the cornermarker being used
  --fullScreen          Display output in fullScreen mode
```

### Recording Chess Games via webcam
```
./record
```

### Getting a still image of a Chess Games via webcam
```
./still
```
