# Imports
from argparse import ArgumentParser
import os
import sys
import torch
import torch.nn.functional as F

import PyQt6.QtCore
import PyQt6.QtWidgets
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel, QWidget
import cv2
import imutils
import numpy as np

from init_model import load_model, device # Import the load_model function from init_model.py

# Argument parser
parser = ArgumentParser(description='Test flow visualization')
parser.add_argument('--cv2', action='store_true', help='Use OpenCV for flow visualization')
parser.add_argument('--full_density', action='store_true', help='Use full density map for flow visualization')

curr_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(curr_dir, '..', '..')
cs_chan_dir = os.path.join(main_dir, 'cs_chan_dataset', 'Crowd Sequence')

sys.path.append(main_dir)

class CameraCV2FlowTest(QWidget):
    def __init__(self, width, height, image_dir, aspect_ratio=True, parent=None):
        super(CameraCV2FlowTest, self).__init__(parent)
        self.screen_width = width
        self.screen_height = height
        self.image_dir = image_dir
        self.maintain_aspect_ratio = aspect_ratio
        self.image_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.png') or f.endswith('.jpg')])
        self.current_image_index = 0

        # Store the previous frame for optical flow calculation
        self.previous_gray_frame = None

        # QLabel to display the images
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(self.screen_width, self.screen_height)

        # Timer for delaying the frame update
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.show_next_image)
        self.timer.start(60)  # Update the frame every 60 ms (16.67 fps)

        # Load the first image
        self.show_next_image()

    def load_image_sequence(self):
        # Load the current image in the sequence
        if self.current_image_index < len(self.image_files):
            self.capture = cv2.imread(self.image_files[self.current_image_index])
            self.current_image_index += 1
        else:
            self.current_image_index = 0  # Loop back to the first image
            self.capture = cv2.imread(self.image_files[self.current_image_index])

    def show_next_image(self):
        self.load_image_sequence()

        if self.capture is not None:
            frame = self.capture

            if self.maintain_aspect_ratio:
                frame = imutils.resize(frame, width=self.screen_width)
            else:
                frame = cv2.resize(frame, (self.screen_width, self.screen_height))

            # Convert the image to grayscale for optical flow calculation
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate optical flow if there's a previous frame
            if self.previous_gray_frame is not None:
                flow_map = self.calculate_optical_flow(self.previous_gray_frame, gray_frame)
                frame = self.draw_flow(frame, flow_map)

            # Update the previous frame
            self.previous_gray_frame = gray_frame

            # Convert the image to a QPixmap for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytesPerLine = ch * w
            convertToQtFormat = QtGui.QImage(frame_rgb.data, w, h, bytesPerLine, QtGui.QImage.Format.Format_RGB888)
            p = convertToQtFormat.scaled(self.screen_width, self.screen_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(p))

    def calculate_optical_flow(self, prev_frame, next_frame):
        # Use the Farneback method to calculate the optical flow
        flow = cv2.calcOpticalFlowFarneback(prev_frame, next_frame, None,
                                            0.5, 3, 15, 3, 5, 1.2, 0)
        return flow

    def draw_flow(self, frame, flow_map, step=16):
        """ Draws the optical flow vectors on the image """
        h, w = frame.shape[:2]
        for y in range(0, h, step):
            for x in range(0, w, step):
                flow = flow_map[y, x]
                start_point = (x, y)
                end_point = (int(x + flow[0]), int(y + flow[1]))
                cv2.arrowedLine(frame, start_point, end_point, (0, 255, 0), 1, tipLength=0.3)
        return frame


