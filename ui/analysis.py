from PyQt6.QtWidgets import QWidget
from ui.camera_stream.camera import Camera

class Analysis(QWidget):
    def __init__(self, width, height, links, main_window):
        super().__init__()

        self.width = width
        self.height = height

        self.main_window = main_window
        self.links = links

        self.camera = None

        self.setup_camera(self.links[0])

    def setup_camera(self, link):
        width = self.width - 40
        height = int(width * 9 / 16)

        self.camera = Camera(width, height, link)
        frame = self.camera.get_video_frame()
        frame.setStyleSheet('qproperty-alignment: AlignCenter;'
                            'margin-top: 10px;')

        print('Camera frame taken')
        self.main_window.set_camera_frame(frame)

    def update_camera(self, link):
        if self.camera:
            print('Deleting stream...')
            self.camera.delete_stream()

        print('Updating camera...')
        self.main_window.remove_camera_frame()
        self.setup_camera(link)