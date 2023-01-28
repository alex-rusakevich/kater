from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt6 import uic
import qtawesome as qta


class UI(QMainWindow):
    def toggleReading(self, event=None, desired_state=None):
        btn = self.toggleReadingBtn

        if desired_state == None:
            state = btn.property("is_reading_shown")

            btn.setProperty("is_reading_shown",
                            not state)
        else:
            btn.setProperty("is_reading_shown", desired_state)

        if btn.property("is_reading_shown"):
            btn.setIcon(qta.icon('ei.eye-open'))
        else:
            btn.setIcon(qta.icon('ei.eye-close'))

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

        self.toggleReading(desired_state=True)
        self.toggleReadingBtn.clicked.connect(self.toggleReading)


def kater(file_in=None):
    app = QApplication([])
    window = UI()
    window.show()
    app.exec()
