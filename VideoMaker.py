# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# see https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
from Video import Video

video=Video()
video.capture(0)
video.record("chessVideo")
