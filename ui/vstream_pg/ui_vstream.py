import PyQt6
from PyQt6.QtWidgets import QLabel, QGridLayout
from ui.vstream_pg.camera_widget import CameraWidget

class Ui_vstream(QLabel):
    def __init__(self, width, height):
        super().__init__()

        self.link = ''
        self.links = []
        self.n_links = 0
        self.cameras = []

        self.width = width
        self.height = height

        self.ml = QGridLayout()
        self.set_stream()

    def set_stream(self):
        self.get_links()
        self.set_widgets()

        print('Adding widgets to layout...')
        for i in range(self.n_links):
            row = i // 2
            col = i % 2
            print(f'Adding camera number [{i}] to layout at row {row}, column {col}...')
            self.ml.addWidget(self.cameras[i].get_video_frame(), row, col)

        print('Setting layout...')
        self.setLayout(self.ml)

    def get_links(self):
        """Get camera links from the txt file in the main folder"""
        try:
            with open('././camera_links.txt', 'r') as f:
                for line in f:
                    link = line.rstrip('\n')
                    self.links.append(link)
                    print(f'Type of link[{self.n_links}]:', type(self.links[self.n_links]))  # 'str'
                    self.n_links += 1
            print(f'Number of links: {self.n_links}')
            print(f'Links: {self.links}')
        except FileNotFoundError:
            print("File not found. Please ensure the camera_links.txt file exists in the main folder.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")

    def set_widgets(self):
        """Set widgets dimensions based on number of cameras and append every camera to the layout"""
        print('Creating camera widgets...')
        for i in range(self.n_links):
            print('Connecting to camera number: ', i)

            num_cols = 2
            num_rows = (self.n_links + num_cols - 1) // num_cols

            frame_width = self.width // num_cols
            frame_height = frame_width * 9 / 16

            if frame_height * num_rows > self.height:
                frame_height = self.height // num_rows
                frame_width = frame_height * 16 / 9

            camera_widget = CameraWidget(int(frame_width), int(frame_height), self.links[i])
            camera_widget.video_frame.mousePressEvent = lambda event, index=i: self.video_clicked(index)
            camera_widget.video_frame.setStyleSheet(f'qproperty-alignment: {int(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)};')
            self.cameras.append(camera_widget)

    def video_clicked(self, index):
        print(f'Video no. {index} clicked...')

        for i in range(self.n_links):
            if i != index:
                self.cameras[i].video_frame.setStyleSheet("border: 2px solid rgb(49,49,49);")
            else:
                self.cameras[index].video_frame.setStyleSheet("border: 2px solid rgb(91,91,133);")
