# import Python
from random import randint
import sys

# import MIDI
import rtmidi_python

# import Pyglet
import select
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

# Score
player1_score = Label('0', x=0, y=0)
player2_score = Label('0', x=0, y=0)

# Class for the Game
class Player(Sprite):
    def __init__(self, LEFTorRIGHT, img, x, y, batch):
        super(Player, self).__init__(img, x, y, batch=batch)
        self.NUMBER = LEFTorRIGHT
        self.isPressed = False
        self.colors = None
        self.score = 0

class Ball(Sprite):
    def __init__(self, img, x, y, batch):
        super(Ball, self).__init__(img=img, x=x, y=y, batch=batch)
        self.dx = 15
        self.dy = randint(-25, 25)

    def reset_ball(self, NUMBER, player1, player2):
        if NUMBER == 0:
            player1.score += 1
            player1_score.text = '' + player1.score
        elif NUMBER == 1:
            player2.score += 1
            player2_score.text = '' + player2.score
        self.x = self.half_x
        self.y = self.half_y
        self.dx = -self.dx
        self.dy = randint(-25, 25)

    def move(self, window):
        self.x += self.dx
        self.y += self.dy

        if self.x + self.width >= window.width:
            self.reset_ball(0, window.players[0], window.players[1])
        elif self.x <= 0:
            self.reset_ball(1, window.players[0], window.players[1])

        if self.y < 0:
            self.dy = -self.dy
            self.y = 0

        if self.y > window.height:
            self.dy = -self.dy
            self.y = window.height - self.height


