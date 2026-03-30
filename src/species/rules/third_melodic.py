from __future__ import annotations

from ..explainer import error
from ..models import CPNote, GridSlot, TemporalGrid, ValidationError
from ..music_core import diatonic_interval, is_consonant, is_step, melodic_direction
from ..plans import iter_real_attacks
from .third_figures import collect_third_species_dissonance_figures


def validate_third_species_melodic_rules(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    attacks = iter_real_attacks(grid, slots)
    if len(attacks) < 2:
        return errors

    figure_map = collect_third_species_dissonance_figures(grid, slots)

    for i in range(1, len(attacks)):
        prev_slot, prev_note = attacks[i - 1]
        curr_slot, curr_note = attacks[i]
        leap = diatonic_interval(prev_note, curr_note)
        if abs(leap) <= 1:
            continue

        if prev_slot.beat in {1, 3} and leap > 0:
            errors.append(
                error(
                    code="accented_leap_must_descend",
                    message="Leap from accented support (beat1/beat3) must descend in strict third species",
                    measure=curr_slot.measure,
                    beat=curr_slot.beat,
                    origin="third_species_exact",
                    evidence={
                        "from_measure": prev_slot.measure,
                        "from_beat": prev_slot.beat,
                        "to_measure": curr_slot.measure,
                        "to_beat": curr_slot.beat,
                        "diatonic_leap": leap,
                    },
                )
            )

        if prev_slot.beat in {2, 4} and leap < 0:
            if not _descending_weak_leap_exception(attacks, i, figure_map):
                errors.append(
                    error(
                        code="weak_leap_direction_forbidden",
                        message="Descending leap from weak beat is forbidden unless it is a controlled third-species exception",
                        measure=curr_slot.measure,
                        beat=curr_slot.beat,
                        origin="third_species_exact",
                        evidence={
                            "from_measure": prev_slot.measure,
                            "from_beat": prev_slot.beat,
                            "to_measure": curr_slot.measure,
                            "to_beat": curr_slot.beat,
                            "diatonic_leap": leap,
                        },
                    )
                )

        if not _leap_between_consonances_or_cambiata(prev_slot.index, prev_note, curr_slot.index, curr_note, grid, figure_map):
            errors.append(
                error(
                    code="leap_endpoint_dissonance_forbidden",
                    message="Leap must connect consonant verticalities except the canonical cambiata leap",
                    measure=curr_slot.measure,
                    beat=curr_slot.beat,
                    origin="third_species_exact",
                    evidence={
                        "from_measure": prev_slot.measure,
                        "from_beat": prev_slot.beat,
                        "to_measure": curr_slot.measure,
                        "to_beat": curr_slot.beat,
                    },
                )
            )

    for i in range(1, len(attacks) - 1):
        prev_slot, prev_note = attacks[i - 1]
        mid_slot, mid_note = attacks[i]
        next_slot, next_note = attacks[i + 1]
        leap = diatonic_interval(prev_note, mid_note)
        if abs(leap) < 3:
            continue
        resolution = diatonic_interval(mid_note, next_note)
        opposite = (leap > 0 and resolution < 0) or (leap < 0 and resolution > 0)
        if not (abs(resolution) == 1 and opposite):
            errors.append(
                error(
                    code="large_leap_not_compensated",
                    message="Large leap must be compensated by immediate step in opposite direction",
                    measure=next_slot.measure,
                    beat=next_slot.beat,
                    origin="third_species_exact",
                    evidence={
                        "leap_from_measure": prev_slot.measure,
                        "leap_from_beat": prev_slot.beat,
                        "leap_to_measure": mid_slot.measure,
                        "leap_to_beat": mid_slot.beat,
                        "resolution_to_measure": next_slot.measure,
                        "resolution_to_beat": next_slot.beat,
                        "leap_diatonic": leap,
                        "resolution_diatonic": resolution,
                    },
                )
            )

    return errors


def _is_cambiata_characteristic_leap(
    from_index: int,
    from_note: int,
    to_index: int,
    to_note: int,
    figure_map: dict[int, str],
) -> bool:
    if figure_map.get(from_index) != "cambiata":
        return False
    return abs(diatonic_interval(from_note, to_note)) == 2 and melodic_direction(from_note, to_note) == -1


def _leap_between_consonances_or_cambiata(
    from_index: int,
    from_note: int,
    to_index: int,
    to_note: int,
    grid: TemporalGrid,
    figure_map: dict[int, str],
) -> bool:
    from_slot = grid.slots[from_index]
    to_slot = grid.slots[to_index]
    from_consonant = is_consonant(from_note, from_slot.cf_pitch)
    to_consonant = is_consonant(to_note, to_slot.cf_pitch)
    if from_consonant and to_consonant:
        return True
    return _is_cambiata_characteristic_leap(from_index, from_note, to_index, to_note, figure_map)


def _descending_weak_leap_exception(
    attacks: list[tuple[GridSlot, int]],
    current_index: int,
    figure_map: dict[int, str],
) -> bool:
    from_slot, from_note = attacks[current_index - 1]
    to_slot, to_note = attacks[current_index]
    leap = diatonic_interval(from_note, to_note)
    if leap != -2:
        return False

    if _is_cambiata_characteristic_leap(from_slot.index, from_note, to_slot.index, to_note, figure_map):
        return True

    if current_index + 1 >= len(attacks):
        return False
    _, next_note = attacks[current_index + 1]
    return is_step(to_note, next_note) and melodic_direction(to_note, next_note) == 1
