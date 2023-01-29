import pyaudio
import wave
from kater.resources import get_tmp_dir
import os.path
import threading

CHUNK_SIZE = 1024

SAMPLE_FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44400

OUTPUT_FILE_NAME = os.path.join(get_tmp_dir().name, "user_record.wav")

is_recording = False
stream = None
frames = []

recording_thread = None
paud = None


def init_recorder():
    global paud
    paud = pyaudio.PyAudio()


def start_recording():
    global is_recording

    if is_recording:
        return None

    is_recording = True

    def record():
        global is_recording, stream, frames, paud

        stream = paud.open(format=SAMPLE_FORMAT, channels=CHANNELS,
                           rate=SAMPLE_RATE, input=True,
                           frames_per_buffer=CHUNK_SIZE)
        frames = []

        while is_recording:
            data = stream.read(CHUNK_SIZE)
            frames.append(data)

    global recording_thread
    recording_thread = threading.Thread(target=record)
    recording_thread.start()


def stop_recording():
    global stream, paud, is_recording, frames, recording_thread

    if not is_recording:
        return None

    is_recording = False
    recording_thread.join()
    stream.stop_stream()
    stream.close()

    sf = wave.open(OUTPUT_FILE_NAME, 'wb')
    sf.setnchannels(CHANNELS)
    sf.setsampwidth(paud.get_sample_size(SAMPLE_FORMAT))
    sf.setframerate(SAMPLE_RATE)
    sf.writeframes(b''.join(frames))
    sf.close()

    return OUTPUT_FILE_NAME
