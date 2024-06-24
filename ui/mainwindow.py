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

        self.video_label = None

        self.sidebar = None
        self.analysis = None

        self.setupUi(self)
        self.setWindowTitle("Crowd Behavior Analysis")
        self.setFixedSize(window_width, window_height)

        self.get_links()

        # self.setup_sidebar_test()
        # self.setup_analysis_test()

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

    # def setup_sidebar_test(self):
    #     print('Into setup_sidebar_test')
    #     widget = QWidget()
    #     layout = QVBoxLayout(self)
    #     layout.setContentsMargins(0, 2, 0, 2)
    #
    #     for i in range(5):
    #         print(f'Camera frame {i+1}')
    #         temp_widget = QWidget()
    #
    #         v_box = QVBoxLayout()
    #         camera_frame = QLabel('Camera Frame')
    #
    #         frame_width = self.label_width - 40
    #         frame_height = int(frame_width * 9 / 16)
    #
    #         camera_frame.setFixedSize(frame_width, frame_height)
    #         camera_frame.mousePressEvent = lambda event, index=i: self.change_test()
    #
    #         if i != 0:
    #             camera_frame.setStyleSheet("border: 2px solid rgb(39,39,39);")
    #         else:
    #             camera_frame.setStyleSheet("border: 2px solid rgb(91,91,133);")
    #
    #         v_box.addWidget(camera_frame)
    #
    #         label = QLabel(f'Camera {i + 1}')
    #         label.setStyleSheet('color: rgb(91,91,133);'
    #                             'qproperty-alignment: AlignLeft;')
    #         v_box.addWidget(label)
    #
    #         temp_widget.setLayout(v_box)
    #
    #         layout.addWidget(temp_widget)
    #
    #     widget.setLayout(layout)
    #     self.scroll_area.setWidget(widget)
    #     self.scroll_area.setWidgetResizable(True)

    # def setup_analysis_test(self):
    #     print('Into setup_analysis_test')
    #     label = QLabel('Test Label No. 0')
    #     label.setFixedSize(self.label_width - 30, int((self.label_width - 30) * 9 / 16))
    #     label.setStyleSheet('margin-bottom: 65px;'
    #                         'margin-left: 12px;')
    #     self.main_vert_layout.addWidget(label)

    def set_camera_frame(self, label):
        print("label size: " + str(label.size()))
        self.video_label = label
        self.main_vert_layout.addWidget(label)
        print('Camera frame added')

    def change_camera(self, link):
        self.analysis.update_camera(link)

    # def change_test(self):
    #     print('Into change_test')
    #     item = self.main_vert_layout.itemAt(self.main_vert_layout.count()-1)
    #     self.main_vert_layout.removeWidget(item.widget())
    #
    #     new_label = QLabel(f'Test Label No. {self.contatore}')
    #     new_label.setFixedSize(self.label_width - 30, int((self.label_width - 30) * 9 / 16))
    #     new_label.setStyleSheet('margin-bottom: 65px;'
    #                             'margin-left: 12px;')
    #
    #     self.main_vert_layout.addWidget(new_label)
    #     self.contatore += 1

    def remove_camera_frame(self):
        if self.video_label:
            item = self.main_vert_layout.itemAt(self.main_vert_layout.count() - 1)

            if item:
                self.main_vert_layout.removeItem(item)
                self.video_label = None
                print('Camera frame removed')

    # def switch_camera(self, video_frame, index):
    #     if self.video_label:
    #         item = self.main_vert_layout.itemAt(self.main_vert_layout.count() - 1)
    #
    #         if item:
    #             self.main_vert_layout.removeItem(item)
    #             self.video_label = video_frame
    #             print('Camera frame removed')
    #
    #
    #         (self.sidebar.scroll_area.widget().layout().itemAt(self.current_index).widget().layout().itemAt(0)
    #             .widget().setStyleSheet("border: 2px solid rgb(39,39,39);"))
    #         self.current_index = index

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
