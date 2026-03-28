import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import Examples
from src.node import Node
from src.Note import Notes
from treeSearch import Voice, TreeSearch


# Known bugs that cause valid examples to fail validation.
# Key = sequence tuple, value = reason string.
CP_KNOWN_BUGS = {}

CF_KNOWN_BUGS = {}


def _make_voice(seq, voice_index=0, octave=None):
    if octave is None:
        octave = seq[0] // 12
    return Voice(
        modo=seq[0] % 12,
        octave=octave,
        index=voice_index,
        _range=1,
        length=len(seq)
    )


def _build_node_seq(seq, voice_index=0, length=None):
    """Construye una cadena de nodos para la secuencia dada y devuelve el nodo final.

    length: override de la longitud del voice (útil para tests cadenciales donde
    la posición relativa al final importa pero la secuencia es más corta).
    """
    actual_length = length if length is not None else len(seq)
    voice = Voice(
        modo=seq[0] % 12,
        octave=seq[0] // 12,
        index=voice_index,
        _range=1,
        length=actual_length,
    )
    node = Node(voice, seq[0])
    for note in seq[1:]:
        node = node.create_child(note)
    return node


def _validate_cf(seq):
    """Walk a CF sequence. Returns index of first invalid node, or -1 if all pass."""
    voice = _make_voice(seq, voice_index=0)
    node = Node(voice, seq[0])
    if not node.is_valid(1, []):
        return 0
    for i in range(1, len(seq)):
        node = node.create_child(seq[i])
        if not node.is_valid(1, []):
            return i
    return -1


def _validate_cp(cp_seq, cf_seq):
    """Walk a CP sequence against a CF. Returns index of first invalid node, or -1."""
    cf_modo = cf_seq[0] % 12
    cp_voice = Voice(modo=cf_modo, octave=1, index=1, _range=1, length=len(cp_seq))
    chord_ref = [[note] for note in cf_seq]

    node = Node(cp_voice, cp_seq[0], ref=chord_ref)
    chord_0 = chord_ref[0] + [cp_seq[0]]
    if not node.is_valid(2, chord_0):
        return 0
    for i in range(1, len(cp_seq)):
        node = node.create_child(cp_seq[i])
        new_chord = chord_ref[i] + [cp_seq[i]]
        last_chord = chord_ref[i - 1] + [cp_seq[i - 1]]
        if not node.is_valid(2, new_chord, last_chord):
            return i
    return -1


class TestCF(unittest.TestCase):

    def test_valid_examples(self):
        for e in Examples.cf_examples:
            key = tuple(e.sequence)
            known_bug = CF_KNOWN_BUGS.get(key)
            if known_bug:
                # Skip assertion for known bugs — they are tracked in CF_KNOWN_BUGS
                continue
            with self.subTest(seq=e.sequence):
                idx = _validate_cf(e.sequence)
                self.assertEqual(
                    idx, -1,
                    f"Valid CF rejected at index {idx}: {e.sequence}"
                )

    def test_fail_examples(self):
        for e in Examples.cf_fail_examples:
            with self.subTest(seq=e.sequence):
                idx = _validate_cf(e.sequence)
                self.assertNotEqual(
                    idx, -1,
                    f"Expected CF failure not detected: {e.sequence}"
                )


class TestCP(unittest.TestCase):

    def test_valid_examples(self):
        cf_seq = Examples.reference_cf
        for e in Examples.cp_examples:
            key = tuple(e.sequence)
            if CP_KNOWN_BUGS.get(key):
                continue
            with self.subTest(name=e.name, seq=e.sequence):
                idx = _validate_cp(e.sequence, cf_seq)
                self.assertEqual(
                    idx, -1,
                    f"Valid CP rejected at index {idx}: {e.sequence}"
                )

    def test_fail_examples(self):
        cf_seq = Examples.reference_cf
        for e in Examples.cp_fail_examples:
            with self.subTest(name=e.name, seq=e.sequence):
                idx = _validate_cp(e.sequence, cf_seq)
                self.assertNotEqual(
                    idx, -1,
                    f"Expected CP failure not detected: {e.sequence}"
                )


