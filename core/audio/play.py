import pyaudio
import time

def play_audio(path, rate, formats, channels):
    chunk = 1024

    # open the file for reading.
    f = open(path, 'rb')

    # create an audio object
    p = pyaudio.PyAudio()

    # open stream based on the wave object which has been input.
    stream = p.open(format = pyaudio.paInt16,
                    channels = channels,
                    rate = rate,
                    output = True)

    # read data (based on the chunk size)
    # data = f.read(chunk)

    # play stream (looping from beginning of file to the end)
    while True:
        # writing to the stream is what *actually* plays the sound.
        data = f.read(chunk)
        if len(data) <= 0:
            break
        stream.write(data)
    time.sleep(0.5)
    # cleanup stuff.
    stream.close()
    p.terminate()
    print('play end')
