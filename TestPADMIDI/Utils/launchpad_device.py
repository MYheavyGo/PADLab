import string
from pygame import midi

__author__ = 'CP-12GSP'


def get_devices():
    ret = []

    for x in range(0, midi.get_count()):
        if not string.find(midi.get_device_info(x)[1], 'Launchpad'):
            ret.append(midi.get_device_info(x))
            ret.append(x)
    return ret
