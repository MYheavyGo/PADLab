# import Python
import sys
# import MIDI
import rtmidi_python

# import Pyglet
import pyglet
from pyglet import font
from pyglet.window import key, mouse
from pyglet.media import Player
from pyglet.gl import *
# import Cocos2D
from cocos.director import director
from cocos.layer import *
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import *
from cocos.menu import *
from cocos.text import *

# VERSION
VERSION = '0.0.5'
TITLE = 'Pong - PAD'


# Class logic of the Game
class Ball(Move):
    def step(self, dt):
        super(Ball, self).step(dt)

        velocity_x = self.target.max_speed * 4
        velocity_y = self.target.max_speed * 4

        self.target.velocity = (velocity_x, velocity_y)


# class of the layer
class BackgroundLayer(Layer):
    def __init__(self, name=''):
        super(BackgroundLayer, self).__init__()
        self.pseudo = name
        self.img = pyglet.resource.image('background.jpg')

    def draw(self):
        glPushMatrix()
        self.transform()
        self.img.blit(0, 0)
        glPopMatrix()


class GameLayer(Layer):
    is_event_handler = True

    def __init__(self):
        w, h = director.get_window_size()
        super(GameLayer, self).__init__()

        # Create the Sprite
        self.player1 = Sprite(pyglet.resource.image('paddle.png'))
        self.player2 = Sprite(pyglet.resource.image('paddle.png'))
        self.ball = Sprite(pyglet.resource.image('ball.png'))

        # Position the sprite
        self.player1.position = 0 + self.player1.width, (h / 2) - (self.player1.height / 2)
        self.player2.position = 1920 - self.player2.width, (h / 2) - (self.player2.height / 2)
        self.ball.position = (w / 2) - (self.ball.width / 2), (h / 2) - (self.ball.height / 2)

        # Init the Sprite
        self.ball.max_speed = 35
        self.ball.velocity = (0, 0)

        # Add the Sprite to the Layer
        self.add(self.player1)
        self.add(self.player2)
        self.add(self.ball)

        # Add the event to the Sprite
        self.ball.do(Ball())

    def on_quit(self):
        director.push(FlipAngular3DTransition(MenuScene(), duration=3))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F1:
            self.on_quit()


# class menu
class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Pong - PAD')

        self.font_title['font_name'] = 'TRACEROUTE'
        self.font_title['font_size'] = 200
        self.font_title['color'] = (255, 10, 10, 255)

        self.font_item['font_name'] = 'TRACEROUTE'
        self.font_item['font_size'] = 60
        self.font_item['color'] = (110, 110, 110, 255)

        self.font_item_selected['font_name'] = 'TRACEROUTE'
        self.font_item_selected['font_size'] = 65
        self.font_item_selected['color'] = (110, 110, 110, 255)

        self.menu_halign = CENTER
        self.menu_valign = CENTER

        items = []
        items.append(MenuItem('Nouvelle partie', self.on_newGame))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Quitter', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def on_newGame(self):
        director.push(FlipAngular3DTransition(GameScene(), duration=3))

    def on_options(self):
        director.push(FlipAngular3DTransition(OptionsScene(), duration=3))

    def on_quit(self):
        sys.exit()


class OptionsMenu(Menu):
    is_event_handler = True

    def __init__(self):
        super(OptionsMenu, self).__init__('Options')

        self.font_title['font_name'] = 'TRACEROUTE'
        self.font_title['font_size'] = 140
        self.font_title['color'] = (255, 10, 10, 255)

        self.font_item['font_name'] = 'TRACEROUTE'
        self.font_item['font_size'] = 50
        self.font_item['color'] = (110, 110, 110, 255)

        self.font_item_selected['font_name'] = 'TRACEROUTE'
        self.font_item_selected['font_size'] = 55
        self.font_item_selected['color'] = (110, 110, 110, 255)

        items = []
        self.volumes = ['Mute', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']

        items.append(MultipleMenuItem('Volume de la musique : ', self.on_music_volume, self.volumes,
                                      int(music_player.volume * 10)))
        items.append(ToggleMenuItem('Afficher les FPS : ', self.on_show_fps, director.show_FPS))
        items.append(MenuItem('Retour', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def on_quit(self):
        director.push(FlipAngular3DTransition(MenuScene(), duration=3))

    def on_show_fps(self, value):
        director.show_FPS = value

    def on_music_volume(self, idx):
        vol = idx / 10.0
        music_player.volume = vol


# class for the Scene
class IntroScene(Scene):
    def __init__(self, *children):
        super().__init__(*children)
        self.add(BackgroundLayer(), z=0)


class MenuScene(Scene):
    def __init__(self, *children):
        super(MenuScene, self).__init__(*children)
        self.add(BackgroundLayer(), z=0)
        self.add(MainMenu(), z=1)


class GameScene(Scene):
    def __init__(self, *children):
        super(GameScene, self).__init__(*children)
        self.add(BackgroundLayer(), z=0)
        self.add(GameLayer(), z=1)


class OptionsScene(Scene):
    def __init__(self, *children):
        super(OptionsScene, self).__init__(*children)
        self.add(BackgroundLayer(), z=0)
        self.add(OptionsMenu(), z=1)


if __name__ == '__main__':
    pyglet.resource.path.append('data')
    pyglet.resource.reindex()
    font.add_directory('data')

    director.init(width=1920, height=1200, caption=TITLE + ' / ' + VERSION, fullscreen=True, resizable=True, vsync=True)
    director.window.set_exclusive_mouse(True)

    icon = pyglet.resource.image('icon.png')
    music = pyglet.resource.media('music_background.mp3', False)
    looper = pyglet.media.SourceGroup(music.audio_format, None)
    looper.loop = True
    looper.queue(music)

    music_player = Player()
    music_player.volume = 1.0
    music_player.queue(looper)
    music_player.play()

    keys = key.KeyStateHandler()
    # intro = IntroScene()
    menu = MenuScene()

    director.window.push_handlers(keys)

    director.run(menu)
