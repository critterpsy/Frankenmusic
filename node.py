from Note import Note, Diatonic


'''haciendo el arbol al reves, index = 1,
    representa penultima nota'''
'''debe ser 2ndo grado en el cantusFirmus y sensible para
contrapunto, sensible = modo - 1, en la escala cromatica y diat'''


class Node:
    def __init__(self, note, lastNode=None):
        self.note = note
        if lastNode is None:
            self.sequence = [note]
            self.pivot = None
            self.parent = None
            self.high = note
            self.disc = 0
            self.hiIndex = 0
            self.modeRep = 1
            self.failures = ['']
        else:
            self.sequence = lastNode.sequence.copy()
            self.sequence.append(note)
            self.failures = lastNode.failures
            self.failures.append('')
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
        print('contructor '+str(self.sequence))
        self.index = len(self.sequence) - 1
        # print('index '+str(self.index))
        self.root = self.sequence[0]

    def counterVoice(self, counters):
        self.counters = counters

    def root(self):
        return self.sequence[0]

    def index(self):
        return len(self.sequence) - 1

    def parent(self):
        if self.index == 0:
            return None
        return self.sequence[self.index - 1]

    def partial(self, n):
        subSequence = self.sequence[0:n]
        return Node.FromSequence(subSequence)

    def jump(self):
        if self.index == 0:
            return 'NaN'
        return self.note - self.parent

    def direction(self):
        if self.index == 0:
            return 0
        return self.jump()/self.jump().abs()

    def checkEnd(self, index, note, counterMode, scaleMode):
        if counterMode:
            print('mode' + str(scaleMode))
            if((scaleMode - 1) - note) % 12 != 0:
                print('beforeEnd should be sensible')
                return False
        elif note != Note.diatonicScale(self.root, 1):
            print('beforeEnd should be root + 1 '+str(self.sequence))
            return False
        return True

    def checkStart(self, counterMode, scaleMode):
        note = self.note
        if counterMode:
            if abs(note - scaleMode) % 12 != 0 and abs(note - scaleMode) % 12 != 7:
                print(scaleMode)
                print('start should be mode or mode + 5th ,note is '+str(note))
                print('scaleMode is ' + str(scaleMode))
                return False
        elif note != self.root:
            print('start should be mode')
            return False
        return True

    def checkTritone(self, note):
        if Note.equals(note, Note.B.value) and Note.equals(
                                                            self.parent,
                                                            Note.F.value):
            print('direct tritone '+str(note)+' '+str(self.parent))
            return False
        if Note.equals(note, Note.F.value) and Note.equals(
                                                          self.parent,
                                                          Note.B.value):
            print('direct tritone')
            return False
        return True

    def checkTritoneInside(self, note):
        index = self.index
        if Note.equals(note, Note.F.value) and Note.equals(
                                            self.sequence[index - 2],
                                            Note.B.value):
            print('surrounding tritone '+str(note)+' '+str(
                                            self.sequence[index - 2]))
            return False
        if Note.equals(note, Note.B.value) and Note.equals(
                                            self.sequence[index - 2],
                                            Note.F.value):
            print('surrounding tritone '+str(note)+' '+str(
                                            self.sequence[index - 2]))
            return False
        return True

    def checkJumpEnd(self):
        if self.index == 2 and self.jump() >= 7:
            print('.jump down before end')
            return False

    def checkLegalJump(self, j):
        if j > 1:
            if j != 2 and j != 3 and j != 4 and j != 5 and j != 7:
                print('salto ilegal '+str(j+1)+'a')
                return False
            j_chrome = self.note - self.parent
            if self.parent - self.sequence[self.index - 2] > 2:
                if not self.isChord():
                    print(
                        'salto en la misma direccion ,debe ser acorde')
                    return False
            if j == 5:
                if abs(j_chrome) == 9:
                    print('note, note - 6M')
                    return False
        elif j < -1:
            if j != -2 and j != -3 and j != -4 and j != -5 and j != -7:
                print('salto ilegal '+str(j))
                return False
            if self.parent - self.sequence[self.index - 2] < -2:
                if not self.isChord():
                    print('not chord')
                    return False
            if j == -5:
                j_chrome = self.note - self.parent
                if j_chrome == -9:
                    print('note , note + 6M')
                    return False

    def checkTritoneIsolated(self, lastJump):
        if self.jump() / lastJump < 0:
            lastPivot = self.pivot
            self.pivot = self.index - 1
            if lastPivot is not None:
                if (self.sequence[lastPivot] - self.parent) % 12 == 6:
                    print(self.note)
                    print(self.jump())
                    print('surrounding tritone ' + str(self.parent))
                    self.pivot = self.index - 1
                    return False
        return True

    def validMelody(self, size=11, counter=False, mode=None):
        index = self.index
        note = self.note
        if index > 0:
            '''si nota es parent, rompe regla de nota repetida'''
            '''contrapunto tiene permitido repetir a los mas dos'''
            if note == self.parent:
                if not counter:
                    print('here repeated note')
                    return False
                elif index >= 2 and self.sequence[index - 2] == note:
                    print('AAA AT COUNTER')
                    return False

            if index == 1 and not self.checkEnd(index, note, counter, mode):
                print('invalid ending '+str(self.sequence))
                return False
            if not self.checkTritone(note):
                print('tritone movement')
                return False
            if index < 2:
                return True
            lastJump = self.sequence[index - 1] - self.sequence[index - 2]
            if lastJump != 0 and not self.checkTritoneIsolated(lastJump):
                print('isolated tritone')
                return False
            if not self.checkJumpEnd():
                return False
            j = Diatonic.index(note) - Diatonic.index(self.parent)
            if j != 0 and not self.checkLegalJump(j):
                print('illegal jump')
                return False
            if index < 3:
                return True
            jump = Diatonic.interval(self.parent, self.note)
            seq = self.sequence
            if not self.checkMovement(jump, seq, index):
                print('invalid movement')
                return False
            if not self.checkSequences(seq, index):
                print('sequences found')
                return False
            if index == size - 1 and not self.checkStart(counter, mode):
                print('invalid start')
                return False

        return True

    def checkMovement(self, jump, seq, index):
        j = Diatonic.interval(seq[index - 2], seq[index - 1])
        print('check movement {}'.format(self.note))
        if j == 1 and jump > 1:
            parent = self.parent
            note = self.note
            p = seq[index - 2]
            print('{} {} {}: jump down + continuos '.format(note, parent, p))
            return False
        elif jump == -1 and j < -1:
            parent = self.parent
            note = self.note
            p = seq[index - 2]
            print('{} {} {}: continous + jumpUp'.format(note, parent, p))
            return False
        return True

    def checkSequences(self, sequence, index):
        print('check sequence '+str(self.note))
        i = index
        note = self.note
        parent = self.parent
        s = sequence
        jump = Diatonic.interval(parent, note)
        if i < 3:
            return True
        interval02 = Diatonic.interval(s[i - 2], s[i - 0])
        interval13 = Diatonic.interval(s[i - 3], s[i - 1])
        print(interval02 == 0)
        print(interval13)
        if interval02 == interval13 and (abs(jump) > 1 or interval02 == 0):

            print('ab , a+x b+x')
            return False
        if i > 5:
            interval25 = Diatonic.interval(s[i - 5], s[i - 2])
            interval14 = Diatonic.interval(s[i - 4], s[i - 1])
            if interval25 == interval14 and abs(jump) > 1:
                if interval14 == Diatonic.interval(s[i - 3], note):
                    print('abc , a+x b+x c+x')
                    return False
        return True

    def validateVoice1(self, cantusFirmus):

        index = self.index
        note = self.note
        reference = cantusFirmus[index]
        print('index :'+str(index))
        if not Note.Consonant(cantusFirmus[index], self.note):
            # print(cantusFirmus[index])
            print(reference)
            print(note)
            print('disssonance')
            return False
        if index > 0:
            lastInterval = abs(self.parent - cantusFirmus[index-1])
            if lastInterval == 7:
                if abs(note - cantusFirmus[index]) == 7:
                    print('parallel fifth')
                    return False
            referenceJump = abs(cantusFirmus[index] - cantusFirmus[index -1])
            if self.jump() != 0 and referenceJump/self.jump() > 0:
                if lastInterval == 7:
                    print('direct fifth')
                    return False
            if lastInterval == 12:
                if abs(note - cantusFirmus[index]) == 12:
                    print('parallel octave')
                    print(self.sequence)
                    print(cantusFirmus)
                    return False
            if self.jump() != 0 and referenceJump/self.jump() > 0:
                print('caca '+str(lastInterval))
                if lastInterval == 0:
                    if cantusFirmus[index] != note:
                        print('direct octave')
                    return False
        print('COUNTERPOINT')
        self.printNotesReverse()
        print(self.sequence[0:index + 1])
        cfNotes = []
        for n in cantusFirmus:
            cfNotes.append(Note(n%12).name + str(n//12))
        print('CANTUS FIRMS    \n:'+str(cfNotes[0:index + 1]))
        print(cantusFirmus[0:index + 1])
        print('INTERVAL :'+str(Note.interval(reference, note)))
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

    def isLongJump(self):
        return self.Jump().abs() > 1

    def printNotes(self):
        seq = self.sequence.copy()
        seq.reverse()
        arr = []
        for s in seq:
            arr.append(Note(s % 12).name + str(int(s/12)))
        print(arr)
        print(seq)

    @staticmethod
    def FromSequence(sequence, octaveShift, reverse=True, isCantus=False):
        failures = ''
        if reverse:
            sequence.reverse()
        for i in range(0, len(sequence)):
            valid = True
            if i == 0:
                node = Node(sequence[0] + 12*octaveShift)
            else:
                print(node)
                node = Node(sequence[i], node)
                valid = node.validMelody(
                                         size=len(sequence),
                                         counter=not isCantus,
                                         mode=node.root)
            if not valid:
                failures.append(node.failures[i])
        print(failures)
        return node
