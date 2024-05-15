from updates import ui_update
import sidebar_menu
from PyQt6.QtWidgets import QApplication

MW_WIDTH = 1000
MW_HEIGHT = 510

if __name__ == "__main__":
    ui_update() # Check if the ui file has been modified, if so, update the py file

    app = QApplication([])
    window = sidebar_menu.Sidebar()
    window.setFixedSize(MW_WIDTH, MW_HEIGHT)
    window.show()
    app.exec()
