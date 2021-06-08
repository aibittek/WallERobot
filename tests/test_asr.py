import sys
import time
import json
from jsonpath import jsonpath
sys.path.append("../core")
sys.path.append("../core/ai/ASR")
import reflection

if __name__ == '__main__':
    appid = "5d2f27d2"
    apikey = "a605c4712faefae730cc84b62c0eb92f"
    auth_id = "f9be5221d3288ef324aeb1a0ce73abcd"

    modules_name = 'iFlytekAIUI'
    modules = __import__(modules_name, fromlist=True)
    asr_imp = reflection.get_class(modules, modules_name)
    asr = asr_imp(appid, apikey, auth_id)
    with open('data.pcm', 'rb') as f:
        audio = f.read()
        r = asr.asr(audio)
        json_data = json.loads(r)
        text = jsonpath(json_data, '$..content')
        print(text[0])
