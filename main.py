import sys
import signal
import time
import queue
import sys
import time
import json
from jsonpath import jsonpath
sys.path.append("core")
sys.path.append("core/audio")
sys.path.append("core/ai/ASR")
sys.path.append("core/ai/TTS")
sys.path.append("core/common")
sys.path.append("core/wakeup")
sys.path.append("libs/modules/x86_64")
import reflection
import play 
from ringbuffer import RingBuffer
from record import AudioRecorder


def signal_handler(signal, frame):
    audio_recorder.stop_record()
    wakeup_running = False
    sys.exit()

def audiocallback(audio_data):
    print(q.qsize())
    q.put(audio_data)

def tts_callback(audio_data):
    play.play_audio(audio_data)

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
    modules_name = 'SnowboyWakeup'
    modules = __import__(modules_name, fromlist=True)
    wakeup_imp = reflection.get_class(modules, modules_name)
    wakeup = wakeup_imp(args)

    # Recording modules initialized & running
    audio_recorder = AudioRecorder(audiocallback=audiocallback)
    audio_recorder.start()

    state = "PASSIVE"
    recordedData = []
    recordingCount = 0
    recording_timeout = 100
    silent_count_threshold = 5
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
                else:
                    silentCount = silentCount + 1
            elif status == 0: #voice found
                silentCount = 0

            if stopRecording == True:
                appid = "5d2f27d2"
                apikey = "a605c4712faefae730cc84b62c0eb92f"
                auth_id = "f9be5221d3288ef324aeb1a0ce73abcd"

                modules_name = 'iFlytekAIUI'
                modules = __import__(modules_name, fromlist=True)
                asr_imp = reflection.get_class(modules, modules_name)
                asr = asr_imp(appid, apikey, auth_id)
                audio = b''.join(recordedData)
                r = asr.asr(audio)
                print(r)
                json_data = json.loads(r)
                text = jsonpath(json_data, '$..content')
                # print('识别结果:' + text[0])

                appid = "5d2f27d2"
                apikey = "a8331910d59d41deea317a3c76d47b60"
                apisecret = "8110566cd9dd13066f9a1e38aeb12a48"
                xcn = 'x2_xiaojuan'
                modules_name = 'iFlytekTTS'
                modules = __import__(modules_name, fromlist=True)
                tts_imp = reflection.get_class(modules, modules_name)
                tts = tts_imp(appid, apikey, apisecret, xcn)
                tts_data = tts.tts(text[0], callback=None)
                with open('tts.pcm', 'wb') as f:
                    f.write(tts_data)
                    f.close()
                play.play_audio('tts.pcm', 16000, 16, 1)
                
                q.queue.clear()
                state = "PASSIVE"
                continue

            recordingCount = recordingCount + 1
            recordedData.append(data)

    print("finished.")