class CameraBoxDensityDifferenceFlowTest(QWidget):
    def __init__(self, width, height, image_dir, aspect_ratio=True, parent=None):
        super(CameraBoxDensityDifferenceFlowTest, self).__init__(parent)
        self.screen_width = width
        self.screen_height = height
        self.image_dir = image_dir
        self.maintain_aspect_ratio = aspect_ratio
        self.image_files = sorted(
            [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.png') or f.endswith('.jpg')])
        self.current_image_index = 0

        # Store the previous density map
        self.previous_density_map = None

        self.model = load_model()
        self.model.eval()

        # QLabel to display the images
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(self.screen_width, self.screen_height)

        # Timer for delaying the frame update
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.show_next_image)
        self.timer.start(60)  # Update the frame every 60 ms (16.67 fps)

        # Load the first image
        self.show_next_image()

    def load_image_sequence(self):
        # Load the current image in the sequence
        if self.current_image_index < len(self.image_files):
            self.capture = cv2.imread(self.image_files[self.current_image_index])
            self.current_image_index += 1
        else:
            self.current_image_index = 0  # Loop back to the first image
            self.capture = cv2.imread(self.image_files[self.current_image_index])

    def show_next_image(self):
        self.load_image_sequence()

        if self.capture is not None:
            frame = self.capture
            orig_height, orig_width = frame.shape[:2]

            if self.maintain_aspect_ratio:
                frame = self.resize_with_aspect_ratio(frame, width=self.screen_width)
            else:
                frame = cv2.resize(frame, (self.screen_width, self.screen_height))

            # Calculate the density map for the current frame
            density_map = self.calculate_density_map(frame.copy())

            # Calculate the density difference if there's a previous map
            if self.previous_density_map is not None:
                diff_density_map = density_map - self.previous_density_map

                if isinstance(diff_density_map, torch.Tensor):
                    # Detach the tensor from the computation graph and convert it to NumPy
                    diff_density_map = diff_density_map.detach().squeeze().cpu().numpy()

                rescaled_diff = cv2.resize(diff_density_map, (orig_width, orig_height), interpolation=cv2.INTER_LINEAR)

                frame = self.draw_density_flow(frame, rescaled_diff)

            # Update the previous density map
            self.previous_density_map = density_map

            # Convert the image to a QPixmap for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytesPerLine = ch * w
            convertToQtFormat = QtGui.QImage(frame_rgb.data, w, h, bytesPerLine, QtGui.QImage.Format.Format_RGB888)
            p = convertToQtFormat.scaled(self.screen_width, self.screen_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(p))

    def calculate_density_map(self, frame):
        if frame.shape[:2] != (224, 224):
            frame = cv2.resize(frame, (224, 224))

        frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255
        frame = frame.to(device)
        density_map = self.model(frame)
        # density_map = F.interpolate(density_map, size=(224, 224), mode='bilinear', align_corners=True) / 64

        return density_map

    def draw_density_flow(self, frame, diff_density_map, grid_rows=30, grid_cols=30):
        """ Draws flow vectors based on the density difference map using a high-density grid """
        h, w = diff_density_map.shape[:2]
        frame_h, frame_w = frame.shape[:2]
        box_height, box_width = h // grid_rows, w // grid_cols
        max_diff = np.max(np.abs(diff_density_map))  # Normalize for scaling

        if max_diff == 0:
            return frame  # If max_diff is zero, skip drawing and return the original frame

        for i in range(grid_rows):
            for j in range(grid_cols):
                y_start, y_end = i * box_height, (i + 1) * box_height
                x_start, x_end = j * box_width, (j + 1) * box_width

                # Calculate gradients (differences) within the grid section to determine flow direction
                grid_diff_x = np.mean(
                    diff_density_map[y_start:y_end, x_start + 1:x_end] - diff_density_map[y_start:y_end,
                                                                         x_start:x_end - 1])
                grid_diff_y = np.mean(
                    diff_density_map[y_start + 1:y_end, x_start:x_end] - diff_density_map[y_start:y_end - 1,
                                                                         x_start:x_end])

                # Normalize flow direction
                scale_factor = 20
                flow_x = (grid_diff_x / max_diff) * box_width * scale_factor
                flow_y = (grid_diff_y / max_diff) * box_height * scale_factor

                # Convert grid coordinates to frame coordinates
                frame_x_start = int(x_start * frame_w / w)
                frame_y_start = int(y_start * frame_h / h)
                frame_x_end = int(x_end * frame_w / w)
                frame_y_end = int(y_end * frame_h / h)

                # Determine the center of the grid cell
                center_x = int((frame_x_start + frame_x_end) / 2)
                center_y = int((frame_y_start + frame_y_end) / 2)

                # Calculate the end point for the flow vector
                end_point_x = int(center_x + flow_x)
                end_point_y = int(center_y + flow_y)

                # Draw the flow vector on the frame
                cv2.arrowedLine(frame, (center_x, center_y), (end_point_x, end_point_y), (0, 255, 0), 1, tipLength=0.3)

        return frame

    def resize_with_aspect_ratio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        """Resizes an image while maintaining its aspect ratio."""
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)


