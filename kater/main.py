from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt6 import uic
import qtawesome as qta


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("kater/kater.ui", self)

        self.setContentsMargins(10, 10, 10, 10)

        # Setting buttons icons
        self.findChild(QPushButton, "startRecording").setIcon(
            qta.icon('fa.microphone'))
        self.findChild(QPushButton, "playExample").setIcon(
            qta.icon('fa.play'))
        self.findChild(QPushButton, "playUserRecord").setIcon(
            qta.icon('fa.play-circle'))
        self.findChild(QPushButton, "saveUserRecord").setIcon(
            qta.icon('fa5s.save'))
        self.findChild(QPushButton, "toggleReading").setIcon(
            qta.icon('ei.eye-open'))


def kater(file_in=None):
    app = QApplication([])
    window = UI()
    window.show()
    app.exec()
