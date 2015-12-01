# Variables globales
import globals as G

# import Python function
from random import randint

# import MIDI library
import rtmidi_python as rtmidi

# import Pyglet library
from pyglet import font, resource as rs
from pyglet.window import key
from pyglet.media import Player, SourceGroup
from pyglet.text import *
from pyglet.graphics import *
from pyglet.sprite import *

# Initialisation
rs.path.append('data')
rs.reindex()
font.add_directory('data')

# Ressources
background = rs.image('background.jpg')
paddle = rs.image('paddle.png')
paddleSimple = rs.image('paddleSimple.png')
ball = rs.image('ball.png')
icon = pyglet.image.load('icon.png')
music = pyglet.resource.media('music_background.mp3', False)


# Class Player
class Player(Sprite):
    "Sprite et donnée du joueur"

    # Constructeur
    def __init__(self, LEFTorRIGHT, img, x, y, batch, window):
        super(Player, self).__init__(img=img, x=x, y=y, batch=batch)
        self.NUMBER = LEFTorRIGHT
        self.isPressed = False
        self.colors = None
        self.score = 0
        self.window = window
        self.minHeight = img.height

        self.positions = []
        self.init_pos()

    # Position du PAD sur le plateau de jeu
    def init_pos(self):
        nbrX = 8
        nbrY = 8

        interval_x = self.window.width // nbrX
        interval_y = self.window.height // nbrY

        for i in range(nbrY):
            for j in range(nbrX // 2):
                if self.NUMBER == 0:
                    self.positions.append((j * interval_x, self.window.height - (i * interval_y) - self.minHeight if self.window.height - (i * interval_y) - self.minHeight > 0 else 0))
                if self.NUMBER == 1:
                    self.positions.append((self.window.width - (j * interval_x) - 30, self.window.height - (i * interval_y) - self.minHeight if self.window.height - (i * interval_y) - self.minHeight > 0 else 0))


# Class ball
class Ball(Sprite):
    "Sprite et logique de la balle"

    # Constructeur
    def __init__(self, img, x, y):
        super(Ball, self).__init__(img=img, x=x, y=y)
        self.dx = -(800 / 1000)     # dx = Vitesse X
        self.dy = 0 / 1000          # dy = Vitesse Y
        self.newX = 0
        self.newY = 0
        self.maxBounceAngle = math.pi / 9


# Class PAD
class PAD:
    "Classe pour utiliser le LaunchPAD"

    # Constructeur
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

    # Méthode d'envoie
    def send_message(self, message):
        self.midiOut.send_message(message)

    def resetButton(self):
        self.send_message([176, 0, 0])

    def reset(self):
        """Methode d'arrêt complet du PAD"""
        self.midiOut.send_message([176, 0, 0])
        self.midiIn.close_port()
        self.midiOut.close_port()


class App(pyglet.window.Window):
    "Logique du jeu et classe principale"

    # Constructeur
    def __init__(self):
        super(App, self).__init__(width=1920, height=1200, caption=G.APP_NAME + ' / ' + G.APP_VERSION, resizable=False, fullscreen=G.FULLSCREEN)

        # Initialisation des variables importantes
        self.music_player = pyglet.media.Player()
        self.batch = Batch()
        self.secondPatch = Batch()
        self.keyboard = key.KeyStateHandler()
        self.pad = PAD()

        # Initialisation des labels de scores
        self.player1_score = Label('0', x=(self.width // 2) // 2 + 200, y=1100, font_size=60, font_name='Roboto Mono')
        self.player2_score = Label('0', x=self.width // 2 + (self.width // 2) // 2 - 200, y=1100, font_size=60, font_name='Roboto Mono')

        # Initialisation des 4 joueurs, 2 pour la difficulté "Moyen" et "Difficile" et 2 pour la difficulté "Facile"
        self.P1 = Player(0, paddle, 0, self.height // 2 - paddle.height // 2, self.batch, self)
        self.P2 = Player(1, paddle, self.width - paddle.width, self.height // 2 - paddle.height // 2, self.batch, self)
        self.P3 = Player(0, paddleSimple, 0, self.height // 2 - paddleSimple.height // 2, self.secondPatch, self)
        self.P4 = Player(1, paddleSimple, self.width - paddleSimple.width, self.height // 2 - paddleSimple.height // 2, self.secondPatch, self)

        # Initilialisation de la balle et du menu de jeu
        self.ball = Ball(ball, self.width // 2 - (ball.width // 2), self.height // 2 - (ball.height // 2))
        self.level = Label('Choisissez le niveau', x=self.width // 2, y=self.height // 2 + 300, anchor_x='center', anchor_y='center', font_size=70)
        self.simple = Label('Facile', x=self.width // 2 - 400, y=self.height // 2, anchor_x='center', anchor_y='center', font_size=50, color=(0, 255, 0, 255))
        self.medium = Label('Moyen', x=self.width // 2, y=self.height // 2, anchor_x='center', anchor_y='center', font_size=50, color=(255, 191, 0, 255))
        self.hard = Label('Difficile', x=self.width // 2 + 400, y=self.height // 2, anchor_x='center', anchor_y='center', font_size=50, color=(255, 0, 0, 255))

        self.players = [self.P1, self.P2]

        self.push_handlers(self.keyboard)

        self.pad.midiIn.callback = self.callback

        # Initialise la musique et la lance
        self.looper = SourceGroup(music.audio_format, None)
        self.looper.loop = True
        self.looper.queue(music)
        self.music_player.volume = 1.0
        self.music_player.queue(self.looper)
        self.music_player.play()

        # Initialisation de variables importantes au jeu
        self.niveau = 2
        self.start = False
        self.freeze = True
        self.mysterious = False
        self.canClick = False
        self.ball.radius = 25

        self.init_led()

        # Lance la boucle du jeu
        pyglet.clock.schedule_interval(self.update, 1 / G.MAX_FPS)

    # Reset du plateau du PAD
    def reset_pad_button(self):
        for i in range(0, 8):
            for j in range(0, 8):
                self.pad.send_message([128, i * 16 + j, 0])

    # Logique du niveau 1 pour déplacer les barres
    def level_1(self, message):
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

    # Logique du niveau 2 pour déplacer les barres
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

    # Logique du niveau 3 pour déplacer les barres
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

    # Fonction qui est appelé lorsqu'un évenement est déclenché sur le PAD
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
                        self.init_led_lvl()
                        self.players = [self.P3, self.P4]
                    elif b == 105:
                        self.niveau = 2
                        self.init_led_lvl()
                        self.players = [self.P1, self.P2]
                    else:
                        self.niveau = 3
                        self.init_led_lvl3()
                        self.players = [self.P1, self.P2]
                    self.start = True
                    self.freeze = False

    # Reset de la balle
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

    # Reset des barres
    def reset_paddle(self):
        for p in self.players:
            if p.NUMBER == 0:
                p.x, p.y = 0, self.height // 2 - p.height // 2
            else:
                p.x, p.y = self.width - p.width, self.height // 2 - p.height // 2

    # Reset du plateau de jeu
    def reset_game(self):
        self.start = False
        self.players[0].score = 0
        self.players[1].score = 0
        self.reset_ball()
        self.pad.resetButton()
        self.init_led()
        self.freeze = True

    # Fonction qui met à jour le jeu, l'affichage
    def update(self, dt):
        if self.freeze:
            return 0

        # Calcul le nouveau X et Y par rapport au FPS
        dt *= 1000
        b = self.ball
        b.newX = b.x + b.dx * dt
        b.newY = b.y + b.dy * dt

        paddle1 = self.players[0]
        paddle2 = self.players[1]

        # Relance le jeu si le score est plus grand ou égale à 7
        if self.players[0].score >= 7:
            self.reset_game()

        if self.players[1].score >= 7:
            self.reset_game()

        # Teste les rebonds en Y et renvoie la balle
        if b.newY < 0:
            b.newY = -b.newY
            b.dy = -b.dy
        elif b.newY + b.width > self.height:
            b.newY -= 2 * ((b.newY + b.width) - self.height)
            b.dy = -b.dy

        # Collisions Balle - Barre gauche
        if b.newX < paddle1.x + paddle1.width <= b.x:
            intersectX = paddle1.x + paddle1.width
            intersectY = b.y - ((b.x - (paddle1.x + paddle1.width)) * (b.y - b.newY)) / (b.x - b.newX)
            if paddle1.y - 50 <= intersectY <= paddle1.y + paddle1.height:
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

                # Augmente la vitesse à chaque fois que la barre touche la balle
                b.dx += 0.07

        # Collisions Balle - Barre droite
        if b.newX > paddle2.x - paddle2.width >= b.x:
            intersectX = paddle2.x - paddle2.width
            intersectY = b.y - ((b.x - (paddle2.x - paddle2.width)) * (b.y - b.newY)) / (b.x - b.newX)
            if paddle2.y - 50 <= intersectY <= paddle2.y + paddle2.height:
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

                # Augmente la vitesse à chaque fois que la barre touche la balle
                b.dx -= 0.07

        # Teste si la balle a dépassé la barre gauche et ajoute un point ou le contraire
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

    # Méthode appelé pour faire un rendu sur la fenêtre
    def on_draw(self):
        window.clear()
        background.blit(0, 0)
        if self.start:
            self.player1_score.draw()
            self.player2_score.draw()
            self.ball.draw()
            if self.niveau == 1:
                self.secondPatch.draw()
            else:
                self.batch.draw()
        else:
            self.level.draw()
            self.simple.draw()
            self.medium.draw()
            self.hard.draw()

    #Méthode qui initialise le niveau 1 et 2 sur le PAD
    def init_led_lvl(self):
        for i in range(8):
            for j in range(1):
                note = i * 16 + j
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Green']])

        for i in range(8):
            for j in range(1):
                note = i * 16 + (7 - j)
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Red']])

    #Méthode qui initialise le niveau 3 sur le PAD
    def init_led_lvl3(self):
        for i in range(8):
            for j in range(3):
                note = i * 16 + j
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Green']])

        for i in range(8):
            for j in range(3):
                note = i * 16 + (7 - j)
                self.pad.send_message([self.pad.turnOnLed, note, self.pad.colorLedFlash['Red']])

    # Initialisation des lumières pour choisir le niveau
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

# Méthode qui est lancé au début du script
if __name__ == '__main__':
    window = App()
    window.set_exclusive_mouse()
    window.set_icon(icon)
    window.clear()
    window.flip()
    pyglet.app.run()
    window.pad.reset()
