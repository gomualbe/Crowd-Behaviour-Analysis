import PyQt6.QtCore
import PyQt6.QtWidgets
import numpy
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel, QWidget
from threading import Thread, Event
from collections import deque
import time
import cv2
import imutils


class Camera(QWidget):
    """Independent camera feed
    Uses threading to grab IP camera frames in the background

    @param width - Width of the video frame
    @param height - Height of the video frame
    @param stream_link - IP/RTSP/Webcam link
    @param aspect_ratio - Whether to maintain frame aspect ratio or force into frame
    """

    def __init__(self, width, height, stream_link=0, aspect_ratio=True, parent=None, deque_size=1):
        super(Camera, self).__init__(parent)
        self.deque = deque(maxlen=deque_size)
        self.screen_width = width
        self.screen_height = height
        self.maintain_aspect_ratio = aspect_ratio
        self.camera_stream_link = stream_link

        self.online = False
        self.capture = None
        self.video_frame = QLabel(self)
        self.stop_event = Event()

        self.load_network_stream()

        self.get_frame_thread = Thread(target=self.get_frame, args=())
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.set_frame)
        self.timer.start(1)

        print('Started camera: {}'.format(self.camera_stream_link))

    def load_network_stream(self):
        def load_network_stream_thread():
            if self.verify_network_stream(self.camera_stream_link):
                print('Stream link opened')
                self.capture = cv2.VideoCapture(self.camera_stream_link)
                self.online = True

        self.load_stream_thread = Thread(target=load_network_stream_thread, args=())
        self.load_stream_thread.daemon = True
        self.load_stream_thread.start()

    def verify_network_stream(self, link):
        cap = cv2.VideoCapture(link)
        if not cap.isOpened():
            return False
        cap.release()
        return True

    def get_frame(self):
        while not self.stop_event.is_set():
            try:
                if self.capture and self.capture.isOpened() and self.online:
                    self.status, frame = self.capture.read()
                    if self.status:
                        self.deque.append(frame)
                    else:
                        self.capture.release()
                        self.online = False
                else:
                    print('Attempting to reconnect', self.camera_stream_link)
                    self.load_network_stream()
                    self.spin(2)
                self.spin(.001)
            except AttributeError:
                pass

    def spin(self, seconds):
        time_end = time.time() + seconds
        while time.time() < time_end:
            PyQt6.QtWidgets.QApplication.processEvents()

    def set_pixmap(self):
        if hasattr(self, 'frame'):
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = self.frame.shape
            bytesPerLine = ch * w
            convertToQtFormat = QtGui.QImage(self.frame.data, w, h, bytesPerLine, QtGui.QImage.Format.Format_RGB888)
            p = convertToQtFormat.scaled(self.screen_width, self.screen_height,
                                         PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.video_frame.setPixmap(QtGui.QPixmap.fromImage(p))

    def set_frame(self):
        if not self.online:
            self.spin(1)
            return

        if self.deque and self.online:
            frame = self.deque[-1]

            if self.maintain_aspect_ratio:
                self.frame = imutils.resize(frame, width=self.screen_width)
            else:
                self.frame = cv2.resize(frame, (self.screen_width, self.screen_height))

            self.set_pixmap()

    def delete_stream(self):
        print('Stopping camera: {}'.format(self.camera_stream_link))
        self.stop_event.set()  # Signal the thread to stop
        self.get_frame_thread.join()  # Wait for the thread to finish

        if self.capture and self.capture.isOpened():
            print('Releasing camera: {}'.format(self.camera_stream_link))
            self.capture.release()

        if self.video_frame:
            self.video_frame.clear()
            self.video_frame.deleteLater()

        self.online = False
        print('Camera stopped safely.')

    def get_video_frame(self):
        return self.video_frame

    def get_link(self):
        return self.camera_stream_link

    def get_current_frame(self):
        if self.deque and self.online:
            frame = self.deque[-1].copy()  # Get the latest frame
            return frame # Return the actual frame if available

        return None  # Return None if there's no frame available
