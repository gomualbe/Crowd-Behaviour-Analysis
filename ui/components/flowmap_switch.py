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

    def emit_toggled_signal(self):
        # Emit the actual state; inverting it made the switch behave backwards.
        self.toggled.emit(self.isChecked())
