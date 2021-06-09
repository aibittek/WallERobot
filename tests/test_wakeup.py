import sys
import signal
import time
import queue

# User define modules
sys.path.append("..")
sys.path.append("../core")
sys.path.append("../core/common")
sys.path.append("../core/wakeup")
sys.path.append("../core/audio")
sys.path.append("../libs/modules/x86_64")
import reflect
from ringbuffer import RingBuffer
from record import AudioRecorder

def signal_handler(signal, frame):
    audio_recorder.stop_record()
    wakeup_running = False
    sys.exit()

def audiocallback(audio_data):
    q.put(audio_data)

if __name__ == '__main__':
    # Capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    wakeup_running = True
    q = queue.Queue(10)

    args = {
        'models': ['../resources/wakeup/walle/walletongxue.pmdl',
                '../resources/wakeup/tianmao/tianmaojingling.pmdl',
                '../resources/wakeup/xiaoaitongxue/xiaoaitongxue.pmdl'],
        'resource': '../resources/common.res',
        'sensitivity': [0.6, 0.6, 0.6],
        'apply_frontend': False,
        'audio_gain': 1,
    }

    # Wakeup modules initialized, use reflect design
    wakeup_imp = reflect.get_class('SnowboyWakeup')
    wakeup = wakeup_imp(args)

    # Recording modules initialized & running
    audio_recorder = AudioRecorder(audiocallback=audiocallback)
    audio_recorder.start()

    # wakeup = SnowboyWakeup(args)
    while wakeup_running:
        data = q.get()
        if len(data) == 0:
            print('data == 0')
            time.sleep(0.02)
        status = wakeup.start(data)
        if status > 0:
            print('被唤醒, 唤醒词:%d' %status)
        elif status == wakeup.WAKEUP_VOICE_FOUND:
            print('在说话')
        elif status == wakeup.WAKEUP_SLIENT_FOUND:
            print('当前没有说话')
        else:
            print('未知错误或未定义错误类型')
