import cv2
import numpy as np
import time
from capture import Capture, Show

class Mask:
    def __init__(self, frame, rng_dict):
        self.mask = None
        self.frame = frame
        self.range_begin = rng_dict['begin']
        self.range_end = rng_dict['end']

    def mask_3d(self, debug=False):
        # takes 2d mask and convert to 3d channel mask
        # return image with 3 channel and back[0] and wihte[255]
        mask = self.mask.astype(np.bool)
        temp = np.ones(self.mask.shape+(3,)) * np.dstack([mask, mask, mask])*255
        resize_temp = cv2.resize(temp, (200,200), fx=.5, fy=.5)
        return resize_temp if debug else temp

    def create(self):
        image_hsv = self.hsv()
        self.mask = cv2.inRange(image_hsv, self.range_begin, self.range_end)
        return self

    def hsv(self):
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

    def add(self, second):
        return self.mask + second.mask
 
class Cloak:
    config = {
        'red':  {
            "lower":{'begin':(0,50,0), 'end':(10,255,255)},
            "upper":{'begin':(170,180,0), 'end':(180,255,255)}
        }, 
    }

    def __init__(self, background, frame):
        self.background = background
        self.frame = np.flip(frame, axis=1) # to display same image

    def hide(self, debug=False):
        m1 = Mask(self.frame, self.config['red']['lower']).create()
        m2 = Mask(self.frame, self.config['red']['upper']).create()
        self.mask = m1.add(m2)
        self.mask_inv = self.bit_not()

        morph = self.morph_ex()
        dialate = self.dilate()
        
        frame = self.frame_roi()
        background = self.backgorund_roi()
        if debug:
            return np.hstack([m1.mask_3d(True), m2.mask_3d(True), self.cloak_3d(morph,True), self.cloak_3d(dialate,True)]) 

        return cv2.addWeighted(frame, 1, background, 1, 0)

    def frame_roi(self):
        return cv2.bitwise_and(self.frame, self.frame, mask=self.mask_inv)

    def backgorund_roi(self):
        return cv2.bitwise_and(self.background, self.background, mask=self.mask)

    def bit_not(self):
        return cv2.bitwise_not(self.mask)

    def morph_ex(self, method=cv2.MORPH_OPEN):
        return cv2.morphologyEx(self.mask, method, np.ones((3,3),np.uint8))
    
    def dilate(self):
        return cv2.dilate(self.mask, np.ones((3,3), np.uint8))

    def cloak_3d(self, mask, debug=False):
        # takes 2d mask and convert to 3d channel mask
        # return image with 3 channel and back[0] and wihte[255]
        mask = mask.astype(np.bool)
        temp = np.ones(mask.shape+(3,)) * np.dstack([mask, mask, mask])*255
        resize_temp = cv2.resize(temp, (200,200), fx=.5, fy=.5)
        return resize_temp if debug else temp

if __name__ == "__main__":
    cap = Capture(0).start() # or give video link
    disp = Show(cap.frame).start()

    # take from few frame as background
    wait = 50 # inerations
    while wait:
        time.sleep(.1)
        background = np.flip(cap.frame, axis=1)
        disp.frame = background
        wait -= 1

    # show after hiding the cloak
    while disp.showing and cap.capturing:
        disp.frame = Cloak(background, cap.frame).hide(debug=False)

    cap.stop()
    disp.stop()


"""
How to use this script?
    1. Run the script and do not change camera position.
    2. Wait for a minute and record the background without person.
    3. Now come to frame[person].
    4. Use any red colored or similar colored cloth/thing to hide yourself.

TODO: Add your custom color to config in cloak class to hide another color.
"""