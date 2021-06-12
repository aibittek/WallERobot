from __future__ import print_function

import sys
import wave
import getopt
import alsaaudio
import time

def play(device, f):	

    format = None

    # 8bit is unsigned in wav files
    if f.getsampwidth() == 1:
        format = alsaaudio.PCM_FORMAT_U8
    # Otherwise we assume signed data, little endian
    elif f.getsampwidth() == 2:
        format = alsaaudio.PCM_FORMAT_S16_LE
    elif f.getsampwidth() == 3:
        format = alsaaudio.PCM_FORMAT_S24_3LE
    elif f.getsampwidth() == 4:
        format = alsaaudio.PCM_FORMAT_S32_LE
    else:
        raise ValueError('Unsupported format')

    periodsize = 1024

    print('%d channels, %d sampling rate, format %d, periodsize %d\n' % (f.getnchannels(),
                                                                         f.getframerate(),
                                                                         format,
                                                                         periodsize))

    device = alsaaudio.PCM(channels=f.getnchannels(), rate=f.getframerate(), format=format, periodsize=periodsize, device=device)
    
    data = f.readframes(periodsize)
    while data:
        # Read data from stdin
        device.write(data)
        data = f.readframes(periodsize)


def usage():
    print('usage: playwav.py [-d <device>] <file>', file=sys.stderr)
    sys.exit(2)

if __name__ == '__main__':

    device = 'hw:0,0'

    opts, args = getopt.getopt(sys.argv[1:], 'd:')
    for o, a in opts:
        if o == '-d':
            device = a
    
    if not args:
        usage()

    chunk = 3200
    f = open(args[0], 'rb')
    out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, channels=1, rate=16000, format=alsaaudio.PCM_FORMAT_S16_LE, periodsize=160, device=device)
    
    # Read data from stdin
    data = f.read(chunk)
    while data:
        start = time.time()
        out.write(data)
        print(time.time()-start)
        data = f.read(chunk)

    # with wave.open(args[0], 'rb') as f:
    #     play(device, f)
    
    time.sleep(1)