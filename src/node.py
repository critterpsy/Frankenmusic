"""
node.py - Node Validation Engine for Counterpoint Rules

This module implements the Node class and validation logic for Renaissance
counterpoint. Each Node represents a single note in a melodic sequence and
contains methods to validate against musical rules for both cantus firmus
and contrapuntal voices.

Key components:
- Node class: Tree node with sequence history and metrics
- Validation rules: Melodic and harmonic constraints (split into focused subreglas)
- Rule dispatchers: Separate logic for CF vs. CP validation
- Quality metrics: Discontinuities, repetitions, variety

Naming conventions:
- prev_note: the integer note value of the immediately preceding position
- melodic_motion(): signed semitone movement from prev_note to note
- melodic_interval_size(): absolute semitone interval (unsigned)
"""

import logging
from .Note import Notes, Diatonic
from . import Note
from . import failureCases
from . import mathutils as mth

logger = logging.getLogger(__name__)

f_ = failureCases
sib = Notes.As.value


class Node:
    """
    Represents a single note in a melodic sequence with full validation state.

    Each node contains the complete note history, current position, and
    accumulated metrics. Provides methods for creating child nodes and
    validating against musical rules.

    Attributes:
        voice: Parent Voice object
        note (int): Current note value
        sequence (list): Complete note history
        index (int): Current position in sequence
        prev_note (int or None): Note value at the previous position (None at root)
        ref: Reference sequence for contrapuntal validation
        Metrics: high, hiIndex, disc (discontinuities), modeRep, pivot
    """

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
            self.prev_note = None
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
        return self.voice.is_cantus()

    def create_child(self, note):
        child = Node(voice=self.voice, is_root=False)
        child.ref = self.ref
        child.note = note
        child.index = self.index + 1
        child.sequence = self.sequence.copy()
        child.sequence.append(note)
        child.pivot = self.pivot
        child.debug = self.debug
        child.prev_note = self.note
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
        return self.valid_cf() and self.valid_cp(chord, lastChord)

    def sensible(self):
        if self.equals(Notes.B) or self.equals(Notes.E):
            return self.note + 1
        return self.note - 1

    # -------------------------------------------------------------------------
    # Melodic motion helpers
    # -------------------------------------------------------------------------

    def melodic_motion(self):
        """Signed semitone movement from prev_note to note. Returns 'NaN' at root."""
        if self.index == 0:
            return 'NaN'
        return self.note - self.prev_note

    def melodic_interval_size(self):
        """Absolute semitone interval between current and previous note."""
        if self.index == 0:
            return 0
        return abs(self.note - self.prev_note)

    # -------------------------------------------------------------------------
    # Harmonic checks (vertical)
    # -------------------------------------------------------------------------

    def _check_sonority(self, chord):
        """General sonority: all notes in chord must form a consonant set."""
        return Note.valid_chord(chord)

    def _check_chord_at_start(self, chord):
        """CP at index 0: must belong to the major chord of the mode."""
        root = self.voice.modo
        ceiling = self.voice.ceiling
        chord_ = Note.chord(root, ceiling, **{'major': True})
        return Note.in_chord(self.note, chord_)

    def _check_chord_at_end(self, chord):
        """CP at last position: must belong to the 3rd of the mode."""
        root = self.voice.modo
        ceiling = self.voice.ceiling
        chord_ = Note.chord(root, ceiling, **{'3rd': True})
        return Note.in_chord(self.note, chord_)

    def _check_chord_at_penultimate(self, chord, num_voices):
        """CP at penultimate: must be in degree-7 chord; top voice must include leading tone."""
        root = self.voice.modo
        ceiling = self.voice.ceiling
        kwargs = {'ag': root + 10}
        chord_ = Note.degree(root, 7, ceiling, **kwargs)
        logger.debug('degree 7 chord: %s', chord_)
        if not Note.in_chord(self.note, chord_):
            return False
        top_voice = (self.voice.index == num_voices - 1)
        if top_voice:
            sensible = root - 1
            return Note.in_chord(sensible, chord)
        return True

    def check_chord(self, chord, num_voices):
        """Validate harmonic position based on sequence index."""
        logger.debug('check_chord: chord=%s ref=%s', chord, self.ref)
        if not self._check_sonority(chord):
            logger.debug('invalid chord')
            return False
        logger.debug('valid chord')
        if self.index == 0:
            return self._check_chord_at_start(chord)
        if self.index == self.length() - 1:
            return self._check_chord_at_end(chord)
        if self.index == self.length() - 2:
            return self._check_chord_at_penultimate(chord, num_voices)
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

    # -------------------------------------------------------------------------
    # Melodic checks (single voice)
    # -------------------------------------------------------------------------

    def checkTritoneInside(self):
        return self.index < 2 or \
            abs(self.note - self.sequence[self.index - 2]) != 6

    def check_jump(self):
        '''Valida que el intervalo melódico esté dentro de los permitidos.

        Prohibido para todas las voces:
          - 6 semitonos (tritono / cuarta aumentada) — también cubierto por checkTritoneInside
          - 9 semitonos (sexta mayor)
          - 10 semitonos (séptima menor)
          - 11 semitonos (séptima mayor)
          - > 12 semitonos

        Prohibido solo en el cantus firmus:
          - 8 semitonos DESCENDENTES (sexta menor descendente)
            Decisión intencional: la sexta menor ASCENDENTE sí está permitida en CF.
        '''
        if self.index == 0:
            return True
        size = self.melodic_interval_size()
        if size in (6, 9, 10, 11):
            return False
        if size > 12:
            return False
        if size == 8 and self.note < self.prev_note and self.is_cantus_firmus():
            return False
        return True

    def checkTritoneIsolated(self):
        index = self.index
        if index < 2:
            return True
        lastJump = self.sequence[index - 1] - self.sequence[index - 2]
        jump = self.note - self.prev_note
        if mth.sign(jump) != mth.sign(lastJump):
            lastPivot = self.pivot
            self.pivot = self.index - 1
            if lastPivot is not None:
                if (self.sequence[lastPivot] - self.prev_note) % 12 == 6:
                    self.pivot = index - 1
                    return False
        return True

    def _check_cf_no_direct_repeat(self):
        """CF: una nota no puede repetir inmediatamente a la anterior."""
        if self.voice.index != 0 or self.index == 0:
            return True
        return self.note != self.prev_note

    def _check_cp_no_skip_repeat(self):
        """CP: si la nota repite a la anterior Y también a seq[i-2]: PROHIBIDO.

        Una repetición aislada (seq[i] == seq[i-1] pero seq[i-2] distinta) sí
        está permitida en CP.
        """
        if self.voice.index == 0 or self.index < 2:
            return True
        return not (self.note == self.prev_note
                    and self.sequence[self.index - 2] == self.note)

    def _check_no_pc_triple(self):
        """Tres notas consecutivas con el mismo pitch-class: PROHIBIDAS en cualquier voz."""
        if self.index < 2:
            return True
        pc = [self.sequence[self.index - 2] % 12,
              self.sequence[self.index - 1] % 12,
              self.note % 12]
        return not (pc[0] == pc[1] == pc[2])

    def check_repetition(self):
        return (
            self._check_cf_no_direct_repeat()
            and self._check_cp_no_skip_repeat()
            and self._check_no_pc_triple()
        )

    # -------------------------------------------------------------------------
    # Cadential helpers
    # -------------------------------------------------------------------------

    def is_cadential_window(self):
        """True when the current position falls within the last 3 notes."""
        return self.index >= self.length() - 3

    def _check_cadential_motion(self, jump, lastJump):
        """Validates melodic motion within the cadential window.

        Ascending leaps always require contrary-motion compensation.
        A descending leap of up to a 4th (5 semitones) may be followed by a
        further descending step at the final position only (e.g. A→E→D in Dorian).
        """
        if lastJump > 2 and jump > 0:
            return False
        if lastJump < -2 and jump < 0:
            is_final = self.index == self.length() - 1
            return is_final and abs(lastJump) <= 5
        return True

    def check_movement(self):
        """After a leap (> step), the next motion must compensate (contrary direction).

        Symmetric for ascending and descending leaps. Within the cadential
        window the specific cadential approach formula overrides the general rule.
        """
        if self.index < 2:
            return True
        jump = self.melodic_motion()
        lastJump = self.sequence[self.index - 1] - self.sequence[self.index - 2]
        if self.is_cadential_window():
            return self._check_cadential_motion(jump, lastJump)
        if abs(lastJump) > 2 and mth.sign(jump) == mth.sign(lastJump):
            return False
        return True

    # -------------------------------------------------------------------------
    # check_note: note-level rules, split into focused subreglas
    # -------------------------------------------------------------------------

    def _check_no_bb_in_cf(self):
        """Bb is forbidden anywhere in the cantus firmus."""
        return not (self.voice.index == 0 and Note.equals(self.note, sib))

    def _check_cf_starts_on_root(self):
        """CF must start on the mode root."""
        if self.index != 0 or self.voice.index != 0:
            return True
        return self.note == self.modo()

    def _check_chromatic_adjacency(self):
        """Reject Bb↔B half-step chromatic motion in any voice."""
        if self.index == 0:
            return True
        prev = self.prev_note
        if Note.equals(self.note, sib + 1) and Note.equals(prev, sib):
            return False
        if Note.equals(self.note, sib) and Note.equals(prev, sib + 1):
            return False
        return True

    def _check_ends_on_root(self):
        """Any voice must end on the mode root."""
        if self.index != self.length() - 1:
            return True
        return Note.equals(self.note, self.modo())

    def _check_cf_antepenultimate(self):
        """CF at length-3: root only allowed with Phrygian semitone approach (e.g. E→F→E)."""
        if self.voice.index != 0 or self.index != self.length() - 3:
            return True
        if not Note.equals(self.note, self.modo()):
            return True
        sup = Note.white_scale(self.modo(), 1)
        return Note.interval(self.modo(), sup) == 1

    def _check_cf_penultimate(self):
        """CF at length-2 must be the diatonic step above the root (supertonic / leading tone)."""
        if self.voice.index != 0 or self.index != self.length() - 2:
            return True
        sup = Note.white_scale(self.modo(), 1)
        return Note.equals(self.note, sup)

    def check_note(self):
        return (
            self._check_no_bb_in_cf()
            and self._check_cf_starts_on_root()
            and self._check_chromatic_adjacency()
            and self._check_ends_on_root()
            and self._check_cf_antepenultimate()
            and self._check_cf_penultimate()
        )

    # -------------------------------------------------------------------------
    # check_sequences: sequential / melodic pattern rules
    # Three window sizes: 3-note, 5-note, 6-note
    # -------------------------------------------------------------------------

    def _check_seq_window3(self, s, i):
        """Reject parallel diatonic sequences in a 3-note window with a leap."""
        jump = Note.interval(s[i - 1], s[i])
        interval02 = Diatonic.interval(s[i - 2], s[i])
        interval13 = Diatonic.interval(s[i - 3], s[i - 1])
        logger.debug('check_sequences w3: seq=%s interval02=%s interval13=%s',
                     s, interval02, interval13)
        if interval02 == interval13 and (abs(jump) > 2 or interval02 == 0):
            return False
        return True

    def _check_seq_skip_repeat(self, s, i):
        """Reject alternating skip pattern: s[i]==s[i-2]==s[i-4]."""
        return not (s[i] == s[i - 2] and s[i - 2] == s[i - 4])

    def _check_seq_window5(self, s, i):
        """Reject parallel sequences in a 5-note window containing a leap,
        including reversed (arch) shapes."""
        interval03 = Diatonic.interval(s[i - 3], s[i])
        interval14 = Diatonic.interval(s[i - 4], s[i - 1])
        interval25 = Diatonic.interval(s[i - 5], s[i - 2])
        window_has_leap = any(Note.interval(s[k], s[k + 1]) > 3
                              for k in range(i - 5, i))
        if window_has_leap and interval25 == interval14 and interval14 == interval03:
            return False
        # Also check reversed (arch) shape
        s_fwd = s[i - 5: i - 2]
        s_rev = list(reversed(s[i - 2:i + 1]))
        s_arch = s_fwd + s_rev
        i_arch = 5
        interval03a = Diatonic.interval(s_arch[0], s_arch[3])
        interval14a = Diatonic.interval(s_arch[1], s_arch[4])
        interval25a = Diatonic.interval(s_arch[2], s_arch[5])
        if window_has_leap and interval25a == interval14a and interval14a == interval03a:
            return False
        return True

    def _check_seq_window6(self, s, i):
        """Reject parallel sequences in a 6-note window containing a leap."""
        interval04 = Diatonic.interval(s[i - 4], s[i])
        interval15 = Diatonic.interval(s[i - 5], s[i - 1])
        interval26 = Diatonic.interval(s[i - 6], s[i - 2])
        window_has_leap = any(Note.interval(s[k], s[k + 1]) > 3
                              for k in range(i - 6, i))
        if window_has_leap and interval04 == interval15 and interval15 == interval26:
            return False
        return True

    def check_sequences(self):
        i = self.index
        s = self.sequence
        if i < 3:
            return True
        if not self._check_seq_window3(s, i):
            return False
        if i < 4:
            return True
        if not self._check_seq_skip_repeat(s, i):
            return False
        if i >= 5 and not self._check_seq_window5(s, i):
            return False
        if i >= 6 and not self._check_seq_window6(s, i):
            return False
        return True

    # -------------------------------------------------------------------------
    # CP generator and validators
    # -------------------------------------------------------------------------

    def cp_valid_generator(self, ref_note, ref_last, chord, ref_index=1,
                           twovoices=False):
        """Genera validaciones armónicas entre esta voz y una voz de referencia.

        ref_note:  nota actual de la voz de referencia en esta posición.
        ref_last:  nota anterior de la voz de referencia (posición i-1).
        ref_index: índice dentro del chord snapshot que corresponde a ref_note;
                   usado para calcular intervalos armónicos repetidos.
        """
        if self.index == 0:
            return
        cp = [self.prev_note, self.note]
        cp_move = cp[1] - cp[0]
        ref = [ref_last, ref_note]
        ref_move = ref[1] - ref[0]
        interval = abs(cp[1] - ref[1]) % 12

        if twovoices:
            if self.ref[self.index] == self.note:
                yield (f_.unison, False)
            else:
                yield ('checkunison', True)

        if interval == 0 and mth.sign(ref_move) == mth.sign(cp_move):
            yield ('checkdirect8', False)
        else:
            yield ('checkdirect8', True)

        if interval == 7 and mth.sign(ref_move) == mth.sign(cp_move):
            yield ('checkdirect5', False)
        else:
            yield ('checkdirect5', True)

        if not Note.consonance(self.note, ref_note):
            yield (f_.dissonance, False)
        else:
            yield (f_.dissonance, True)

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
                                 reference[i][ref_index],
                                 sequence[index - 4 + i]))
            if len(set(intervals)) == 1:
                yield ('checkrepintervals', False)
            else:
                yield ('checkrepintervals', True)

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
            ref_note = chord[i]
            ref_last = lastChord[i] if self.index > 0 else None
            if self.voice.index == 1:
                logger.debug('reference=%s sequence=%s chord=%s lastchord=%s',
                             self.ref, self.sequence, chord, lastChord)
            generator = self.cp_valid_generator(ref_note, ref_last, chord,
                                                ref_index=i)
            if not self.yield_validate(*generator):
                logger.debug('invalid node cp at %d', self.index)
                return False
            else:
                logger.debug('valid node-cp at %d', self.index)
        return True

    def valid_cf(self):
        if self.voice.index > 0:
            logger.debug('generating cp validation from: %s', self.sequence)
        generator = self.cf_valid_generator()
        if self.yield_validate(*generator):
            logger.debug('valid sequence %s, voice_index: %d',
                         self.sequence, self.voice.index)
            return True
        else:
            logger.debug('invalid node cf at %s', self.sequence)
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

    def debug_log(self, operation, result=None):
        self.log_function(operation, result=result)
        index = self.index
        failures = self.failures
        message = str(operation) + '[{}]'.format(self.index)
        self.fail = True
        if not result:
            if index < len(failures):
                failures[index] = failures[index] + message
            else:
                failures.append(message)
        else:
            logger.debug('pass %s', operation)

    def log_function(self, method_name, **kwargs):
        result = kwargs.get('result')
        logger.debug('log function: %s, result: %s', method_name, result)

    def __str__(self):
        numerical = self.sequence
        notes = []
        for note in numerical:
            if note:
                notes.append(str(Notes(note % 12)) + str(note//12))
            else:
                notes.append('none')
        error_log = str(self.failures) if self.debug else ''
        return str(numerical) + '\nnotes :\n  ' + str(notes) + '\nfailures :\n ' + error_log
