import PyQt6
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from ui.camera_stream.camera import Camera

class Analysis(QWidget):
    def __init__(self, width, height, links, main_window):
        super().__init__()

        self.width = width
        self.height = height

        self.main_window = main_window
        self.links = links

        self.camera = None
        self.widget = None

        self.setup_camera(self.links[0])

    def setup_camera(self, link):
        width = self.width - 30
        height = width * 9 / 16

        self.camera = Camera(width, int(height), link)
        frame = self.camera.get_video_frame()
        frame.setStyleSheet('margin-bottom: 60;')

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(frame)
        self.widget.setLayout(layout)

        self.main_window.set_camera_frame(self.widget)

    def update_camera(self, link):
        self.camera.capture.release()
        self.camera.deleteLater()

        self.setup_camera(link)

    # def update_camera(self, camera):
    #     self.all.removeWidget(self.stream)
    #
    #     self.stream = camera
    #     self.stream.setStyleSheet(f'qproperty-alignment: {int(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)};')
    #     self.all.addWidget(self.stream)