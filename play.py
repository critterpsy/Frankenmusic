# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# python-rtmidi must be installed with its dependecies to play midis
# The backends are 3, as it says in the linux section of this site:
# https://spotlightkid.github.io/python-rtmidi/installation.html#linux
# You also need a midi to wav convertor that can open a port.
# The package timdity is all right for ubuntu.
# After installing with `sudo apt install timdity`
# You can run a daemon once with `timdity -iA`

# %%
from mido import MidiFile
import mido


# %%
mid = MidiFile('midis/VampireKillerCV1.mid', clip=True)
print(mid)


# %%
for track in mid.tracks:
    print(track)


# %%
for msg in mid.tracks[2]:
    print(msg)


# %%
import os

from mido import MidiFile


cv1 = MidiFile('midis/VampireKillerCV1.mid', clip=True)

message_numbers = []
duplicates = []

for track in cv1.tracks:
    if len(track) in message_numbers:
        duplicates.append(track)
    else:
        message_numbers.append(len(track))

for track in duplicates:
    cv1.tracks.remove(track)

cv1.save('midis/new_song.mid')


# %%
import time
import mido
from mido import Message

# mido.set_backend('mido.backends.pygame')

# print(mido.get_output_names())
 
port = mido.open_output('TiMidity:TiMidity port 0 128:0')
 
for note in range(60, 80):
    print(note)
    port.send(Message('note_on', note=note))
    time.sleep(0.1)
    port.send(Message('note_off', note=note))
    time.sleep(0.1)


# %%
import time
import rtmidi

from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

NOTE = 60  # middle C

midiout = rtmidi.MidiOut()

with (midiout.open_port(0) if midiout.get_ports() else
        midiout.open_virtual_port("My virtual output")):
    note_on = [NOTE_ON, NOTE, 112]
    note_off = [NOTE_OFF, NOTE, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)
    time.sleep(0.1)

del midiout

# %%
import mido
from mido import MidiFile

cv1 = MidiFile('midis/VampireKillerCV1.mid', clip=True)

port = mido.open_output('TiMidity:TiMidity port 0 128:0')


for msg in cv1.play():
    port.send(msg)


# %%
import mido
from mido import MidiFile
import asyncio
from mido import Message
port = mido.open_output('TiMidity:TiMidity port 1 128:1')


loop = asyncio.get_event_loop()
queue = asyncio.Queue()


def callback(message):
    loop.call_soon_threadsafe(
        queue.put_nowait, message)


for note in range(60, 80):
    callback(Message('note_on', note=note, time=0.7))
    callback(Message('note_off', note=note, time=0.1))

async def stream():
    while True:
        yield await queue.get()


async for msg in stream():
    asyncio.sleep(msg.time)
    port.send(msg)
# %%
