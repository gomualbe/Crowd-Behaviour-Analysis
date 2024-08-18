from subprocess import call
from ui.mainwindow import MainWindow
from PyQt6.QtWidgets import QApplication
import sys
from time import sleep

# Testing imports
import os
from init_model import load_model, device
import torch
import torch.nn.functional as F
import cv2
from PyQt6.QtGui import QPixmap, QImage
import numpy as np

MW_WIDTH = 1460
MW_HEIGHT = 708
LB_WIDTH = 1236
LB_HEIGHT = 594

# http://admin:admin@192.168.1.6:8081/video
# http://192.168.1.7:8080/video

main_dir = os.path.dirname(os.path.abspath(__file__))

def qimage_to_numpy(image: QImage) -> np.ndarray:
    """Convert QImage to a NumPy array."""
    image = image.convertToFormat(QImage.Format.Format_RGB888)
    width, height = image.width(), image.height()
    ptr = image.bits()
    ptr.setsize(height * width * 3)
    arr = np.array(ptr).reshape(height, width, 3)  # Copies the data
    return arr

def test_model():
    model = load_model()
    model.eval()

    frame = QPixmap(os.path.join(main_dir, 'circa_23.jpg')) # Load a sample frame (insert your own path)
    frame = frame.toImage()  # Convert QPixmap to QImage
    frame = qimage_to_numpy(frame)  # Convert QImage to NumPy array

    # Grid analysis setup: dividing the frame into a 4x4 grid
    grid_rows, grid_cols = 4, 4
    box_height, box_width = frame.shape[0] // grid_rows, frame.shape[1] // grid_cols
    total_people_count = 0

    for i in range(grid_rows):
        for j in range(grid_cols):
            y_start, y_end = i * box_height, (i + 1) * box_height
            x_start, x_end = j * box_width, (j + 1) * box_width
            grid_section = frame[y_start:y_end, x_start:x_end]

            grid_section = cv2.resize(grid_section, (224, 224))

            grid_section_tensor = (torch.from_numpy(grid_section).permute(2, 0, 1)
                                   .unsqueeze(0).float() / 255)
            grid_section_tensor = grid_section_tensor.to(device)

            with torch.no_grad():
                crop_pred = model(grid_section_tensor)
                crop_pred = F.interpolate(crop_pred, size=(box_height, box_width), mode='bilinear',
                                          align_corners=True) / 64
                people_count = torch.sum(crop_pred).item()
                print(f'({i},{j}) count: {people_count}')

            total_people_count += int(people_count)

    print(f"Detected people count (Grid Analysis): {total_people_count}")

if __name__ == "__main__":
    # call("pyuic6 ui/mainwindow.ui -o ui/ui_mainwindow.py", shell=True)

    app = QApplication([])

    # test_model()

    window = MainWindow(MW_WIDTH, MW_HEIGHT, LB_WIDTH, LB_HEIGHT)

    sleep(3)
    window.show()
    sys.exit(app.exec())
