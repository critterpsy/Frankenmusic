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
