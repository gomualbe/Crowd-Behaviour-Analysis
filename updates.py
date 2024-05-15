import os
import platform
from subprocess import call, run

def ui_update():
    sidebar_ui = "ui/sidebar.ui"
    sidebar_py = "ui/ui_sidebar.py"
    resources_qrc = "ui/resources.qrc"
    resources_rc = "ui/resources_rc.py"
    # vstream_ui = "ui/vstream_pg/vstream.ui"
    # vstream_py = "ui/vstream_pg/ui_vstream.py"

    if platform.system() == "Windows":  # Update in Windows systems
        run(["powershell", "-Command", "pyside6-rcc ui\\resources.qrc | ForEach-Object { $_ -replace 'PySide6', 'PyQt6' } | Set-Content ui\\resources_rc.py"])
        # call("pyside6-rcc ui\\resources.qrc | ForEach-Object { $_ -replace 'PySide6', 'PyQt6' } | Set-Content ui\\resources_rc.py", shell=True)
    else:  # Update in Linux or macOS systems
        call("pyside6-rcc ui/resources.qrc | sed 's#PySide6#PyQt6#g' > ui/resources_rc.py", shell=True)

    # call("pyqt6-uic ui/sidebar.ui -o ui/ui_sidebar.py", shell=True)
    call("pyuic6 ui/sidebar.ui -o ui/ui_sidebar.py", shell=True)
    # call("pyuic6 ui/vstream_pg/vstream.ui -o ui/vstream_pg/ui_vstream.py", shell=True)

