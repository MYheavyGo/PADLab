import sys
import random
import time
import string
from pygame import midi
from Utils.launchpad_charset import CHARTAB
from Utils.launchpad_device import get_devices

MIDI_BUFFER_OUT = 128
MIDI_BUFFER_IN = 16
print(sys.version + "\n" + str(sys.api_version) + "\n" + str(sys.version_info) + "\n" + str(sys.getwindowsversion()))


class ButtonTable:
    def __init__(self):
        self.buttons = []
        self.init_buttons()
        print(str(self.buttons) + "\ncount " + str(len(self.buttons)))

    def init_buttons(self):
        for x in xrange(0, 9):
            for y in xrange(0, 9):
                self.buttons.append([x, y, False])

    def get_cell(self, x, y):
        if y > 0:
            pos = x * y
        else:
            pos = x
        return self.buttons[pos]

    def set_cell(self, info, x, y, click):
        if y > 0:
            pos = x * y
        else:
            pos = x
        info[2] = click
        self.buttons[pos] = info
        return self.buttons[pos]


class LaunchPAD:

    def __init__(self):
        devices = get_devices()
        print(devices)
        self.note = None
        self.pad = ButtonTable()
        self.cell = None
        if devices[2][3] > 0:
            self.midiOut = midi.Output(devices[3], 0)
        if devices[0][2] > 0:
            self.midiIn = midi.Input(devices[1])

    def read_check(self):
        """Verifie si on peut recevoir des donnees depuis le PAD"""
        return self.midiIn.poll()

    def led_all_on(self):
        """Allume toutes les LED"""
        self.midiOut.write_short(176, 0, 127)

    def test_write(self):
        for column in xrange(0, 9):
            for row in xrange(0, 8):
                self.midiOut.write_short(144, (16 * row) + column, 15)
                time.sleep(0.05)
        time.sleep(2)

        for column in xrange(9, -1, -1):
            for row in xrange(9, -1, -1):
                self.midiOut.write_short(128, (16 * row) + column, 12)
                time.sleep(0.05)
        time.sleep(2)

    def turn_on_on_press(self):
        """Allume la LED lorsqu'on presse dessus et aussi le sens contraire"""
        if self.read_check():
            self.note = self.midiIn.read(1)
            # print(self.note)
            if self.note[0][0][0] == 144 and self.note[0][0][2] > 0:
                y = self.note[0][0][1] & 0x0f
                x = (self.note[0][0][1] & 0xf0) >> 4
                print("x --> " + str(x) + "\ny --> " + str(y) + "\npos --> " + str((y > 0 if x * y else x)))
                if self.pad.get_cell(x, y)[2]:
                    self.cell = self.pad.set_cell(self.pad.get_cell(x, y), x, y, False)
                    self.midiOut.write_short(128, self.note[0][0][1], 12)
                else:
                    self.cell = self.pad.set_cell(self.pad.get_cell(x, y), x, y, True)
                    self.midiOut.write_short(144, self.note[0][0][1], 60)
                print(self.cell)
                time.sleep(0.05)

    def reset(self):
        """Methode qui reset le PAD en eteignanr toutes les LEDs"""
        self.midiOut.write_short(176, 0, 0)


def main():
    """Methode main qui permet d'initialiser l'API MIDI ainsi que le LaunchPAD"""
    midi.init()
    launchpad = LaunchPAD()
    # pad.led_all_on()
    # pad.test_write()
    while 1:
        launchpad.turn_on_on_press()
        if launchpad.note is not None:
            if launchpad.note[0][0][1] == 120:
                break
    launchpad.reset()
    midi.quit()

main()
