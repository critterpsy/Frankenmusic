from Note import Notes, Diatonic
import Note
import failureCases
import mathutils as mth
from termcolor import colored

'''haciendo el arbol al reves, index = 1,
    representa penultima nota'''
'''debe ser 2ndo grado en el cantusFirmus y sensible para
contrapunto, sensible = modo - 1, en la escala cromatica y diat'''

f_ = failureCases
sib = Notes.As.value


class Node:
    def __init__(self, voice, note=None, is_root=True, debug=False, ref=None):
        self.voice = voice
        self.note = note
        self.debug = debug
        if is_root:
            self.ref = ref
            self.root_node = self
            self.index = 0
            self.sequence = [self.note]
            self.pivot = 0
            self.parent = None
            self.high = self.note
            self.disc = 0
            self.hiIndex = 0
            self.modeRep = 1
            if self.debug:
                self.failures = ['']

    def length(self):
        return self.voice.length

    def modo(self):
        return self.voice.modo

    def ceiling(self):
        return self.voice.ceiling

    def voice_index(self):
        return self.voice.index

    def is_cantus_firmus(self):
        return self.voice.is_cantus_firmus()

    def create_child(self, note):
        child = Node(voice=self.voice, is_root=False)
        child.ref = self.ref
        child.note = note
        child.index = self.index + 1
        child.sequence = self.sequence.copy()
        child.sequence.append(note)
        child.pivot = self.pivot
        child.debug = self.debug
        child.parent = self.note
        if note == self.sequence[0]:
            child.modeRep = self.modeRep + 1
        else:
            child.modeRep = self.modeRep
        if note > self.high:
            child.hiIndex = self.index + 1
            child.high = note
        else:
            child.hiIndex = self.hiIndex
            child.high = self.high
        if abs(note - self.note) > 2:
            child.disc = self.disc + 1
        else:
            child.disc = self.disc
        if child.debug:
            child.failures = self.failures.copy()
        return child

    def equals(self, note):
        return Note.equals(self.note, note)

    def is_valid(self, num_voices, chord, lastChord=None):
        cantus_firmus = self.voice.index == 0
        if cantus_firmus:
            return self.valid_cf()
        # input()
        return self.valid_cf() and self.valid_cp(chord, lastChord)

    def sensible(self):
        if self.equals(Notes.B) or self.equals(Notes.E):
            return self.note + 1
        return self.note - 1

    def jump(self):
        if self.index == 0:
            return 'NaN'
        return self.note - self.parent

    def check_chord(self, chord, num_voices):
        '''check if notes in chord are in harmonic relation'''
        print('checkchord!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        Note.print_chord(chord)
        print(self.ref)
        # input()
        if not Note.valid_chord(chord):
            print('invalid chord')
            # input()
            return False
        print('valid chord')
        # input()
        root = self.voice.modo
        ceiling = self.voice.ceiling

        if self.index == 0:
            filter = {'major': True}
            chord_ = Note.chord(root, ceiling, **filter)
            return Note.in_chord(self.note, chord_)

        elif self.index == self.length() - 1:
            filter = {'3rd': True}
            chord_ = Note.chord(root, ceiling, **filter)
            return Note.in_chord(self.note, chord_)

        elif self.index == self.length() - 2:
            kwargs = {'ag': root + 10}
            chord_ = Note.degree(root, 7, ceiling, **kwargs)
            print('----------------------------------------------')
            print(chord_)
            print(Note.print_chord(chord_))
            if not Note.in_chord(self.note, chord_):
                return False
            top_voice = (self.voice.index == num_voices - 1)
            if top_voice:
                sensible = root - 1
                return Note.in_chord(sensible, chord)
            return True
        return True

    def check_direct5(self, voice1, voice2):
        index = self.index
        if index == 0:
            return True
        move1 = voice1[index] - voice1[index - 1]
        move2 = voice2[index] - voice2[index - 1]
        direct = mth.sign(move1) == mth.sign(move2)
        interval = Note.interval(voice1[index - 1], voice2[index - 1])

        if interval == 7 and direct:
            return False
        return True

    def check_direct8(self, voice1, voice2):
        index = self.index
        if index == 0:
            return True
        move1 = voice1[index] - voice1[index - 1]
        move2 = voice2[index] - voice2[index - 1]
        direct = mth.sign(move1) == mth.sign(move2)
        interval = Note.interval(voice1[index - 1], voice2[index - 1])

        if interval == 12 or interval == 0:
            if direct:
                return False
        return True

    def checkTritoneInside(self):
        return self.index < 2 or \
            abs(self.note - self.sequence[self.index - 2]) != 6

    def check_jump_end(self):
        if self.index == self.length() - 2 and self.jump() >= 7:
            return False
        return True

    def check_jump(self):
        ''' checa si el salto es valido, i.e intervalo permitido'''
        if self.index == 0:
            return True
        jump = abs(self.jump())
        if jump == 11:
            return False
        if jump > 12:
            return False
        if jump == 10:
            return False
        if jump == 9:
            return False
        if jump == 6:
            return False
        if jump == 8:
            if self.note < self.parent:
                return False
        diat = Note.Diatonic.interval(self.parent, self.note, debug=False)
        if jump == 4 and abs(diat) == 3:
            return False

        return True

    def checkTritoneIsolated(self):
        index = self.index
        if index < 2:
            return True
        lastJump = self.sequence[index - 1] - self.sequence[index - 2]
        jump = self.note - self.parent
        if mth.sign(jump) != mth.sign(lastJump):
            lastPivot = self.pivot
            self.pivot = self.index - 1
            if lastPivot is not None:
                if (self.sequence[lastPivot] - self.parent) % 12 == 6:
                    self.pivot = index - 1
                    return False
        return True

    def check_repetition(self):
        if self.index == 0:
            return True
        note = self.note
        counterMode = self.voice.index != 0
        if note == self.parent:
            if not counterMode:
                return False
            elif self.index >= 2 and self.sequence[self.index - 2] == note:
                return False
        if self.index >= 2:
            index = self.index
            notes = self.sequence[index - 2:]
            notes_ = [note % 12 for note in notes]
            if notes_[0] == notes_[1] and notes_[0] == notes_[2]:
                return False
        return True

    def check_movement(self):
        if self.index < 2:
            return True
        jump = self.jump()
        lastJump = self.sequence[self.index - 1] - self.sequence[self.index - 2]
        is_ending = self.index == self.length() - 1
        if lastJump < -2 and jump < 0:
            return is_ending and abs(lastJump) <= 5
        if jump > 2 and lastJump > 0:
            return False
        return True

    def check_note(self):
        if self.debug:
            pass
        index = self.index
        voice_index = self.voice.index
        note = self.note
        if voice_index == 0 and Note.equals(note, sib):
            return False
        if index == 0:
            if voice_index == 0:
                if note != self.modo():
                    return False
        else:
            lastnote = self.parent
            if Note.equals(note, sib + 1) and Note.equals(lastnote, sib):
                return False
            if Note.equals(note, sib) and Note.equals(lastnote, sib + 1):
                return False
            if index == self.length() - 1 and not Note.equals(
                                                            note,
                                                            self.modo()):
                return False
            if voice_index == 0:
                sup = Note.white_scale(self.modo(), 1)
                if index == self.length() - 3 and Note.equals(note, self.modo()):
                    return False
                if index == self.length() - 2 and not Note.equals(note, sup):
                    return False
                if index == self.length() - 1 and not Note.equals(
                                                                note,
                                                                self.modo()):
                    return False
        return True

    def check_sequences(self):
        i = self.index
        note = self.note
        parent = self.parent
        s = self.sequence
        if i < 3:
            return True
        jump = Note.interval(parent, note)
        print(self.sequence)
        print(s[i - 2])
        print(s[i])
        interval02 = Diatonic.interval(s[i - 2], s[i - 0])
        interval13 = Diatonic.interval(s[i - 3], s[i - 1])

        print('intreval02', interval02)

        print('interval13', interval13)

        if interval02 == interval13 and (abs(jump) > 2 or interval02 == 0):
            return False
        if i < 4:
            return True
        if s[i] == s[i-2] and s[i - 2] == s[i - 4]:
            return False
        interval14 = Note.interval(s[i - 1], s[i - 4])
        if i >= 5:
            interval03 = Diatonic.interval(s[i - 3], s[i - 0])
            interval25 = Diatonic.interval(s[i - 5], s[i - 2])
            interval14 = Diatonic.interval(s[i - 4], s[i - 1])
            if interval25 == interval14:
                if interval14 == interval03:
                    return False
            s, s_ = s[i - 5: i - 2], s[i - 2:]
            s_.reverse()
            s = s + s_
            i = 5
            interval03 = Diatonic.interval(s[0], s[3])
            interval14 = Diatonic.interval(s[1], s[4])
            interval25 = Diatonic.interval(s[2], s[5])
            if interval25 == interval14:
                if interval14 == interval03:
                    return False
        i = self.index
        if i >= 6:
            s = self.sequence
            interval04 = Diatonic.interval(s[i - 4], s[i - 0])
            interval15 = Diatonic.interval(s[i - 5], s[i - 1])
            interval26 = Diatonic.interval(s[i - 6], s[i - 2])
            if interval04 == interval15:
                if interval15 == interval26:
                    return False
        return True

    def cp_valid_generator(self, cf_, cf_last, chord, cf_index=1,
                           twovoices=False):
        # print()
        try:
            cp = [self.parent, self.note]
            cp_move = cp[1] - cp[0]
            cf = [cf_last, cf_]
            cf_move = cf[1] - cf[0]
            interval = abs(cp[1] - cf[1]) % 12
            # input()
            if twovoices:
                if self.reference[self.index] == self.note:
                    yield (f_.unison, False)
                else:
                    yield ('checkunison', True)

            if interval == 0 and mth.sign(cf_move) == mth.sign(cp_move):
                yield ('checkdirect8', False)
            else:
                yield ('checkdirect8', True)

            if interval == 7 and mth.sign(cf_move) == mth.sign(cp_move):
                yield ('checkdirect5', False)
            else:
                yield ('checkdirect5', True)

            if not self.check_chord(chord, 2):
                yield ('checkchord', False)
            else:
                yield ('checkchord', True)

            if self.index >= 4:
                reference = self.ref[self.index - 4:]
                sequence = self.sequence
                index = self.index
                intervals = []
                for i in range(4):
                    intervals.append(Note.Diatonic.interval(
                                     reference[i][cf_index],
                                     sequence[index - 4 + i]))
                if len(set(intervals)) == 1:
                    yield ('checkrepintervals', False)
                else:
                    yield ('checkrepintervals', True)
        except Exception as e:
            assert(self.index == 0)
            yield (e, True)

    def cf_valid_generator(self):

        yield (self.check_note, False) if not self.check_note() else \
            (self.check_note, True)

        yield (self.check_repetition, False) if not self.check_repetition() else \
            (self.check_repetition, True)

        yield (self.checkTritoneInside, False) if not self.checkTritoneInside() else \
            (self.checkTritoneInside, True)

        yield (self.check_jump, False) if not self.check_jump() \
            else (self.check_jump, True)

        yield (self.check_movement, False) if not self.check_movement() else \
            (self.check_movement, True)

        yield (self.checkTritoneIsolated, False) if not self.checkTritoneIsolated() else \
            (self.checkTritoneIsolated, True)
        yield (self.check_sequences, False) if not self.check_sequences() \
            else (self.check_sequences, True)

    def valid_cp(self, chord, lastChord):

        voice_index = self.voice.index
        size = len(chord)
        for i in range(0, size):
            if i == voice_index:
                continue
            cf = chord[i]
            cf_last = lastChord[i] if self.index > 0 else None
            if self.voice.index == 1:
                print('reference \n')
                print(self.ref)
                print('sequence\n')
                print(self.sequence)
                print('chord is {}', chord)
                print('lastchord is {}', lastChord)
            generator = self.cp_valid_generator(cf, cf_last, chord, cf_index=i)
            if not self.yield_validate(*generator):
                print('invalid node cp at', self.index)
                return False
            else:
                print('valid node-cp at ', self.index)
        return True

    def valid_cf(self):
        if self.voice.index > 0:
            print('generating cp validation from :', self)
            # input()
        generator = self.cf_valid_generator()
        if self.yield_validate(*generator):
            print('\nvalid sequence {}, voice_index: {}'.format(
                self.sequence, self.voice.index))
            return True
        else:
            print('\ninvalid node cf at', self.sequence)
            return False

    def yield_validate(self, *generator):
        valid = True
        for value in generator:
            assert(value is not None)
            operation = value[0]
            failure = value[1]
            valid &= failure
            if self.debug:
                self.debug_log(operation=operation,
                               result=failure)
            elif not valid:
                return False
        return valid

    @staticmethod
    def FromSequence(*sequence, octaveShift=0, reverse=True, is_cantus=False):
        '''avoid shallow copy of sequence'''
        if reverse:
            sequence.reverse()
        for i in range(0, len(sequence)):
            valid = True
            if i == 0:
                node = Node(sequence[0] + 12*octaveShift, debug=True)
            else:
                node = Node(sequence[i], lastNode=node, debug=True)
            valid = node.validMelody(
                                     size=len(sequence),
                                     counter=not is_cantus)
        # print('node failures {}:'.format(node.failures))
        return node

    def debug_log(self, operation, result=None):
        self.log_function(operation, result=result)
        index = self.index
        failures = self.failures
        message = str(operation) + '[{}]'.format(self.index)
        self.fail = True
        if not result:
            try:
                log = failures[index]
                failures[index] = log + message
            except Exception:
                failures.append(message)
            if result:
                print(colored('failure {}'.format(operation), 'red'))
        else:
            print(colored('pass {}'.format(operation), 'green'))
        # input()

    def log_function(self, method_name, **kwargs):
        message = 'log function: {}'.format(method_name)
        result = kwargs.get('result')
        color = 'green' if result is True else 'red'
        print(colored('{} , result :{}'.format(message, result), color))

    def __str__(self):
        numerical = self.sequence
        notes = []
        for note in numerical:
            if note:
                notes.append(str(Notes(note % 12)) + str(note//12))
            else:
                notes.append('none')
        error_log = str(self.failures) if self.debug else ''
        # print('reference')
        Note.print_sequence(self.ref)
        params = {'hi': self.high, 'hiIndex': self.hiIndex, 'discontinuities':
            self.disc}
        print(params)
        return str(numerical) + '\nnotes :\n  ' + str(notes) + '\nfailures :\n ' + error_log
