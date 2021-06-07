#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File          : main.py
@Description   : snowboy wakeup
@Date          : 2021/05/31 15:14:19
@Author        : kuili
@Email         : 55239610@qq.com
'''

import snowboydecoder
import sys
import os
import signal
import webAIUI
import tts
import json
from jsonpath import jsonpath

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

print(sys.argv)
if len(sys.argv) != 4:
    print("Error: need to specify 3 model names")
    print("Usage: python main.py 1st.model 2nd.model 3nd.model")
    sys.exit(-1)
models = sys.argv[1:]
print(models)

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

sensitivity = [0.5]*len(models)
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
# callbacks = [lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING),
#              lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING),
#              lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)]
def callbacks():
    print('recording audio...')

print('Listening... Press Ctrl+C to exit')

def audioRecorderCallback(fname):
    print("audiocallback:" + fname)
    # ASR
    r = webAIUI.getText(fname)
    # TTS
    print('ASR result')
    json_data = json.loads(r)
    text = jsonpath(json_data, '$..content')
    print(text[0])
    tts.TTS(text[0])
    # Play TTS
    # with sr.AudioFile(fname) as source:
    #     audio = r.record(source)  # read the entire audio file
    os.remove(fname)

# main loop
detector.start(detected_callback = callbacks,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check = interrupt_callback,
               sleep_time=0.03)

detector.terminate()
