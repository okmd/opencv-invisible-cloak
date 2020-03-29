import cv2
import threading
import numpy as np
import time


class Capture:
    def __init__(self, source=0):
        self.source = source
        self.capturing = False
        self.capture = cv2.VideoCapture(self.source)
        self.__init_frame()

    def __init_frame(self):
        self.frame = np.ones((int(self.capture.get(4)),int(self.capture.get(3)),3))*255

    def start(self):
        if self.capture:
            self.capturing = True
            threading.Thread(target=self.update, args=()).start()
        else:
            print("Info: Unable to initialize camera.")
        return self

    def update(self):
        while self.capturing:
            self.status, self.frame = self.capture.read()
            if self.status:
                self.status, self.frame = self.capture.read()
            else:
                self.stop()

    def bgr2hsv(self):
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

    def bgr2rgb(self):
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

    def stop(self):
        if self.capturing:
            print("INFO: Stopped Capturing.")
        self.capturing = False
        
    
    def __del__(self):
        self.capture.release()


class Show:
    def __init__(self, frame):
        self.frame = frame
        self.showing = False

    def start(self):
        self.showing = True
        threading.Thread(target=self.display).start()
        return self
    
    def stop(self):
        if self.showing:
            print("INFO: Stopped Displaying.")
        self.showing = False
        
    
    def display(self):
        while self.showing:
            cv2.imshow("Camera", self.frame)
            if cv2.waitKey(1) == ord('q'):
                self.stop()
    

if __name__ == "__main__":
    cap = Capture(source=0).start()
    disp = Show(cap.frame).start()

    while disp.showing and cap.capturing:
        disp.frame = cap.frame

    cap.stop()
    disp.stop()

