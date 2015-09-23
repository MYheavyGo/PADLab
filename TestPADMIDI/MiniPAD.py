"""midiOut = rtmidi2.MidiOut()
midiIn = rtmidi2.MidiIn()

#print(rtmidi2.get_in_ports())
# print(rtmidi2.get_out_ports())


def callback(message, time_stamp):
    print(message, time_stamp)


midiIn.callback = callback

midiOut.open_port(0)
midiIn.open_port(0)

midiOut.send_noteon(0, 48, 100)
midi_out = rtmidi_python.MidiOut()
available_ports = midi_out.ports

print available_ports

if available_ports:
    midi_out.open_port(0)
else:
    midi_out.open_virtual_port("My virtual port")

note_on = [0x90, 60, 112]
note_off = [0x80, 60, 0]
midi_out.send_message(note_on)
time.sleep(0.5)
midi_out.send_message(note_off)

del midi_out
"""

# Pauli Laine December 2010
# Distribute and modify freely

import time
import random
import pygame
import pygame.midi

# Initialize
pygame.init()
time.sleep(0.2)
pygame.midi.init()
output_id = pygame.midi.get_default_output_id()
print 'output', output_id
MidiOut = pygame.midi.Output(0, 0)


class Scheduler:
    def __init__(self):
        # Here we have a small scheduling ring buffer with 4 bars each with 192 resolution
        # 192 resolution seems to be good enough for normal purposes
        self.sixe = int(192 * 4)
        self.onlist = []
        # Note_ons and note_offs in separate lists makes sorting non-necessary
        for n in range(self.sixe):
            tmp = []
            self.onlist.append(tmp)
        self.offlist = []
        for n in range(self.sixe):
            tmp = []
            self.offlist.append(tmp)

    def insertnote(self, note):
        posit = note.startp % self.sixe
        tmpnode = self.onlist[posit % len(self.onlist)]
        tmpnode.append(note)
        self.onlist[posit] = tmpnode

    def insertnoteoff(self, note):
        posit = note.endp % self.sixe
        tmpnode = self.offlist[posit % len(self.onlist)]
        tmpnode.append(note)
        self.offlist[posit] = tmpnode

    def putnote(self, note):
        posit = note.startp % self.sixe
        endposit = note.endp % self.sixe
        self.insertnote(note)
        self.insertnoteoff(note)

    def handletick(self, posit):
        posit %= self.sixe
        tmpoff = self.offlist[posit]
        tmpon = self.onlist[posit]
        self.onlist[posit] = []
        self.offlist[posit] = []
        self.playticks(tmpoff, tmpon)

    def playticks(self, noteoffs, noteons):
        # Noteoffs first so as to avoid 'insta_kill' of a unisono note
        for note in noteoffs:
            MidiOut.write([[[0x90 + note.chan, note.pitch, 0], pygame.midi.time()]])

        for note in noteons:
            MidiOut.write([[[0x90 + note.chan, note.pitch, note.dyn], pygame.midi.time()]])


# Notes with same startp will play simultaneously, as chords
# Note.endp controls the duration of the note
# startp and endp are 'ticks' - time interval controlled by
# pygame.time.wait() between calls to scheduler.handletick

class Note:
    def __init__(self):
        self.startp, self.endp = 0, 0
        self.dyn, self.chan = 65, 0
        self.pitch = 60


# Make a scheduler instance
s = Scheduler()


def testmidi():
    globtick = 0
    for k in range(121):

        if (k % 3 == 0):
            n = Note()
            testpitch = k % 7 + (k / 7)  # just some mod-stuff to add variety to pitches
            n.pitch = 34 + ((testpitch + 30) % 60)

            ## Note starttime and endtime
            n.startp = globtick + (1 + (3 * (k % 8)))  # some variety to rhythms
            n.endp = globtick + (8 + (3 * (k % 8)))  # listen for chords

            # Note is appended to scheduler to a place determined by note.startp
            s.putnote(n)

            # Handle Note.startp's and endp's positioned in current tick
        s.handletick(globtick)

        globtick += 1
        # Adjust this to control tempo
        pygame.time.wait(20)

    # Ensure that all notes are ended
    for k in range(23):
        s.handletick(globtick)
        globtick += 1
        pygame.time.wait(20)


def testmidi_random():
    globtick = 0
    for k in range(121):
        n = Note()
        n.pitch = random.randint(36, 72)

        # Note starttime and endtime
        stara = random.randint(1, 12)
        dura = random.randint(2, 8)
        n.startp = globtick + stara
        n.endp = globtick + stara + dura
        n.dyn = random.randint(30, 90)
        s.putnote(n)


        # Handle Note.startp's and endp's positioned in current tick
        s.handletick(globtick)

        globtick += 1
        # Adjust this to control tempo
        pygame.time.wait(180)

    # Ensure that all notes are ended
    for k in range(23):
        s.handletick(globtick)
        globtick += 1
        pygame.time.wait(80)


# testmidi()
testmidi_random()
