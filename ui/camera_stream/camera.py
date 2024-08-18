import PyQt6.QtCore
import PyQt6.QtWidgets
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel, QWidget
from threading import Thread, Event
from collections import deque
import time
import cv2
import imutils
from PyQt6.QtGui import QPainter, QPen, QColor


class GridLabel(QLabel):
    def __init__(self, width, height):
        super().__init__()
        self.grid_rows = 4
        self.grid_cols = 4
        self.width = width
        self.height = height
        self.x_offset = 0
        self.y_offset = 0

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)

        pen = QPen(QColor(169, 169, 169, 150)) # Light gray color
        pen.setWidth(1)
        painter.setPen(pen)

        row_height = self.height // self.grid_rows
        col_width = self.width // self.grid_cols

        # Draw the grid lines
        for i in range(1, self.grid_cols):
            painter.drawLine(self.x_offset + i * col_width, self.y_offset,
                             self.x_offset + i * col_width, self.y_offset + self.height)
        for i in range(1, self.grid_rows):
            painter.drawLine(self.x_offset, self.y_offset + i * row_height,
                             self.x_offset + self.width, self.y_offset + i * row_height)

        # Write the grid labels
        for  i in range(self.grid_rows):
            for j in range(self.grid_cols):
                label_text = f"Q{i * self.grid_cols + j + 1}"
                text_pos = QtCore.QPoint(self.x_offset + j * col_width + 5,
                                         self.y_offset + (i + 1) * row_height - 5)
                painter.drawText(text_pos, label_text)

        painter.end()


class Camera(QWidget):

    def __init__(self, width, height, stream_link=0, aspect_ratio=True, parent=None, deque_size=1):
        super(Camera, self).__init__(parent)
        self.deque = deque(maxlen=deque_size)
        self.screen_width = width
        self.screen_height = height
        self.maintain_aspect_ratio = aspect_ratio
        self.camera_stream_link = stream_link

        self.grid_label = GridLabel(self.screen_width, self.screen_height)
        self.video_frame = QLabel(self)
        self.stop_event = Event()

        self.online = False
        self.capture = None

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

            video_width = p.width()
            video_height = p.height()

            x_offset = (self.screen_width - video_width) // 2
            y_offset = (self.screen_height - video_height) // 2

            self.grid_label.width = video_width
            self.grid_label.height = video_height
            self.grid_label.x_offset = x_offset
            self.grid_label.y_offset = y_offset

            self.grid_label.update()

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
            self.grid_label.setPixmap(self.video_frame.pixmap())  # Set the video frame pixmap
            self.grid_label.update()  # Redraw the grid on top of the video frame

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

    def get_video_frame(self, analysis=False):
        if not analysis:
            return self.video_frame

        return self.grid_label  # Return the grid label, which now overlays the video stream

    def get_link(self):
        return self.camera_stream_link

    def get_current_frame(self):
        if self.deque and self.online:
            frame = self.deque[-1].copy()  # Get the latest frame
            return frame  # Return the actual frame if available

        return None  # Return None if there's no frame available
