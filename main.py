import os
import sys
import signal
import time
import queue
import sys
import time
import json
import alsaaudio
import platform
from jsonpath import jsonpath
sys.path.append("core")
sys.path.append("core/audio")
sys.path.append("core/ai/ASR")
sys.path.append("core/ai/TTS")
sys.path.append("core/common")
sys.path.append("core/wakeup")
if platform.system() == "Linux":
    if platform.processor() == 'x86_64':
        sys.path.append('libs/modules/x86_64')
    else:
        sys.path.append('libs/modules/pi')
else:
    raise ImportError("now snowboy only runs on pi or Ubuntu 16.04.")
import reflect
import play 
from ringbuffer import RingBuffer
from record import AudioRecorder
from play import AudioPlayer

stopRecording = False

def signal_handler(signal, frame):
    audio_recorder.stop_record()
    audio_player.stop()
    wakeup_running = False
    sys.exit()

def audiocallback(audio_data):
    if not stopRecording:
        q.put(audio_data)

def tts_callback(status, audio_data):
    audio_player.play(audio_data)

if __name__ == '__main__':
    # Capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    wakeup_running = True
    q = queue.Queue(10)

    args = {
        'models': ['resources/wakeup/walle/walletongxue.pmdl',
                'resources/wakeup/tianmao/tianmaojingling.pmdl',
                'resources/wakeup/xiaoaitongxue/xiaoaitongxue.pmdl'],
        'resource': 'resources/common.res',
        'sensitivity': [0.6, 0.6, 0.6],
        'apply_frontend': False,
        'audio_gain': 1,
    }

    # Wakeup modules initialized, use reflect design
    wakeup_imp = reflect.get_class('SnowboyWakeup')
    wakeup = wakeup_imp(args)

    # Starting AudioPlayer
    global audio_player
    audio_player = AudioPlayer('hw:0,0', 16000, alsaaudio.PCM_FORMAT_S16_LE, 1)
    
    # Recording modules initialized & running
    audio_recorder = AudioRecorder(audiocallback=audiocallback)
    audio_recorder.start()

    state = "PASSIVE"
    recordedData = []
    recordingCount = 0
    recording_timeout = 100
    silent_count_threshold = 2
    while wakeup_running:
        data = q.get()
        status = wakeup.start(data)
        if status == wakeup.WAKEUP_ERROR:
            print('未知错误或未定义错误类型')

        if state == "PASSIVE":
            if status > 0: #key word found
                recordedData = []
                recordedData.append(data)
                silentCount = 0
                recordingCount = 0
                message = "Keyword " + str(status) + " detected at time: "
                message += time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time()))
                print(message)
                state = "ACTIVE"
                continue
        elif state == "ACTIVE":
            stopRecording = False
            if recordingCount > recording_timeout:
                stopRecording = True
            elif status == wakeup.WAKEUP_SLIENT_FOUND: #silence found
                if silentCount > silent_count_threshold:
                    stopRecording = True
                    print('检测到后端点')
                else:
                    silentCount = silentCount + 1
            elif status == 0: #voice found
                silentCount = 0

            # start asr && tts
            if stopRecording == True:

                appid = "5d2f27d2"
                apikey = "a605c4712faefae730cc84b62c0eb92f"
                auth_id = "f9be5221d3288ef324aeb1a0ce73abcd"

                asr_imp = reflect.get_class('iFlytekAIUI')
                asr = asr_imp(appid, apikey, auth_id)
                audio = b''.join(recordedData)
                r = asr.asr(audio)
                result = str(r, encoding = "utf-8")
                print(result)
                json_data = json.loads(r)
                content = jsonpath(json_data, '$..content')
                if not content:
                    print('没有找到识别结果')
                    state = "PASSIVE"
                    stopRecording = False
                    continue

                print('识别结果:' + content[0])
                appid = "5d2f27d2"
                apikey = "a8331910d59d41deea317a3c76d47b60"
                apisecret = "8110566cd9dd13066f9a1e38aeb12a48"
                xcn = 'x2_xiaojuan'

                tts_imp = reflect.get_class('iFlytekTTS')
                tts = tts_imp(appid, apikey, apisecret, xcn)
                tts_data = tts.tts(content[0], callback=tts_callback)
                
                while audio_player.playing:
                    time.sleep(0.1)

                state = "PASSIVE"
                stopRecording = False
                continue

            recordingCount = recordingCount + 1
            recordedData.append(data)

    print("finished.")
