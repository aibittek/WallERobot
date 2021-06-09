import sys 
sys.path.append("../core")
sys.path.append("../core/ai/TTS")
import reflect

def audio_callback(audio_data):
    with open('data.pcm', 'ab') as f:
        f.write(audio_data)

if __name__ == '__main__':
    appid = 'xxxxxxxx'
    apikey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    apisecret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    vcn = 'x2_xiaojuan'
    text = '榴莲太贵了，可以给我换个搓衣板吗'

    tts_imp = reflect.get_class('iFlytekTTS')
    tts = tts_imp(appid, apikey, apisecret, vcn)
    audio_data = tts.tts(text, callback=audio_callback)
    with open('tts.pcm', 'ab') as f:
        f.write(audio_data)
