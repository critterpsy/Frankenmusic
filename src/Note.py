"""Legacy pitch and interval helpers used by the first-species engine.

This module intentionally keeps the historical public API (`note_range`,
`degree`, `chord`, `succesor`, etc.) because the legacy search engine and its
tests depend on those names. The refactor below makes the musical semantics
explicit without changing the behavior of the existing engine.
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)

CONSONANT_INTERVAL_CLASSES = frozenset({0, 3, 4, 7, 8, 9})
WHITE_PITCH_CLASSES = frozenset({0, 2, 4, 5, 7, 9, 11})


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
    """Return True when two pitch values match by pitch class."""
    return (note1 - note2) % 12 == 0


def is_white(note):
    """Return True when the pitch belongs to the white-note collection."""
    return note % 12 in WHITE_PITCH_CLASSES


def print_sequence(s):
    """Pretty-print a vertical sequence for interactive legacy debugging."""
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
    """Return the unsigned chromatic interval in semitones."""
    return abs(note1 - note2)


def successor_white_note(note):
    """Return the next ascending white note from ``note``."""
    if is_white(note + 1):
        return note + 1
    return note + 2


def predecessor_white_note(note):
    """Return the next descending white note from ``note``."""
    if is_white(note - 1):
        return note - 1
    return note - 2


def succesor(note):
    """Legacy alias kept for compatibility with older code paths."""
    return successor_white_note(note)


def antecesor(note):
    """Legacy alias kept for compatibility with older code paths."""
    return predecessor_white_note(note)


def white_scale(root, step):
    """Move ``step`` diatonic white-note degrees away from ``root``."""
    if step == 0:
        return root
    if step > 0:
        return successor_white_note(white_scale(root, step - 1))
    return predecessor_white_note(white_scale(root, step + 1))


def str_interval(fr, to):
    """Return the legacy text label used by historical debug output."""
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
    """Return the unsigned chromatic interval between two notes."""
    diff = abs(note1 - note2)
    return diff % 12 if modulo12 else diff


def interval_table(s1, s2, reverse):
    """Build a list of pairwise intervals between two sequences."""
    s = []
    if reverse:
        s1 = s1.copy()
        s2 = s2.copy()
        s1.reverse()
        s2.reverse()
    for i in range(0, len(s1)):
        s.append(interval(s1[i], s2[i]))
    return s


def consonance(note1, note2):
    """Returns True if the interval between note1 and note2 is consonant.

    Consonant intervals (mod 12): unison (0), minor 3rd (3), major 3rd (4),
    perfect 5th (7), minor 6th (8), major 6th (9).

    The perfect 4th (5 st) is treated as a dissonance against the bass in
    Renaissance first-species counterpoint, following standard doctrine.
    """
    return interval(note1, note2) in CONSONANT_INTERVAL_CLASSES


def _normalized_chord_pitch_classes(notes):
    """Normalize a chord against its lowest note and deduplicate pitch classes."""
    ordered = sorted(notes)
    root = ordered[0]
    normalized = [(note - root) % 12 for note in ordered]
    return list(dict.fromkeys(normalized))


def _adjacent_intervals(values):
    """Return adjacent differences for an ordered list of pitch classes."""
    return [values[i] - values[i - 1] for i in range(1, len(values))]


def valid_chord(chord):
    """Validate the legacy first-species vertical sonority model.

    This is intentionally conservative and historical: it accepts the exact
    vertical spellings the legacy engine was built around, rather than acting
    as a complete Renaissance harmony model.
    """
    logger.debug('chord received %s', chord)
    chord = _normalized_chord_pitch_classes(chord)
    intervals = _adjacent_intervals(chord)
    if len(intervals) == 0:
        return True
    first = intervals[0]
    ln = len(intervals)
    logger.debug('checking chord %s, intervals %s', chord, intervals)
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
    """Return True when the interval is not treated as consonant."""
    return not consonance(note1, note2)


def unison(note1, note2):
    """Return True only for exact pitch equality, not pitch-class equality."""
    return note1 == note2


def clamp(note, ceiling):
    """Wrap a pitch down by octaves until it fits at or below ``ceiling``."""
    while note > ceiling:
        note -= 12
    return note


def print_chord(chord):
    """Pretty-print a chord for legacy debugging output."""
    if chord is None:
        return
    ar = []
    for note in chord:
        ar.append(Notes(note % 12).name + str(note//12))
    print(ar)


def chord(note, ceiling, **filter):
    """Build the legacy note collection for a triadic sonority around ``note``.

    Supported historical filters:
    - ``major``: raise the third chromatically
    - ``ag``: sharpen the pitch class matching the provided note
    - ``3rd`` / ``5th`` / ``root``: omit that chord factor
    """
    use_major_third = filter.get('major')
    accidental_target = filter.get('ag')
    omit_third = filter.get('3rd')
    omit_fifth = filter.get('5th')
    omit_root = filter.get('root')

    chord_notes = []
    if not omit_root:
        chord_notes.append(note)
        if note + 12 <= ceiling:
            chord_notes.append(note + 12)

    if not omit_third:
        if use_major_third:
            third = note + 4
        else:
            third = white_scale(note, 2)
        if third > ceiling:
            third -= 12
        chord_notes.append(third)

    if not omit_fifth:
        fifth = white_scale(note, 4)
        if fifth > ceiling:
            fifth -= 12
        chord_notes.append(fifth)

    if accidental_target is not None:
        for i, chord_note in enumerate(chord_notes):
            if (chord_note - accidental_target) % 12 == 0:
                chord_notes[i] = clamp(chord_note + 1, ceiling)
    return chord_notes


def fifth(note, ceiling):
    """Return the white-note fifth above ``note`` within ``ceiling``."""
    fifth = white_scale(note, 4)
    if fifth > ceiling:
        fifth -= 12
    return fifth


def degree(note, n, ceiling, **filter):
    """Return the legacy chord collection built on scale degree ``n`` above ``note``."""
    nth = white_scale(note, n - 1)
    if nth > ceiling:
        nth -= 12
    return chord(nth, ceiling, **filter)


def _apply_major_third_override(note_collection, root):
    """Apply the legacy 'major third' replacement in-place-compatible order."""
    note_collection.remove(white_scale(root, 3))
    note_collection.append(root + 4)


def _append_b_flat_variants(note_collection, root, octaves, top):
    """Append Bb spellings historically allowed by the legacy pitch range builder."""
    for octave in range(0, octaves + 1):
        b_flat = 10
        b_flat = root + ((b_flat - root) % 12) + 12 * octave
        if b_flat <= top:
            note_collection.append(b_flat)


def note_range(root, octaves=1, **filter):
    """Build the legacy pitch search domain above ``root``.

    This helper does more than range construction: it can enforce consonance,
    white-note filtering, omission of a pitch class, major-third adjustment,
    and optional Bb insertion. The semantics are historical and intentionally
    preserved because the legacy search engine relies on them.
    """
    note_collection = []
    chord_filter = filter.get('chord')
    require_consonance = filter.get('consonances') or chord_filter
    white_notes_only = filter.get('whites')
    excluded_pitch = filter.get('!note')
    add_b_flat = filter.get('add_sib')
    top = root + 12 * octaves

    for note in range(root, root + 12 * octaves + 1):
        if require_consonance and not consonance(root, note):
            continue
        if chord_filter and interval(root, note) in (8, 9):
                continue
        if white_notes_only and not is_white(note):
            continue
        if excluded_pitch and equals(note, excluded_pitch):
            continue
        note_collection.append(note)

    if filter.get('major'):
        _apply_major_third_override(note_collection, root)
    if add_b_flat:
        _append_b_flat_variants(note_collection, root, octaves, top)
    return note_collection


def in_chord(note, chord):
    """Return True when ``note`` matches any chord tone by pitch class."""
    for chord_note in chord:
        if equals(note, chord_note):
            return True
    return False


def chord_matches(chord1, chord2):
    """Return True when every note in ``chord1`` is represented in ``chord2``."""
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
