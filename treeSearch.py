from src.node import Node
from src import Note
import sys
from src.tree import SNode
import logging
import random


logger = logging.getLogger('treeSearch')

"""constants"""
Notes = Note.Notes
sib = Notes.As


class Voice:

    def __init__(self, modo, octave, index=0, _range=1,
                 length=11, plagal=False, debug=False):
        self.index = index
        self.length = length
        self.is_cantus_firmus = (index == 0)
        self.modo = modo % 12 + 12 * octave
        self.floor = self.modo if not plagal else self.modo - 7
        self.ceiling = self.floor + _range * 12
        self.plagal = plagal
        self.pool = []

    def is_cantus(self):
        return self.index == 0

    def range(self):
        octaves = (self.ceiling - self.floor) // 12
        return Note.note_range(self.floor, octaves, **{'add_sib': True,
                               'whites': True})

    def found(self):
        return len(self.pool) > 0

    def start(self):
        if self.is_cantus():
            return [self.modo]
        filter = {'3rd': True}
        return Note.degree(self.modo, 1, self.ceiling - 1, **filter)

    def cadence(self):
        if self.is_cantus():
            return [Note.white_scale(self.modo, 1)]
        if self.index == 1:
            return [self.modo - 1, self.modo + 12]
        note = self.modo
        kwargs = {'ag': note - 2}
        return Note.degree(note=note, n=7, ceiling=self.ceiling, **kwargs)

    def endings(self):
        if self.is_cantus():
            return [self.modo]
        filter = {'major': True}
        return Note.degree(self.modo, n=1, ceiling=self.ceiling, **filter)

    def add(self, node):
        self.pool.append(node)

    def size(self):
        return len(self.pool)

    def get_notes(self, index=None):
        assert(self.pool is not None)
        return self.pool[-1 if index is None else index]

    def __str__(self):
        index = 'cf' if self.index == 0 else self.index
        string = 'modo: {}, value {}'.format(Notes(self.modo%12), self.modo)
        string += '\n\tindex: {}'.format(index)
        string += '\n\tlength: {}'.format(self.length)
        string += '\n\tplagal: {}'.format(self.plagal)
        return string


