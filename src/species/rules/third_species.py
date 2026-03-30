from __future__ import annotations

from ..config import CPDisposition, SpeciesEngineConfig
from ..explainer import error
from ..models import CPNote, TemporalGrid, ValidationError
from ..music_core import (
    cadential_subtonic_distance,
    interval_label,
    is_cadential_subtonic,
    is_consonant,
    is_white_note,
    same_diatonic_pitch,
)
from ..plans import first_real_attack, iter_real_attacks
from .third_figures import (
    classify_third_species_weak_slot,
    collect_third_species_dissonance_figures,
)


def validate_third_species_vertical_rules(
    grid: TemporalGrid,
    slots: list[CPNote],
    config: SpeciesEngineConfig,
) -> tuple[list[ValidationError], list[dict]]:
    errors: list[ValidationError] = []
    trace: list[dict] = []
    n_measures = grid.cf_length

    _validate_measure_shape(grid, slots, config, errors)
    _validate_modal_membership(grid, slots, errors)
    _validate_cadential_inflection(grid, slots, errors)
    _validate_opening(grid, slots, config, errors, trace)
    _validate_strong_beats(grid, slots, errors)
    _validate_weak_beats(grid, slots, errors)
    _validate_repetitions(grid, slots, errors, n_measures)

    return errors, trace


def _validate_measure_shape(
    grid: TemporalGrid,
    slots: list[CPNote],
    config: SpeciesEngineConfig,
    errors: list[ValidationError],
) -> None:
    n = grid.cf_length
    for measure in range(1, n):
        base = (measure - 1) * 4
        beat1 = slots[base]
        beat2 = slots[base + 1]
        beat3 = slots[base + 2]
        beat4 = slots[base + 3]

        if beat1 is None and not (measure == 1 and config.allow_half_rest_start):
            errors.append(
                error(
                    code="invalid_opening_interval",
                    message=f"Measure {measure} beat1 cannot be empty",
                    measure=measure,
                    beat=1,
                    origin="third_species_exact",
                    evidence={"rule": "metric_4_to_1"},
                )
            )
        if beat2 is None:
            errors.append(
                error(
                    code="missing_attack",
                    message=f"Measure {measure} beat2 cannot be empty in third species",
                    measure=measure,
                    beat=2,
                    origin="third_species_exact",
                    evidence={"rule": "metric_4_to_1"},
                )
            )
        if beat3 is None:
            errors.append(
                error(
                    code="missing_attack",
                    message=f"Measure {measure} beat3 cannot be empty in third species",
                    measure=measure,
                    beat=3,
                    origin="third_species_exact",
                    evidence={"rule": "metric_4_to_1"},
                )
            )
        if beat4 is None:
            errors.append(
                error(
                    code="missing_attack",
                    message=f"Measure {measure} beat4 cannot be empty in third species",
                    measure=measure,
                    beat=4,
                    origin="third_species_exact",
                    evidence={"rule": "metric_4_to_1"},
                )
            )

    final = slots[-1]
    if final is None:
        errors.append(
            error(
                code="invalid_final_cadence",
                message="Final strong beat cannot be empty",
                measure=n,
                beat=1,
                origin="third_species_exact",
                evidence={"rule": "final_collapsed_measure"},
            )
        )


def _opening_interval_valid(
    cp_note: int,
    cf_note: int,
    disposition: CPDisposition,
) -> bool:
    label = interval_label(cp_note, cf_note)
    if disposition == CPDisposition.ABOVE:
        if cp_note <= cf_note:
            return False
        return label in {"P5", "P8"}
    if cp_note > cf_note:
        return False
    return label in {"P1", "P8"}


