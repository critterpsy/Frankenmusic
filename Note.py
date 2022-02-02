from enum import Enum


class Notes(Enum):
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


def equals(note1, note2):
    return (note1 - note2) % 12 == 0


def is_white(note):
    note = note % 12
    if note <= 4:
        if note % 2 == 0:
            return True
        return False
    else:
        if note % 2 == 0:
            return False
        return True


def print_sequence(s):
    if s is None:
        return
    s_ = []
    for i in range(len(s)):
        if s[i] is None:
            continue
        st = '('
        for j in range(len(s[i])):
            note = Notes(s[i][j] % 12).name + str(s[i][j]//12)
            st += ', {}'.format(note)
        st = st + ')'
        s_.append(st)
    print(s_)



def ninterval(note1, note2):
    return abs(note1 - note2)


def succesor(note):
    """ succesor regresa la siguiente nota mayor o igual que note"""
    if is_white(note + 1):
        return note + 1
    return note + 2


def antecesor(note):
    if is_white(note - 1):
        return note - 1
    return note - 2


def white_scale(root, step):
    if step == 0:
        return root
    if step > 0:
        return succesor(white_scale(root, step - 1))
    return antecesor(white_scale(root, step + 1))


def str_interval(fr, to):
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


def interval(note1, note2, modulo12=True):
    return abs(note1 - note2) % (12 if modulo12 else 1)


def interval_table(s1, s2, reverse):
    s = []
    if reverse:
        s1 = s1.copy()
        s2 = s2.copy()
        s1.reverse()
        s2.reverse()
    for i in range(0, len(s1)):
        s.append(interval(s1[i], s2[i]))


def consonance(note1, note2, imperfect=False):
    inter = interval_12(note1, note2)

    if inter == 0:
        return True
    if inter == 7:
        return True
    if inter == 3:
        return True
    if inter == 4:
        return True
    if inter == 8:
        return True
    if inter == 9:
        return True
    if inter == 5 and imperfect:
        return True
    return False


def valid_chord(chord):
    print('chord received {}'.format(chord))
    chord.sort()
    min = chord[0]
    chord = map(lambda x: (x - min) % 12, chord)
    chord = list(dict.fromkeys(chord))
    intervals = []
    for i in range(1, len(chord)):
        intervals.append(chord[i] - chord[i - 1])
    """ unison """
    if len(intervals) == 0:
        return True
    first = intervals[0]
    ln = len(intervals)
    print('checking chord', chord)
    print(intervals)
    if ln == 1:
        if first == 3 or first == 4 or first == 7 or first == 8 or first == 9:
            return True
        return False
    if ln == 2:
        if first == 3:
            if intervals[1] == 4 or intervals[1] == 5 or intervals[1] == 6:
                return True
        if first == 4:
            if intervals[1] == 3 or intervals[1] == 5:
                return True
        return False
    return False


def dissonance(note1, note2):
    return not consonance(note1, note2)


def unison(note1, note2):
    return note1 == note2


def clamp(note, ceiling):
    while(note > ceiling):
        note -= 12
    return note


def print_chord(chord):
    if chord is None:
        return
    ar = []
    for note in chord:
        ar.append(Notes(note % 12).name + str(note//12))
    print(ar)


def chord(note, ceiling, **filter):
    major = filter.get('major')
    accend = filter.get('ag')
    filterthird = filter.get('3rd')
    filterfifth = filter.get('5th')
    filterroot = filter.get('root')
    chord = []
    if not filterroot:
        chord.append(note)
        if note + 12 <= ceiling:
            chord.append(note + 12)
    if not filterthird:
        if major:
            third = note + 4
        else:
            third = white_scale(note, 2)
        if third > ceiling:
            third -= 12
        chord.append(third)
    if not filterfifth:
        fifth = white_scale(note, 4)
        if fifth > ceiling:
            fifth -= 12
        chord.append(fifth)
    if accend is not None:
        for i in range(0, len(chord)):
            if (chord[i] - accend) % 12 == 0:
                chord[i] = clamp(chord[i] + 1, ceiling)
    return chord


def fifth(note, ceiling):
    fifth = white_scale(note, 4)
    if fifth > ceiling:
        fifth -= 12
    return fifth


def degree(note, n, ceiling, **filter):
    nth = white_scale(note, n - 1)
    if nth > ceiling:
        nth -= 12
    return chord(nth, ceiling, **filter)


def note_range(root, octaves=1, **filter):
    rng = []
    chord = filter.get('chord')
    consonance = filter.get('consonances') or chord
    white_notes = filter.get('whites')
    filter_note = filter.get('!note')
    sib = filter.get('add_sib')
    top = root + 12 * octaves
    for note in range(root, root + 12*octaves + 1):
        if consonance and not consonance(root, note):
            continue
        if chord:
            if interval(root, note) == 8 or interval(root, note) == 9:
                continue
        if white_notes and not is_white(note):
            continue
        if filter_note and equals(note, filter_note):
            continue
        rng.append(note)
    if filter.get('major'):
        rng.remove(white_scale(root, 3))
        rng.append(root + 4)
    if sib:
        for i in range(0, octaves + 1):
            sib = 10
            sib = root + ((sib - root) % 12) + 12 * i
            if sib <= top:
                rng.append(sib)
    return rng


def in_chord(note, chord):
    ''' returns true if note matches%12 any note in chord'''
    for i in range(0, len(chord)):
        if equals(note, chord[i]):
            return True
    return False


def chord_matches(chord1, chord2):
    for note in chord1:
        if not in_chord(note, chord2):
            return False
    return True


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
    def interval(note1, note2, debug=True):
        # if debug:
        #     print('note is ', note1)
        #     print('note is ', note2)
        note1 = Diatonic.index(note1)
        note2 = Diatonic.index(note2)
        #
        # if debug:
        #     print('index1', note1)
        #     print('index2', note2)
        #     print('interval is ', note2 - note1)

        return note2 - note1


class ScaleMode(Enum):
    Ionian = 1
    Dorian = 2
    Phrygian = 3
    Lydian = 4
    Mixolydian = 5
    Aeolian = 6
    Locrian = 7
