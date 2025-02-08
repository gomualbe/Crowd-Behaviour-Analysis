from ui.camera_stream.camera import Camera
import PyQt6
from PyQt6 import QtCore

class CameraWidget(Camera):
    """Camera class for multistream page,
    it adds a signal to the Camera class to emit when the camera is clicked"""
    clicked = PyQt6.QtCore.pyqtSignal()

    def __init__(self, stream_link, parent=None, deque_size=1):
        super(CameraWidget, self).__init__(stream_link, parent, deque_size)
        self.pressPos = None

    def mousePressEvent(self, event):
        if event.button() == PyQt6.Qt.MouseButton.LeftButton:
            self.pressPos = event.pos()

    def mouseReleaseEvent(self, event):
        if (self.pressPos is not None and
                event.button() == PyQt6.Qt.MouseButton.LeftButton and
                self.rect().contains(self.pressPos)):
            self.clicked.emit()

        self.pressPos = None