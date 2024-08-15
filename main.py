from subprocess import call
from ui.mainwindow import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

MW_WIDTH = 1280
MW_HEIGHT = 708
LB_WIDTH = 1056
LB_HEIGHT = 594

# http://admin:admin@192.168.1.140:8081/video
# https://192.168.1.222:8080/video

if __name__ == "__main__":
    # call("pyuic6 ui/mainwindow.ui -o ui/ui_mainwindow.py", shell=True)

    app = QApplication([])
    window = MainWindow(MW_WIDTH, MW_HEIGHT, LB_WIDTH, LB_HEIGHT)
    window.show()
    sys.exit(app.exec())
