# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#   合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os

import tts

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

class RequestParam(object):
    # 初始化
    def __init__(self, appid, apikey, apisecret, text, vcn):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret
        self.text = text
        self.vcn = vcn
        # 公共参数(common)
        self.CommonArgs = {"app_id": self.appid}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": self.vcn, "tte": "utf8"}
        content = base64.b64encode(self.text.encode('utf-8')).decode('utf-8')
        # print(content)
        self.Data = {"status": 2, "text": content}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.apisecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.apikey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

class iFlytekTTS(tts.TTS):
    def __init__(self, appid, apikey, apisecret, vcn):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret
        self.vcn = vcn
        
    def tts(self, text, callback=None):
        self.text = text
        self.param = RequestParam(appid=self.appid, apisecret=self.apisecret,
                        apikey=self.apikey, text=self.text, vcn=self.vcn)
        self.callback = callback
        websocket.enableTrace(False)
        self.url = self.param.create_url()
        self.ws = websocket.WebSocketApp(self.url,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return b''.join(self.audio_data)
    
    def on_message(self, ws, message):
        try:
            # print(message)
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            if status == 2:
                self.audio_data.append(audio)
                if self.callback:
                    self.callback(status, audio)
                print("ws is closed")
                self.ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                self.audio_data.append(audio)
                if self.callback:
                    self.callback(status, audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket错误的处理
    def on_error(self, ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(self, ws):
        print("### closed ###")

    # 收到websocket连接建立的处理
    def on_open(self, ws):
        def run(*args):
            d = {"common": self.param.CommonArgs,
                "business": self.param.BusinessArgs,
                "data": self.param.Data,
                }
            d = json.dumps(d)
            print("------>开始发送文本数据:" + d)
            self.audio_data = []
            self.ws.send(d)
            # if os.path.exists('./demo.pcm'):
            #     os.remove('./demo.pcm')

        thread.start_new_thread(run, ())
