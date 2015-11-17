# import Python
from random import randint, random
import sys
import math
# import MIDI
import rtmidi_python as rtmidi
# import Pyglet
from builtins import print
from pyglet import font, clock, app, resource as rs
from pyglet.window import key
from pyglet.media import Player, SourceGroup
from pyglet.text import *
from pyglet.graphics import *
from pyglet.sprite import *
# import Numpy
import numpy as np

# VERSION
VERSION = '0.1.0'
TITLE = 'Pong - PAD'

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
        self.dx = 800 / 1000
        self.dy = 1 / 1000
        self.newX = 0
        self.newY = 0
        self.maxBounceAngle = math.pi / 12

# Class for the move
class PAD:
    def __init__(self):
        self.midiOut = rtmidi.MidiOut()
        self.midiIn = rtmidi.MidiIn()

        if len(self.midiOut.ports) > 1:
            self.midiOut.open_port(1)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

        if len(self.midiIn.ports) > 0:
            self.midiIn.open_port(0)
        else:
            sys.exit("Pas d'appareil MIDI trouvé")

    def reset(self):
        """Methode qui d'arrêt complet du PAD"""
        self.midiOut.send_message([176, 0, 0])
        self.midiIn.close_port()
        self.midiOut.close_port()

class Menu:
    pass

class App(pyglet.window.Window):
    def __init__(self):
        super(App, self).__init__(width=1920, height=1200, caption=TITLE + ' / ' + VERSION, resizable=False, fullscreen=True, vsync=True)
        self.pad = PAD()
        self.pad.midiIn.callback = self.callback

        self.looper = SourceGroup(music.audio_format, None)
        self.music_player = pyglet.media.Player()
        self.batch = Batch()
        self.niveau = 2

        self.looper.loop = True
        self.looper.queue(music)

        self.music_player.volume = 1.0
        self.music_player.queue(self.looper)
        #self.music_player.play()

        self.player1_score = Label('0', x=(self.width // 2) // 2 + 200, y=1100, font_size=60, font_name='Roboto Mono')
        self.player2_score = Label('0', x=self.width // 2 + (self.width // 2) // 2 - 200, y=1100, font_size=60, font_name='Roboto Mono')

        self.ball = Ball(ball, self.width // 2 - (ball.width // 2), self.height // 2 - (ball.height // 2), batch=self.batch)
        self.ball.half_x = self.width // 2 - (ball.width // 2)
        self.ball.half_y = self.height // 2 - (ball.height // 2)
        self.players = [Player(0, paddle, 0, self.height // 2 - paddle.height // 2, self.batch, self), Player(1, paddle, self.width - paddle.width, self.height // 2 - paddle.height // 2, self.batch, self)]

        self.paused = False

        self.keys = key.KeyStateHandler()
        pyglet.clock.schedule_interval(self.update, 1 / 60)

    def level_1(self, message):
        pass

    def level_2(self, message):
        nbrButton = 4
        if message[0] == 144:
            x = message[1] // 16
            y = message[1] - (16 * x)

            print(message, x, y, sep=' - ')

            if y < 1:
                self.players[0].x, self.players[0].y = self.players[0].positions[(x * nbrButton) + y]

            if y > 6:
                self.players[1].x, self.players[1].y = self.players[1].positions[(x * nbrButton) + nbrButton + (nbrButton - y) - 1]

    def level_3(self, message):
        nbrButton = 4
        if message[0] == 144:
            x = message[1] // 16
            y = message[1] - (16 * x)

            print(message, x, y, sep=' - ')

            if y < 3:
                self.players[0].x, self.players[0].y = self.players[0].positions[(x * nbrButton) + y]

            if y > 4:
                self.players[1].x, self.players[1].y = self.players[1].positions[(x * nbrButton) + nbrButton + (nbrButton - y) - 1]

    def callback(self, message, dt):
        if self.niveau == 1:
            self.level_1(message)
        elif self.niveau == 2:
            self.level_2(message)
        elif self.niveau == 3:
            self.level_3(message)

    def reset_ball(self, winner):
        self.ball.x, self.ball.y = self.width / 2 - self.ball.width / 2, self.height / 2 - self.ball.height / 2
        if winner == 1:
            self.ball.dx = -(800 / 1000)
        else:
            self.ball.dx = 800 / 1000
        self.ball.dy = 1 / 1000

        self.reset_paddle()

    def reset_paddle(self):
        for p in self.players:
            if p.NUMBER == 0:
                p.x, p.y = 0, self.height // 2 - p.height // 2
            else:
                p.x, p.y = self.width - p.width, self.height // 2 - p.height // 2


    def update(self, dt):
        dt *= 1000
        b = self.ball
        b.newX = b.x + b.dx * dt
        b.newY = b.y + b.dy * dt

        paddle1 = self.players[0]
        paddle2 = self.players[1]

        if b.newY < 0:
            b.newY = -b.newY
            b.dy = -b.dy
        elif b.newY + b.width > self.height:
            b.newY -= 2 * ((b.newY + b.width) - self.height)
            b.dy = -b.dy

        if b.newX < paddle1.x + paddle1.width <= b.x:
            intersectX = paddle1.x + paddle1.width
            intersectY = b.y - ((b.x - (paddle1.x + paddle1.width)) * (b.y - b.newY)) / (b.x - b.newX)
            if paddle1.y <= intersectY <= paddle1.y + paddle1.height:
                relativeIntersectY = (paddle1.y + (paddle1.height / 2)) - intersectY
                bounceAngle = (relativeIntersectY / (paddle1.height / 2)) * (math.pi / 2 - b.maxBounceAngle)
                ballSpeed = math.sqrt(b.dx * b.dx + b.dy * b.dy)
                ballTravelLeft = (b.newY - intersectY) / (b.newY - b.y)
                b.dx = ballSpeed * math.cos(bounceAngle)
                b.dy = ballSpeed * -math.sin(bounceAngle)
                b.newX = intersectX + ballTravelLeft * ballSpeed * math.cos(bounceAngle)
                b.newY = intersectY + ballTravelLeft * ballSpeed * math.sin(bounceAngle)

                b.dx += 0.03

        if b.newX > paddle2.x - paddle2.width >= b.x:
            intersectX = paddle2.x - paddle2.width
            intersectY = b.y - ((b.x - (paddle2.x - paddle2.width)) * (b.y - b.newY)) / (b.x - b.newX)
            if paddle2.y <= intersectY <= paddle2.y + paddle2.height:
                relativeIntersectY = (paddle2.y + (paddle2.height / 2)) - intersectY
                bounceAngle = (relativeIntersectY / (paddle2.height / 2)) * (math.pi / 2 - b.maxBounceAngle)
                ballSpeed = math.sqrt(b.dx * b.dx + b.dy * b.dy)
                ballTravelLeft = (b.newY - intersectY) / (b.newY - b.y)
                b.dx = ballSpeed * math.cos(bounceAngle) * -1
                b.dy = ballSpeed * math.sin(bounceAngle) * -1
                b.newX = intersectX - ballTravelLeft * ballSpeed * math.cos(bounceAngle)
                b.newY = intersectY - ballTravelLeft * ballSpeed * math.sin(bounceAngle)

                b.dx -= 0.03

        if b.newX < 0:
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
        self.player1_score.draw()
        self.player2_score.draw()
        self.batch.draw()


if __name__ == '__main__':
    window = App()
    window.set_exclusive_mouse()
    window.set_icon(icon)
    pyglet.app.run()
    window.pad.reset()