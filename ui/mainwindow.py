from ui.analysis import Analysis
from ui.sidebar import Sidebar
from ui.ui_mainwindow import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSlot, QSize, QPointF
from PyQt6.QtGui import QLinearGradient, QGradient, QPainter, QColor, QPalette
from PyQt6.QtWidgets import QAbstractButton
from PyQt6.QtCore import Qt, pyqtSignal

class SwitchPrivate(QObject):
    def __init__(self, q, parent=None):
        super().__init__(parent=parent)
        self.mPointer = q
        self.mPosition = 0.0
        self.mGradient = QLinearGradient()
        self.mGradient.setSpread(QGradient.Spread.PadSpread)

        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b'position')
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(200)

        self.animation.setEasingCurve(QEasingCurve.Type.InOutExpo)
        self.animation.finished.connect(self.mPointer.update)

    @pyqtProperty(float)
    def position(self):
        return self.mPosition

    @position.setter
    def position(self, value):
        self.mPosition = value
        self.mPointer.update()

    def draw(self, painter):
        r = self.mPointer.rect()
        margin = int(r.height() / 12)

        # Use QPalette.ColorRole to get colors
        shadow = self.mPointer.palette().color(QPalette.ColorRole.Dark)
        light = self.mPointer.palette().color(QPalette.ColorRole.Light)
        button_on = QColor('#5b5b85')
        button_off = self.mPointer.palette().color(QPalette.ColorRole.Button)

        painter.setPen(Qt.PenStyle.NoPen)

        self.mGradient.setColorAt(0, shadow.darker(130))
        self.mGradient.setColorAt(1, light.darker(130))
        self.mGradient.setStart(0, r.height())
        self.mGradient.setFinalStop(0, 0)
        painter.setBrush(self.mGradient)
        painter.drawRoundedRect(r, r.height() / 2, r.height() / 2)

        self.mGradient.setColorAt(0, shadow.darker(140))
        self.mGradient.setColorAt(1, light.darker(160))
        self.mGradient.setStart(0, 0)
        self.mGradient.setFinalStop(0, r.height())
        painter.setBrush(self.mGradient)
        painter.drawRoundedRect(r.adjusted(margin, margin, -margin, -margin), r.height() / 2, r.height() / 2)

        # Change button color depending on the state
        if self.mPointer.isChecked():
            button_color = button_on
        else:
            button_color = button_off

        self.mGradient.setColorAt(0, button_color.darker(130))
        self.mGradient.setColorAt(1, button_color)

        painter.setBrush(self.mGradient)

        x = r.height() / 2.0 + self.mPosition * (r.width() - r.height())
        painter.drawEllipse(QPointF(x, r.height() / 2), r.height() / 2 - margin, r.height() / 2 - margin)

    @pyqtSlot(bool, name='animate')
    def animate(self, checked):
        self.animation.setDirection(
            QPropertyAnimation.Direction.Forward if checked else QPropertyAnimation.Direction.Backward)
        self.animation.start()


class Switch(QAbstractButton):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.dPtr = SwitchPrivate(self)
        self.setCheckable(True)
        self.clicked.connect(self.dPtr.animate)
        self.clicked.connect(self.emit_toggled_signal)

    def sizeHint(self):
        return QSize(45, 22)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.dPtr.draw(painter)

    def resizeEvent(self, event):
        self.update()

    def emit_toggled_signal(self, checked):
        self.toggled.emit(checked)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, window_width, window_height, label_width, label_height):
        super().__init__()

        self.window_width = window_width
        self.window_height = window_height
        self.label_width = label_width
        self.label_height = label_height

        self.links = []
        self.cameras = []

        self.video_label = None

        self.sidebar = None
        self.analysis = None

        self.setupUi(self)
        self.setWindowTitle("Crowd Behavior Analysis")
        self.setFixedSize(window_width, window_height)

        self.get_links()

        self.setStyleSheet("""
                    QToolTip {
                        background-color: #313131;
                        color: #5b5b85;
                        border: 1px solid #272727;
                    }
                """)

        self.switch = Switch()
        self.switch.setToolTip('Switch between density map and flow map.')
        self.count_vert_layout.insertWidget(1, self.switch, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.setup_sidebar()
        self.setup_analysis()

    def setup_sidebar(self):
        width = self.window_width - self.label_width
        height = 665

        self.sidebar = Sidebar(width, height, self.links, self)

    def setup_analysis(self):
        width = self.label_width - 180
        height = self.label_height - 180

        self.analysis = Analysis(width, height, self.links, self, self.switch)

    def set_camera_frame(self, label):
        print("Label size: " + str(label.size()))
        self.video_label = label
        self.main_vert_layout.addWidget(label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        print('Camera frame added')

    def change_camera(self, link):
        self.analysis.update_camera(link)

    def remove_camera_frame(self):
        if self.video_label:
            item = self.main_vert_layout.itemAt(self.main_vert_layout.count() - 1)

            if item:
                self.main_vert_layout.removeItem(item)
                self.video_label = None
                print('Camera frame removed')

    def update_people_count(self, count):
        self.count_label.setText(f'Total count: {count}')

    def get_links(self):
        try:
            with open('././camera_links.txt', 'r') as f:
                for line in f:
                    link = line.rstrip('\n')
                    self.links.append(link)
            print(f'Links: {self.links}')
        except FileNotFoundError:
            print("File not found. Please ensure the camera_links.txt file exists in the main folder.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
