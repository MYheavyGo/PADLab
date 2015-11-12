# Python / Import
from __future__ import division
from random import randint
import sys
# rtmidi / Import
import rtmidi_python as rtmidi
# Numpy / Import
import numpy as np
# Kivy / Import
from Cython.Compiler.Errors import message
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock

VERSION = '0.2.3'
TITLE = "Game / Porte ouverte CEFF"
DESCRIPTION = "Game with the Kivy and a LaunchPAD for the controller"

# Constantes OpenGL
WIDTH = Window.width
HEIGHT = Window.height

# Constantes pour le launchPAD
MIDI_ON_LED = 144
MIDI_OFF_LED = 128
MIDI_AUTOMAP_ON = 176
MIDI_GREEN = 0
MIDI_RED = 0
DICO_COLOR = {"White": (0, 0), "Red_FULL": (3, 0), "Red_LOW": (1, 0), "Green_FULL": (0, 3), "Green_LOW": (0, 1),
              "Yellow_FULL": (3, 3)}

isPressed = False

print(sys.version, str(sys.api_version), str(sys.version_info), str(sys.getwindowsversion()), sep=' // ')
print("Version du programme ", VERSION, sep=': ')


class Button:
    def __init__(self, x, y):
        self.isPressed = False
        self.color = None
        self.pos = (x, y)


class ButtonTable:
    def __init__(self):
        self.buttons = np.array([[Button(x=x, y=y) for y in range(9)] for x in range(8)])

    def get_cell(self, x, y):
        return self.buttons[x][y]

    def set_cell(self, x, y, click, color):
        self.buttons[x][y].color = color
        self.buttons[x][y].isPressed = click


class LaunchPAD:
    def __init__(self):
        self.midiOut = rtmidi.MidiOut()
        self.midiIn = rtmidi.MidiIn()
        self.note = None
        self.pad = ButtonTable()
        self.baseColor = None

        if len(self.midiOut.ports) > 1:
            self.midiOut.open_port(1)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

        if len(self.midiIn.ports) > 0:
            self.midiIn.callback = self.callback
            self.midiIn.open_port(0)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

    def init(self, colorDefault):
        # self.baseColor = self.get_led_color(DICO_COLOR["Green_FULL"][0], DICO_COLOR["Green_FULL"][1])
        # self.midiOut.send_message([MIDI_AUTOMAP_ON, 106, self.baseColor])
        # self.baseColor = self.get_led_color(DICO_COLOR["Red_FULL"][0], DICO_COLOR["Red_FULL"][1])
        # self.midiOut.send_message([MIDI_AUTOMAP_ON, 107, self.baseColor])
        # self.baseColor = self.get_led_color(DICO_COLOR["Yellow_FULL"][0], DICO_COLOR["Yellow_FULL"][1])
        # self.midiOut.send_message([MIDI_AUTOMAP_ON, 108, self.baseColor])

        self.baseColor = colorDefault

    def callback(self, message, time_stamp):
        global isPressed
        if message:
            self.note = message
            if message[0] == 144:
                if message[2] == 127:
                    isPressed = True
                elif message[2] == 0:
                    isPressed = False
            # if message[0] == 176 and message[1] == 104:
            #     pass
            #     # self.quit = True
            # elif message[1] == 105 and message[2] == 127:
            #     self.clear()
            # elif message[1] == 106:
            #     self.baseColor = DICO_COLOR["Green_FULL"]
            # elif message[1] == 107:
            #     self.baseColor = DICO_COLOR["Red_FULL"]
            # elif message[1] == 108:
            #     self.baseColor = DICO_COLOR["Yellow_FULL"]
            # else:
            #     self.turn_on_on_press()
            #     pass

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
        self.pad.buttons = np.array([[Button(x=x, y=y) for y in range(9)] for x in range(8)])
        self.init(self.baseColor)

    def turn_on_on_press(self):
        """Allume la LED lorsqu'on presse dessus et l'eteint lorsqu'on reappuie"""
        if self.note[0] == 144 and self.note[2] == 127:
            x = self.note[1] // 16
            y = self.note[1] - (16 * x)

            changeColor = False
            button = self.pad.get_cell(x, y)
            color = self.get_led_color(self.baseColor[0], self.baseColor[1])

            if button.color is not color:
                changeColor = True

            if not button.isPressed or changeColor:
                self.pad.set_cell(x, y, True, color)
                self.midiOut.send_message([MIDI_ON_LED, self.note[1], color])
            elif button.isPressed:
                self.pad.set_cell(x, y, False, color)
                self.midiOut.send_message([MIDI_OFF_LED, self.note[1], color])

    def reset(self):
        """Methode qui d'arrêt complet du PAD"""
        self.midiOut.send_message([176, 0, 0])
        self.midiIn.close_port()
        self.midiOut.close_port()


