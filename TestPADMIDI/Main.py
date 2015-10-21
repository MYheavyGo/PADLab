import sys
import time
import rtmidi_python as rtmidi
import numpy as np
import pyglet

VERSION = '0.0.1'
MIDI_ON_LED = 144
MIDI_OFF_LED = 128
MIDI_GREEN = 0
MIDI_RED = 0
INDEX_COLOR = [0, 1, 2, 3]

print(sys.version, str(sys.api_version), str(sys.version_info), str(sys.getwindowsversion()), sep='\n')
print("Version du programme ", VERSION, sep=': ')

window = pyglet.window.Window()


class ColorList:
    def __init__(self):
        self.colors = np.array([(0, 0), (0, 3), (3, 0), (3, 3)])


class ButtonTable:
    def __init__(self):
        self.buttons = np.zeros((8, 9), dtype=bool)

    def get_cell(self, x, y):
        return self.buttons[x][y]

    def set_cell(self, x, y, click):
        self.buttons[x][y] = click


class LaunchPAD:

    def __init__(self):
        self.quit = False
        self.midiOut = rtmidi.MidiOut()
        self.midiIn = rtmidi.MidiIn()
        self.note = None
        self.color = None
        self.pad = ButtonTable()
        self.rgb = ColorList()

        if len(self.midiOut.ports) > 1:
            self.midiOut.open_port(1)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

        if len(self.midiIn.ports) > 0:
            self.midiIn.callback = self.callback
            self.midiIn.open_port(0)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

    def callback(self, message, time_stamp):
        if message:
            self.note = message
            print(self.note)
            if message[0] == 176 and message[1] == 104:
                self.quit = True
            elif message[1] == 105:
                self.clear()
            elif message[1] == 106:
                self.color = INDEX_COLOR[1]
            elif message[1] == 107:
                self.color = INDEX_COLOR[2]
            elif message[1] == 108:
                self.color = INDEX_COLOR[3]
            else:
                self.turn_on_on_press(self.color)

    @staticmethod
    def get_led_color(red, green):
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
        self.midiOut.send_message([176, 0, 127])

    def clear(self):
        """Allume toutes les LED"""
        self.midiOut.send_message([176, 0, 0])
        self.pad.buttons = np.zeros((8, 9), dtype=bool)

    def test_write(self):
        for row in range(0, 8):
            for column in range(0, 9):
                color = self.get_led_color(self.rgb.colors[0][0], self.rgb.colors[0][1])
                self.midiOut.send_message(MIDI_OFF_LED, (16 * row) + column, color)
                time.sleep(0.05)
        time.sleep(2)

        color = self.get_led_color(0, 0)
        for column in range(9, -1, -1):
            for row in range(9, -1, -1):
                self.midiOut.send_message(MIDI_ON_LED, (16 * row) + column, color)
                time.sleep(0.05)
        time.sleep(2)

    def turn_on_on_press(self, index=1):
        """Allume la LED lorsqu'on presse dessus et l'eteint lorsqu'on reappuie"""
        color = self.get_led_color(self.rgb.colors[index][0], self.rgb.colors[index][1])
        if self.note[0] == 144 and self.note[2] == 127:
            x = self.note[1] // 16
            y = self.note[1] - (16 * x)

            # self.midiOut.send_message([MIDI_ON_LED, self.note[1], color])
            color = self.get_led_color(self.rgb.colors[index][0], self.rgb.colors[index][1])

            if not self.pad.get_cell(x, y):
                print("Allume")
                self.pad.set_cell(x, y, True)
                self.midiOut.send_message([MIDI_ON_LED, self.note[1], color])
            else:
                print("Eteint")
                color = 0
                self.pad.set_cell(x, y, False)
                self.midiOut.send_message([MIDI_OFF_LED, self.note[1], color])

    def reset(self):
        """Methode qui reset le PAD en eteignanr toutes les LEDs"""
        self.midiOut.send_message([176, 0, 0])
        self.midiIn.close_port()
        self.midiOut.close_port()


def init(windows, pad):
    print(windows, pad)
    pass


def main():
    """Methode main qui permet d'initialiser l'API MIDI ainsi que le LaunchPAD"""
    launchpad = LaunchPAD()
    launchpad.color = INDEX_COLOR[1]

    init(window, launchpad)

    pyglet.app.run()

    @window.event
    def on_draw():
        window.clear()

    @window.event
    def on_exit():
        launchpad.reset()
        del launchpad

main()
