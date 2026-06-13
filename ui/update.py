from subprocess import call

if __name__ == "__main__":
    call("pyuic6 ui/mainwindow.ui -o ui/ui_mainwindow.py", shell=True)