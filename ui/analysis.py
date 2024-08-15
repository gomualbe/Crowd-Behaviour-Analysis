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

curr_dir = os.path.abspath(os.path.dirname(__file__))
main_dir = os.path.join(curr_dir, '..')
onnx_path = os.path.join(main_dir, 'onnx', 'model.onnx')

class ProcessingThread(QThread):
    people_count_signal = pyqtSignal(int)

    def __init__(self, camera, onnx=False):
        super().__init__()
        self.camera = camera
        self.onnx = onnx

        if self.onnx:
            self.session = ort.InferenceSession(onnx_path) # Load the ONNX model
        else:
            self.model = load_model() # Load the PyTorch model
            self.model.eval()


    def set_camera(self, camera):
        self.camera = camera

    def run(self):
        self.msleep(5000)  # Sleep for 5 seconds before starting the processing loop

        while True:
            frame = self.camera.get_current_frame()

            if frame is None:
                print("No frame available to process.")
                continue

            # Resize frame to 224x224 if needed
            if frame.shape[:2] != (224, 224):
                frame = cv2.resize(frame, (224, 224))

            if self.onnx:
                try:
                    input_blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0 / 255, size=(224, 224), mean=(0, 0, 0),
                                                       swapRB=True, crop=False)
                    output = self.session.run(None, {self.session.get_inputs()[0].name: input_blob})
                    people_count = np.argmax(output[0])

                    print(f"Detected people count: {people_count}")
                    self.people_count_signal.emit(int(people_count))
                except Exception as e:
                    print(f"Error during blob creation or inference: {e}")
            else:
                # Convert frame to tensor and move to the device
                frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255

                with torch.no_grad():
                    frame = frame.to(device)

                    crop_imgs, crop_masks = [], []
                    b, c, h, w = frame.size()
                    rh, rw = 224, 224
                    for i in range(0, h, rh):
                        gis, gie = max(min(h - rh, i), 0), min(h, i + rh)
                        for j in range(0, w, rw):
                            gjs, gje = max(min(w - rw, j), 0), min(w, j + rw)
                            crop_imgs.append(frame[:, :, gis:gie, gjs:gje])
                            mask = torch.zeros([b, 1, h, w]).to(device)
                            mask[:, :, gis:gie, gjs:gje].fill_(1.0)
                            crop_masks.append(mask)
                    crop_imgs, crop_masks = map(lambda x: torch.cat(x, dim=0), (crop_imgs, crop_masks))

                    crop_preds = []
                    nz, bz = crop_imgs.size(0), 8
                    for i in range(0, nz, bz):
                        gs, gt = i, min(nz, i + bz)
                        crop_pred = self.model(crop_imgs[gs:gt])

                        _, _, h1, w1 = crop_pred.size()

                        crop_pred = F.interpolate(crop_pred, size=(h1 * 8, w1 * 8), mode='bilinear',
                                                  align_corners=True) / 64

                        crop_preds.append(crop_pred)
                    crop_preds = torch.cat(crop_preds, dim=0)

                    # splice them to the original size
                    idx = 0
                    pred_map = torch.zeros([b, 1, h, w]).to(device)
                    for i in range(0, h, rh):
                        gis, gie = max(min(h - rh, i), 0), min(h, i + rh)
                        for j in range(0, w, rw):
                            gjs, gje = max(min(w - rw, j), 0), min(w, j + rw)
                            pred_map[:, :, gis:gie, gjs:gje] += crop_preds[idx]
                            idx += 1
                    # for the overlapping area, compute average value
                    mask = crop_masks.sum(dim=0).unsqueeze(0)
                    outputs = pred_map / mask
                    people_count = torch.sum(outputs).item()

                print(f"Detected people count (PyTorch): {people_count}")
                self.people_count_signal.emit(int(people_count))

            self.msleep(3000)  # Sleep for 3 seconds

class Analysis(QWidget):
    def __init__(self, width, height, links, main_window):
        super().__init__()

        self.width = width
        self.height = height

        self.main_window = main_window
        self.links = links

        self.camera = None

        # Separate thread for frame processing
        self.processing_thread = ProcessingThread(self.camera)
        self.processing_thread.people_count_signal.connect(self.main_window.update_people_count)

        self.setup_camera(self.links[0])

        self.processing_thread.start() # Start the thread

    def setup_camera(self, link):
        width = self.width - 40
        height = int(width * 9 / 16)

        self.camera = Camera(width, height, link)
        frame_video = self.camera.get_video_frame()
        frame_video.setStyleSheet('qproperty-alignment: AlignCenter;'
                                  'margin-top: 10px;')

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