class TreeSearch:

    def __init__(self, modo=Notes.D, length=11, plagal=False,
                 num_voices=1, debug=False, sequential=False,
                 exhaustive_search=False):
        self.modo = modo.value
        self.length = length
        self.plagal = plagal
        self.num_voices = num_voices
        self.voices = []
        self.sequential = sequential
        self.exhaustive_search = exhaustive_search
        self.debug = debug
        self.parameters = self.Parameters(self)
        logger.debug('%s', self)
        for i in range(num_voices):
            self.add_voice(i, _range=1, octave=i)

    class Parameters:
        def __init__(self, instance, **kwargs):
            kwargs['hiIndex'] = kwargs.get('hiIndex', 1 * instance.length // 2)
            kwargs['disc'] = kwargs.get('disc', 3)
            kwargs['modeRep'] = kwargs.get('modeRep', 3)
            kwargs['variety'] = kwargs.get('variety', 5)
            logger.debug('init parameters: %s', kwargs)
            self.high_index = kwargs.get('hiIndex')
            self.discontinuities = kwargs.get('disc')
            self.modeRep = kwargs.get('modeRep')
            self.variety = kwargs.get('variety')

    def to_chord(self, *args, omit=None):
        '''Build a chord array from all found voices.

        For each voice at index ``i``, picks the sequence at positional
        argument ``args[i]``. If ``i >= len(args)`` (no index passed for
        that voice), the last generated sequence is used (pool[-1]).

        Voices that have not yet produced any result are silently skipped
        and do not appear in the output.

        ``omit`` excludes a specific voice index; used internally during
        search to build the reference chord without the voice being searched.

        Returns a list of ``self.length`` chord snapshots, each a list of
        note values (one per included voice) at that time step.
        '''
        sequences = []
        for i in range(len(self.voices)):
            if omit == i:
                continue
            if not self.voices[i].found():
                continue
            selected = args[i] if i < len(args) else None
            sequences.append(self.voices[i].get_notes(index=selected))

        return [
            [sequences[k].sequence[j] for k in range(len(sequences))]
            for j in range(self.length)
        ]

    def add_voice(self, index, _range, octave):
        voice = Voice(modo=self.modo,
                      octave=octave,
                      index=index,
                      _range=_range,
                      length=self.length)
        logger.debug('adding voice %s', voice)
        try:
            self.voices[index] = voice
        except Exception:
            self.voices.append(voice)

    def push_node(self, index, node):
        '''commit node object to selected voice's pool'''
        self.voices[index].add(node)

    def generate_voices(self):
        '''recursively generate a treesearch using previously generated voices as reference or cantusFirmus'''
        for i in range(0, len(self.voices)):
            firmus = self.voices[0:i]
            self.search_voice(self.voices[i], cf=firmus)

    def _note_name(self, num):
        octave = num // 12
        name = Notes(num % 12).name
        return f"{name}{octave}"

    def display_voice_found(self, voice_index):
        '''Muestra un log limpio de las voces encontradas hasta voice_index'''
        voice = self.voices[voice_index]
        label = "CF" if voice.is_cantus() else f"CP{voice_index}"
        count = voice.size()
        seq = voice.pool[0].sequence if voice.found() else []
        notes = "  ".join(f"{self._note_name(n):>4}" for n in seq)
        print(f"  [{label}] {count} secuencia(s) → {notes}")

        if voice_index > 0:
            cf = self.voices[0]
            if cf.found():
                cf_seq = cf.pool[0].sequence
                cf_notes = "  ".join(f"{self._note_name(n):>4}" for n in cf_seq)
                cp_seq = seq
                cp_notes = "  ".join(f"{self._note_name(n):>4}" for n in cp_seq)
                print(f"  CF  →  {cf_notes}")
                print(f"  CP  →  {cp_notes}")

    def display_voices(self, tree=False, size=3):
        '''display '''
        if not tree:
            for v in self.voices:
                if v.found():
                    print(v.get_notes())
        else:
            for v in self.voices:
                size = min(size, len(v.pool))
                for i in range(size):
                    print(v.pool[i])

    def search_voice(self, voice, cf=None):
        # input()
        voice_index = voice.index
        start_ = voice.start()
        range_ = voice.range()
        cadence_ = voice.cadence()
        endings_ = voice.endings()
        num_voices_ = self.num_voices
        length_ = self.length
        sequential_ = self.sequential
        # exhaustive_search=False (default): stop at the first valid sequence found.
        # exhaustive_search=True: keep exploring and accumulate all valid sequences.
        stop_on_first = not self.exhaustive_search
        chord = self.to_chord(omit=voice_index)

        logger.debug('sequential: %s', sequential_)

        def search(note, depth=0, last_node=None):
            if depth == 0:
                node = Node(voice, note, debug=self.debug, ref=chord)
                last_chord = None
            else:
                node = last_node.create_child(note)
                last_chord = chord[depth - 1] + [last_node.note]
            new_chord = chord[depth] + [node.note]
            # print(' \nexploring node {}'.format(node))
            # print('chord {}'.format(new_chord))
            if not node.is_valid(num_voices_, new_chord, last_chord):
                return
            if depth + 1 == length_:
                if voice_index == 0:
                    if not self.prune_node(node):
                        return
                else:
                    if not self.prune_node(node, disc=3, modeRep=2, variety=5, high=length_//3):
                        return
                logger.debug('PUSHING NODE')
                self.push_node(voice_index, node)
                if stop_on_first:
                    return True
                return
            if depth + 1 == length_ - 2:
                # print('cadence')
                inspect_set = cadence_
            elif depth + 1 == length_ - 1:
                inspect_set = endings_
            else:
                inspect_set = range_

            for n in inspect_set:
                n_ = random.choice(inspect_set) if not sequential_ else n
                if n == node.note and voice_index == 0:
                    continue
                # if voice_index == 1 and n in chord[depth + 1]:
                #     continue
                found = search(note=n_, depth=depth + 1, last_node=node)
                if found and stop_on_first:
                    return True

        for i in range(len(start_)):
            logger.debug('voice %d search start', voice_index)
            found = search(start_[i])
            logger.debug('%d node(s) found for voice %d', voice.size(), voice_index)
            if found:
                # input()
                break
        self.display_voice_found(voice_index)

    def __str__(self):
        return 'search info \n\t modo {}   \n\t sequential {} \
            \n\t exhaustive_search {}'.format(
            self.modo, self.sequential, self.exhaustive_search)

    def prune_node(self, node, **kwargs):

        disc = kwargs.get('disc')
        modeRep = kwargs.get('modeRep')
        variety = kwargs.get('variety')
        high_index = kwargs.get('high')

        if not high_index:
            high_index = self.parameters.high_index
        if not disc:
            disc = self.parameters.discontinuities
        if not modeRep:
            modeRep = self.parameters.modeRep
        if not variety:
            variety = self.parameters.variety
        if kwargs.get('debug'):
            params = {'disc': disc,
                      'modeRep': modeRep,
                      'variety': variety,
                      'hi': high_index}
            logger.debug('prune params: %s', params)

        if node.disc > disc:
            # print('disc > ', disc)
            # input()
            return False
        if node.hiIndex < high_index:
            # print('hiindex <', high_index)
            # input()
            return False
        if len(dict.fromkeys(node.sequence)) < variety:
            # print('variety <', variety)
            # input()
            return False
        if node.modeRep < modeRep:
            # print('mode rep <', modeRep)
            # input()
            return False
        return True



