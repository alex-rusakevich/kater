from zipfile import ZipFile
import json
import os
import tempfile


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


def get_tmp_dir():
    global tempdir
    return tempdir
