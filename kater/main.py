from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt6 import uic
import qtawesome as qta
from kater.resources import Ktr_Object, load_global_ktr_obj, get_global_ktr_obj, get_tmp_dir
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtCore import QUrl


class UI(QMainWindow):
    def toggleReading(self, event=None, desired_state=None):
        btn = self.toggleReadingBtn

        if desired_state == None:
            state = btn.property("is_reading_shown")

            btn.setProperty("is_reading_shown", not state)
        else:
            btn.setProperty("is_reading_shown", desired_state)

        if btn.property("is_reading_shown"):
            btn.setIcon(qta.icon('ei.eye-open'))
        else:
            btn.setIcon(qta.icon('ei.eye-close'))

    def toggleRecording(self, event=None, desired_state=None):
        btn = self.startRecording

        if desired_state == None:
            state = btn.property("is_recording")

            btn.setProperty("is_recording", not state)
        else:
            btn.setProperty("is_recording", desired_state)

        if btn.property("is_recording"):
            btn.setText("Stop")
            btn.setIcon(qta.icon('fa.microphone-slash'))
        else:
            btn.setText("Start")
            btn.setIcon(qta.icon('fa.microphone'))

    def toggleExamplePlay(self, event=None, desired_state=None):
        btn = self.playExample

        if desired_state == None:
            state = btn.property("is_playing")
            btn.setProperty("is_playing", not state)
        else:
            btn.setProperty("is_playing", desired_state)

        if btn.property("is_playing"):
            btn.setText("Pause the example")
            btn.setIcon(qta.icon('fa.pause-circle'))

            if hasattr(self, "player"):
                self.player.play()
        else:
            btn.setText("Play the example")
            btn.setIcon(qta.icon('fa.play-circle'))

            if hasattr(self, "player"):
                self.player.pause()

    def __init__(self):
        super().__init__()
        uic.loadUi("kater/kater.ui", self)

        self.setContentsMargins(10, 10, 10, 10)

        # Setting buttons icons
        self.findChild(QPushButton, "playUserRecord").setIcon(
            qta.icon('fa.play-circle'))
        self.findChild(QPushButton, "saveUserRecord").setIcon(
            qta.icon('fa5s.save'))

        self.findChild(QPushButton, "resetUserRecord").setIcon(
            qta.icon('fa.stop'))

        self.toggleRecording(desired_state=False)
        self.startRecording.clicked.connect(self.toggleRecording)

        # Setting top icons

        self.findChild(QPushButton, "resetExample").setIcon(
            qta.icon('fa.stop'))

        self.findChild(QPushButton, "resetAll").setIcon(
            qta.icon('mdi.reload'))

        self.toggleExamplePlay(desired_state=False)
        self.playExample.clicked.connect(self.toggleExamplePlay)

        self.toggleReading(desired_state=True)
        self.toggleReadingBtn.clicked.connect(self.toggleReading)

    def closeEvent(self, event):
        get_tmp_dir().cleanup()

    def use_global_object(self):
        def example_media_status_changed(status):
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                btn = self.playExample
                btn.setProperty("is_playing", False)
                btn.setText("Play the example")
                btn.setIcon(qta.icon('fa.play-circle'))
                self.player.stop()

        ktr_obj = get_global_ktr_obj()
        self.readingText.setText(ktr_obj.text)

        player = QMediaPlayer()
        audio_output = QAudioOutput()
        player.setAudioOutput(audio_output)

        audio_file_path = str(get_tmp_dir().name) + \
            f"/audio{ktr_obj.audio['ext']}"
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(ktr_obj.audio["bin"])

        player.setSource(QUrl.fromLocalFile(audio_file_path))
        audio_output.setVolume(100)
        self.player = player
        self.audio_output = audio_output

        self.player.mediaStatusChanged.connect(example_media_status_changed)

        self.reading = ktr_obj.reading


def kater(file_in=None):
    app = QApplication([])

    window = UI()
    window.show()

    if file_in:
        load_global_ktr_obj(file_in)
        window.use_global_object()

    app.exec()
