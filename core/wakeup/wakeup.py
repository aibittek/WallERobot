# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractclassmethod

class Wakeup(metaclass=ABCMeta):

    WAKEUP_VOICE_FOUND      = 0
    WAKEUP_ERROR            = -1
    WAKEUP_SLIENT_FOUND     = -2
    
    @abstractclassmethod
    def start(self, audio_data):
        """ 
        Start detect wakeup status.

        :param audio_data: audio data
        :return: wakeup status, if have models, return value greater than 0
        """
        pass
    