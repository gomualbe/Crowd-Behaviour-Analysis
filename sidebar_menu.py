import ui.resources_rc # Foundamental for rendering images
from ui.ui_sidebar import Ui_MainWindow
from ui.vstream_pg.ui_vstream import Ui_vstream
from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class Sidebar(QMainWindow, Ui_MainWindow):
    def __init__(self, label_width=757, label_height=450):
        super().__init__()

        self.setupUi(self)
        self.setWindowTitle("Crowd Behavior Analysis")

        # Set the first page in the stacked widget to vstream page
        self.vstream = Ui_vstream(label_width, label_height)
        self.stackedWidget.addWidget(self.vstream)
        self.dashboard_button.click() # Simulate the click - we are in the first page when we start

        # "Listeners"
        self.dashboard_button.clicked.connect(self.switch_to_firstpage)
        self.menu_button.clicked.connect(self.switch_to_secondpage)
        self.settings_button.clicked.connect(self.switch_to_thirdpage)

    def switch_to_firstpage(self):
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_secondpage(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_thirdpage(self):
        self.stackedWidget.setCurrentIndex(2)

