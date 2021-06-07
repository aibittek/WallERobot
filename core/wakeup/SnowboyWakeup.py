# -*- coding:utf-8 -*-

import os
import sys
import wakeup
import snowboydetect

class SnowboyWakeup(wakeup.Wakeup):
    def __init__(self, args):
        print(args)
        tm = type(args['models'])
        ts = type(args['sensitivity'])
        if tm is not list:
            args['models'] = [args['models']]
        if ts is not list:
            args['sensitivity'] = [args['sensitivity']]
        model_str = ",".join(args['models'])
        sensitivity = args['sensitivity']

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=args['resource'].encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(args['audio_gain'])
        self.detector.ApplyFrontend(args['apply_frontend'])
        self.num_hotwords = self.detector.NumHotwords()

        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

    def start(self, audio_data):
        return self.detector.RunDetection(audio_data)