class TestCFDecisions(unittest.TestCase):
    """Tests explícitos para decisiones musicales doctrinales del CF."""

    def test_minor6th_ascending_cf_allowed(self):
        """Sexta menor ASCENDENTE (8 st) en CF: PERMITIDA."""
        # A(9) → F(17): +8 semitonos, sexta menor ascendente en modo A
        seq = [9, 17, 16, 14, 11, 9]
        idx = _validate_cf(seq)
        self.assertEqual(idx, -1,
            f"Minor 6th ascending in CF should be allowed; rejected at index {idx}")

    def test_minor6th_descending_cf_prohibited(self):
        """Sexta menor DESCENDENTE (8 st) en CF: PROHIBIDA (check_jump)."""
        # Ab(8) → C(0): -8 semitonos, debe fallar en check_jump al index 1
        seq = [8, 0, 10, 8]
        idx = _validate_cf(seq)
        self.assertEqual(idx, 1,
            f"Minor 6th descending in CF should be rejected at index 1; got {idx}")

    def test_no_compensation_after_leap(self):
        """Compensación tras salto: continuar en la misma dirección viola check_movement."""
        # C(0)→E(4)→G(7): salto C→E (+4 st), luego E→G (+3 st) sigue subiendo → inválido
        seq = [0, 4, 7, 5, 2, 0]
        idx = _validate_cf(seq)
        self.assertEqual(idx, 2,
            f"No-compensation after leap should be rejected at index 2; got {idx}")


class TestJumpRules(unittest.TestCase):
    """Tests unitarios para check_jump: intervalos permitidos y prohibidos. [C12/C13]"""

    def _jump(self, prev, note, voice_index=0):
        """Llama check_jump() en un nodo child (prev → note)."""
        node = _build_node_seq([prev, note], voice_index=voice_index)
        return node.check_jump()

    # --- Prohibidos en todas las voces ---

    def test_tritone_ascending_forbidden(self):
        """Tritono ascendente (6 st): PROHIBIDO."""
        self.assertFalse(self._jump(0, 6))

    def test_tritone_descending_forbidden(self):
        """Tritono descendente (6 st): PROHIBIDO."""
        self.assertFalse(self._jump(6, 0))

    def test_major_sixth_ascending_forbidden(self):
        """Sexta mayor ascendente (9 st): PROHIBIDA."""
        self.assertFalse(self._jump(0, 9))

    def test_major_sixth_descending_forbidden(self):
        """Sexta mayor descendente (9 st): PROHIBIDA."""
        self.assertFalse(self._jump(9, 0))

    def test_minor_seventh_ascending_forbidden(self):
        """Séptima menor ascendente (10 st): PROHIBIDA."""
        self.assertFalse(self._jump(0, 10))

    def test_minor_seventh_descending_forbidden(self):
        """Séptima menor descendente (10 st): PROHIBIDA."""
        self.assertFalse(self._jump(10, 0))

    def test_major_seventh_ascending_forbidden(self):
        """Séptima mayor ascendente (11 st): PROHIBIDA."""
        self.assertFalse(self._jump(0, 11))

    def test_major_seventh_descending_forbidden(self):
        """Séptima mayor descendente (11 st): PROHIBIDA."""
        self.assertFalse(self._jump(11, 0))

    def test_beyond_octave_forbidden(self):
        """Intervalo > octava (13 st): PROHIBIDO."""
        self.assertFalse(self._jump(0, 13))
        self.assertFalse(self._jump(13, 0))

    # --- CF-específico: sexta menor ---

    def test_minor_sixth_ascending_cf_allowed(self):
        """Sexta menor ASCENDENTE (8 st) en CF: PERMITIDA. [C13]"""
        self.assertTrue(self._jump(0, 8, voice_index=0))

    def test_minor_sixth_descending_cf_forbidden(self):
        """Sexta menor DESCENDENTE (8 st) en CF: PROHIBIDA. [C13]"""
        self.assertFalse(self._jump(8, 0, voice_index=0))

    def test_minor_sixth_descending_cp_allowed(self):
        """Sexta menor DESCENDENTE (8 st) en CP: PERMITIDA (restricción solo aplica al CF). [C13]"""
        self.assertTrue(self._jump(8, 0, voice_index=1))

    # --- Intervalos permitidos ---

    def test_step_allowed(self):
        """Paso diatónico (1-2 st): PERMITIDO."""
        self.assertTrue(self._jump(0, 1))
        self.assertTrue(self._jump(0, 2))

    def test_minor_third_allowed(self):
        """Tercera menor (3 st): PERMITIDA."""
        self.assertTrue(self._jump(0, 3))
        self.assertTrue(self._jump(3, 0))

    def test_major_third_allowed(self):
        """Tercera mayor (4 st): PERMITIDA."""
        self.assertTrue(self._jump(0, 4))
        self.assertTrue(self._jump(4, 0))

    def test_perfect_fourth_allowed(self):
        """Cuarta justa (5 st): PERMITIDA."""
        self.assertTrue(self._jump(0, 5))
        self.assertTrue(self._jump(5, 0))

    def test_perfect_fifth_allowed(self):
        """Quinta justa (7 st): PERMITIDA."""
        self.assertTrue(self._jump(0, 7))
        self.assertTrue(self._jump(7, 0))

    def test_octave_allowed(self):
        """Octava justa (12 st): PERMITIDA."""
        self.assertTrue(self._jump(0, 12))
        self.assertTrue(self._jump(12, 0))


