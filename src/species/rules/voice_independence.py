from __future__ import annotations

from ..explainer import error
from ..models import CPNote, TemporalGrid, ValidationError
from ..music_core import perfect_species
from ..plans import iter_real_attacks


def validate_voice_independence(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    errors.extend(_validate_adjacent_perfect_parallel(grid, slots))
    errors.extend(_validate_strong_support_perfect_parallel(grid, slots))
    return errors


def _validate_adjacent_perfect_parallel(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    attacks = iter_real_attacks(grid, slots)
    for i in range(1, len(attacks)):
        prev_slot, prev_cp = attacks[i - 1]
        curr_slot, curr_cp = attacks[i]
        prev_cf = prev_slot.cf_pitch
        curr_cf = curr_slot.cf_pitch
        prev_kind = perfect_species(prev_cp, prev_cf)
        curr_kind = perfect_species(curr_cp, curr_cf)
        if prev_kind is None or curr_kind is None or prev_kind != curr_kind:
            continue
        cp_move = curr_cp - prev_cp
        cf_move = curr_cf - prev_cf
        if cp_move != 0 and cf_move != 0:
            errors.append(
                error(
                    code="adjacent_perfect_parallel",
                    message="Perfect parallel between adjacent attacks is forbidden",
                    measure=curr_slot.measure,
                    beat=curr_slot.beat,
                    origin="inherited_first_species",
                    evidence={
                        "previous_attack": {
                            "measure": prev_slot.measure,
                            "beat": prev_slot.beat,
                            "cp": prev_cp,
                            "cf": prev_cf,
                            "species": prev_kind,
                        },
                        "current_attack": {
                            "measure": curr_slot.measure,
                            "beat": curr_slot.beat,
                            "cp": curr_cp,
                            "cf": curr_cf,
                            "species": curr_kind,
                        },
                    },
                )
            )
    return errors


def _validate_strong_support_perfect_parallel(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    strong = [(slot, slots[slot.index]) for slot in grid.strong_slots if slots[slot.index] is not None]
    for i in range(1, len(strong)):
        prev_slot, prev_cp = strong[i - 1]
        curr_slot, curr_cp = strong[i]
        prev_kind = perfect_species(prev_cp, prev_slot.cf_pitch)
        curr_kind = perfect_species(curr_cp, curr_slot.cf_pitch)
        if prev_kind is None or curr_kind is None or prev_kind != curr_kind:
            continue
        errors.append(
            error(
                code="strong_support_perfect_parallel",
                message="Perfect species repetition across consecutive strong supports is forbidden",
                measure=curr_slot.measure,
                beat=curr_slot.beat,
                origin="inherited_first_species",
                evidence={
                    "previous_strong": {
                        "measure": prev_slot.measure,
                        "cp": prev_cp,
                        "cf": prev_slot.cf_pitch,
                        "species": prev_kind,
                    },
                    "current_strong": {
                        "measure": curr_slot.measure,
                        "cp": curr_cp,
                        "cf": curr_slot.cf_pitch,
                        "species": curr_kind,
                    },
                },
            )
        )
    return errors
