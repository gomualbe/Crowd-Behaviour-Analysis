import ui.resources_rc # foundamental for rendering images
from ui.ui_sidebar import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton

class Sidebar(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowTitle("Crowd Behavior Analysis")
        self.icon_only_widget.hide() # Hide the icon only widget sidebar

        self.dashboard_1.clicked.connect(self.switch_to_firstpage)
        self.dashboard_2.clicked.connect(self.switch_to_secondpage)

        self.menu_1.clicked.connect(self.switch_to_secondpage)
        self.menu_2.clicked.connect(self.switch_to_thirdpage)

        self.settings_1.clicked.connect(self.switch_to_thirdpage)
        self.settings_2.clicked.connect(self.switch_to_firstpage)

    def switch_to_firstpage(self):
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_secondpage(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_thirdpage(self):
        self.stackedWidget.setCurrentIndex(2)