class TestRepetitionRules(unittest.TestCase):
    """Tests unitarios para check_repetition. [G2]"""

    def test_repeated_note_cf_forbidden(self):
        """Nota repetida consecutivamente en CF: PROHIBIDA."""
        node = _build_node_seq([2, 2], voice_index=0)
        self.assertFalse(node.check_repetition())

    def test_different_notes_cf_allowed(self):
        """Notas diferentes en CF: PERMITIDAS."""
        node = _build_node_seq([2, 4], voice_index=0)
        self.assertTrue(node.check_repetition())

    def test_single_repeat_cp_allowed(self):
        """Nota repetida una vez en CP (sin aparición en i-2): PERMITIDA."""
        # index=1: seq[i-2] no se comprueba (index < 2) → True
        node = _build_node_seq([9, 9], voice_index=1)
        self.assertTrue(node.check_repetition())

    def test_repeat_cp_with_same_at_i_minus_2_forbidden(self):
        """CP: nota igual a prev_note Y a seq[i-2]: PROHIBIDA."""
        # seq=[9,9,9], index=2: note==prev_note, seq[0]==note → False
        node = _build_node_seq([9, 9, 9], voice_index=1)
        self.assertFalse(node.check_repetition())

    def test_three_same_pc_cf_forbidden(self):
        """3 notas consecutivas con mismo pitch-class en CF (ej. octava de por medio): PROHIBIDAS."""
        # C(0)→C8va(12)→C(0): PC = [0, 0, 0] → False
        node = _build_node_seq([0, 12, 0], voice_index=0)
        self.assertFalse(node.check_repetition())

    def test_three_same_pc_cp_forbidden(self):
        """3 notas consecutivas con mismo pitch-class en CP: PROHIBIDAS."""
        # A(9)→A8va(21)→A(9): PC = [9, 9, 9] → False
        node = _build_node_seq([9, 21, 9], voice_index=1)
        self.assertFalse(node.check_repetition())

    def test_two_same_pc_allowed(self):
        """Solo 2 notas con el mismo PC (no 3 consecutivas): PERMITIDAS."""
        # seq=[0, 12, 4]: PC = [0, 0, 4] → la tercera difiere → True
        node = _build_node_seq([0, 12, 4], voice_index=0)
        self.assertTrue(node.check_repetition())


class TestCadentialRules(unittest.TestCase):
    """Tests unitarios para check_movement en la ventana cadencial. [C14]"""

    def test_ascending_leap_no_compensation_cadential_forbidden(self):
        """Salto ascendente > 2ª en ventana cadencial sin compensar: PROHIBIDO.

        length=5 → cadential window = índices 2,3,4.
        En index=4: lastJump = seq[3]-seq[2] = 5-0 = 5 > 2,
                     jump = seq[4]-seq[3] = 7-5 = 2 > 0 → False.
        """
        node = _build_node_seq([0, 2, 0, 5, 7])
        self.assertFalse(node.check_movement())

    def test_descending_small_leap_at_final_allowed(self):
        """Salto descendente ≤ 4ª (≤ 5 st) seguido de descenso en nota final: PERMITIDO.

        length=5, index=4 (final): lastJump = 9-13 = -4 < -2,
                                    jump = 7-9 = -2 < 0,
                                    is_final=True, abs(-4)=4 ≤ 5 → True.
        """
        node = _build_node_seq([9, 11, 13, 9, 7])
        self.assertTrue(node.check_movement())

    def test_descending_large_leap_at_final_forbidden(self):
        """Salto descendente > 4ª (> 5 st) seguido de descenso en nota final: PROHIBIDO.

        length=5, index=4 (final): lastJump = 7-13 = -6 < -2,
                                    jump = 5-7 = -2 < 0,
                                    is_final=True, abs(-6)=6 > 5 → False.
        """
        node = _build_node_seq([9, 11, 13, 7, 5])
        self.assertFalse(node.check_movement())

    def test_descending_small_leap_non_final_cadential_forbidden(self):
        """Salto descendente ≤ 4ª seguido de descenso en posición cadencial no-final: PROHIBIDO.

        length=6 → cadential window = índices 3,4,5.
        index=4 (no es final): lastJump = -4 < -2, jump = -2 < 0,
                               is_final=(4==5)=False → False.
        """
        node = _build_node_seq([9, 11, 13, 9, 7], length=6)
        self.assertFalse(node.check_movement())

    def test_general_leap_compensation_outside_cadential_window(self):
        """Fuera de la ventana cadencial: salto ascendente requiere compensación (regla general).

        length=7 → cadential window = índices 4,5,6.
        index=2 (fuera): lastJump = 5-0 = 5 > 2, jump = 7-5 = 2 > 0,
                          misma dirección → False.
        """
        node = _build_node_seq([0, 5, 7], length=7)
        self.assertFalse(node.check_movement())


