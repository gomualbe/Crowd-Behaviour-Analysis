from ui.analysis import Analysis
from ui.sidebar import Sidebar
from ui.ui_mainwindow import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtCore


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

        self.setup_sidebar()
        self.setup_analysis()

    def setup_sidebar(self):
        width = self.window_width - self.label_width
        height = 665

        self.sidebar = Sidebar(width, height, self.links, self)

    def setup_analysis(self):
        width = self.label_width - 180
        height = self.label_height - 180

        self.main_view.setStyleSheet("""
            QVBoxLayout {
                background-color: rgb(169, 169, 69);
            }
        """)#count_vert_layout

        self.analysis = Analysis(width, height, self.links, self)

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

    def update_q_count(self, i, j, count):
        if i == 0 and j == 0:
            print(f'Q1 count: {count}')
            self.count_q1.setText(f'Q1 count: {int(count)}')
        elif i == 0 and j == 1:
            print(f'Q2 count: {count}')
            self.count_q2.setText(f'Q2 count: {int(count)}')
        elif i == 0 and j == 2:
            print(f'Q3 count: {count}')
            self.count_q3.setText(f'Q3 count: {int(count)}')
        elif i == 0 and j == 3:
            print(f'Q4 count: {count}')
            self.count_q4.setText(f'Q4 count: {int(count)}')
        elif i == 1 and j == 0:
            print(f'Q5 count: {count}')
            self.count_q5.setText(f'Q5 count: {int(count)}')
        elif i == 1 and j == 1:
            print(f'Q6 count: {count}')
            self.count_q6.setText(f'Q6 count: {int(count)}')
        elif i == 1 and j == 2:
            print(f'Q7 count: {count}')
            self.count_q7.setText(f'Q7 count: {int(count)}')
        elif i == 1 and j == 3:
            print(f'Q8 count: {count}')
            self.count_q8.setText(f'Q8 count: {int(count)}')
        elif i == 2 and j == 0:
            print(f'Q9 count: {count}')
            self.count_q9.setText(f'Q9 count: {int(count)}')
        elif i == 2 and j == 1:
            print(f'Q10 count: {count}')
            self.count_q10.setText(f'Q10 count: {int(count)}')
        elif i == 2 and j == 2:
            print(f'Q11 count: {count}')
            self.count_q11.setText(f'Q11 count: {int(count)}')
        elif i == 2 and j == 3:
            print(f'Q12 count: {count}')
            self.count_q12.setText(f'Q12 count: {int(count)}')
        elif i == 3 and j == 0:
            print(f'Q13 count: {count}')
            self.count_q13.setText(f'Q13 count: {int(count)}')
        elif i == 3 and j == 1:
            print(f'Q14 count: {count}')
            self.count_q14.setText(f'Q14 count: {int(count)}')
        elif i == 3 and j == 2:
            print(f'Q15 count: {count}')
            self.count_q15.setText(f'Q15 count: {int(count)}')
        elif i == 3 and j == 3:
            print(f'Q16 count: {count}')
            self.count_q16.setText(f'Q16 count: {int(count)}')

    def update_people_count(self, count):
        self.count_label.setText(f'Count: {count}')

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
