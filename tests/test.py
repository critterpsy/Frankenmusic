import unittest
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import Examples
from src.node import Node
from treeSearch import Voice


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


if __name__ == '__main__':
    unittest.main()