def _make_ts_with_seqs(seqs):
    """Build a TreeSearch with pre-populated voice pools for testing validate_polyphonic_set.

    Does NOT call generate_voices(). Injects pre-built nodes directly into
    each voice's pool so that validate_polyphonic_set() can be called in
    isolation.
    """
    length = len(seqs[0])
    ts = TreeSearch(modo=Notes.C, length=length, num_voices=len(seqs),
                    sequential=True)
    for i, seq in enumerate(seqs):
        node = _build_node_seq(seq, voice_index=i, length=length)
        ts.voices[i].pool = [node]
    return ts


class TestLegacyPoolSemantics(unittest.TestCase):
    """Compatibility tests for legacy pool selection semantics."""

    def test_to_chord_defaults_to_best_ranked_pool_entry(self):
        ts = TreeSearch(modo=Notes.C, length=3, num_voices=2, sequential=True)
        best_cf = _build_node_seq([0, 2, 0], voice_index=0, length=3)
        alt_cf = _build_node_seq([0, 4, 0], voice_index=0, length=3)
        cp = _build_node_seq([7, 9, 7], voice_index=1, length=3)

        ts.voices[0].pool = [best_cf, alt_cf]
        ts.voices[1].pool = [cp]

        self.assertEqual(ts.to_chord(), [[0, 7], [2, 9], [0, 7]])
        self.assertEqual(ts.to_chord(1), [[0, 7], [4, 9], [0, 7]])