class App(pyglet.window.Window):
    def __init__(self):
        super(App, self).__init__(width=1920, height=1200, caption=TITLE + ' / ' + VERSION, resizable=False, fullscreen=True, vsync=True)
        self.looper = SourceGroup(music.audio_format, None)
        self.music_player = pyglet.media.Player()
        self.batch = Batch()

        self.looper.loop = True
        self.looper.queue(music)

        self.music_player.volume = 1.0
        self.music_player.queue(self.looper)
        self.music_player.play()

        self.ball = Ball(ball, self.width // 2 - (ball.width // 2), self.height // 2- (ball.height // 2), batch=self.batch)
        self.ball.half_x = self.width // 2 - (ball.width // 2)
        self.ball.half_y = self.height // 2 - (ball.height // 2)
        self.players = [Player(0, paddle, 0, self.height // 2 - paddle.height // 2, self.batch), Player(1, paddle, self.width - paddle.width, self.height // 2 - paddle.height // 2, self.batch)]

        self.paused = False

        self.keys = key.KeyStateHandler()
        pyglet.clock.schedule(self.update)

    def update(self,dt):
        self.ball.move(self)
        pass

    def on_draw(self):
        window.clear()
        background.blit(0, 0)
        self.batch.draw()
        player1_score.draw()
        player2_score.draw()


if __name__ == '__main__':
    window = App()
    window.set_exclusive_mouse()
    window.set_icon(icon)
    pyglet.app.run()


# Class for the PAD

    # # Class logic of the Game
    # class Ball(Move):
    #     def step(self, dt):
    #         super(Ball, self).step(dt)
    #
    #         velocity_x = self.target.max_speed * 10
    #         velocity_y = 0  # self.target.max_speed * 4
    #
    #         self.target.velocity = (velocity_x, velocity_y)
    #
    #
    # # Class of the layer
    # class BackgroundLayer(Layer):
    #     def __init__(self, name=''):
    #         super(BackgroundLayer, self).__init__()
    #         self.pseudo = name
    #         self.img = pyglet.resource.image('background.jpg')
    #
    #     def draw(self):
    #         glPushMatrix()
    #         self.transform()
    #         self.img.blit(0, 0)
    #         glPopMatrix()
    #
    #
    # class GameLayer(Layer):
    #     is_event_handler = True
    #
    #     def __init__(self):
    #         w, h = director.get_window_size()
    #         super(GameLayer, self).__init__()
    #
    #         # Create the Sprite
    #         self.player1 = Sprite(pyglet.resource.image('paddle.png'))
    #         self.player2 = Sprite(pyglet.resource.image('paddle.png'))
    #         self.ball = Sprite(pyglet.resource.image('ball.png'))
    #
    #         # Add cshape property to Sprite
    #         self.player1.cshape = cm.AARectShape(self.player1.position, self.player1.width // 2, self.player1.height // 2)
    #         self.player2.cshape = cm.AARectShape(self.player2.position, self.player2.width // 2, self.player2.height // 2)
    #         self.ball.cshape = cm.CircleShape(self.ball.position, 5)
    #
    #         # Add a collison manager
    #         self.collisionManager = cm.CollisionManagerBruteForce()
    #         self.collisionManager.add(self.ball)
    #         self.collisionManager.add(self.player1)
    #         self.collisionManager.add(self.player2)
    #
    #         # Position the sprite
    #         self.player1.position = 0 + self.player1.width, (h // 2) + (self.player1.height // 2)
    #         self.player2.position = w - self.player2.width, (h // 2) + (self.player2.height // 2)
    #         self.ball.position = (w // 2) - (self.ball.width / 2), (h // 2) + (self.ball.height // 2)
    #
    #         # Init the player
    #         self.player1.positions = np.array([[Player(x, y) for y in range(0, 3)] for x in range(8)])
    #         self.player2.positions = np.array([[Player(x, y) for y in range(4, 8)] for x in range(8)])
    #
    #         # Init the ball
    #         self.ball.max_speed = 35
    #         self.ball.velocity = (0, 0)
    #
    #         # Add the Sprite to the Layer
    #         self.add(self.player1)
    #         self.add(self.player2)
    #         self.add(self.ball)
    #
    #         self.ball.do(Move())
    #         self.schedule(self.update)
    #
    #     def update(self, dt):
    #         self.ball.cshape.center = self.ball.position
    #         self.player1.cshape.center = self.player1.position
    #         self.player2.cshape.center = self.player2.position
    #
    #         for obj in self.collisionManager.objs:
    #             print(obj)
    #
    #         collisions = self.collisionManager.objs_colliding(self.ball)
    #         if collisions:
    #             if self.player1 in collisions:
    #                 print('Player 1 --> Ball')
    #             elif self.player2 in collisions:
    #                 print('Player 2 --> Ball')
    #
    #     def on_quit(self):
    #         director.push(FlipAngular3DTransition(MenuScene(), duration=3))
    #
    #     def on_key_press(self, symbol, modifiers):
    #         if symbol == key.F1:
    #             self.on_quit()
    #
    #
    # # Class menu
    # class MainMenu(Menu):
    #     def __init__(self):
    #         super(MainMenu, self).__init__('Pong - PAD')
    #
    #         self.font_title['font_name'] = 'TRACEROUTE'
    #         self.font_title['font_size'] = 200
    #         self.font_title['color'] = (255, 10, 10, 255)
    #
    #         self.font_item['font_name'] = 'TRACEROUTE'
    #         self.font_item['font_size'] = 60
    #         self.font_item['color'] = (110, 110, 110, 255)
    #
    #         self.font_item_selected['font_name'] = 'TRACEROUTE'
    #         self.font_item_selected['font_size'] = 65
    #         self.font_item_selected['color'] = (110, 110, 110, 255)
    #
    #         self.menu_halign = CENTER
    #         self.menu_valign = CENTER
    #
    #         items = []
    #         items.append(MenuItem('Nouvelle partie', self.on_newGame))
    #         items.append(MenuItem('Options', self.on_options))
    #         items.append(MenuItem('Quitter', self.on_quit))
    #
    #         self.create_menu(items, zoom_in(), zoom_out())
    #
    #     def on_newGame(self):
    #         director.push(FlipAngular3DTransition(GameScene(), duration=3))
    #
    #     def on_options(self):
    #         director.push(FlipAngular3DTransition(OptionsScene(), duration=3))
    #
    #     def on_quit(self):
    #         sys.exit()
    #
    #
    # class OptionsMenu(Menu):
    #     is_event_handler = True
    #
    #     def __init__(self):
    #         super(OptionsMenu, self).__init__('Options')
    #
    #         self.font_title['font_name'] = 'TRACEROUTE'
    #         self.font_title['font_size'] = 140
    #         self.font_title['color'] = (255, 10, 10, 255)
    #
    #         self.font_item['font_name'] = 'TRACEROUTE'
    #         self.font_item['font_size'] = 50
    #         self.font_item['color'] = (110, 110, 110, 255)
    #
    #         self.font_item_selected['font_name'] = 'TRACEROUTE'
    #         self.font_item_selected['font_size'] = 55
    #         self.font_item_selected['color'] = (110, 110, 110, 255)
    #
    #         items = []
    #         self.volumes = ['Mute', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
    #
    #         items.append(MultipleMenuItem('Volume de la musique : ', self.on_music_volume, self.volumes,
    #                                       int(music_player.volume * 10)))
    #         items.append(ToggleMenuItem('Afficher les FPS : ', self.on_show_fps, director.show_FPS))
    #         items.append(MenuItem('Retour', self.on_quit))
    #
    #         self.create_menu(items, zoom_in(), zoom_out())
    #
    #     def on_quit(self):
    #         director.push(FlipAngular3DTransition(MenuScene(), duration=3))
    #
    #     def on_show_fps(self, value):
    #         director.show_FPS = value
    #
    #     def on_music_volume(self, idx):
    #         vol = idx / 10.0
    #         music_player.volume = vol
    #
    #
    # # Class for the Scene
    # class IntroScene(Scene):
    #     def __init__(self, *children):
    #         super().__init__(*children)
    #         self.add(BackgroundLayer(), z=0)
    #
    #
    # class MenuScene(Scene):
    #     def __init__(self, *children):
    #         super(MenuScene, self).__init__(*children)
    #         self.add(BackgroundLayer(), z=0)
    #         self.add(MainMenu(), z=1)
    #
    #
    # class GameScene(Scene):
    #     def __init__(self, *children):
    #         super(GameScene, self).__init__(*children)
    #         self.add(BackgroundLayer(), z=0)
    #         self.add(GameLayer(), z=1)
    #
    #
    # class OptionsScene(Scene):
    #     def __init__(self, *children):
    #         super(OptionsScene, self).__init__(*children)
    #         self.add(BackgroundLayer(), z=0)
    #         self.add(OptionsMenu(), z=1)

    # director.init(width=1920, height=1200, caption=TITLE + ' / ' + VERSION, fullscreen=False, resizable=True,
    #              vsync=True)
    # director.window.set_exclusive_mouse(True)
    # menu = MenuScene()

    # director.window.push_handlers(keys)

    # director.run(menu)