def _validate_modal_membership(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
) -> None:
    n = grid.cf_length
    if not grid.slots:
        return

    final_slot = grid.slots[-1]
    final_cp = slots[final_slot.index]
    tonic = final_slot.cf_pitch
    expected_cadential_note = (
        None
        if final_cp is None
        else final_cp - cadential_subtonic_distance(tonic)
    )
    allowed_measure = n - 1

    for slot in grid.slots:
        cp_note = slots[slot.index]
        if cp_note is None:
            continue
        if is_white_note(cp_note):
            continue

        allow_cadential_chromatic = (
            slot.measure == allowed_measure
            and slot.beat == 4
            and expected_cadential_note is not None
            and is_cadential_subtonic(cp_note, final_cp, tonic)
        )
        if allow_cadential_chromatic:
            continue

        errors.append(
            error(
                code="note_outside_modal_scale",
                message="CP note is outside the modal scale outside the cadential slot",
                measure=slot.measure,
                beat=slot.beat,
                origin="third_species_exact",
                evidence={
                    "cp_note": cp_note,
                    "tonic": tonic,
                    "expected_cadential_note": expected_cadential_note,
                    "allowed_slot": {"measure": allowed_measure, "beat": 4},
                },
            )
        )


def _validate_cadential_inflection(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
) -> None:
    n = grid.cf_length
    if n < 2:
        return

    final_slot = grid.slots[-1]
    final_cp = slots[final_slot.index]
    if final_cp is None:
        return

    penultimate_base = (n - 2) * 4
    beat3 = slots[penultimate_base + 2]
    beat4 = slots[penultimate_base + 3]
    if beat3 is None or beat4 is None:
        return
    if not is_cadential_subtonic(beat4, final_cp, final_slot.cf_pitch):
        return
    if not same_diatonic_pitch(beat3, beat4):
        return

    errors.append(
        error(
            code="cadential_chromatic_inflection_forbidden",
            message="Cadential leading tone cannot be preceded by the same diatonic pitch in altered form",
            measure=n - 1,
            beat=4,
            origin="third_species_exact",
            evidence={
                "penultimate_beat3": beat3,
                "penultimate_beat4": beat4,
                "final_note": final_cp,
                "tonic": final_slot.cf_pitch,
            },
        )
    )


def _validate_opening(
    grid: TemporalGrid,
    slots: list[CPNote],
    config: SpeciesEngineConfig,
    errors: list[ValidationError],
    trace: list[dict],
) -> None:
    opening = first_real_attack(grid, slots)
    if opening is None:
        errors.append(
            error(
                code="invalid_opening_interval",
                message="CP has no real attack",
                measure=1,
                beat=1,
                origin="third_species_exact",
                evidence={"rule": "opening"},
            )
        )
        return

    slot, cp_note = opening
    if not _opening_interval_valid(cp_note, slot.cf_pitch, config.cp_disposition):
        errors.append(
            error(
                code="invalid_opening_interval",
                message="Opening interval is invalid for selected disposition",
                measure=slot.measure,
                beat=slot.beat,
                origin="third_species_exact",
                evidence={
                    "cp_note": cp_note,
                    "cf_note": slot.cf_pitch,
                    "interval": interval_label(cp_note, slot.cf_pitch),
                    "disposition": config.cp_disposition.value,
                },
            )
        )
    else:
        trace.append(
            {
                "kind": "opening_valid",
                "measure": slot.measure,
                "beat": slot.beat,
                "interval": interval_label(cp_note, slot.cf_pitch),
            }
        )


def _validate_strong_beats(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
) -> None:
    n = grid.cf_length
    for slot in grid.strong_slots:
        cp_note = slots[slot.index]
        if cp_note is None:
            continue
        label = interval_label(cp_note, slot.cf_pitch)

        if not is_consonant(cp_note, slot.cf_pitch):
            errors.append(
                error(
                    code="strong_beat_dissonance",
                    message="Strong beat must be consonant in third species",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="third_species_exact",
                    evidence={"interval": label},
                )
            )
            continue

        if 1 < slot.measure < n and slot.beat == 1 and label == "P1":
            errors.append(
                error(
                    code="interior_beat1_unison_forbidden",
                    message="Interior beat1 unison is forbidden",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="third_species_exact",
                    evidence={"interval": label},
                )
            )


