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

    frame = QPixmap(os.path.join(main_dir, 'images', 'IMG_5.jpg')) # Load a sample frame (insert your own path)
    frame = frame.toImage()  # Convert QPixmap to QImage
    frame = qimage_to_numpy(frame)  # Convert QImage to NumPy array

    # Resize frame to 224x224 if needed
    if frame.shape[:2] != (224, 224):
        frame = cv2.resize(frame, (224, 224))

    # Convert frame to tensor and move to the device
    frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255

    with torch.no_grad():
        frame = frame.to(device)
        density_map = model(frame)
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

            total_people_count += people_count

    print(f"\nDetected people count (Total): {total}")
    print(f"Detected people count (Grid Analysis): {total_people_count}")

if __name__ == "__main__":
    # call("pyuic6 ui/mainwindow.ui -o ui/ui_mainwindow.py", shell=True)

    app = QApplication([])

    # test_model()

    window = MainWindow(MW_WIDTH, MW_HEIGHT, LB_WIDTH, LB_HEIGHT)

    sleep(3)
    window.show()
    sys.exit(app.exec())
