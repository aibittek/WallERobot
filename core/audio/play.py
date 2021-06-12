from __future__ import print_function

import sys
import wave
import getopt
import alsaaudio
import time
import ringbuffer

# OS X: brew install boost
# Ubuntu: apt-get install libboost-all-dev
# Windows: Install the latest version of Boost then set the BOOST_ROOT environment variable to point to its folder.
# Then:
# pip install ringbuf
from ringbuf import RingBuffer
import _thread as thread

# Documentation:
# https://larsimmisch.github.io/pyalsaaudio/libalsaaudio.html#module-alsaaudio

class AudioPlayer():
    def __init__(self, device, rate, formats, channels):
        self.device = device
        self.rate = rate
        self.formats = formats
        self.channels = channels
        self.chunk = 320
        self.playing = False
        self.buffer = RingBuffer(format='B', capacity=320000)
        
        self.stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, 
            channels=self.channels, 
            rate=self.rate, 
            # format=alsaaudio.PCM_FORMAT_S16_LE, 
            format=self.formats,
            periodsize=self.chunk // self.formats,
            device=self.device)

    def play(self, data):
        if self.playing:
            self.buffer.push(data)
        else:
            self.playing = True
            self.buffer.push(data)
            def run(*args):
                while self.playing:
                    data = self.buffer.pop(self.chunk)
                    if data:
                        self.stream.write(data)
                    else:
                        self.playing = False
                    
            thread.start_new_thread(run, ())

    def stop(self):
        self.playing = False
