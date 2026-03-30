from __future__ import annotations

from typing import Literal

from src import Note


MovementType = Literal["similar", "contrary", "oblique", "static"]


def pitch_equals(note1: int, note2: int) -> bool:
    return note1 == note2


def chromatic_interval(note1: int, note2: int) -> int:
    return abs(note2 - note1)


def chromatic_interval_class(note1: int, note2: int) -> int:
    return chromatic_interval(note1, note2) % 12


def diatonic_interval(note1: int, note2: int) -> int:
    return Note.Diatonic.interval(note1, note2)


def melodic_direction(note1: int, note2: int) -> int:
    diff = diatonic_interval(note1, note2)
    if diff > 0:
        return 1
    if diff < 0:
        return -1
    return 0


def is_step(note1: int, note2: int) -> bool:
    return abs(diatonic_interval(note1, note2)) == 1


def interval_label(note1: int, note2: int) -> str:
    diff = chromatic_interval(note1, note2)
    mod = diff % 12
    if mod == 0:
        return "P1" if diff == 0 else "P8"
    if mod == 1:
        return "m2"
    if mod == 2:
        return "M2"
    if mod == 3:
        return "m3"
    if mod == 4:
        return "M3"
    if mod == 5:
        return "P4"
    if mod == 6:
        return "A4/d5"
    if mod == 7:
        return "P5"
    if mod == 8:
        return "m6"
    if mod == 9:
        return "M6"
    if mod == 10:
        return "m7"
    return "M7"


def is_consonant(note1: int, note2: int) -> bool:
    return interval_label(note1, note2) in {"P1", "P5", "P8", "m3", "M3", "m6", "M6"}


def is_strong_consonance(note1: int, note2: int) -> bool:
    return interval_label(note1, note2) in {"m3", "M3", "P5", "m6", "M6", "P8"}


def is_perfect_interval(note1: int, note2: int) -> bool:
    return interval_label(note1, note2) in {"P1", "P5", "P8"}


def perfect_species(note1: int, note2: int) -> str | None:
    label = interval_label(note1, note2)
    if label == "P5":
        return "P5"
    if label in {"P1", "P8"}:
        return "P1/P8"
    return None


def movement_between_voices(cp_prev: int, cp_now: int, cf_prev: int, cf_now: int) -> MovementType:
    cp_dir = melodic_direction(cp_prev, cp_now)
    cf_dir = melodic_direction(cf_prev, cf_now)
    if cp_dir == 0 and cf_dir == 0:
        return "static"
    if cp_dir == 0 or cf_dir == 0:
        return "oblique"
    if cp_dir == cf_dir:
        return "similar"
    return "contrary"


def is_white_note(note: int) -> bool:
    return Note.is_white(note)


def is_cadential_subtonic(note: int, final_note: int, tonic: int) -> bool:
    return note == final_note - cadential_subtonic_distance(tonic)


def same_diatonic_pitch(note1: int, note2: int) -> bool:
    return Note.Diatonic.equals(Note.Diatonic.index(note1), Note.Diatonic.index(note2))


def cadential_subtonic_distance(tonic: int) -> int:
    """Chromatic distance from cadential subtonic to tonic.

    By default, modal cadence raises degree 7 to a leading tone (1 semitone below tonic).
    In Phrygian (E final), cadence keeps the whole-step subtonic (2 semitones below tonic).
    """
    return 2 if tonic % 12 == 4 else 1
