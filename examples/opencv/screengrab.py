#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# see https://stackoverflow.com/a/54246290/1497139
# renders at > 65 fps on a mac mini
import numpy as np
import cv2
from mss import mss
from PIL import Image
import time

last_time = time.time()
bbox = {'top': 50, 'left': 50, 'width': 800, 'height': 640}
sum = 0
count = 0
sct = mss()
while 1:
    sct_img = sct.grab(bbox)
    grabtime = time.time() - last_time
    sum += 1 / grabtime
    count = count + 1
    print('grab took %3.2f s= %4.1f fps avg=%4.1f fps' % (grabtime, 1 / grabtime, sum / count))
    cv2.imshow('screen', np.array(sct_img))
    last_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
