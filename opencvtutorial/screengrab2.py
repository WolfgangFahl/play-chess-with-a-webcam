#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# https://stackoverflow.com/a/51643195/1497139

import numpy as np
import cv2
from PIL import ImageGrab as ig
import time

last_time = time.time()
while(True):
    bbox = (50, 50, 800, 640)
    screen = ig.grab(bbox=bbox)
    grabtime = time.time() - last_time
    print('grab took %3.1f s= %3.1f fps' % (grabtime, 1 / grabtime))
    title = "screen %d,%d %d,%d " % (bbox)
    cv2.imshow(title, np.array(screen))
    last_time = time.time()
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
