from Note import Note, Diatonic
import array


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
            if((scaleMode - 1) - note) % 12 != 0:
                print('beforeEnd should be sensible')
                return False
        elif note != Note.diatonicScale(self.root, 1):
            print('beforeEnd should be root + 1')
            return False
        return True

    def checkStart(self, counterMode, scaleMode):
        note = self.note
        if counterMode:
            if(scaleMode - note) % 12 != 0 and (scaleMode - note) % 12 != 7:
                print('start should be mode or mode + 5th')
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

    def validMelody(self, counterMode=False, mode=None):
        index = self.index
        note = self.note
        if index > 0:
            '''si nota es parent, rompe regla de nota repetida'''
            '''contrapunto tiene permitido repetir a los mas dos'''
            if note == self.parent:
                if not counterMode:
                    print('here repeated note')
                    return False
                elif index >= 2 and self.sequence[index - 2] == note:
                    print('AAA AT COUNTER')
                    return False
            '''haciendo el arbol al reves, index = 1,
                representa penultima nota'''
            '''debe ser 2ndo grado en el cantusFirmus y sensible para
            contrapunto, sensible = modo - 1, en la escala cromatica y diat'''
            if index == 1:
                print('caca'+str(self))
                if not self.checkEnd(index, note, counterMode, mode):
                    print('invalid ending')
                    return False
            if not self.checkTritone(note):
                print('tritone movement')
                return False
            if index >= 2:
                lastJump = self.sequence[index - 1] - self.sequence[index - 2]
                if lastJump != 0:
                    if self.jump() / lastJump < 0:
                        lastPivot = self.pivot
                        self.pivot = index - 1
                        if lastPivot is not None:
                            if (self.sequence[lastPivot] - self.parent) % 12 == 6:
                                print(note)
                                print(self.jump())
                                print('surrounding tritone ' + str(self.parent))
                                self.pivot = index - 1
                                return False

                if index == 2 and self.jump() >= 7:
                    print('.jump down before end')
                    return False
                ''''index in whiteScale'''
                note = int(note + int(note/5))/2
                parent = self.parent
                parent = int((parent + int(parent/5))/2)
                '''salto en terminos de blancas , intervalos diatonicos'''
                j = note - parent
                if j > 1:
                    if j != 2 and j != 3 and j != 4 and j != 5 and j != 7:
                        print('salto ilegal '+str(j+1)+'a')
                        return False
                    j_chrome = self.note - self.parent
                    if self.parent - self.sequence[index - 2] > 2:
                        if not self.isChord():
                            print(
                                'salto en la misma direccion ,debe ser acorde')
                            return False
                    if j == 5:
                        if abs(j_chrome) == 9:
                            print('sexta menor no permitida')
                elif j < -1:
                    if j != -2 and j != -3 and j != -4 and j != -5 and j != -7:
                        return False
                    if self.parent - self.sequence[index - 2] < -2:
                        if not self.isChord():
                            return False
                    if j == -5:
                        j_chrome = self.note - self.parent
                        if j_chrome == 9:
                            print('note , note + 6M')
            if index >= 3:
                note = self.note
                jump = Diatonic.interval(self.parent, note)
                seq = self.sequence
                if not self.checkMovement(jump, seq, index):
                    print(jump)
                    print('note' + str(self.note))
                    print(self.sequence)
                    print(Diatonic.index(note))
                    print('invalid movement')
                    return False
                if not self.checkSequences(seq, index):
                    print('sequences found')
                    return False
                if index == 10 and not self.checkStart(counterMode, mode):
                    print('invalid start')

        return True

    def checkMovement(self, jump, seq, index):
        j = Diatonic.interval(seq[index - 2], seq[index - 1])
        if j == 1 and jump > 1:
            parent = str(self.parent)
            note = str(self.note)
            p = str(seq[index - 2])
            print('jump down + continuos ' + note + ' ' + parent + ' ' + p)
            return False
        elif jump == -1 and j < -1:
            print(index)
            print(self.note)
            print(self.jump())
            print('continous + jumpUp')
            return False
        return True

    def checkSequences(self, sequence, index):
        i = index
        note = self.note
        parent = self.parent
        s = sequence
        jump = Diatonic.interval(parent, note)
        if i < 3:
            return True
        interval02 = Diatonic.interval(s[i - 2], s[i - 0])
        interval13 = Diatonic.interval(s[i - 3], s[i - 1])
        if interval02 == interval13 and abs(jump) > 1:
            print('ab , a+x b+x')
            return False
        if i > 5:
            interval25 = Diatonic.interval(s[i - 5], s[i - 2])
            interval14 = Diatonic.interval(s[i - 4], s[i - 1])
            if interval25 == interval14:
                if interval14 == Diatonic.interval(s[i - 3], note):
                    print('abc , a+x b+x c+x')
                    return False
        return True


    def validateVoice1(self, cantusFirmus):

        index = self.index
        note = self.note
        reference = cantusFirmus[index]
        print('index :'+str(index))
        if index == 1:
            if (note - (cantusFirmus[0] - 1)) % 7:
                print('at index : len - 1 should be sensible , not :'+str(note))
                return False
        if not Note.Consonant(cantusFirmus[index], self.note):
            # print(cantusFirmus[index])
            print('disssonance')
            return False
        interval = Note.nInterval(cantusFirmus[index], self.note)
        if index > 0:
            lastInterval = Note.nInterval(cantusFirmus[index-1], self.parent)
            if interval == 7:
                if Note.nInterval(cantusFirmus[index], note) == 7:
                    print('parallel fifth')
                    return False
            referenceJump = cantusFirmus[index] - cantusFirmus[index -1]
            if self.jump() != 0 and referenceJump/self.jump() > 0:
                if lastInterval == 4:
                    print('direct fifth')
                    return False
            if interval == 12:
                if Note.nInterval(cantusFirmus[index], note) == 12:
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
            cfNotes.append(Note(n).name)
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
            arr.append(Note(s).name)
        print(arr)

    def printNotesReverse(self):
        seq = self.sequence
        arr = []
        for s in seq:
            arr.append(Note(s).name)
        print(arr)

    @staticmethod
    def interval(note1, note2):
        note2 - note1

    @staticmethod
    def tritone(note1, note2):
        return (note1 == 4 and note2 == 7) or (note1 == 7 and note2 == 4)


def sequenceToCantus(s, reverse=False, validate=False):
    if reverse:
        s.reverse()
    length = len(s)
    for i in range(0, length):
        if i == 0:
            lastNode = Node(s[0])
        else:
            lastNode = Node(s[i], lastNode)
        if not lastNode.validMelody():
            print('INVALID MELODY '+str(lastNode.sequence))
