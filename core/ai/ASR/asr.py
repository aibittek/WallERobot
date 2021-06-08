# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractclassmethod

class ASR(metaclass=ABCMeta):
    
    @abstractclassmethod
    def asr(self, audio):
        """ 
        Start speech recognition.

        :param audio: 16000 16bit signed int mono, if audio = None means end of speak.
        :return: text: return text.
        """
        pass
    