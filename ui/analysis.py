import PyQt6.QtGui
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QThread, pyqtSignal
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

class ProcessingThread(QThread):
    people_count_signal = pyqtSignal(int)

    def __init__(self, camera, window, onnx=False):
        super().__init__()
        self.camera = camera
        self.onnx = onnx
        self.window = window

        if self.onnx:
            self.session = ort.InferenceSession(onnx_path) # Load the ONNX model
        else:
            self.model = load_model() # Load the PyTorch model
            self.model.eval()


    def set_camera(self, camera):
        self.camera = camera

    def run(self):
        self.msleep(4000)  # Sleep for 4 seconds before starting the processing loop

        while True:
            frame = self.camera.get_current_frame()

            if frame is None:
                print("No frame available to process.")
                continue

            # Grid analysis setup: dividing the frame into a 4x4 grid
            grid_rows, grid_cols = 4, 4
            box_height, box_width = frame.shape[0] // grid_rows, frame.shape[1] // grid_cols
            total_people_count = 0

            start = time.time()

            for i in range(grid_rows):
                for j in range(grid_cols):
                    y_start, y_end = i * box_height, (i + 1) * box_height
                    x_start, x_end = j * box_width, (j + 1) * box_width
                    grid_section = frame[y_start:y_end, x_start:x_end]

                    grid_section = cv2.resize(grid_section, (224, 224))

                    if self.onnx:
                        input_blob = cv2.dnn.blobFromImage(grid_section, scalefactor=1.0 / 255, size=(224, 224),
                                                           mean=(0, 0, 0), swapRB=True, crop=False)
                        output = self.session.run(None, {self.session.get_inputs()[0].name: input_blob})
                        people_count = np.argmax(output[0])
                    else:
                        grid_section_tensor = (torch.from_numpy(grid_section).permute(2, 0, 1)
                                               .unsqueeze(0).float() / 255)
                        grid_section_tensor = grid_section_tensor.to(device)

                        with torch.no_grad():
                            crop_pred = self.model(grid_section_tensor)
                            crop_pred = F.interpolate(crop_pred, size=(box_height, box_width), mode='bilinear',
                                                      align_corners=True) / 64
                            people_count = torch.sum(crop_pred).item()

                        # Update the people count for the grid section
                        self.window.update_q_count(i, j, people_count)

                    total_people_count += int(people_count)
                    self.msleep(15) # Sleep for 15 milliseconds before processing the next grid section

            end = time.time()
            print(f"Time taken for full frame processing: {end - start} seconds")
            print(f"Detected people count (Grid Analysis): {total_people_count}")
            self.people_count_signal.emit(total_people_count)

class Analysis(QWidget):
    def __init__(self, width, height, links, main_window):
        super().__init__()

        self.width = width
        self.height = height

        self.main_window = main_window
        self.links = links

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

        print('Camera frame taken')
        self.main_window.set_camera_frame(frame_video)
        self.processing_thread.set_camera(self.camera)

    def update_camera(self, link):
        if self.camera:
            print('Deleting stream...')
            self.camera.delete_stream()

        print('Updating camera...')
        self.main_window.remove_camera_frame()
        self.setup_camera(link)
