# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractclassmethod

class TTS(metaclass=ABCMeta):
    
    @abstractclassmethod
    def tts(self, text, callback=None):
        """ 
        Start text to speech.

        :param text: text which transfer to speech
        :param callback: stream audio data callback
        :return: pcm data, 16000 16bit signed int mono
        """
        pass
    