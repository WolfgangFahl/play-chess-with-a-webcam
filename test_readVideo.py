import numpy as np
import cv2
import os

cap = cv2.VideoCapture('chessVideo2019-10-17_134753.avi')
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
