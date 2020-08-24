from Note import Note, Diatonic
import failureCases

'''haciendo el arbol al reves, index = 1,
    representa penultima nota'''
'''debe ser 2ndo grado en el cantusFirmus y sensible para
contrapunto, sensible = modo - 1, en la escala cromatica y diat'''

f_ = failureCases


class Node:
    def __init__(self, note, lastNode=None, debug=False):
        if debug:
            self.fail = False
        self.note = note
        if lastNode is None:
            self.sequence = [note]
            self.pivot = None
            self.parent = None
            self.high = note
            self.disc = 0
            self.hiIndex = 0
            self.modeRep = 1
            if debug:
                self.failures = ['']
        else:
            self.sequence = lastNode.sequence.copy()
            self.sequence.append(note)
            self.pivot = lastNode.pivot
            self.parent = lastNode.note
            if note == self.sequence[0]:
                self.modeRep = lastNode.modeRep + 1
            else:
                self.modeRep = lastNode.modeRep
            if note >= lastNode.high:
                self.high = note
                self.hiIndex = lastNode.index + 1
            else:
                self.high = lastNode.high
                self.hiIndex = lastNode.hiIndex
            if abs(self.note - self.parent) > 2:
                self.disc = lastNode.disc + 1
            else:
                self.disc = lastNode.disc
            if debug:
                self.failures = lastNode.failures
                self.failures.append('')
        self.index = len(self.sequence) - 1
        self.debug = debug
        self.root = self.sequence[0]

    def partial(self, n):
        subSequence = self.sequence[0:n]
        return Node.FromSequence(subSequence)

    def get_scale_mode(self):
        return self.root

    def debugLog(self, message, details=None):
        self.fail = True
        index = self.index
        failures = self.failures
        message = message + '[{}]'.format(self.index) + 'value error: {}'.format(self.note)
        if details:
            message = message + ' function :{} '.format(details)
        try:
            log = failures[index]
            failures[index] = log + message
        except Exception:
            failures.append(message)
        # if self.debug:
        #     print(self.failures)

    def jump(self):
        if self.index == 0:
            return 'NaN'
        return self.note - self.parent

    def checkEnd(self, index, note, counterMode, scaleMode):
        print('checking end {}'.format(self.debug))
        if self.debug:
            print('checking End function! {}'.format(scaleMode))
            print('note is {} '.format(self.note))
            print('root is :{} '.format(self.root))
        if counterMode:
            if self.root - 1 != note:
                return False
        elif note != Note.diatonicScale(self.root, 1):
            # print('beforeEnd should be root + 1 '+str(self.sequence))
            return False
        return True

    def checkStart(self, counterMode, scaleMode):
        print('cacacaca')
        if self.debug:
            print(counterMode)
            print('note is {}'.format(self.note))
            print('scaleMode is {}'.format(scaleMode))
        note = self.note
        if counterMode:
            fifth = Note.diatonicScale(scaleMode, 4) % 12
            print('fifth{}'.format(fifth))
            if abs(note - scaleMode) % 12 == 0:
                return True
            if (note - fifth) % 12 == 0:
                return True
                # print(scaleMode)
            # print('start should be mode or mode + 5th ,note is '+str(note))
            return False
        elif note != self.root:
            # print('start should be mode')
            return False
        return True

    def checkTritone(self, note):
        if Note.equals(note, Note.B.value) and Note.equals(
                                                            self.parent,
                                                            Note.F.value):
            # print('direct tritone '+str(note)+' '+str(self.parent))
            return False
        if Note.equals(note, Note.F.value) and Note.equals(
                                                          self.parent,
                                                          Note.B.value):
            # print('direct tritone')
            return False
        return True

    def checkTritoneInside(self, note):
        index = self.index
        if Note.equals(note, Note.F.value) and Note.equals(
                                            self.sequence[index - 2],
                                            Note.B.value):
            # print('surrounding tritone '+str(note)+' '+str(
            #                                 self.sequence[index - 2]))
            return False
        if Note.equals(note, Note.B.value) and Note.equals(
                                            self.sequence[index - 2],
                                            Note.F.value):
            # print('surrounding tritone '+str(note)+' '+str(
                                            # self.sequence[index - 2]))
            return False
        return True

    def checkJumpEnd(self):
        if self.index == 2 and self.jump() >= 7:
            # print('.jump down before end')
            return False
        return True

    def checkLegalJump(self, j):
        if j > 1:
            if j != 2 and j != 3 and j != 4 and j != 5 and j != 7:
                # print('salto ilegal '+str(j+1)+'a')
                return False
            j_chrome = self.note - self.parent
            if self.parent - self.sequence[self.index - 2] > 2:
                if not self.isChord():
                    # print('salto en la misma direccion ,debe ser acorde')
                    return False
            if j == 5:
                if abs(j_chrome) == 9:
                    # print('note, note - 6M')
                    return False
        elif j < -1:
            if j != -2 and j != -3 and j != -4 and j != -5 and j != -7:
                # print('salto ilegal '+str(j))
                return False
            if self.parent - self.sequence[self.index - 2] < -2:
                if not self.isChord():
                    # print('not chord')
                    return False
            if j == -5:
                j_chrome = self.note - self.parent
                if j_chrome == -9:
                    # print('note , note + 6M')
                    return False
        return True

    def checkTritoneIsolated(self, lastJump):
        if self.jump() / lastJump < 0:
            lastPivot = self.pivot
            self.pivot = self.index - 1
            if lastPivot is not None:
                if (self.sequence[lastPivot] - self.parent) % 12 == 6:
                    # print('surrounding tritone ' + str(self.parent))
                    self.pivot = self.index - 1
                    return False
        return True

    def checkRepetition(self, counterMode=False):
        note = self.note
        if note == self.parent:
            if not counterMode:
                return False
            elif self.index >= 2 and self.sequence[self.index - 2] == note:
                return False
        return True

    def validMelody(self, size=11, counter=False, mode=None):
        index = self.index
        note = self.note
        if index > 0:
            '''si nota es parent, rompe regla de nota repetida'''
            '''contrapunto tiene permitido repetir a los mas dos'''
            if not self.checkRepetition(counter):
                # print('repeated note')
                if self.debug:
                    self.debugLog(f_.repeated_note, 'checkRepeteadNote')
                else:
                    return False
            print('checking here!!!!!!!!!!{}'.format(index))
            if index == 1 and not self.checkEnd(index, note, counter, mode):
                # print('invalid ending '+str(self.sequence))
                if self.debug:
                    self.debugLog(f_.bad_ending, 'checkEnd')
                else:
                    return False
            else:
                print('mierda!')
            if not self.checkTritone(note):
                if self.debug:
                    self.debugLog(f_.tritone, 'triton check')
                else:
                    return False
            if index < 2 and not self.debug:
                return True
            if not self.checkJumpEnd():
                if self.debug:
                    print('here!!!!')
                    self.debugLog(f_.bad_movement, 'checkJumpEnd {}'.format(index))
                else:
                    return False
            lastJump = self.sequence[index - 1] - self.sequence[index - 2]
            if lastJump != 0 and not self.checkTritoneIsolated(lastJump):
                if self.debug:
                    self.debugLog(f_.isolated_tritone, 'checkITritone')
                else:
                    return False
            j = Diatonic.index(note) - Diatonic.index(self.parent)
            if j != 0 and not self.checkLegalJump(j):
                if self.debug:
                    self.debugLog(f_.badJump, 'checkBadJump')
                else:
                    return False
            if index < 3 and not self.debug:
                return True
            jump = Diatonic.interval(self.parent, self.note)
            seq = self.sequence
            if not self.checkMovement(jump, seq, index):
                if self.debug:
                    self.debugLog(f_.bad_movement, str(self.index))
                else:
                    return False
            if not self.checkSequences(seq, index):
                # print('sequences found')
                if self.debug:
                    self.debugLog(f_.seq)
                else:
                    return False
            if index == size - 1 and not self.checkStart(counter, mode):
                if self.debug:
                    self.debugLog(f_.bad_start)
                else:
                    return False
            if self.debug and self.fail:
                return False
        return True

    def checkMovement(self, jump, seq, index):
        j = Diatonic.interval(seq[index - 2], seq[index - 1])
        # print('check movement {}'.format(self.note))
        if j == 1 and jump > 1:
            # print('{} {} {}: jump down + continuos '.format(note, parent, p))
            return False
        elif jump == -1 and j < -1:
            # print('{} {} {}: continous + jumpUp'.format(note, parent, p))
            return False
        return True

    def checkSequences(self, sequence, index):
        # print('check sequence '+str(self.note))
        i = index
        note = self.note
        parent = self.parent
        s = sequence
        jump = Diatonic.interval(parent, note)
        if i < 3:
            return True
        interval02 = Diatonic.interval(s[i - 2], s[i - 0])
        interval13 = Diatonic.interval(s[i - 3], s[i - 1])
        if interval02 == interval13 and (abs(jump) > 1 or interval02 == 0):

            # print('ab , a+x b+x')
            return False
        if i > 5:
            interval25 = Diatonic.interval(s[i - 5], s[i - 2])
            interval14 = Diatonic.interval(s[i - 4], s[i - 1])
            if interval25 == interval14 and abs(jump) > 1:
                if interval14 == Diatonic.interval(s[i - 3], note):
                    # print('abc , a+x b+x c+x')
                    return False
        return True

    def valid_cp(self, cantusFirmus):
        index = self.index
        note = self.note
        # print('index :'+str(index))
        if not Note.Consonant(cantusFirmus[index], self.note):
            if self.debug:
                self.debugLog(f_.dissonance)
            return False
        if index > 0:
            lastInterval = abs(self.parent - cantusFirmus[index-1])
            if lastInterval == 7:
                if abs(note - cantusFirmus[index]) == 7 and self.debug:
                    self.debugLog(f_.parallel5)
                    # print('parallel fifth')
                    return False
            referenceJump = abs(cantusFirmus[index] - cantusFirmus[index -1])
            if self.jump() != 0 and referenceJump/self.jump() > 0:
                if lastInterval == 7 and self.debug:
                    self.debugLog(f_.direct5)
                    # print('direct fifth')
                    return False
            if lastInterval == 12:
                if abs(note - cantusFirmus[index]) == 12 and self.debug:
                    self.debugLog(f_.parallel5)
                    # print('parallel octave')
                    return False
            if self.jump() != 0 and referenceJump/self.jump() > 0:
                if lastInterval == 0:
                    if cantusFirmus[index] != note and self.debug:
                        # print('direct octave')
                        self.debugLog(f_.direct8)
                    return False
        elif index == 0:
            pass
        cfNotes = []
        for n in cantusFirmus:
            cfNotes.append(Note(n % 12).name + str(n//12))
        # print('CANTUS FIRMS    \n:'+str(cfNotes[0:index + 1]))
        # print(cantusFirmus[0:index + 1])
        # print('INTERVAL :'+str(Note.interval(reference, note)))
        return True

    def isChord(self):
        if self.index < 2:
            return False
        j = Diatonic.interval(self.parent, self.note)
        j_ = Diatonic.interval(self.sequence[self.index - 2], self.parent)
        if j == -2 and j_ == -3:
            return True
        if j == 2 and j_ == 3:
            return True
        if j == -2 and j_ == -2:
            return True
        if j == 2 and j_ == 2:
            return True
        return False

    def printNotes(self):
        seq = self.sequence.copy()
        seq.reverse()
        arr = []
        for s in seq:
            arr.append(Note(s % 12).name + str(int(s/12)))
        print(arr)
        print(seq)

    @staticmethod
    def FromSequence(sequence, octaveShift=0, reverse=True, is_cantus=False):
        '''avoid shallow copy of sequence'''
        sequence = sequence.copy()
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
                                     counter=not is_cantus,
                                     mode=node.root)
        # print('node failures {}:'.format(node.failures))
        return node

    @staticmethod
    def debug_cp(input_sequence,
                 octave_shift=0,
                 is_cantus=False,
                 cantus_firmus=None):
        '''avoid shallow copy of sequence'''
        sequence = input_sequence.copy()
        sequence.reverse()
        cf = cantus_firmus.copy()
        cf.reverse()
        for i in range(0, len(sequence)):
            if i == 0:
                node = Node(sequence[0] + 12*octave_shift, debug=True)
            else:
                node = Node(sequence[i], lastNode=node, debug=True)
            node.validMelody(
                             size=len(sequence),
                             counter=True,
                             mode=node.root)
            node.valid_cp(cf)
        print('node failures {}:'.format(node.failures))
        return node

    def __str__(self):
        numerical = self.sequence
        notes = []
        for note in numerical:
            if note:
                notes.append(str(Note(note % 12)) + str(note//12))
            else:
                notes.append('none')
        error_log = str(self.failures) if self.debug else ''
        return str(numerical) + '\nnotes :\n  ' + str(notes) + '\nfailures :\n ' + error_log
