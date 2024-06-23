import PyQt6
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel
from ui.camera_stream.camera_widget import CameraWidget

class Sidebar(QWidget):
    def __init__(self, width, height, links, main_window):
        super().__init__()

        self.width = width
        self.height = height
        self.links = links

        self.n_links = len(self.links)
        self.cameras = []

        self.main_window = main_window
        self.scroll_area = main_window.scroll_area

        self.init_ui()

    def init_ui(self):
        self.set_stream_widgets()

        widget = QWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        for i in range(self.n_links):
            temp_widget = QWidget()

            v_box = QVBoxLayout()
            camera_frame = self.cameras[i].get_video_frame()
            camera_frame.setStyleSheet("border: 2px solid rgb(39,39,39);")
            v_box.addWidget(camera_frame)

            label = QLabel(f'Camera {i+1}')
            label.setStyleSheet('color: rgb(91,91,133);'
                                'qproperty-alignment: AlignLeft;')
            v_box.addWidget(label)

            temp_widget.setLayout(v_box)

            layout.addWidget(temp_widget)

        widget.setLayout(layout)
        self.scroll_area.setWidget(widget)
        self.scroll_area.setWidgetResizable(True)

        self.cameras[0].video_frame.setStyleSheet("border: 2px solid rgb(91,91,133);")
        
    def set_stream_widgets(self):
        """Set widgets dimensions based on number of cameras and append every camera to an array of camera widgets"""
        print('Creating camera widgets...')
        for i in range(self.n_links):
            frame_width = self.width - 40
            frame_height = int(frame_width * 9 / 16)

            camera_widget = CameraWidget(int(frame_width), int(frame_height), self.links[i])
            camera_widget.video_frame.mousePressEvent = lambda event, index=i: self.camera_clicked(index)
            # camera_widget.video_frame.mousePressEvent = lambda event, index=i: self.camera_clicked_2(index)
            camera_widget.video_frame.setStyleSheet(f'qproperty-alignment: {int(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)};')
            self.cameras.append(camera_widget)

    def camera_clicked(self, index):
        print(f'Camera no. {index+1} clicked...')

        for i in range(self.n_links):
            if i != index:
                self.cameras[i].video_frame.setStyleSheet("border: 2px solid rgb(39,39,39);")
            else:
                self.cameras[index].video_frame.setStyleSheet("border: 2px solid rgb(91,91,133);")

        self.main_window.camera_label.setText(f'Camera No.: {index+1}')
        self.main_window.change_camera(self.links[index])

    # def camera_clicked_2(self, index):
    #     print(f'Camera no. {index+1} clicked...')
    #
    #     for i in range(self.n_links):
    #         if i != index:
    #             self.cameras[i].video_frame.setStyleSheet("border: 2px solid rgb(39,39,39);")
    #         else:
    #             self.cameras[index].video_frame.setStyleSheet("border: 2px solid rgb(91,91,133);")
    #
    #     self.main_window.camera_label.setText(f'Camera No.: {index+1}')
    #     self.main_window.switch_camera(self.cameras[index].video_frame, index)