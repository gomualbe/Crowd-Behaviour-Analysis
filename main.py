from ui.mainwindow import MainWindow
from PyQt6.QtWidgets import QApplication
import sys
from time import sleep

MW_WIDTH = 1326
MW_HEIGHT = 708
LB_WIDTH = 1236
LB_HEIGHT = 594

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow(MW_WIDTH, MW_HEIGHT, LB_WIDTH, LB_HEIGHT)
    sleep(1)
    window.show()
    sys.exit(app.exec())