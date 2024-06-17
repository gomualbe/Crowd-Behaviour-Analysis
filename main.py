from updates import ui_update
import sidebar_menu
from PyQt6.QtWidgets import QApplication

MW_WIDTH = 1280
MW_HEIGHT = 720

# http://admin:admin@192.168.1.140:8081/video
# https://192.168.1.10:8080/video

if __name__ == "__main__":
    ui_update() # Check if the ui file has been modified, if so, update

    app = QApplication([])
    window = sidebar_menu.Sidebar()
    window.setFixedSize(MW_WIDTH, MW_HEIGHT)
    window.show()
    app.exec()
