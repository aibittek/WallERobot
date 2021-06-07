# -*- coding:utf-8 -*-

import threading
import pyaudio
import wave

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

class AudioRecorder(threading.Thread):
    def __init__(self, 
            audiofile='', 
            audiocallback=None,
            chunk = 2048,
            formats = pyaudio.paInt16,
            channels = 1,
            rate = 16000):
        threading.Thread.__init__(self)
        self.running = True
        self.audiofile = audiofile
        self.audiocallback = audiocallback
        self.chunk = chunk
        self.formats = formats
        self.channels = channels
        self.rate = rate

    def run(self):
        with no_alsa_error():
            audio = pyaudio.PyAudio()
        if self.audiofile:
            wavfile = wave.open(self.audiofile, 'wb')
            wavfile.setnchannels(self.channels)
            wavfile.setsampwidth(audio.get_sample_size(self.formats))
            wavfile.setframerate(self.rate)
        stream = audio.open(format=self.formats,
                               channels=self.channels,
                               rate=self.rate,
                               input=True)
        
        print('start recording...')
        while self.running:
            data = stream.read(self.chunk)
            if self.audiofile and wavfile:
                wavfile.writeframes(data)
            if self.audiocallback:
                self.audiocallback(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        if self.audiofile and wavfile:
            wavfile.close()

    def stop_record(self):
        self.running = False
        self.join()
    