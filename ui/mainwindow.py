from ui.components.analysis import Analysis
from ui.components.sidebar import Sidebar
from ui.ui_mainwindow import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtCore
from ui.components.flowmap_switch import Switch
from time import sleep

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, window_width, window_height, label_width, label_height):
        super().__init__()

        self.window_width = window_width
        self.window_height = window_height
        self.label_width = label_width
        self.label_height = label_height

        self.links = []
        self.cameras = []

        self.video_label = None

        self.sidebar = None
        self.analysis = None

        self.setupUi(self)
        self.setWindowTitle("Crowd Behavior Analysis")
        self.setFixedSize(window_width, window_height)

        self.get_links()

        # Set the tooltip style
        self.setStyleSheet("""
                    QToolTip {
                        background-color: #313131;
                        color: #5b5b85;
                        border: 1px solid #272727;
                    }
                """)

        self.switch = Switch()
        self.switch.setToolTip('Switch between density map (counting) and flow map.')
        self.labels_hor_layout.insertWidget(1, self.switch, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.setup_sidebar()

    def setup_sidebar(self):
        width = self.window_width - self.label_width
        height = 665

        self.sidebar = Sidebar(width, height, self.links, self)

    def setup_analysis(self):
        width = self.label_width - 180
        height = self.label_height - 180

        self.analysis = Analysis(width, height, self, self.switch)

    def change_camera(self, camera):
        print(f"[DEBUG] Changing to camera instance: {camera}")
        self.remove_camera_frame()
        self.analysis.setup_camera(camera)
        print(f"[DEBUG] Camera changed to: {camera}")

    def remove_camera_frame(self):
        if self.video_label:
            # removeItem alone leaves the old label parented and visible, so it
            # would overlap the new one. Detach it from the layout and hide it
            # (the widget itself belongs to its Camera and must not be deleted).
            self.main_vert_layout.removeWidget(self.video_label)
            self.video_label.setParent(None)
            self.video_label = None
            print('Camera frame removed')

    def update_people_count(self, count):
        self.count_label.setText(f'Total count: {count}')

    def set_camera_frame(self, label):
        self.video_label = label
        self.main_vert_layout.addWidget(label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        print("[DEBUG] Camera frame added and UI updated")

    def get_links(self):
        try:
            with open('././camera_links.txt', 'r') as f:
                for line in f:
                    link = line.rstrip('\n')
                    self.links.append(link)
            print(f'Links: {self.links}')
        except FileNotFoundError:
            print("File not found. Please ensure the camera_links.txt file exists in the main folder.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")