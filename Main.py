# Globales
import globals as G
# import Python
from random import randint, random
import sys
import math
# import MIDI
import rtmidi_python as rtmidi
# import Pyglet
from pyglet import font, clock, app, resource as rs
from pyglet.window import key
from pyglet.media import Player, SourceGroup
from pyglet.text import *
from pyglet.graphics import *
from pyglet.sprite import *
# import Numpy
import numpy as np
import matplotlib.pyplot as plt

# Initialisation
rs.path.append('data')
rs.reindex()
font.add_directory('data')

# Ressources
background = rs.image('background.jpg')
paddle = rs.image('paddle.png')
ball = rs.image('ball.png')
icon = pyglet.image.load('icon.png')
music = pyglet.resource.media('music_background.mp3', False)


# Class for the Game
class Player(Sprite):
    def __init__(self, LEFTorRIGHT, img, x, y, batch, window):
        super(Player, self).__init__(img=img, x=x, y=y, batch=batch)
        self.NUMBER = LEFTorRIGHT
        self.isPressed = False
        self.colors = None
        self.score = 0
        self.window = window

        self.positions = []
        self.init_pos()

    def init_pos(self):
        nbrX = 8
        nbrY = 8

        interval_x = self.window.width // nbrX
        interval_y = self.window.height // nbrY

        for i in range(nbrY):
            for j in range(nbrX // 2):
                if self.NUMBER == 0:
                    self.positions.append((j * interval_x, self.window.height - (i * interval_y) - paddle.height if self.window.height - (i * interval_y) - paddle.height > 0 else 0))
                if self.NUMBER == 1:
                    self.positions.append((self.window.width - (j * interval_x) - 30, self.window.height - (i * interval_y) - paddle.height if self.window.height - (i * interval_y) - paddle.height > 0 else 0))


class Ball(Sprite):
    def __init__(self, img, x, y, batch):
        super(Ball, self).__init__(img=img, x=x, y=y, batch=batch)
        self.dx = -(800 / 1000)
        self.dy = 0 / 1000
        self.newX = 0
        self.newY = 0
        self.maxBounceAngle = math.pi / 8


# Class for the move
class PAD:
    def __init__(self):
        self.midiOut = rtmidi.MidiOut()
        self.midiIn = rtmidi.MidiIn()
        self.colorLed = {'None': 12, 'Red': 15, 'Amber': 63, 'Yellow': 62, 'Green': 60}
        self.colorLedFlash = {'Red': 11, 'Amber': 59, 'Yellow': 58, 'Green': 56}
        self.buttonLevel = [104, 105, 106]
        self.turnOnLed = 144
        self.turnOnAutomap = 176

        if len(self.midiOut.ports) > 1:
            self.midiOut.open_port(1)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

        if len(self.midiIn.ports) > 0:
            self.midiIn.open_port(0)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

    def send_message(self, message):
        self.midiOut.send_message(message)

    def resetButton(self):
        self.send_message([176, 0, 0])

    def reset(self):
        """Methode qui d'arrêt complet du PAD"""
        self.midiOut.send_message([176, 0, 0])
        self.midiIn.close_port()
        self.midiOut.close_port()


class App(pyglet.window.Window):
    def __init__(self):
        super(App, self).__init__(width=1920, height=1200, caption=G.APP_NAME + ' / ' + G.APP_VERSION, resizable=False, fullscreen=G.FULLSCREEN)
        self.music_player = pyglet.media.Player()
        self.batch = Batch()
        self.keyboard = key.KeyStateHandler()
        self.pad = PAD()

        self.player1_score = Label('0', x=(self.width // 2) // 2 + 200, y=1100, font_size=60, font_name='Roboto Mono')
        self.player2_score = Label('0', x=self.width // 2 + (self.width // 2) // 2 - 200, y=1100, font_size=60, font_name='Roboto Mono')
        self.players = [Player(0, paddle, 0, self.height // 2 - paddle.height // 2, self.batch, self), Player(1, paddle, self.width - paddle.width, self.height // 2 - paddle.height // 2, self.batch, self)]
        self.ball = Ball(ball, self.width // 2 - (ball.width // 2), self.height // 2 - (ball.height // 2), batch=self.batch)
        self.level = Label('Choisissez le niveau', x=self.width // 2, y=self.height // 2 + 300, anchor_x='center', anchor_y='center', font_size=70)
        self.simple = Label('Facile', x=self.width // 2 - 400, y=self.height // 2, anchor_x='center', anchor_y='center', font_size=50, color=(0, 255, 0, 255))
        self.medium = Label('Moyen', x=self.width // 2, y=self.height // 2, anchor_x='center', anchor_y='center', font_size=50, color=(255, 191, 0, 255))
        self.hard = Label('Difficile', x=self.width // 2 + 400, y=self.height // 2, anchor_x='center', anchor_y='center', font_size=50, color=(255, 0, 0, 255))

        self.push_handlers(self.keyboard)

        self.pad.midiIn.callback = self.callback

        self.looper = SourceGroup(music.audio_format, None)
        self.looper.loop = True
        self.looper.queue(music)

        self.music_player.volume = 1.0
        self.music_player.queue(self.looper)
        # self.music_player.play()

        self.niveau = 2
        self.start = False
        self.freeze = True
        self.mysterious = False
        self.canClick = False

        self.ball.radius = 25

        self.init_led()

        pyglet.clock.schedule_interval(self.update, 1 / G.MAX_FPS)

    def level_1(self, message):
        #if not self.canClick:
        #    return 0

        nbrButton = 4
        if message[0] == 144:
            x = message[1] // 16
            y = message[1] - (16 * x)

            if y > 7:
                return 0

            if y < 1:
                self.players[0].x, self.players[0].y = self.players[0].positions[(x * nbrButton) + y]
                self.canClick = False

            if y > 6:
                self.players[1].x, self.players[1].y = self.players[1].positions[(x * nbrButton) + nbrButton + (nbrButton - y) - 1]
                self.canClick = False

    def level_2(self, message):
        nbrButton = 4
        if message[0] == 144:
            x = message[1] // 16
            y = message[1] - (16 * x)

            if y > 7:
                return 0

            if y < 1:
                self.players[0].x, self.players[0].y = self.players[0].positions[(x * nbrButton) + y]

            if y > 6:
                self.players[1].x, self.players[1].y = self.players[1].positions[(x * nbrButton) + nbrButton + (nbrButton - y) - 1]

    def level_3(self, message):
        nbrButton = 4
        if message[0] == 144:
            x = message[1] // 16
            y = message[1] - (16 * x)

            if y > 7:
                return 0

            if y < 3:
                self.players[0].x, self.players[0].y = self.players[0].positions[(x * nbrButton) + y]

            if y > 4:
                self.players[1].x, self.players[1].y = self.players[1].positions[(x * nbrButton) + nbrButton + (nbrButton - y) - 1]

    def callback(self, message, dt):
        if self.start:
            if self.freeze is not True:
                if self.niveau == 1:
                    self.level_1(message)
                if self.niveau == 2:
                    self.level_2(message)
                elif self.niveau == 3:
                    self.level_3(message)
                if message[1] == 111 and message[0] == 176:
                    self.reset_game()
        else:
            for b in self.pad.buttonLevel:
                if message[1] == b:
                    if b == 104:
                        self.niveau = 1
                    elif b == 105:
                        self.niveau = 2
                        self.init_led_lvl2()
                    else:
                        self.niveau = 3
                        self.init_led_lvl3()
                    self.start = True
                    self.freeze = False

    def reset_ball(self, winner=2):
        self.ball.x, self.ball.y = self.width / 2 - self.ball.width / 2, self.height / 2 - self.ball.height / 2
        if winner == 2:
            r = randint(0, 2)
            if r == 0:
                self.ball.dx = 800 / 1000
            elif r == 1:
                self.ball.dx = -800 / 1000
        elif winner == 1:
            self.ball.dx = 800 / 1000
        elif winner == 0:
            self.ball.dx = -800 / 1000

        self.ball.dy = 0 / 1000
        self.reset_paddle()

    def reset_paddle(self):
        for p in self.players:
            if p.NUMBER == 0:
                p.x, p.y = 0, self.height // 2 - p.height // 2
            else:
                p.x, p.y = self.width - p.width, self.height // 2 - p.height // 2

    def reset_game(self):
        self.start = False
        self.players[0].score = 0
        self.players[1].score = 0
        self.reset_ball()
        self.pad.resetButton()
        self.init_led()
        self.freeze = True

    def calcul_pente(self):
        a = self.ball.dx
        b = self.ball.dy
        x = 0
        m = b / a
        h = self.ball.newY - self.ball.y
        print(h)
        if self.ball.dx < 0:
            x = 30
            y = m * x + h
        else:
            x = 1890
            y = m * x + h

        if y < 0:
            y += 575

        if self.ball.x > 1700 or self.ball.x < 210:
            self.Point = x, y
            return True

        return False

    def update(self, dt):
        if self.freeze:
            return 0

        dt *= 1000
        p = None
        b = self.ball
        b.newX = b.x + b.dx * dt
        b.newY = b.y + b.dy * dt

        paddle1 = self.players[0]
        paddle2 = self.players[1]

        if self.players[0].score >= 10:
            self.reset_game()

        if self.players[1].score >= 10:
            self.reset_game()

        if b.newY < 0:
            b.newY = -b.newY
            b.dy = -b.dy
        elif b.newY + b.width > self.height:
            b.newY -= 2 * ((b.newY + b.width) - self.height)
            b.dy = -b.dy

        if self.niveau == 1:
            self.mysterious = self.calcul_pente()

        if self.mysterious:
            print(self.Point)

        if b.newX < paddle1.x + paddle1.width <= b.x:
            intersectX = paddle1.x + paddle1.width
            intersectY = b.y - ((b.x - (paddle1.x + paddle1.width)) * (b.y - b.newY)) / (b.x - b.newX)
            if paddle1.y <= intersectY <= paddle1.y + paddle1.height:
                relativeIntersectY = (paddle1.y + (paddle1.height / 2)) - intersectY
                b.bounceAngle = (relativeIntersectY / (paddle1.height / 2)) * (math.pi / 2 - b.maxBounceAngle)
                ballSpeed = math.sqrt(b.dx * b.dx + b.dy * b.dy)
                if b.newY - b.y != 0:
                    ballTravelLeft = (b.newY - intersectY) / (b.newY - b.y)
                else:
                    ballTravelLeft = 0
                b.dx = ballSpeed * math.cos(b.bounceAngle)
                b.dy = ballSpeed * -math.sin(b.bounceAngle)
                b.newX = intersectX + ballTravelLeft * ballSpeed * math.cos(b.bounceAngle)
                b.newY = intersectY + ballTravelLeft * ballSpeed * math.sin(b.bounceAngle)

                b.dx += 0.07

        if b.newX > paddle2.x - paddle2.width >= b.x:
            intersectX = paddle2.x - paddle2.width
            intersectY = b.y - ((b.x - (paddle2.x - paddle2.width)) * (b.y - b.newY)) / (b.x - b.newX)
            if paddle2.y - 300 <= intersectY <= paddle2.y + paddle2.height:
                relativeIntersectY = (paddle2.y + (paddle2.height / 2)) - intersectY
                b.bounceAngle = (relativeIntersectY / (paddle2.height / 2)) * (math.pi / 2 - b.maxBounceAngle)
                ballSpeed = math.sqrt(b.dx * b.dx + b.dy * b.dy)
                if b.newY - b.y != 0:
                    ballTravelLeft = (b.newY - intersectY) / (b.newY - b.y)
                else:
                    ballTravelLeft = 0
                b.dx = ballSpeed * math.cos(b.bounceAngle) * -1
                b.dy = ballSpeed * math.sin(b.bounceAngle) * -1
                b.newX = intersectX - ballTravelLeft * ballSpeed * math.cos(b.bounceAngle)
                b.newY = intersectY - ballTravelLeft * ballSpeed * math.sin(b.bounceAngle)

                b.dx -= 0.07

        if b.newX < -100:
            paddle2.score += 1
            self.reset_ball(0)
            return
        elif b.newX + b.width > self.width + 100:
            paddle1.score += 1
            self.reset_ball(1)
            return

        self.player1_score.text = str(self.players[0].score)
        self.player2_score.text = str(self.players[1].score)

        b.x = b.newX
        b.y = b.newY

    def on_draw(self):
        window.clear()
        background.blit(0, 0)
        if self.start:
            self.player1_score.draw()
            self.player2_score.draw()
            self.batch.draw()
        else:
            self.level.draw()
            self.simple.draw()
            self.medium.draw()
            self.hard.draw()

    def init_led_lvl2(self):
        for i in range(8):
            for j in range(1):
                note = i * 16 + j
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Green']])

        for i in range(8):
            for j in range(1):
                note = i * 16 + (7 - j)
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Red']])

    def init_led_lvl3(self):
        for i in range(8):
            for j in range(3):
                note = i * 16 + j
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Green']])

        for i in range(8):
            for j in range(3):
                note = i * 16 + (7 - j)
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Red']])

    def init_led(self):
        i = 0
        for b in self.pad.buttonLevel:
            if i == 0:
                color = self.pad.colorLed['Green']
            elif i == 1:
                color = self.pad.colorLed['Amber']
            else:
                color = self.pad.colorLed['Red']
            self.pad.send_message([self.pad.turnOnAutomap, b, color])
            i += 1


if __name__ == '__main__':
    window = App()
    window.set_exclusive_mouse()
    window.set_icon(icon)
    window.clear()
    window.flip()
    pyglet.app.run()
    window.pad.reset()
