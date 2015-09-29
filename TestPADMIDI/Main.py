import sys
import time
import rtmidi2
import numpy as np

MIDI_ON_LED = 128
MIDI_OFF_LED = 144
print(sys.version + "\n" + str(sys.api_version) + "\n" + str(sys.version_info) + "\n" + str(sys.getwindowsversion()))


class ButtonTable:
    def __init__(self):
        self.buttons = None
        self.init_buttons()
        # print(str(self.buttons) + "\ncount " + str(len(self.buttons)))

    def init_buttons(self):
        self.buttons = []
        for x in range(0, 9):
            for y in range(0, 9):
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
        self.midiOut = rtmidi2.MidiOut()
        self.midiIn = rtmidi2.MidiIn()
        self.note = None
        self.pad = ButtonTable()
        self.midiOut.open_port(1)
        self.midiIn.open_port(0)

    def led_all_on(self):
        """Allume toutes les LED"""
        self.midiOut.send_noteon(176, 0, 127)

    def led_all_off(self):
        """Allume toutes les LED"""
        self.midiOut.send_noteon(176, 0, 0)

    def test_write(self):
        for column in range(0, 9):
            for row in range(0, 8):
                self.midiOut.send_noteon(MIDI_OFF_LED, (16 * row) + column, 15)
                time.sleep(0.05)
        time.sleep(2)

        for column in range(9, -1, -1):
            for row in range(9, -1, -1):
                self.midiOut.send_noteon(MIDI_ON_LED, (16 * row) + column, 12)
                time.sleep(0.05)
        time.sleep(2)

    def test_many_write(self):
        notes = range(127)
        velocities = 0
        self.midiOut.send_noteon_many(MIDI_ON_LED, notes, velocities)
        time.sleep(1)
        self.midiOut.send_noteon_many(MIDI_ON_LED, notes, [0] * len(notes))

    def turn_on_on_press(self):
        """Allume la LED lorsqu'on presse dessus et aussi le sens contraire"""
        if self.note is not None:
            print(self.note)
            time.sleep(0.05)
            if self.note[0] == 144 and self.note[2] > 0:
                y = self.note[1] & 0x0f
                x = (self.note[1] & 0xf0) >> 4
                print(self.pad.get_cell(x, y))
                if self.pad.get_cell(x, y)[2]:
                    self.pad.set_cell(self.pad.get_cell(x, y), x, y, False)
                    self.midiOut.send_noteon(128, self.note[1], 12)
                else:
                    self.pad.set_cell(self.pad.get_cell(x, y), x, y, True)
                    self.midiOut.send_noteon(144, self.note[1], 60)

    def reset(self):
        """Methode qui reset le PAD en eteignanr toutes les LEDs"""
        self.midiOut.send_noteon(176, 0, 0)


def main():
    """Methode main qui permet d'initialiser l'API MIDI ainsi que le LaunchPAD"""
    launchpad = LaunchPAD()
    launchpad.led_all_on()
    time.sleep(0.1)
    launchpad.led_all_off()
    launchpad.test_many_write()
    """while True:
        message, delta_time = launchpad.midiIn.get_message()
        if message:
            launchpad.note = message
            # print(message, delta_time)
            if message[1] == 104:
                break
            else:
                launchpad.turn_on_on_press()"""
    launchpad.reset()

main()
