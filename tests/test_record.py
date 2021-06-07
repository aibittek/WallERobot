import sys 
import signal
sys.path.append("../core/audio")
from record import AudioRecorder

def signal_handler(signal, frame):
    audio_recorder.stop_record()

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def audiocallback(audio_data):
    with open('output.pcm', 'ab+') as f:
        f.write(audio_data)

audio_recorder = AudioRecorder(audiofile='test.wav', audiocallback=audiocallback)
audio_recorder.start()
