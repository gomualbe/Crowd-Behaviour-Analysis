from ui.camera_stream.camera import Camera
import PyQt6
from PyQt6 import QtCore

class CameraWidget(Camera):
    """Camera class for multistream page,
    it adds a signal to the Camera class to emit when the camera is clicked"""
    clicked = PyQt6.QtCore.pyqtSignal()

    def __init__(self, width, height, stream_link=0, aspect_ratio=True, parent=None, deque_size=1):
        super(CameraWidget, self).__init__(width, height, stream_link, aspect_ratio, parent, deque_size)

    def mousePressEvent(self, event):
        if event.butt == PyQt6.Qt.MouseButton.LeftButton:
            self.pressPos = event.pos()

    def mouseReleaseEvent(self, event):
        # Ensure that the left button was pressed and released within the geometry of the widget
        # if so, emit the signal
        if self.pressPos is not None and event.button() == PyQt6.Qt.MouseButton.LeftButton:
            self.clicked.emit()

        self.pressPos = None