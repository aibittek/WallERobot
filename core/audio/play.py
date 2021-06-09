import pyaudio
import time

class AudioPlayer():
    def __init__(self, rate, formats, channels, callback):
        self.rate = rate
        self.formats = formats
        self.channels = channels
        self.callback = callback
        self.chunk = 2048

        # create an audio object
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
                        output = True)

    def play(self, data):
        self.stream.write(data)

    def stop(self):
        # wait for stream to finish
        while self.stream.is_active():
            time.sleep(0.1)
        self.stream.stop_stream()
    
    def stop(self):
        self.stream.close()
        self.audio.terminate()
