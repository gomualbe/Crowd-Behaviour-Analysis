from ui.analysis import Analysis
from ui.sidebar import Sidebar
from ui.ui_mainwindow import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, window_width, window_height, label_width, label_height):
        super().__init__()

        self.window_width = window_width
        self.window_height = window_height
        self.label_width = label_width
        self.label_height = label_height

        self.links = []
        self.cameras = []

        self.widget = None

        self.sidebar = None
        self.analysis = None

        self.setupUi(self)
        self.setWindowTitle("Crowd Behavior Analysis")
        self.setFixedSize(window_width, window_height)

        self.get_links()
        self.setup_sidebar()
        self.setup_analysis()

    def setup_sidebar(self):
        width = self.window_width - self.label_width
        height = 665

        self.sidebar = Sidebar(width, height, self.links, self)

    def setup_analysis(self):
        width = self.label_width
        height = self.label_height

        self.analysis = Analysis(width, height, self.links, self)

    def set_camera_frame(self, widget):
        self.main_vert_layout.addWidget(widget)
        self.widget = widget

    def change_camera(self, link):
        self.main_vert_layout.removeWidget(self.widget)
        self.main_vert_layout.addWidget(self.analysis.update_camera(link))

    def get_links(self):
        """Get camera links from the txt file in the main folder"""
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