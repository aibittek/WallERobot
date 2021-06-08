import requests
import time
import hashlib
import base64

import asr

class iFlytekAIUI(asr.ASR):
    def __init__(self, appid, apikey, authid):
        self.appid = appid
        self.apikey = apikey
        self.authid = authid
        self.base_url = "http://openapi.xfyun.cn/v2/aiui"

    def asr(self, audio):
        r = requests.post(self.base_url, headers=self.buildHeader(), data=audio)
        return r.content

    def buildHeader(self):
        curTime = str(int(time.time()))
        param = "{\"result_level\":\"complete\",\"auth_id\":\""+self.authid+"\",\"data_type\":\"audio\",\"sample_rate\":\"16000\",\"scene\":\"main_box\"}"
        #使用个性化参数时参数格式如下：
        #param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\",\"pers_param\":\""+PERS_PARAM+"\"}"
        paramBase64 = base64.b64encode(param.encode('utf-8'))
        paramBase64 = paramBase64.decode('utf-8')
        m2 = hashlib.md5()
        m2.update((self.apikey + curTime + paramBase64).encode('utf-8'))
        checkSum = m2.hexdigest()

        header = {
            'X-CurTime': curTime,
            'X-Param': paramBase64,
            'X-Appid': self.appid,
            'X-CheckSum': checkSum,
        }
        return header