def _validate_weak_beats(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
) -> None:
    for slot in grid.weak_slots:
        cp_note = slots[slot.index]
        if cp_note is None:
            continue
        if is_consonant(cp_note, slot.cf_pitch):
            continue

        figure = classify_third_species_weak_slot(grid, slots, slot.index)
        if figure in {"passing_tone", "lower_neighbor", "cambiata"}:
            continue
        if figure == "upper_neighbor":
            errors.append(
                error(
                    code="upper_neighbor_dissonant_forbidden",
                    message="Dissonant upper neighbor is not allowed in pure third species",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="third_species_exact",
                    evidence={"cp_note": cp_note, "cf_note": slot.cf_pitch},
                )
            )
            continue

        errors.append(
            error(
                code="weak_dissonance_figure_invalid",
                message="Weak dissonance must be passing tone, lower neighbor, or cambiata",
                measure=slot.measure,
                beat=slot.beat,
                origin="third_species_exact",
                evidence={"cp_note": cp_note, "cf_note": slot.cf_pitch},
            )
        )


def _validate_repetitions(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
    n_measures: int,
) -> None:
    for measure in range(1, n_measures):
        base = (measure - 1) * 4
        beat1 = slots[base]
        beat2 = slots[base + 1]
        beat3 = slots[base + 2]
        beat4 = slots[base + 3]
        next_beat1 = slots[base + 4]

        if beat1 is not None and beat2 is not None and beat1 == beat2:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Immediate repetition beat1 == beat2 is forbidden",
                    measure=measure,
                    beat=2,
                    origin="third_species_exact",
                    evidence={"beat1": beat1, "beat2": beat2},
                )
            )
        if beat2 is not None and beat3 is not None and beat2 == beat3:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Immediate repetition beat2 == beat3 is forbidden",
                    measure=measure,
                    beat=3,
                    origin="third_species_exact",
                    evidence={"beat2": beat2, "beat3": beat3},
                )
            )
        if beat3 is not None and beat4 is not None and beat3 == beat4:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Immediate repetition beat3 == beat4 is forbidden",
                    measure=measure,
                    beat=4,
                    origin="third_species_exact",
                    evidence={"beat3": beat3, "beat4": beat4},
                )
            )
        if beat4 is not None and next_beat1 is not None and beat4 == next_beat1:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Immediate repetition beat4 == next beat1 is forbidden",
                    measure=measure + 1,
                    beat=1,
                    origin="third_species_exact",
                    evidence={"beat4_prev_measure": beat4, "beat1_next_measure": next_beat1},
                )
            )
        if beat2 is not None and beat4 is not None and beat2 == beat4:
            errors.append(
                error(
                    code="trivial_weak_repetition_forbidden",
                    message="Trivial weak-beat repetition beat2 == beat4 is forbidden",
                    measure=measure,
                    beat=4,
                    origin="third_species_exact",
                    evidence={"beat2": beat2, "beat4": beat4},
                )
            )

    attacks = iter_real_attacks(grid, slots)
    for i in range(1, len(attacks)):
        curr_slot, curr_note = attacks[i]
        _, prev_note = attacks[i - 1]
        if curr_note == prev_note:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Immediate melodic repetition is forbidden",
                    measure=curr_slot.measure,
                    beat=curr_slot.beat,
                    origin="third_species_exact",
                    evidence={"previous_note": prev_note, "current_note": curr_note},
                )
            )

    figure_map = collect_third_species_dissonance_figures(grid, slots)
    dissonant_slots = sorted(figure_map.keys())
    for i in range(1, len(dissonant_slots)):
        prev_idx = dissonant_slots[i - 1]
        curr_idx = dissonant_slots[i]
        if figure_map[prev_idx] != "lower_neighbor" or figure_map[curr_idx] != "lower_neighbor":
            continue
        prev_note = slots[prev_idx]
        curr_note = slots[curr_idx]
        if prev_note is not None and prev_note == curr_note:
            curr_slot = grid.slots[curr_idx]
            errors.append(
                error(
                    code="consecutive_lower_neighbor_reuse_forbidden",
                    message="Reusing the same lower-neighbor note twice in a row is forbidden",
                    measure=curr_slot.measure,
                    beat=curr_slot.beat,
                    origin="third_species_exact",
                    evidence={"neighbor_note": curr_note},
                )
            )
