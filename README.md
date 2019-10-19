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
scripts/install
```

### Testing
```
scripts/test

============================= test session starts =============================
platform darwin -- Python 3.7.4, pytest-5.2.1, py-1.8.0, pluggy-0.12.0
rootdir: /Users/wf/source/python/play-chess-with-a-webcam
plugins: cov-2.8.1
collected 10 items                                                            

src/test_ChessCam.py .                                                  [ 10%]
src/test_OpenCV_version.py .                                            [ 20%]
src/test_Video.py ...                                                   [ 50%]
src/test_findBoard.py .....                                             [100%]

---------- coverage: platform darwin, python 3.7.4-final-0 -----------
Name                         Stmts   Miss  Cover
------------------------------------------------
src/Args.py                     10      7    30%
src/BoardFinder.py             184     12    93%
src/Cell.py                     10      4    60%
src/ChessCam.py                 83     57    31%
src/InputManager.py             57     37    35%
src/MovementDetector.py         55     40    27%
src/StateDetector.py            93     75    19%
src/Video.py                   133     48    64%
src/chessUtils.py               78     55    29%
src/mathUtils.py                49     25    49%
src/test_ChessCam.py             4      0   100%
src/test_OpenCV_version.py       6      0   100%
src/test_Video.py               28      0   100%
src/test_findBoard.py           49      0   100%
------------------------------------------------
TOTAL                          839    360    57%


============================= 10 passed in 24.76s =============================
```

### Starting
```
scripts/run
```
### Usage
```
scripts/run -h
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
scripts/record
```

### Getting a still image of a Chess Games via webcam
```
scripts/still
```
