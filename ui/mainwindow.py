from ui.components.analysis import Analysis
from ui.components.sidebar import Sidebar
from ui.ui_mainwindow import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtCore
from ui.components.flowmap_switch import Switch

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

        self.setStyleSheet("""
                    QToolTip {
                        background-color: #313131;
                        color: #5b5b85;
                        border: 1px solid #272727;
                    }
                """)

        self.switch = Switch()
        self.switch.setToolTip('Switch between density map (counting) and flow map.')
        self.count_vert_layout.insertWidget(1, self.switch, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.setup_sidebar()
        self.setup_analysis()

    def setup_sidebar(self):
        width = self.window_width - self.label_width
        height = 665

        self.sidebar = Sidebar(width, height, self.links, self)

    def setup_analysis(self):
        width = self.label_width - 180
        height = self.label_height - 180

        self.analysis = Analysis(width, height, self.links, self, self.switch)

    def set_camera_frame(self, label):
        print("Label size: " + str(label.size()))
        self.video_label = label
        self.main_vert_layout.addWidget(label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        print('Camera frame added')

    def change_camera(self, link):
        self.analysis.update_camera(link)

    def remove_camera_frame(self):
        if self.video_label:
            item = self.main_vert_layout.itemAt(self.main_vert_layout.count() - 1)

            if item:
                self.main_vert_layout.removeItem(item)
                self.video_label = None
                print('Camera frame removed')

    def update_people_count(self, count):
        self.count_label.setText(f'Total count: {count}')

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
