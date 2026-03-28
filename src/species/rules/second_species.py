from __future__ import annotations

from ..config import CPDisposition, SpeciesEngineConfig
from ..explainer import error
from ..models import CPNote, TemporalGrid, ValidationError
from ..music_core import (
    interval_label,
    is_consonant,
    is_step,
    is_strong_consonance,
    melodic_direction,
)
from ..plans import first_real_attack


def validate_second_species_vertical_rules(
    grid: TemporalGrid,
    slots: list[CPNote],
    config: SpeciesEngineConfig,
) -> tuple[list[ValidationError], list[dict]]:
    errors: list[ValidationError] = []
    trace: list[dict] = []
    n_measures = grid.cf_length

    _validate_measure_shape(grid, slots, config, errors)
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
        strong_slot = (measure - 1) * 2
        weak_slot = strong_slot + 1
        strong = slots[strong_slot]
        weak = slots[weak_slot]
        if weak is None:
            errors.append(
                error(
                    code="weak_dissonance_not_strict_passing",
                    message=f"Measure {measure} beat2 cannot be empty in second species",
                    measure=measure,
                    beat=2,
                    origin="second_species_exact",
                    evidence={"rule": "metric_2_to_1"},
                )
            )
        if strong is None and not (measure == 1 and config.allow_half_rest_start):
            errors.append(
                error(
                    code="invalid_opening_interval",
                    message=f"Measure {measure} beat1 cannot be empty",
                    measure=measure,
                    beat=1,
                    origin="second_species_exact",
                    evidence={"rule": "metric_2_to_1"},
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
                origin="second_species_exact",
                evidence={"rule": "final_full_measure"},
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
                origin="second_species_exact",
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
                origin="second_species_exact",
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
        if 1 < slot.measure < n:
            if label == "P1":
                errors.append(
                    error(
                        code="interior_unison_forbidden",
                        message="Interior unison is forbidden on strong beats",
                        measure=slot.measure,
                        beat=slot.beat,
                        origin="second_species_exact",
                        evidence={"interval": label},
                    )
                )
                continue
            if not is_strong_consonance(cp_note, slot.cf_pitch):
                errors.append(
                    error(
                        code="strong_beat_dissonance",
                        message="Interior strong beat must be consonant",
                        measure=slot.measure,
                        beat=slot.beat,
                        origin="second_species_exact",
                        evidence={"interval": label},
                    )
                )


def _validate_weak_beats(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
) -> None:
    n = grid.cf_length
    for slot in grid.weak_slots:
        cp_note = slots[slot.index]
        if cp_note is None:
            continue
        label = interval_label(cp_note, slot.cf_pitch)
        if 1 < slot.measure < n and label == "P1":
            errors.append(
                error(
                    code="interior_unison_forbidden",
                    message="Interior unison is forbidden on weak beats",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="second_species_exact",
                    evidence={"interval": label},
                )
            )
            continue

        if not is_consonant(cp_note, slot.cf_pitch):
            strong = slots[slot.index - 1]
            next_strong = slots[slot.index + 1]
            if strong is None or next_strong is None:
                errors.append(
                    error(
                        code="weak_dissonance_not_strict_passing",
                        message="Weak dissonance requires surrounding strong supports",
                        measure=slot.measure,
                        beat=slot.beat,
                        origin="second_species_exact",
                        evidence={"interval": label},
                    )
                )
                continue

            step_in = is_step(strong, cp_note)
            step_out = is_step(cp_note, next_strong)
            dir_in = melodic_direction(strong, cp_note)
            dir_out = melodic_direction(cp_note, next_strong)
            strict_passing = step_in and step_out and dir_in == dir_out and dir_in != 0
            if not strict_passing:
                errors.append(
                    error(
                        code="weak_dissonance_not_strict_passing",
                        message="Weak dissonance must be strict passing tone",
                        measure=slot.measure,
                        beat=slot.beat,
                        origin="second_species_exact",
                        evidence={
                            "interval": label,
                            "step_in": step_in,
                            "step_out": step_out,
                            "dir_in": dir_in,
                            "dir_out": dir_out,
                            "strong": strong,
                            "weak": cp_note,
                            "next_strong": next_strong,
                        },
                    )
                )


def _validate_repetitions(
    grid: TemporalGrid,
    slots: list[CPNote],
    errors: list[ValidationError],
    n_measures: int,
) -> None:
    # Intra-measure and barline repetitions
    for measure in range(1, n_measures):
        strong_idx = (measure - 1) * 2
        weak_idx = strong_idx + 1
        strong = slots[strong_idx]
        weak = slots[weak_idx]
        next_strong = slots[weak_idx + 1]
        if strong is not None and weak is not None and strong == weak:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Repetition beat1 == beat2 is forbidden before final measure",
                    measure=measure,
                    beat=2,
                    origin="second_species_exact",
                    evidence={"beat1": strong, "beat2": weak},
                )
            )
        if weak is not None and next_strong is not None and weak == next_strong:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Repetition beat2 == next beat1 is forbidden",
                    measure=measure + 1,
                    beat=1,
                    origin="second_species_exact",
                    evidence={"beat2_prev_measure": weak, "beat1_next_measure": next_strong},
                )
            )

    # Any immediate repetition before final measure.
    real_attacks: list[tuple[int, int, int]] = []
    for slot in grid.slots:
        note = slots[slot.index]
        if note is not None:
            real_attacks.append((slot.measure, slot.beat, note))
    for i in range(1, len(real_attacks)):
        measure, beat, note = real_attacks[i]
        _, _, prev_note = real_attacks[i - 1]
        if note == prev_note and measure < n_measures:
            errors.append(
                error(
                    code="immediate_repetition_forbidden",
                    message="Immediate melodic repetition is forbidden before final measure",
                    measure=measure,
                    beat=beat,
                    origin="second_species_exact",
                    evidence={"previous_note": prev_note, "current_note": note},
                )
            )
