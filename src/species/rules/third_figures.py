from __future__ import annotations

from typing import Literal

from ..models import CPNote, TemporalGrid
from ..music_core import diatonic_interval, is_consonant, is_step, melodic_direction
ThirdFigureKind = Literal[
    "consonant",
    "passing_tone",
    "lower_neighbor",
    "cambiata",
    "upper_neighbor",
    "invalid",
]


def classify_third_species_weak_slot(
    grid: TemporalGrid,
    slots: list[CPNote],
    weak_index: int,
) -> ThirdFigureKind:
    slot = grid.slots[weak_index]
    weak = slots[weak_index]
    if weak is None:
        return "invalid"
    if slot.beat not in {2, 4}:
        return "invalid"
    if is_consonant(weak, slot.cf_pitch):
        return "consonant"

    lower_neighbor = _is_lower_neighbor(grid, slots, weak_index)
    if lower_neighbor:
        return "lower_neighbor"

    if _is_upper_neighbor(grid, slots, weak_index):
        return "upper_neighbor"

    if _is_cambiata(grid, slots, weak_index):
        return "cambiata"

    if _is_passing_tone(grid, slots, weak_index):
        return "passing_tone"

    return "invalid"


def collect_third_species_dissonance_figures(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> dict[int, ThirdFigureKind]:
    figures: dict[int, ThirdFigureKind] = {}
    for slot in grid.weak_slots:
        note = slots[slot.index]
        if note is None or is_consonant(note, slot.cf_pitch):
            continue
        figures[slot.index] = classify_third_species_weak_slot(grid, slots, slot.index)
    return figures


def _is_passing_tone(grid: TemporalGrid, slots: list[CPNote], weak_index: int) -> bool:
    prev_slot, prev_note, next_slot, next_note = _surrounding_support(grid, slots, weak_index)
    if prev_slot is None or prev_note is None or next_slot is None or next_note is None:
        return False

    weak = slots[weak_index]
    assert weak is not None

    if not is_consonant(prev_note, prev_slot.cf_pitch):
        return False
    if not is_consonant(next_note, next_slot.cf_pitch):
        return False

    step_in = is_step(prev_note, weak)
    step_out = is_step(weak, next_note)
    dir_in = melodic_direction(prev_note, weak)
    dir_out = melodic_direction(weak, next_note)
    if not (step_in and step_out and dir_in != 0 and dir_in == dir_out):
        return False

    if _is_upper_neighbor(grid, slots, weak_index):
        return False

    return True


def _is_lower_neighbor(grid: TemporalGrid, slots: list[CPNote], weak_index: int) -> bool:
    prev_slot, prev_note, next_slot, next_note = _surrounding_support(grid, slots, weak_index)
    if prev_slot is None or prev_note is None or next_slot is None or next_note is None:
        return False
    weak = slots[weak_index]
    assert weak is not None

    if not is_consonant(prev_note, prev_slot.cf_pitch):
        return False
    if not is_consonant(next_note, next_slot.cf_pitch):
        return False
    if prev_note != next_note:
        return False

    if diatonic_interval(prev_note, weak) != -1:
        return False
    if not is_step(prev_note, weak):
        return False
    if not is_step(weak, next_note):
        return False
    dir_in = melodic_direction(prev_note, weak)
    dir_out = melodic_direction(weak, next_note)
    return dir_in != 0 and dir_out != 0 and dir_in == -dir_out


def _is_upper_neighbor(grid: TemporalGrid, slots: list[CPNote], weak_index: int) -> bool:
    prev_slot, prev_note, next_slot, next_note = _surrounding_support(grid, slots, weak_index)
    if prev_slot is None or prev_note is None or next_slot is None or next_note is None:
        return False
    weak = slots[weak_index]
    assert weak is not None

    if not is_consonant(prev_note, prev_slot.cf_pitch):
        return False
    if not is_consonant(next_note, next_slot.cf_pitch):
        return False
    if prev_note != next_note:
        return False
    if diatonic_interval(prev_note, weak) != 1:
        return False
    if not is_step(prev_note, weak):
        return False
    if not is_step(weak, next_note):
        return False
    dir_in = melodic_direction(prev_note, weak)
    dir_out = melodic_direction(weak, next_note)
    return dir_in != 0 and dir_out != 0 and dir_in == -dir_out


def _is_cambiata(grid: TemporalGrid, slots: list[CPNote], weak_index: int) -> bool:
    weak_slot = grid.slots[weak_index]
    # Canon 2026-03-30: cambiata in pure 4:1 is only recognized as
    # a beat2 dissonance resolved inside the same measure (1-2-3-4).
    if weak_slot.beat != 2:
        return False
    if weak_index < 1 or weak_index + 2 >= len(slots):
        return False

    n1_slot = grid.slots[weak_index - 1]
    n2_slot = weak_slot
    n3_slot = grid.slots[weak_index + 1]
    n4_slot = grid.slots[weak_index + 2]
    n1 = slots[n1_slot.index]
    n2 = slots[n2_slot.index]
    n3 = slots[n3_slot.index]
    n4 = slots[n4_slot.index]
    if n1 is None or n2 is None or n3 is None or n4 is None:
        return False
    if n1_slot.measure != n2_slot.measure or n3_slot.measure != n2_slot.measure or n4_slot.measure != n2_slot.measure:
        return False
    if (n1_slot.beat, n2_slot.beat, n3_slot.beat, n4_slot.beat) != (1, 2, 3, 4):
        return False

    if not is_consonant(n1, n1_slot.cf_pitch):
        return False
    if is_consonant(n2, n2_slot.cf_pitch):
        return False
    if not is_consonant(n3, n3_slot.cf_pitch):
        return False
    if not is_consonant(n4, n4_slot.cf_pitch):
        return False

    entry_dir = melodic_direction(n1, n2)
    if entry_dir != -1:
        return False
    if not is_step(n1, n2):
        return False

    out_dir = melodic_direction(n2, n3)
    if out_dir != entry_dir:
        return False
    if abs(diatonic_interval(n2, n3)) != 2:
        return False

    if not is_step(n3, n4):
        return False
    if melodic_direction(n3, n4) != -entry_dir:
        return False

    return True


def _surrounding_support(
    grid: TemporalGrid,
    slots: list[CPNote],
    weak_index: int,
) -> tuple[object | None, int | None, object | None, int | None]:
    prev_index = weak_index - 1
    next_index = weak_index + 1
    if prev_index < 0 or next_index >= len(slots):
        return None, None, None, None
    prev_slot = grid.slots[prev_index]
    next_slot = grid.slots[next_index]
    prev_note = slots[prev_index]
    next_note = slots[next_index]
    if prev_note is None or next_note is None:
        return None, None, None, None
    return prev_slot, prev_note, next_slot, next_note
