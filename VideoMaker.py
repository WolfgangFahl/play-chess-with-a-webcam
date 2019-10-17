# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# see https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
import cv2
import numpy as np
import sys
from time import strftime


cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT ))
fps =  int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
filename="chessVideo%s.avi" % strftime("%Y-%m-%d_%H%M%S")

out = cv2.VideoWriter(filename,fourcc, 20.0, (width,height))
print ("recording %s with %dx%d at %d fps press q to stop recording" % (filename,width,height,fps))


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        # flip the frame
        # frame = cv2.flip(frame,0)

        # write the  frame
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
print ("finished")
