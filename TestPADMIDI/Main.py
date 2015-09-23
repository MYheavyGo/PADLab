from pygame import midi
from Utils.launchpad_charset import CHARTAB


class LaunchPAD:
    def __init__(self):
        midi.init()
        self.count = midi.get_count()
        for x in xrange(0, self.count):
            print(midi.get_device_info(x))
        self.midiIn = midi.MIDIIN
        self.midiOut = midi.MIDIOUT

    def __del__(self):
        midi.quit()


def main():
    pad = LaunchPAD()

main()
