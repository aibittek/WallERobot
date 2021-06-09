import pyaudio
import time
from ctypes import *
from contextlib import contextmanager

def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class AudioPlayer():
    def __init__(self, rate, formats, channels, callback):
        self.rate = rate
        self.formats = formats
        self.channels = channels
        self.callback = callback
        self.chunk = 1024

        # create an audio object
        with no_alsa_error():
            self.audio = pyaudio.PyAudio()

        # open stream based on the wave object which has been input.
        # self.stream = self.audio.open(format = pyaudio.paInt16,
        #                 channels = self.channels,
        #                 rate = self.rate,
        #                 output = True,
        #                 stream_callback=self.callback)
        self.stream = self.audio.open(format = pyaudio.paInt16,
                        channels = self.channels,
                        rate = self.rate,
                        output = True,
                        frames_per_buffer = 4096)

    def play(self, data):
        self.stream.write(data)

    def stop(self):
        # wait for stream to finish
        # while self.stream.is_active():
        #     time.sleep(0.1)
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
