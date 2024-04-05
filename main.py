from updates import ui_update
import sidebar_menu
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    ui_update() # Check if the ui file has been modified, if so, update the py file

    app = QApplication([])
    window = sidebar_menu.Sidebar()
    window.show()
    app.exec()
