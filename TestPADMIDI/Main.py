import sys
import string
from pygame import midi
from Utils.launchpad_charset import CHARTAB

class Midi:
    def __init__(self):
        midi.init()

    def __del__(self):
        midi.quit()

    def get_devices(self):
        ret = []
        for x in range(midi.get_count()):
            md = midi.get_device_info(x)
            ret.append(md)
        return ret

    def search_device(self, name, output, input):
        device = None
        devices = self.get_devices()

        for x in devices:
            if string.find(x[1], name) >= 0:
                if output:
                    device = x
                elif input:
                    device = x

        return device

    def get_time(self):
        return midi.time()


class LaunchPAD:

    def __init__(self):
        self.midiBase = Midi()
        self.midiIn = self.midiBase.search_device('Launchpad', True, False)
        self.midiOut = self.midiBase.search_device('Launchpad', False, True)

    def open(self, number=0, name='Launchpad'):
        self.midiIn = midi


def main():
    pad = LaunchPAD()

main()
