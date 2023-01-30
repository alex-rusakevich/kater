from zipfile import ZipFile
import json
import os
import tempfile
import wave
import sys
import os.path as op
from os import listdir
from vosk import Model, KaldiRecognizer, SetLogLevel
from functools import cmp_to_key
import re
from PyQt6.QtWidgets import QMessageBox
from kater.util import panic


ktr_obj = None


class Ktr_Object:
    def __init__(self, ktr_file_path):
        input_zip = ZipFile(ktr_file_path)
        files = {name: input_zip.read(name) for name in input_zip.namelist()}

        self.config = json.loads(files["metainf.json"].decode('utf-8'))

        self.audio = {"bin": files[self.config["audio"]],
                      "ext": os.path.splitext(self.config["audio"])[1]}
        self.text = files[self.config["text"]].decode('utf-8')
        self.reading = files[self.config["reading"]].decode('utf-8')

        self.lang = self.config["lang"]


def load_global_ktr_obj(ktr_file_path):
    global ktr_obj
    ktr_obj = Ktr_Object(ktr_file_path)


def get_global_ktr_obj():
    global ktr_obj
    return ktr_obj


tempdir = tempfile.TemporaryDirectory()
print("tempdir is", tempdir.name)


def get_tmp_dir():
    global tempdir
    return tempdir


SetLogLevel(0)
MODELS_PATH = "./vosk_models"
current_model = None


def load_vosk_model(lang_code="cn"):
    model_list = []

    for model_directory in [f for f in listdir(MODELS_PATH) if op.isdir(op.join(MODELS_PATH, f))]:
        if model_directory.find(f"-{lang_code}-") != -1:
            model_list.append(model_directory)

    def compare(model_1, model_2):
        def is_small(model): return "-small-" in model

        def get_version(model): return float(
            re.search(r'\d+\.\d+', model, re.IGNORECASE).group(0))

        if get_version(model_1) > get_version(model_2):
            return -1
        elif get_version(model_1) < get_version(model_2):
            return 1
        else:
            if not is_small(model_1) and is_small(model_2):
                return -1
            elif is_small(model_1) and not is_small(model_2):
                return 1
            else:
                return 0

    model_path = ""

    if len(model_list) == 0:
        error_msg = f'Please, visit <a href="https://alphacephei.com/vosk/models">\
https://alphacephei.com/vosk/models</a>, download language model at "vosk_models" folder'

        panic(
            f"No language model found for language \"{lang_code}\".", error_msg)
    elif len(model_list) == 1:
        model_path = model_list[0]
    else:
        model_list = sorted(model_list, key=cmp_to_key(compare))
        model_path = model_list[0]

    model_path = op.join("./vosk_models", model_path)

    global current_model
    current_model = Model(model_path)


def audio_to_text(path_to_audio):
    wf = wave.open(path_to_audio, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        panic(f"Cannot load audio \"{path_to_audio}\".",
              "Audio file must be WAV format mono PCM.")

    global current_model

    rec = KaldiRecognizer(current_model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    return rec.FinalResult()
