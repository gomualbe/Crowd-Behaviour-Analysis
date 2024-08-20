import PyQt6.QtGui
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QThread, pyqtSignal

import ui.mainwindow
from ui.camera_stream.camera import Camera
import os
import onnxruntime as ort
import cv2
import torch
import numpy as np
import torch.nn.functional as F
from init_model import load_model, device
import time

curr_dir = os.path.abspath(os.path.dirname(__file__))
main_dir = os.path.join(curr_dir, '..')
onnx_path = os.path.join(main_dir, 'onnx', 'model.onnx')

q_counts = np.zeros((4, 4))

class ProcessingThread(QThread):
    people_count_signal = pyqtSignal(int)

    def __init__(self, camera, window, onnx=False):
        super().__init__()
        self.camera = camera
        self.onnx = onnx
        self.window = window

        self.p_frame = None

        if self.onnx:
            self.session = ort.InferenceSession(onnx_path)  # Load the ONNX model
        else:
            self.model = load_model()  # Load the PyTorch model
            self.model.eval()

    def set_camera(self, camera):
        self.camera = camera

    def run(self):
        self.msleep(4000)  # Sleep for 4 seconds before starting the processing loop

        while True:
            frame = self.camera.get_current_frame()
            f_copy = frame.copy()

            if frame is None:
                print("No frame available to process.")
                continue

            # Resize frame to 224x224 if needed
            if frame.shape[:2] != (224, 224):
                frame = cv2.resize(frame, (224, 224))

            start = time.time()

            if self.onnx:
                try:
                    input_blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0 / 255, size=(224, 224), mean=(0, 0, 0),
                                                       swapRB=True, crop=False)
                    output = self.session.run(None, {self.session.get_inputs()[0].name: input_blob})
                    density_map = output[0]

                except Exception as e:
                    print(f"Error during blob creation or inference: {e}")
                    continue
            else:
                # Convert frame to tensor and move to the device
                frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255

                with torch.no_grad():
                    frame = frame.to(device)
                    density_map = self.model(frame)
                    density_map = F.interpolate(density_map, size=(224, 224), mode='bilinear', align_corners=True) / 64

                total = density_map.sum(dim=(1, 2, 3)).item()

            # Divide density map into a 4x4 grid and count people in each box
            total_people_count = 0
            grid_rows, grid_cols = 4, 4
            box_height, box_width = density_map.shape[2] // grid_rows, density_map.shape[3] // grid_cols

            for i in range(grid_rows):
                for j in range(grid_cols):
                    y_start, y_end = i * box_height, (i + 1) * box_height
                    x_start, x_end = j * box_width, (j + 1) * box_width

                    grid_section = density_map[:, :, y_start:y_end, x_start:x_end]
                    people_count = torch.sum(grid_section).item()
                    print(f'({i},{j}) count: {people_count}')

                    q_counts[i, j] = people_count
                    total_people_count += people_count

            end = time.time()

            if self.camera.grid_label.density_flag and self.p_frame is not None:
                flow_map = self.calculate_optical_flow(self.p_frame, f_copy)
                self.camera.draw_flow_map(flow_map)

            self.p_frame = f_copy.copy()

            self.camera.set_q_counts(q_counts)

            print(f"\nDetected people count (Total): {total}")
            print(f"Detected people count (Grid Analysis): {total_people_count}")
            self.people_count_signal.emit(int(total_people_count))

            print(f"\nTime taken: {end - start:.2f} sec\n\n")

            self.msleep(15)  # Sleep for 15 msec (60+ fps)

    def calculate_optical_flow(self, prev_frame, current_frame):
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(prev_gray, current_gray, None,  0.5, 3, 16,
                                            3, 5, 1.2, 0)
        return flow


class Analysis(QWidget):
    def __init__(self, width, height, links, main_window, switch):
        super().__init__()

        self.width = width
        self.height = height

        self.main_window = main_window
        self.links = links
        self.switch = switch

        self.camera = None

        # Separate thread for frame processing
        self.processing_thread = ProcessingThread(self.camera, self.main_window)
        self.processing_thread.people_count_signal.connect(self.main_window.update_people_count)

        self.setup_camera(self.links[0])

        self.processing_thread.start() # Start the thread

    def setup_camera(self, link):
        width = self.width - 40
        height = int(width * 9 / 16)

        self.camera = Camera(width, height, link)
        frame_video = self.camera.get_video_frame(analysis=True)

        time.sleep(2)

        print('Camera frame taken')
        self.main_window.set_camera_frame(frame_video)
        self.processing_thread.set_camera(self.camera)
        self.switch.toggled.connect(self.camera.toggle_density_flag)

    def update_camera(self, link):
        if self.camera:
            print('Deleting stream...')
            self.camera.delete_stream()

        print('Updating camera...')
        self.main_window.remove_camera_frame()
        self.setup_camera(link)
