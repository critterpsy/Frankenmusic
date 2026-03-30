from __future__ import annotations

from ..explainer import error
from ..models import CPNote, TemporalGrid, ValidationError
from ..music_core import interval_label, perfect_species
from ..plans import iter_real_attacks


def validate_third_species_voice_independence(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    errors.extend(_validate_adjacent_perfect_parallel(grid, slots))
    errors.extend(_validate_strong_support_perfect_parallel(grid, slots))
    errors.extend(_validate_direct_perfect_to_strong_support(grid, slots))
    errors.extend(_validate_support_streaks(grid, slots))
    errors.extend(_validate_restricted_preceding_perfects(grid, slots))
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
    strong = [
        (slot, slots[slot.index])
        for slot in grid.strong_slots
        if slots[slot.index] is not None
    ]
    for i in range(1, len(strong)):
        prev_slot, prev_cp = strong[i - 1]
        curr_slot, curr_cp = strong[i]
        prev_kind = perfect_species(prev_cp, prev_slot.cf_pitch)
        curr_kind = perfect_species(curr_cp, curr_slot.cf_pitch)
        if prev_kind is None or curr_kind is None or prev_kind != curr_kind:
            continue
        cp_move = curr_cp - prev_cp
        cf_move = curr_slot.cf_pitch - prev_slot.cf_pitch
        if cp_move != 0 and cf_move != 0:
            errors.append(
                error(
                    code="strong_support_perfect_parallel",
                    message="Parallel perfect species across consecutive strong supports is forbidden",
                    measure=curr_slot.measure,
                    beat=curr_slot.beat,
                    origin="inherited_first_species",
                    evidence={
                        "previous_strong": {
                            "measure": prev_slot.measure,
                            "beat": prev_slot.beat,
                            "cp": prev_cp,
                            "cf": prev_slot.cf_pitch,
                            "species": prev_kind,
                        },
                        "current_strong": {
                            "measure": curr_slot.measure,
                            "beat": curr_slot.beat,
                            "cp": curr_cp,
                            "cf": curr_slot.cf_pitch,
                            "species": curr_kind,
                        },
                    },
                )
            )
    return errors


def _validate_direct_perfect_to_strong_support(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    attacks = iter_real_attacks(grid, slots)
    for i in range(1, len(attacks)):
        prev_slot, prev_cp = attacks[i - 1]
        curr_slot, curr_cp = attacks[i]
        if not curr_slot.is_strong:
            continue
        curr_kind = perfect_species(curr_cp, curr_slot.cf_pitch)
        if curr_kind is None:
            continue
        cp_move = curr_cp - prev_cp
        cf_move = curr_slot.cf_pitch - prev_slot.cf_pitch
        if cp_move == 0 or cf_move == 0:
            continue
        if (cp_move > 0 and cf_move > 0) or (cp_move < 0 and cf_move < 0):
            if abs(cp_move) > 2:
                errors.append(
                    error(
                        code="direct_perfect_to_strong_support",
                        message="Direct motion by leap into perfect strong support is forbidden",
                        measure=curr_slot.measure,
                        beat=curr_slot.beat,
                        origin="inherited_first_species",
                        evidence={
                            "from_measure": prev_slot.measure,
                            "from_beat": prev_slot.beat,
                            "to_measure": curr_slot.measure,
                            "to_beat": curr_slot.beat,
                            "cp_move": cp_move,
                            "cf_move": cf_move,
                            "species": curr_kind,
                        },
                    )
                )
    return errors


def _validate_support_streaks(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    strong_beat1 = [
        slot
        for slot in grid.strong_slots
        if slot.beat == 1 and slots[slot.index] is not None
    ]
    if not strong_beat1:
        return errors

    perfect_streak = 0
    last_perfect_kind: str | None = None
    imperfect_streak = 0
    last_imperfect_label: str | None = None

    for slot in strong_beat1:
        cp_note = slots[slot.index]
        assert cp_note is not None
        perfect_kind = perfect_species(cp_note, slot.cf_pitch)
        iv_label = interval_label(cp_note, slot.cf_pitch)

        if perfect_kind is not None:
            if perfect_kind == last_perfect_kind:
                perfect_streak += 1
            else:
                perfect_streak = 1
                last_perfect_kind = perfect_kind
            if perfect_streak >= 3:
                errors.append(
                    error(
                        code="identical_perfect_support_streak_forbidden",
                        message="Three identical perfect supports in consecutive measure openings are forbidden",
                        measure=slot.measure,
                        beat=slot.beat,
                        origin="third_species_exact",
                        evidence={"perfect_kind": perfect_kind, "streak": perfect_streak},
                    )
                )
            imperfect_streak = 0
            last_imperfect_label = None
            continue

        last_perfect_kind = None
        perfect_streak = 0

        if iv_label in {"m3", "M3", "m6", "M6"}:
            if iv_label == last_imperfect_label:
                imperfect_streak += 1
            else:
                imperfect_streak = 1
                last_imperfect_label = iv_label
            if imperfect_streak >= 4:
                errors.append(
                    error(
                        code="identical_imperfect_support_streak_forbidden",
                        message="More than three identical imperfect supports in measure openings are forbidden",
                        measure=slot.measure,
                        beat=slot.beat,
                        origin="third_species_exact",
                        evidence={"interval": iv_label, "streak": imperfect_streak},
                    )
                )
        else:
            imperfect_streak = 0
            last_imperfect_label = None

    return errors


def _validate_restricted_preceding_perfects(
    grid: TemporalGrid,
    slots: list[CPNote],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    n = grid.cf_length
    for measure in range(2, n + 1):
        curr_base = (measure - 1) * 4
        curr_beat1 = slots[curr_base]
        if curr_beat1 is None:
            continue
        curr_cf = grid.cf[measure - 1]
        curr_kind = perfect_species(curr_beat1, curr_cf)
        if curr_kind is None:
            continue

        prev_base = (measure - 2) * 4
        if curr_kind == "P5":
            restricted = [(3, prev_base + 2), (4, prev_base + 3)]
            restricted_kind = "P5"
        else:
            restricted = [(2, prev_base + 1), (3, prev_base + 2), (4, prev_base + 3)]
            restricted_kind = "P1/P8"

        prev_cf = grid.cf[measure - 2]
        for beat, idx in restricted:
            prev_note = slots[idx]
            if prev_note is None:
                continue
            if perfect_species(prev_note, prev_cf) != restricted_kind:
                continue
            errors.append(
                error(
                    code="perfect_support_entry_prepared_by_same_perfect_forbidden",
                    message="New strong perfect support cannot be prefigured by same perfect species in previous weak/relative-strong beats",
                    measure=measure,
                    beat=1,
                    origin="third_species_exact",
                    evidence={
                        "current_kind": curr_kind,
                        "previous_measure": measure - 1,
                        "previous_beat": beat,
                        "restricted_kind": restricted_kind,
                    },
                )
            )
            break

    return errors
