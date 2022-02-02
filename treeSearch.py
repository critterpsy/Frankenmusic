from node import Node
import Note
import sys
from tree import SNode
import logging
import random


searched_cf = []

serialized_cf = []
js = []
pruned_cf = []
maxDepth = 11
counterP = []
debug_mode = True
debug_break_search = True

logger = logging.getLogger('treeSearch')
logging.basicConfig(filename='example.log', level=logging.DEBUG)
filehandler_dbg = logging.FileHandler(logger.name + '-debug.log', mode='w')

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
        try:
            self.pool.append(node)
        except Exception:
            self.pool = {node}

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
                 tree_search=False):
        self.modo = modo.value
        self.length = length
        self.plagal = plagal
        self.num_voices = num_voices
        self.voices = []
        self.sequential = sequential
        self.tree_search = tree_search
        self.debug = debug
        print(self)
        for i in range(num_voices):
            self.add_voice(i, _range=1, octave=i)

    class Parameters:
        def __init__(self, instance, **kwargs):
            print('init paramters')
            kwargs['hiIndex'] = kwargs.get('hiIndex', 1 * instance.length // 2)
            kwargs['disc'] = kwargs.get('disc', 3)
            kwargs['modeRep'] = kwargs.get('modeRep', 3)
            kwargs['variety'] = kwargs.get('variety', 5)
            print(kwargs)
            self.high_index = kwargs.get('hiIndex')
            self.discontinuities = kwargs.get('disc')
            self.modeRep = kwargs.get('modeRep')
            self.variety = kwargs.get('variety')

    def to_chord(self, *args, omit=None):
        '''selects a sequence from each voice's tree, default sequence is last generated, then creates a chord array '''
        chord = []
        sequences = []
        for i in range(len(self.voices)):
            if omit == i:
                continue
            try:
                selected = args[i]
            except Exception:
                selected = None
            voice = self.voices[i]
            try:
                sequences.append(voice.get_notes(index=selected))
            except Exception:
                pass

        for j in range(self.length):
            ch = []
            for i in range(len(sequences)):
                ch.append(sequences[i].sequence[j])
            chord.append(ch)
        # input()
        return chord

    def add_voice(self, index, _range, octave):
        voice = Voice(modo=self.modo,
                      octave=octave,
                      index=index,
                      _range=_range,
                      length=self.length)
        print('adding voice {}'.format(voice))
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

    # def generate_second_species(self):
    #     self.search_voice(self.voices[0])
    #     cf = self.voices.get
    #     for note in self.voices[]

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
        found_break = not self.tree_search
        chord = self.to_chord(omit=voice_index)

        print(sequential_)

        # print(range_)

        # print(cadence_)

        test_cf = [2,5,3,2,7,5,9,7,5,4,2]
        test_cf = [2,5,4,2,7,5,9,7,5,4,2]
        test_cp = [9,9,7,9,11,12,12,11,14,13,14]
        test_cp = test_cf = None

        def search(note, depth=0, last_node=None):
            if test_cp and voice_index != 0:
                note = test_cp[depth]
            elif test_cf and voice_index == 0:
                note = test_cf[depth]
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
                print('---------------------------')
                return
            if depth + 1 == length_:
                if voice_index == 0:
                    if not self.prune_node(node):
                        return
                else:
                    if not self.prune_node(node, disc=3, modeRep=2, variety=5, high=length_//3):
                        return
                print('PUSHING NODE')
                self.push_node(voice_index, node)
                if found_break:
                    return True
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
                if found and found_break:
                    return True

        for i in range(len(start_)):
            print('\nvoice {} search start'.format(voice_index))
            found = search(start_[i])
            print('{} node(s) found for voice {}'.format(voice.size(),
                                                       voice_index))
            if found:
                # input()
                break
        self.display_voices()

    def __str__(self):
        return 'search info \n\t modo {}   \n\t sequential {} \
            \n\t treeSearch {}'.format(
            self.modo, self.sequential, self.tree_search)

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
            print(params)
            input()

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



def main():

    new_search = TreeSearch(modo=Notes.D, length=11, plagal=False,
                            tree_search=False, num_voices=2, debug=False,
                            sequential=(False))
    params = {}
    new_search.parameters = TreeSearch.Parameters(new_search, **params)
    new_search.generate_voices()


if __name__ == '__main__':
    main()