class Paddle(Widget):
    score = NumericProperty(0)
    posPaddle = ListProperty([])

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            if self.collide_widget(ball):
                vx, vy = ball.velocity
                offset = (ball.center_y - self.center_y) / (self.height / 2)
                bounced = Vector(-1 * vx, vy)
                if bounced.x >= ball.velocity_max[0] or bounced.x <= ball.velocity_max[1]:
                    pass
                else:
                    if bounced.x > 0:
                        bounced.x += ball.velocity_up
                    else:
                        bounced.x -= ball.velocity_up
                ball.velocity = bounced.x, bounced.y + offset

    def init_move(self, first):
        nbrY = 8
        nbrX = 8

        pos_x = (Window.width // 2) // nbrX
        pos_y = Window.height // nbrY

        for i in range(nbrX):
            for j in range(nbrY // 2):
                if first:
                    self.posPaddle.append((pos_x * j, Window.height - pos_y * i))
                else:
                    self.posPaddle.append((Window.width - pos_x * j, pos_y * i))
        print(self.posPaddle)


class Ball(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity_max = (30, -30)
    velocity_up = 0.5

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class Game(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    launchpad = LaunchPAD()
    launchpad.init(DICO_COLOR["Green_FULL"])

    firstTime = True

    # launchpad.midiOut.send_message([MIDI_ON_LED, 32, 51])
    # launchpad.midiOut.send_message([MIDI_ON_LED, 80, 51])
    # launchpad.midiOut.send_message([MIDI_ON_LED, 39, 51])
    # launchpad.midiOut.send_message([MIDI_ON_LED, 87, 51])

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        if Window.width > WIDTH and self.firstTime:
            self.player1.init_move(True)
            self.player2.init_move(False)
            self.firstTime = False

        if isPressed:
            self.move_paddle(self.launchpad.note, self.player1, self.player2)

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if self.ball.y < 0 or self.ball.top > self.height:
            self.ball.velocity_y *= -1

        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, randint(-10, 10)))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, randint(-10, 10)))

    def move_paddle(self, message, player1, player2):
        posNot = [(3, 4), (19, 20), (35, 36), (51, 52), (67, 68), (83, 84), (99, 100), (115, 116)]

        x = message[1] // 16
        y = message[1] - (16 * x)

        # print("x -->", x, "y -->", y)

        if message[1] <= posNot[x][0]:
            print(x + y, " / x -->", player1.posPaddle[y][0], "y -->", player1.posPaddle[y][1])
            player1.x = player1.posPaddle[x * y][0]
            player1.y = player1.posPaddle[x * y][1]
        elif message[1] >= posNot[x][1]:
            player2.x = player2.posPaddle[y][0]
            player2.y = player2.posPaddle[y][1]

class MainApp(App):
    def build(self):
        self.title = TITLE
        Window.fullscreen = "auto"
        game = Game()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


def main():
    """Methode main qui permet d'initialiser l'API MIDI ainsi que le LaunchPAD"""
    window = MainApp()
    window.run()


main()
