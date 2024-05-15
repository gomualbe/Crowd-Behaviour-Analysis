from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from ui.vstream_pg.stream_thread import StreamThread

class Ui_vstream(QLabel):
    def __init__(self, width, height):
        super().__init__()

        self.vert_layout = QVBoxLayout()
        self.horiz_layout = QHBoxLayout()

        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedHeight(20)
        self.connect_button.setFixedWidth(80)
        self.connect_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) # Not expanding
        self.connect_button.setStyleSheet("color: rgb(238, 238, 238); background-color: rgb(91,91,133); "
                                          "border-radius: 10px; font-weight: bold;")

        self.quit_button = QPushButton("Quit")
        self.quit_button.setFixedHeight(20)
        self.quit_button.setFixedWidth(80)
        self.quit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Not expanding
        self.quit_button.setStyleSheet("color: rgb(238, 238, 238); background-color: rgb(91,91,133); "
                                       "border-radius: 10px; font-weight: bold;")

        self.link_lineedit = QLineEdit()
        self.link_lineedit.setFixedHeight(20)
        self.link_lineedit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) # Only Horiz. expand
        self.link_lineedit.setStyleSheet("color: rgb(238, 238, 238); background-color: rgb(39, 39, 39); "
                                         "border-radius: 10px; padding-left:10px;")

        # Put LineEdit and buttons in a Horiz. layout
        self.horiz_layout.addWidget(self.link_lineedit)
        self.horiz_layout.addWidget(self.connect_button)
        self.horiz_layout.addWidget(self.quit_button)

        # Stream Label
        self.stream_label = QLabel()
        self.stream_label.setFixedSize(width, height)
        self.stream_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.stream_label.setStyleSheet("background-color: rgb(5, 5, 5);")
        self.stream_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) # Vert. center the stream

        # Put all in a Vert. layout
        self.vert_layout.addLayout(self.horiz_layout)
        self.vert_layout.addWidget(self.stream_label)
        self.setLayout(self.vert_layout)

        # If the button has been clicked, send the link to the new class
        self.connect_button.clicked.connect(self.setStream)
        self.quit_button.clicked.connect(self.deleteStream)

    def setStream(self):
        link = ''

        if self.link_lineedit.text() == '':
            link = 'http://192.168.1.222:8080/video' # Default link (testing)
            # http://admin:admin@192.168.1.140:8081/video
        else:
            link = self.link_lineedit.text()

        self.s_thread = StreamThread(link=link)

        self.s_thread.start()
        self.s_thread.ImageUpdate.connect(self.imageUpdate)

        self.setLayout(self.vert_layout)
        self.vert_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def imageUpdate(self, image):
        self.stream_label.setPixmap(QPixmap.fromImage(image))

    def deleteStream(self):
        self.s_thread.stop()