class CameraFullDensityDifferenceFlowTest(QWidget):
    def __init__(self, width, height, image_dir, aspect_ratio=True, parent=None):
        super(CameraFullDensityDifferenceFlowTest, self).__init__(parent)
        self.screen_width = width
        self.screen_height = height
        self.image_dir = image_dir
        self.maintain_aspect_ratio = aspect_ratio
        self.image_files = sorted(
            [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.png') or f.endswith('.jpg')])
        self.current_image_index = 0

        # Store the previous density map
        self.previous_density_map = None

        self.model = load_model()
        self.model.eval()

        # QLabel to display the images
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(self.screen_width, self.screen_height)

        # Timer for delaying the frame update
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.show_next_image)
        self.timer.start(60)  # Update the frame every 60 ms (16.67 fps)

        # Load the first image
        self.show_next_image()

    def load_image_sequence(self):
        # Load the current image in the sequence
        if self.current_image_index < len(self.image_files):
            self.capture = cv2.imread(self.image_files[self.current_image_index])
            self.current_image_index += 1
        else:
            self.current_image_index = 0  # Loop back to the first image
            self.capture = cv2.imread(self.image_files[self.current_image_index])

    def show_next_image(self):
        self.load_image_sequence()

        if self.capture is not None:
            frame = self.capture
            orig_height, orig_width = frame.shape[:2]

            if self.maintain_aspect_ratio:
                frame = self.resize_with_aspect_ratio(frame, width=self.screen_width)
            else:
                frame = cv2.resize(frame, (self.screen_width, self.screen_height))

            # Calculate the density map for the current frame
            density_map = self.calculate_density_map(frame.copy())

            # Calculate the density difference if there's a previous map
            if self.previous_density_map is not None:
                diff_density_map = density_map - self.previous_density_map

                if isinstance(diff_density_map, torch.Tensor):
                    # Detach the tensor from the computation graph and convert it to NumPy
                    diff_density_map = diff_density_map.detach().squeeze().cpu().numpy()

                rescaled_diff = cv2.resize(diff_density_map, (orig_width, orig_height), interpolation=cv2.INTER_LINEAR)

                frame = self.draw_density_flow(frame, rescaled_diff)

            # Update the previous density map
            self.previous_density_map = density_map

            # Convert the image to a QPixmap for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytesPerLine = ch * w
            convertToQtFormat = QtGui.QImage(frame_rgb.data, w, h, bytesPerLine, QtGui.QImage.Format.Format_RGB888)
            p = convertToQtFormat.scaled(self.screen_width, self.screen_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(p))

    def calculate_density_map(self, frame):
        if frame.shape[:2] != (224, 224):
            frame = cv2.resize(frame, (224, 224))

        frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255
        frame = frame.to(device)
        density_map = self.model(frame)
        density_map = F.interpolate(density_map, size=(224, 224), mode='bilinear', align_corners=True) / 64

        return density_map

    def draw_density_flow(self, frame, diff_density_map, step=11):
        """ Draws flow vectors based on the density difference map with multi-directional arrows """
        h, w = diff_density_map.shape[:2]
        frame_h, frame_w = frame.shape[:2]

        # Normalize the density difference map to handle the flow direction and magnitude
        max_diff = np.max(np.abs(diff_density_map))
        if max_diff == 0:
            return frame  # If max_diff is zero, skip drawing and return the original frame

        for y in range(0, h - step, step):
            for x in range(0, w - step, step):
                # Calculate gradients (differences) to determine the flow direction
                flow_x = np.mean(
                    diff_density_map[y:y + step, x + 1:x + step + 1] - diff_density_map[y:y + step, x:x + step])
                flow_y = np.mean(
                    diff_density_map[y + 1:y + step + 1, x:x + step] - diff_density_map[y:y + step, x:x + step])

                # Normalize flow direction
                scale_factor = 20
                flow_x = (flow_x / max_diff) * step * scale_factor
                flow_y = (flow_y / max_diff) * step * scale_factor

                # Map the coordinates from the density map to the frame
                start_x = int(x * frame_w / w)
                start_y = int(y * frame_h / h)

                # Calculate the end points for the flow vector
                end_x = int(start_x + flow_x)
                end_y = int(start_y + flow_y)

                # Draw the flow vector on the frame
                cv2.arrowedLine(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 1, tipLength=0.3)

        return frame

    def resize_with_aspect_ratio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        """Resizes an image while maintaining its aspect ratio."""
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)


class MainWindow(QWidget):
    def __init__(self, cv2_flag: bool, full_density: bool):
        super().__init__()
        self.setWindowTitle("Image Flow Sequence Test")
        self.setGeometry(100, 100, 800, 600)

        img_dir = os.path.join(cs_chan_dir, 'Sequence10')

        if cv2_flag:
            self.camera_test = CameraCV2FlowTest(800, 600, img_dir)
        else:
            if full_density:
                self.camera_test = CameraFullDensityDifferenceFlowTest(800, 600, img_dir)
            else:
                self.camera_test = CameraBoxDensityDifferenceFlowTest(800, 600, img_dir)

        # Set up layout
        layout = PyQt6.QtWidgets.QVBoxLayout()
        layout.addWidget(self.camera_test)

        self.setLayout(layout)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.cv2:
        print('Using OpenCV for flow visualization')
    else:
        if args.full_density:
            print('Using full density map for flow visualization')
        else:
            print('Using box-to-box density map difference for flow visualization')

    app = PyQt6.QtWidgets.QApplication([])
    window = MainWindow(args.cv2, args.full_density)
    window.show()
    app.exec()