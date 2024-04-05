import os
import platform
from subprocess import call

def ui_update():
    sidebar_ui = "ui/sidebar.ui"
    sidebar_py = "ui/ui_sidebar.py"
    resources_qrc = "ui/resources.qrc"
    resources_rc = "ui/resources_rc.py"

    # Checks the last modification date of the files
    ui_modified = os.path.getmtime(sidebar_ui)
    py_modified = os.path.getmtime(sidebar_py) if os.path.exists(sidebar_py) else 0
    qrc_modified = os.path.getmtime(resources_qrc)
    rc_modified = os.path.getmtime(resources_rc) if os.path.exists(resources_rc) else 0

    # Updates files if the ui file is newer than the py file
    if ui_modified > py_modified or qrc_modified > rc_modified:
        if platform.system() == "Windows": # Update in Windows systems
            call("pyside6-rcc ui\\resources.qrc | ForEach-Object { $_ -replace 'PySide6', 'PyQt6' } | Set-Content ui\\resources_rc.py", shell=True)
        else: # Update in Linux or macOS systems
            call("pyside6-rcc ui/resources.qrc | sed 's#PySide6#PyQt6#g' > ui/resources_rc.py", shell=True)

        call("pyqt6-uic ui/sidebar.ui -o ui/ui_sidebar.py", shell=True)
