from enum import Enum


class Note(Enum):
    C = 0
    Cs = 1
    D = 2
    Ds = 3
    E = 4
    F = 5
    Fs = 6
    G = 7
    Gs = 8
    A = 9
    As = 10
    B = 11

    @staticmethod
    def equals(note1, note2):
        return (note1 - note2) % 12 == 0

    @staticmethod
    def isWhite(note):
        note = note % 12
        if note <= 4:
            if note % 2 == 0:
                return True
            return False
        else:
            if note % 2 == 0:
                return False
            return True

    @staticmethod
    def absoluteInterval(note1, note2):
        return abs(note1 - note2) % 12

    @staticmethod
    def diatonicScale(root, step):
        if step == 0:
            return root
        if step > 0:
            for i in range(1, step + 1):
                succ = 2 if (root % 12 != 4 and root % 12 != 11) else 1
                root = root + succ
            return root
        for i in range(1, (-step) + 1):
            succ = -2 if (root % 12 != 0 and root % 12 != 5) else -1
            root = root + succ
        return root

    @staticmethod
    def interval(fr, to):
        s = str(abs(to - fr)+1)
        s_ = (to - fr) % 12
        if abs(to - fr)+1 < 10:
            s = ' ' + s
        if s_ < 5:
            if s_ == 0:
                return s + 'A'
            if s_ % 2 == 0:
                s = s + 'M'
            else:
                s = s + 'm'
        else:
            if s_ == 5 or s_ == 7 or s_ == 0:
                return s + 'A'
            if s_ == 6:
                return s + 'Ag'
            if s_ < 12:
                if s_ % 2 == 0:
                    s = s + 'm'
                else:
                    s = s + 'M'
        return s

    @staticmethod
    def nInterval(note1, note2):
        return abs(note2 - note1) % 12

    @staticmethod
    def printSequence(s, reverse):
        if reverse:
            s = s.copy()
            s.reverse()
            string = ''
        count = 0
        for n in s:
            coeff = '0' if int(n/10) == 0 else ''
            if count != 0:
                string = string + ',   '+coeff + str(n)
            else:
                string = ' ' + coeff + str(n)
            count = count + 1
        print(string)

    @staticmethod
    def printIntervales(s1, s2, reverse):
        s = []
        if reverse:
            s1 = s1.copy()
            s2 = s2.copy()
            s1.reverse()
            s2.reverse()
        for i in range(0, len(s1)):
            s.append(Note.nInterval(s1[i], s2[i]))
        print(s)

    @staticmethod
    def Consonant(note1, note2, debug=False):
        interval = Note.nInterval(note1, note2)
        if interval != 12:
            interval = interval % 12
        if interval == 12:
            if debug:
                print('8va consonance')
            return True
        if interval == 0:
            if debug:
                print(' '+str(note1)+','+str(note2))
            return True
        if interval == 7:
            if debug:
                print(str(interval)+' st consonance '+str(note1)+','+str(note2))
            return True
        if interval == 12:
            if debug:
                print(str(interval)+' st consonance '+str(note1)+','+str(note2))
            return True
        if interval == 3:
            if debug:
                print(str(interval)+' st consonance '+str(note1)+','+str(note2))
            return True
        if interval == 4:
            if debug:
                print(str(interval)+' st consonance '+str(note1)+','+str(note2))
            return True
        if interval == 8:
            if debug:
                print(str(interval)+' st consonance '+str(note1)+','+str(note2))
            return True
        if interval == 9:
            if debug:
                print(str(interval)+' st consonance '+str(note1)+','+str(note2))
            return True
        if debug:
            print(
                 str(interval)+' st disonance ' +
                 Note(note1 % 12).name + ',' + Note(note2 % 12).name)
        if debug:
            print(str(note1)+' '+str(note2))
        return False

    @staticmethod
    def unison(note1, note2):
        return note1 == note2


class Diatonic(Enum):
    C = 0
    D = 1
    E = 2
    F = 3
    G = 4
    A = 5
    B = 6

    @staticmethod
    def equals(note1, note2):
        return (note1 - note2) % 7 == 0

    @staticmethod
    def index(note12):
        # if note < 0:
        #     note = note % 12
        #     return int((note12 + int(note12/5))/2)
        oct = note12//12
        note12 = note12 % 12
        return (note12 + note12//5) // 2 + 7*oct

    @staticmethod
    def interval(note1, note2):
        note1 = Diatonic.index(note1)
        note2 = Diatonic.index(note2)
        return note2 - note1


class ScaleMode(Enum):
    Ionian = 1
    Dorian = 2
    Phrygian = 3
    Lydian = 4
    Mixolydian = 5
    Aeolian = 6
    Locrian = 7