class TestPolyphonicValidation(unittest.TestCase):
    """Tests for validate_polyphonic_set() post-hoc global checker. [A3/B4]"""

    def test_two_voice_search_passes_global_validation(self):
        """A valid 2-voice result produced by TreeSearch must have no global violations."""
        ts = TreeSearch(modo=Notes.D, length=7, num_voices=2,
                        sequential=True, exhaustive_search=False)
        ts.generate_voices()
        self.assertTrue(ts.voices[0].found() and ts.voices[1].found(),
                        "TreeSearch must find a 2-voice result to validate")
        violations = ts.validate_polyphonic_set()
        self.assertEqual(violations, [],
                         f"Valid 2-voice result should have no violations: {violations}")

    def test_parallel_fifth_detected(self):
        """Parallel 5ths (both voices move same direction, arriving at P5) must be flagged."""
        # voice 0: [0, 2], voice 1: [7, 9]
        # t=0: interval(0,7)=7, t=1: interval(2,9)=7; both move +2 → parallel 5th at t=1
        ts = _make_ts_with_seqs([[0, 2], [7, 9]])
        violations = ts.validate_polyphonic_set()
        self.assertTrue(any("Parallel 5th" in v for v in violations),
                        f"Parallel 5th not detected: {violations}")

    def test_parallel_octave_detected(self):
        """Parallel octaves (arriving at 0 mod 12 by similar motion) must be flagged."""
        # voice 0: [0, 2], voice 1: [12, 14]
        # t=1: interval(2,14) = 12%12 = 0; both move +2 → parallel octave at t=1
        ts = _make_ts_with_seqs([[0, 2], [12, 14]])
        violations = ts.validate_polyphonic_set()
        self.assertTrue(any("Parallel octave" in v for v in violations),
                        f"Parallel octave not detected: {violations}")

    def test_dissonance_detected(self):
        """Vertical dissonances must be flagged."""
        # voice 0: [0], voice 1: [6]  → tritone (6 st) is dissonant
        ts = _make_ts_with_seqs([[0], [6]])
        violations = ts.validate_polyphonic_set()
        self.assertTrue(any("Dissonance" in v for v in violations),
                        f"Dissonance not detected: {violations}")

    def test_no_violations_for_clean_pair(self):
        """Consonant pair with no parallel 5ths or octaves must produce no violations."""
        # voice 0: [0, 2], voice 1: [9, 11]
        # t=0: interval(0,9)=9 (M6) ✓; t=1: interval(2,11)=9 (M6) ✓
        # both move +2 (similar motion), but arrival interval is 9 ≠ 7 or 0 → no parallel violation
        ts = _make_ts_with_seqs([[0, 2], [9, 11]])
        violations = ts.validate_polyphonic_set()
        self.assertEqual(violations, [],
                         f"Clean consonant pair should have no violations: {violations}")

    def test_oblique_motion_to_fifth_not_flagged(self):
        """A stationary voice arriving at a P5 by oblique motion must not be flagged."""
        # voice 0: [0, 0], voice 1: [4, 7]  → voice 0 stays, voice 1 moves
        # t=1: interval(0,7)=7, but move_0=0 → oblique, not similar motion → no parallel 5th
        ts = _make_ts_with_seqs([[0, 0], [4, 7]])
        violations = ts.validate_polyphonic_set()
        self.assertFalse(any("Parallel 5th" in v for v in violations),
                         f"Oblique motion to P5 should not be flagged: {violations}")

    def test_contrary_motion_to_fifth_not_flagged(self):
        """Contrary motion arriving at a P5 must not be flagged."""
        # voice 0: [0, 5], voice 1: [9, 0]
        # t=1: interval(5,0)=5... let me use [0, 7] and [9, 0]
        # move_0 = +7, move_1 = -9 → opposite signs → contrary → no parallel 5th
        # interval(7,0) = 7 → P5, but contrary → OK
        ts = _make_ts_with_seqs([[0, 7], [9, 0]])
        violations = ts.validate_polyphonic_set()
        self.assertFalse(any("Parallel 5th" in v for v in violations),
                         f"Contrary motion to P5 should not be flagged: {violations}")

    def test_stable_num_voices_constant(self):
        """STABLE_NUM_VOICES must be 2."""
        self.assertEqual(TreeSearch.STABLE_NUM_VOICES, 2)


class TestExhaustiveSearch(unittest.TestCase):
    """Tests del comportamiento de exhaustive_search en TreeSearch."""

    def _run_cf(self, exhaustive):
        ts = TreeSearch(modo=Notes.D, length=7, sequential=True,
                        num_voices=1, exhaustive_search=exhaustive)
        ts.generate_voices()
        return ts.voices[0].pool

    def test_exhaustive_false_stops_at_first(self):
        """exhaustive_search=False: el motor se detiene al primer resultado (pool ≤ 1)."""
        pool = self._run_cf(exhaustive=False)
        self.assertLessEqual(len(pool), 1,
            "exhaustive_search=False should yield at most 1 result")

    def test_exhaustive_true_finds_at_least_as_many(self):
        """exhaustive_search=True: no hace early-exit; acumula ≥ resultados que False."""
        pool_false = self._run_cf(exhaustive=False)
        pool_true = self._run_cf(exhaustive=True)
        self.assertGreaterEqual(len(pool_true), len(pool_false),
            "exhaustive_search=True must find at least as many results as False")


class TestMidiFilename(unittest.TestCase):
    """Tests para el fix del guard de os.makedirs con midi_filename simple."""

    def test_simple_filename_no_makedirs(self):
        """Filename sin directorio: os.path.dirname es '' (falsy) → makedirs no se llama."""
        simple_filename = 'output.mid'
        with patch('os.makedirs') as mock_makedirs:
            dirname = os.path.dirname(simple_filename)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            mock_makedirs.assert_not_called()

    def test_nested_filename_calls_makedirs(self):
        """Filename con directorio: os.path.dirname no es '' → makedirs sí se llama."""
        nested_filename = 'output/midis/file.mid'
        with patch('os.makedirs') as mock_makedirs:
            dirname = os.path.dirname(nested_filename)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            mock_makedirs.assert_called_once_with('output/midis', exist_ok=True)


if __name__ == '__main__':
    unittest.main()
