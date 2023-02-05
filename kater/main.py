from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
from PyQt6 import uic, QtGui
import qtawesome as qta
from kater.resources import Ktr_Object, load_global_ktr_obj, get_global_ktr_obj, get_tmp_dir, load_vosk_model, audio_to_text
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtTest import QTest
import math
import sys
import os.path
import os
from kater.recorder import start_recording, stop_recording, OUTPUT_FILE_NAME, init_recorder
from kater.compare import *
import json
import re
import statistics
from kater.util import show_log


class UI(QMainWindow):
    def toggleReading(self, event=None, desired_state=None):
        btn = self.toggleReadingBtn

        if desired_state == None:
            state = btn.property("is_reading_shown")

            btn.setProperty("is_reading_shown", not state)
        else:
            btn.setProperty("is_reading_shown", desired_state)

        if not btn.property("is_reading_shown"):
            btn.setIcon(qta.icon('ei.eye-open'))
            if hasattr(self, "text"):
                self.readingText.setText(self.text)
        else:
            btn.setIcon(qta.icon('ei.eye-close'))
            if hasattr(self, "reading") and hasattr(self, "text"):
                self.readingText.setText(self.text + "\n" + self.reading)

    def toggleRecording(self, event=None, desired_state=None):
        btn = self.startRecordingBtn

        if desired_state == None:
            state = btn.property("is_recording")

            btn.setProperty("is_recording", not state)
        else:
            btn.setProperty("is_recording", desired_state)

        if btn.property("is_recording"):
            btn.setText("Stop")
            btn.setIcon(qta.icon('fa.microphone-slash'))
            btn.setStyleSheet(
                "background-color: palette(highlight); color: palette(bright-text);")

            start_recording()
        else:
            btn.setText("Start")
            btn.setIcon(qta.icon('fa.microphone'))
            btn.setStyleSheet(
                "background-color: palette(button); color: palette(button-text);")

            if record_path := stop_recording():  # Go to result processing
                vosk_result = re.sub(
                    r"(?<=\d),(?=\d+)", ".", audio_to_text(record_path))

                vosk_result = json.loads(vosk_result)

                # Calc text confidence
                confs = []

                if "result" not in vosk_result.keys():
                    return

                for res in vosk_result["result"]:
                    confs.append(res["conf"])
                confidence = statistics.mean(confs)

                result = calc_total_result([
                    test_reading_levenstein(
                        self.lang, self.reading, vosk_result["text"], confidence),
                ])

                self.resultLabel.setText(self.resultLabel.orig_text.replace(
                    "...", str(round(result.result * 100))))
                self.resultLabel.mark_log = result.log

                self.fullResultTitle = result.name
                self.fullResultMessage = result.log

                self.showFullResultBtn.setEnabled(True)
                self.resetAllBtn.setEnabled(True)
                self.startRecordingBtn.setEnabled(False)

    def togglePlay(self, event=None, desired_state=None):
        btn = self.playBtn

        if desired_state == None:
            state = btn.property("is_playing")
            btn.setProperty("is_playing", not state)
        else:
            btn.setProperty("is_playing", desired_state)

        if btn.property("is_playing"):
            btn.setText("Pause")
            btn.setIcon(qta.icon('fa.pause-circle'))

            if hasattr(self, "player"):
                self.player.play()
        else:
            btn.setText("Play")
            btn.setIcon(qta.icon('fa.play-circle'))

            if hasattr(self, "player"):
                self.player.pause()

    def showResultMessage(self):
        if self.fullResultMessage == "" or self.fullResultTitle == "":
            return None

        show_log(self.fullResultTitle, self.fullResultMessage)

    def reset_all(self):
        self.showFullResultBtn.setEnabled(False)
        self.fullResultMessage = ""
        self.fullResultTitle = ""
        self.startRecordingBtn.setEnabled(True)
        self.resultLabel.setText(self.resultLabel.orig_text)
        self.resetAllBtn.setEnabled(False)

    def __init__(self):
        super().__init__()
        uic.loadUi("kater/ui/kater.ui", self)

        # Downloaded from https://www.flaticon.com/free-icon/speedboat_2012527?term=speedboat&page=1&position=94&origin=tag&related_id=2012527
        self.setWindowIcon(QtGui.QIcon("./icon.png"))

        self.setContentsMargins(10, 10, 10, 10)

        # Setting buttons icons
        self.findChild(QPushButton, "playBtn").setIcon(
            qta.icon('fa.play-circle'))

        self.findChild(QPushButton, "stopBtn").setIcon(
            qta.icon('fa.stop-circle'))

        self.fullResultTitle = ""
        self.fullResultMessage = ""
        self.showFullResultBtn.clicked.connect(self.showResultMessage)
        self.showFullResultBtn.setIcon(qta.icon('fa.question-circle'))
        self.showFullResultBtn.setEnabled(False)

        self.resetAllBtn.setIcon(qta.icon('fa.refresh'))
        self.resetAllBtn.clicked.connect(self.reset_all)
        self.resetAllBtn.setEnabled(False)

        self.toggleRecording(desired_state=False)
        self.startRecordingBtn.clicked.connect(self.toggleRecording)
        self.startRecordingBtn_shortcut = QShortcut(
            QKeySequence("SPACE"), self)
        self.startRecordingBtn_shortcut.activated.connect(
            lambda: QTest.mouseClick(self.startRecordingBtn, Qt.LeftButton))

        self.resultLabel.orig_text = self.resultLabel.text()

        self.togglePlay(desired_state=False)
        self.playBtn.clicked.connect(self.togglePlay)

        self.toggleReadingBtn.clicked.connect(self.toggleReading)

        def stop_btn_clicked(status):
            if hasattr(self, "player"):
                self.togglePlay(desired_state=False)
                self.player.stop()
        self.stopBtn.clicked.connect(stop_btn_clicked)

    def use_global_object(self):
        def example_media_status_changed(status):
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                btn = self.playBtn
                btn.setProperty("is_playing", False)
                btn.setText("Play")
                btn.setIcon(qta.icon('fa.play-circle'))
                self.player.stop()

        def setTimeLabel(position, position_max):
            position_ms = position % 1000
            position_sec = math.floor(position / 1000)
            position_min = math.floor(position_sec / 60)
            position_sec = position_sec % 60

            position_max_ms = position_max % 1000
            position_max_sec = math.floor(position_max / 1000)
            position_max_min = math.floor(position_max_sec / 60)
            position_max_sec = position_max_sec % 60

            self.playTimeLabel.setText(
                f"{position_min:02d}:{position_sec:02d}.{position_ms:03d} / {position_max_min:02d}:{position_max_sec:02d}.{position_max_ms:03d}")

        def player_position_changed(position):
            perc = round((position / self.player.duration()) * 100)

            self.recordTimeSlider.blockSignals(True)
            self.recordTimeSlider.setValue(perc)
            self.recordTimeSlider.blockSignals(False)

            setTimeLabel(position, self.player.duration())

        def slider_value_changed(position):
            result_pos = round(position / 100 * self.player.duration())
            self.player.setPosition(result_pos)

        ktr_obj = get_global_ktr_obj()

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
        self.player.positionChanged.connect(player_position_changed)
        self.recordTimeSlider.valueChanged.connect(slider_value_changed)

        setTimeLabel(0, self.player.duration())

        self.reading = ktr_obj.reading
        self.text = ktr_obj.text

        self.toggleReading(False)

        self.current_ktr = ktr_obj
        self.lang = ktr_obj.lang

        load_vosk_model(ktr_obj.lang)


def kater(file_in=None):
    init_recorder()
    app = QApplication([])

    window = UI()
    window.show()

    if not file_in:
        home_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), os.pardir, "modules/")

        FILTER = """
            'Kater train reading' file (*.ktr)
        """
        SELECTED_FILTER = "'Kater train reading' file (*.ktr)"
        file_name = QFileDialog.getOpenFileName(
            None, 'Open file', home_dir, FILTER, SELECTED_FILTER)

        if file_name[0]:
            file_in = file_name[0]
        else:
            sys.exit(1)

    load_global_ktr_obj(file_in)
    window.use_global_object()

    sys.exit(app.exec())
    get_tmp_dir().cleanup()
