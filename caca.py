import mido
from mido import MidiFile
import asyncio
from mido import Message
port = mido.open_output('TiMidity:TiMidity port 1 128:1')
 
 
async def playAsync():
    for note in range(60, 80):
        print(note)
        port.send(Message('note_on', note=note))
        await asyncio.sleep(1.9)
        port.send(Message('note_off', note=note))
        await asyncio.sleep(0.1)
