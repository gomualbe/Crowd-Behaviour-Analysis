# Imports
import PyQt6.QtCore
import PyQt6.QtWidgets
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel, QWidget, QApplication
from threading import Thread, Event
from collections import deque
import time
import cv2
from PyQt6.QtGui import QPainter, QPen, QColor
import numpy as np

# Custom QLabel class to display the video frame and draw grid/flow map on top of it
class CustomLabel(QLabel):
    def __init__(self, width, height):
        super().__init__()
        self.grid_rows = 4
        self.grid_cols = 4
        self.width = width
        self.height = height
        self.h = 0
        self.w = 0
        self.x_offset = 0
        self.y_offset = 0
        self.q_counts = np.zeros((4, 4))
        self.density_flag = False
        self.flow_map = None

        self.setFixedSize(self.width, self.height) # Set the size of the label

    def set_pixmap(self, pixmap):
        if pixmap:
            scaled_pixmap = pixmap.scaled(self.width, self.height,
                                          PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                          PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
            super().setPixmap(scaled_pixmap)
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Draw the video frame
        pixmap = self.pixmap()
        if pixmap:
            painter.drawPixmap(self.rect(), pixmap)

        if self.density_flag and self.flow_map is not None:
            self.draw_flow(painter) # Draw the flow map on top of the video frame
        else:
            self.draw_grid(painter) # Draw the grid with updated count on top of the video frame

        painter.end()

    def set_q_counts(self, counts):
        self.q_counts = counts
        self.update()

    def set_flow_map(self, flow_map, frame):
        self.flow_map = flow_map
        self.h, self.w = frame.shape[:2]
        self.update()

    def draw_grid(self, painter):
        # Draw the grid and counts
        pen = QPen(QColor(169, 169, 169, 150))  # Light gray color
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
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                label_text = f"{int(self.q_counts[i, j])}"
                text_width = painter.fontMetrics().horizontalAdvance(label_text)
                text_pos = QtCore.QPoint(self.x_offset + (j + 1) * col_width - text_width - 5,
                                         self.y_offset + i * row_height + painter.fontMetrics().ascent() + 5)

                painter.setPen(QColor(255, 0, 0, 200))
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(text_pos, label_text)

    def draw_flow(self, painter):
        if self.flow_map is None:
            return

        pen = QPen(QColor(0, 255, 0, 200))  # Green color for flow lines
        pen.setWidth(2)
        painter.setPen(pen)

        step_size = 22  # Adjust the step size according to the flow map resolution

        # Calculate the scaling factors between the original image size and the displayed size
        scale_x = self.width / self.w
        scale_y = self.height / self.h

        for y in range(0, self.h, step_size):
            for x in range(0, self.w, step_size):
                flow_vector = self.flow_map[y, x]

                # Scale the start point to the displayed image size
                start_x = int(x * scale_x)
                start_y = int(y * scale_y)

                # Scale the flow vector
                end_x = int((x + flow_vector[0]) * scale_x)
                end_y = int((y + flow_vector[1]) * scale_y)

                start_point = QtCore.QPoint(start_x, start_y)
                end_point = QtCore.QPoint(end_x, end_y)

                # Draw the arrow using QPainter
                painter.drawLine(start_point, end_point)

                # Optionally, draw the arrowhead
                self.draw_arrowhead(painter, start_point, end_point)

    def draw_arrowhead(self, painter, start_point, end_point):
        arrow_size = 1  # Size of the arrowhead
        angle = np.arctan2(start_point.y() - end_point.y(), start_point.x() - end_point.x())

        p1 = QtCore.QPointF(
            end_point.x() + arrow_size * np.cos(angle + np.pi / 4),
            end_point.y() + arrow_size * np.sin(angle + np.pi / 4)
        )
        p2 = QtCore.QPointF(
            end_point.x() + arrow_size * np.cos(angle - np.pi / 4),
            end_point.y() + arrow_size * np.sin(angle - np.pi / 4)
        )

        end_point_f = QtCore.QPointF(end_point)

        arrowhead = QtGui.QPolygonF([end_point_f, p1, p2])
        painter.drawPolygon(arrowhead)

    def toggle_density_flag(self, flag):
        self.density_flag = flag
        self.update()

class Camera(QWidget):
    def __init__(self, stream_link=0, parent=None, deque_size=1):
        super(Camera, self).__init__(parent)
        self.deque = deque(maxlen=deque_size)
        self.camera_stream_link = stream_link
        self.density_flag = False

        # Define separate sizes:
        self.sidebar_width = 195
        self.sidebar_height = int(self.sidebar_width * 9 / 16)  # e.g., ~110 pixels tall
        self.analysis_width = 1056  # A larger width for analysis
        self.analysis_height = int(self.analysis_width * 9 / 16)  # should be 594

        # The sidebar uses video_frame (small) and analysis uses custom_label (big)
        self.video_frame = QLabel(self)
        self.video_frame.setFixedSize(self.sidebar_width, self.sidebar_height)
        self.custom_label = CustomLabel(self.analysis_width, self.analysis_height)

        self.stop_event = Event()
        self.online = False
        self.capture = None

        self.load_network_stream()

        self.get_frame_thread = Thread(target=self.get_frame)
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.set_frame)
        self.timer.start(1)

        print('Started camera: {}'.format(self.camera_stream_link))

    def set_pixmap(self):
        if hasattr(self, 'frame') and self.frame is not None:
            # Convert the captured frame (in its full resolution) to RGB
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytesPerLine = ch * w
            qimg = QtGui.QImage(frame_rgb.data, w, h, bytesPerLine,
                                QtGui.QImage.Format.Format_RGB888)
            full_pixmap = QtGui.QPixmap.fromImage(qimg)

            # For the sidebar, scale to sidebar size with smooth transformation:
            sidebar_pixmap = full_pixmap.scaled(
                self.sidebar_width, self.sidebar_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation)
            self.video_frame.setPixmap(sidebar_pixmap)

            # For the analysis view, scale to analysis size with smooth transformation:
            analysis_pixmap = full_pixmap.scaled(
                self.analysis_width, self.analysis_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation)
            self.custom_label.set_pixmap(analysis_pixmap)

    def load_network_stream(self):
        def load_network_stream_thread():
            if self.verify_network_stream(self.camera_stream_link):
                print('Stream link opened')
                self.capture = cv2.VideoCapture(self.camera_stream_link)
                self.online = True

        self.load_stream_thread = Thread(target=load_network_stream_thread)
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
                    ret, frame = self.capture.read()
                    if ret:
                        self.deque.append(frame)
                    else:
                        self.capture.release()
                        self.online = False
                else:
                    print('Attempting to reconnect', self.camera_stream_link)
                    self.load_network_stream()
                    self.spin(2)
                self.spin(0.001)
            except AttributeError:
                pass

    def spin(self, seconds):
        time_end = time.time() + seconds
        while time.time() < time_end:
            QApplication.processEvents()

    def set_frame(self):
        if not self.online:
            self.spin(1)
            return

        if self.deque and self.online:
            self.frame = self.deque[-1]
            self.set_pixmap()

    def set_q_counts(self, counts):
        self.custom_label.set_q_counts(counts)

    def toggle_density_flag(self, flag):
        self.density_flag = flag
        self.custom_label.toggle_density_flag(flag)
        print('Density flag:', flag)

    def draw_flow_map(self, flow_map, frame):
        self.custom_label.set_flow_map(flow_map, frame)
        self.custom_label.update()

    def get_video_frame(self, analysis=False):
        return self.custom_label if analysis else self.video_frame

    def get_current_frame(self):
        if self.deque and self.online:
            return self.deque[-1].copy()  # Return the latest frame copy
        return None