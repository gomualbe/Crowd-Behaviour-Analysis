from PyQt6.QtCore import QThread, pyqtSignal
import os
import onnxruntime as ort
import cv2
import torch
import numpy as np
import torch.nn.functional as F
from init_model import load_model, device
from ui.camera_stream.camera import Camera
import time

curr_dir = os.path.abspath(os.path.dirname(__file__))
main_dir = os.path.join(curr_dir, '..')
onnx_path = os.path.join(main_dir, 'onnx', 'model.onnx')

q_counts = np.zeros((4, 4)) # 4x4 grid to store people count for each box

class ProcessingThread(QThread):
    people_count_signal = pyqtSignal(int)

    def __init__(self, flag, onnx=False):
        super().__init__()
        self.camera = None
        self.onnx = onnx
        self.p_frame = None
        self.flag = flag
        self._isRunning = True

        if self.onnx: # Never used at the moment
            self.session = ort.InferenceSession(onnx_path)  # Load the ONNX model
        else:
            self.model = load_model()  # Load the PyTorch model
            self.model.eval()

    def set_camera(self, camera: Camera):
        self.camera = camera

    def set_flag(self, flag):
        self.flag = flag

    def update_camera(self, camera: Camera):
        # Just swap the reference; the run loop reads self.camera each iteration.
        # Toggling _isRunning here raced the loop and could kill the thread.
        self.camera = camera

    def run(self):
        self.msleep(4000)  # Sleep for 4 seconds before starting the processing loop

        while self._isRunning:
            print(f"Processing thread running... Flag: {self.flag}")
            if self.flag: # Counting mode
                frame = self.camera.get_current_frame()

                if frame is None:
                    # print("No frame available to process.")
                    self.msleep(50)  # avoid a busy loop while waiting for frames
                    continue

                # Resize frame to 224x224 if needed
                if frame.shape[:2] != (224, 224):
                    frame = cv2.resize(frame, (224, 224))

                # start = time.time()

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

                    # total = density_map.sum(dim=(1, 2, 3)).item()

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
                        # print(f'({i},{j}) count: {people_count}')

                        q_counts[i, j] = people_count
                        total_people_count += people_count

                # end = time.time()

                self.camera.set_q_counts(q_counts)

                # print(f"\nDetected people count (Total): {total}")
                # print(f"Detected people count (Grid Analysis): {total_people_count}")
                self.people_count_signal.emit(int(total_people_count))

                # print(f"\nTime taken: {end - start:.2f} sec\n\n")
            else: # Flow map mode
                frame = self.camera.get_current_frame()

                if frame is None:
                    # print("No frame available to process.")
                    self.msleep(50)  # avoid a busy loop while waiting for frames
                    continue

                # Initialize p_frame in the first iteration
                if self.p_frame is None:
                    self.p_frame = frame
                    continue

                # Ensure both frames are not None before processing
                flow_map = self.calculate_optical_flow(self.p_frame, frame)
                self.camera.draw_flow_map(flow_map, frame)

                # Update the previous frame
                self.p_frame = frame

            self.msleep(30)  # Sleep for 30 msec (30+ fps)

    def calculate_optical_flow(self, prev_frame, curr_frame):
        if prev_frame is None or curr_frame is None:
            print("[ERROR] Optical Flow: One of the frames is None. Skipping calculation.")
            return None

        # Convert to grayscale if needed
        if len(prev_frame.shape) == 3:
            prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        if len(curr_frame.shape) == 3:
            curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Ensure both frames have the same size
        if prev_frame.shape[1] != curr_frame.shape[1] and prev_frame.shape[0] != curr_frame.shape[0]:
            print(f"[WARNING] Optical Flow: Resizing frames from {curr_frame.shape} to {prev_frame.shape}")
            curr_frame = cv2.resize(curr_frame, (prev_frame.shape[1], prev_frame.shape[0]))

        # Now compute optical flow
        flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        return flow