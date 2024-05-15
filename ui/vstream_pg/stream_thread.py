from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import cv2 as cv

class StreamThread(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, link=None):
        super().__init__()
        self.link = link

    def run(self):
        self.ThreadActive = True

        cap = cv.VideoCapture(self.link)

        while self.ThreadActive:
            ret, frame = cap.read()

            if ret:
                image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                convert_to_qt = QImage(image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
                pic = convert_to_qt.scaled(757, 440, Qt.AspectRatioMode.KeepAspectRatio)
                self.ImageUpdate.emit(pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()