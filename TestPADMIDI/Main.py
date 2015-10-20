import sys
import time
import rtmidi_python as rtmidi
# import numpy as np

MIDI_ON_LED = 128
MIDI_OFF_LED = 144
MIDI_GREEN = 0
MIDI_RED = 0
INDEX_COLOR = [0, 1, 2, 3]
print(sys.version + "\n" + str(sys.api_version) + "\n" + str(sys.version_info) + "\n" + str(sys.getwindowsversion()))


class ColorList:
    def __init__(self):
        self.colors = None
        self.init_color()
        # print(self.colors)

    def init_color(self):
        self.colors = []
        for r in range(0, 4, 3):
            for g in range(0, 4, 3):
                self.colors.append((r, g))


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
        self.midiOut = rtmidi.MidiOut()
        self.midiIn = rtmidi.MidiIn()
        self.note = None
        self.color = None
        self.pad = ButtonTable()
        self.rgb = ColorList()
        self.midiOut.open_port(1)
        self.midiIn.open_port(0)
        # print(self.rgb.colors)

    def get_led_color(self, red, green):
        led = 0

        red = min(int(red), 3)
        red = max(red, 0)

        green = min(int(green), 3)
        green = max(green, 0)

        led |= red
        led |= green << 4

        return led

    def led_all_on(self):
        """Allume toutes les LED"""
        self.midiOut.send_noteon(176, 0, 127)

    def led_all_off(self):
        """Allume toutes les LED"""
        self.midiOut.send_noteon(176, 0, 0)

    def test_write(self):
        for row in range(0, 8):
            for column in range(0, 9):
                color = self.get_led_color(self.rgb.colors[0][0], self.rgb.colors[0][1])
                self.midiOut.send_noteon(MIDI_OFF_LED, (16 * row) + column, color)
                time.sleep(0.05)
        time.sleep(2)

        color = self.get_led_color(0, 0)
        for column in range(9, -1, -1):
            for row in range(9, -1, -1):
                self.midiOut.send_noteon(MIDI_ON_LED, (16 * row) + column, color)
                time.sleep(0.05)
        time.sleep(2)

    def turn_on_on_press(self, index=1):
        """Allume la LED lorsqu'on presse dessus et aussi le sens contraire"""
        if self.note is not None:
            # print(self.note)
            time.sleep(0.05)
            color = self.get_led_color(self.rgb.colors[index][0], self.rgb.colors[index][1])
            if self.note[0] == 144 and self.note[2] > 0:
                y = self.note[1] & 0x0f
                x = (self.note[1] & 0xf0) >> 4
                # print(self.pad.get_cell(x, y))
                if self.pad.get_cell(x, y)[2]:
                    self.pad.set_cell(self.pad.get_cell(x, y), x, y, False)
                    self.midiOut.send_message([128, self.note[1], color])
                else:
                    color = 0
                    self.pad.set_cell(self.pad.get_cell(x, y), x, y, True)
                    self.midiOut.send_message([144, self.note[1], color])

    def reset(self):
        """Methode qui reset le PAD en eteignanr toutes les LEDs"""
        self.midiOut.send_message([176, 0, 0])


def init(pad):
    pad.color = 2
    pad.midiOut.send_message([MIDI_ON_LED, 104, pad.get_led_color(pad.rgb.colors[pad.color][0], pad.rgb.colors[pad.color][1])])
    pass


def main(INDEX_COLOR=None):
    """Methode main qui permet d'initialiser l'API MIDI ainsi que le LaunchPAD"""
    mdid = rtmidi.MidiOut()

    launchpad = LaunchPAD()
    launchpad.color = INDEX_COLOR[1]

    init(launchpad)

    # launchpad.led_all_on()
    # time.sleep(0.1)
    # launchpad.led_all_off()
    # launchpad.test_write()

    while True:
        message, delta_time = launchpad.midiIn.get_message()
        if message:
            print(message)
            launchpad.note = message
            # print(message, delta_time)

            if message[1] == 104:
                break
            elif message[1] == 105:
                launchpad.reset()
            elif message[1] == 106:
                launchpad.color = INDEX_COLOR[1]
            elif message[1] == 107:
                launchpad.color = INDEX_COLOR[2]
            elif message[1] == 108:
                launchpad.color = INDEX_COLOR[3]
            else:
                launchpad.turn_on_on_press(launchpad.color)
    launchpad.reset()
    del launchpad

main(INDEX_COLOR=INDEX_COLOR)
