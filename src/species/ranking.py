from __future__ import annotations

from .models import CPNote, ScoreBreakdown, TemporalGrid
from .music_core import interval_label, is_step
from .plans import iter_real_attacks
from .rules.third_figures import collect_third_species_dissonance_figures


def rank_slots(grid: TemporalGrid, slots: list[CPNote]) -> ScoreBreakdown:
    attacks = iter_real_attacks(grid, slots)
    if len(attacks) < 2:
        return ScoreBreakdown(total_score=0.0, contributions={}, weights={}, details={})

    intervals = [attacks[i][1] - attacks[i - 1][1] for i in range(1, len(attacks))]
    abs_intervals = [abs(v) for v in intervals]
    steps = sum(1 for v in abs_intervals if v <= 2)
    leaps = sum(1 for v in abs_intervals if v > 2)

    weights = {
        "stepwise_motion": 45.0,
        "low_consecutive_leaps": 35.0,
        "smooth_contour": 25.0,
        "imperfect_consonance_preference": 10.0,
        "balanced_direction": 10.0,
        "cadence_preparation": 30.0,
    }

    # Predominio de grado conjunto.
    step_ratio = steps / len(abs_intervals)
    stepwise_score = step_ratio * weights["stepwise_motion"]

    # Baja densidad de saltos consecutivos.
    consecutive_leaps = 0
    for i in range(1, len(abs_intervals)):
        if abs_intervals[i] > 2 and abs_intervals[i - 1] > 2:
            consecutive_leaps += 1
    leap_penalty = (consecutive_leaps / max(1, len(abs_intervals) - 1)) * weights["low_consecutive_leaps"]
    low_leap_score = weights["low_consecutive_leaps"] - leap_penalty

    # Contorno poco anguloso.
    direction_changes = 0
    prev_sign = 0
    for diff in intervals:
        sign = 1 if diff > 0 else (-1 if diff < 0 else 0)
        if sign != 0 and prev_sign != 0 and sign != prev_sign:
            direction_changes += 1
        if sign != 0:
            prev_sign = sign
    smooth_contour_score = max(
        0.0,
        weights["smooth_contour"] - (direction_changes / max(1, len(intervals) - 1)) * weights["smooth_contour"],
    )

    # Preferencia por imperfectas en fuertes.
    strong_imperfect = 0
    strong_total = 0
    for slot in grid.strong_slots:
        note = slots[slot.index]
        if note is None:
            continue
        strong_total += 1
        if interval_label(note, slot.cf_pitch) in {"m3", "M3", "m6", "M6"}:
            strong_imperfect += 1
    imperfect_ratio = (strong_imperfect / strong_total) if strong_total else 0.0
    imperfect_score = imperfect_ratio * weights["imperfect_consonance_preference"]

    # Balance ascenso/descenso.
    asc = sum(1 for diff in intervals if diff > 0)
    desc = sum(1 for diff in intervals if diff < 0)
    balance = 1.0 - (abs(asc - desc) / max(1, asc + desc))
    balanced_score = balance * weights["balanced_direction"]

    # Preparación perceptual de cadencia.
    cadence_score = 0.0
    if len(attacks) >= 3:
        prev = attacks[-2][1]
        final = attacks[-1][1]
        if is_step(prev, final):
            cadence_score += weights["cadence_preparation"] * 0.65
        before_prev = attacks[-3][1]
        if abs(prev - before_prev) <= 2:
            cadence_score += weights["cadence_preparation"] * 0.35

    contributions = {
        "stepwise_motion": stepwise_score,
        "low_consecutive_leaps": low_leap_score,
        "smooth_contour": smooth_contour_score,
        "imperfect_consonance_preference": imperfect_score,
        "balanced_direction": balanced_score,
        "cadence_preparation": cadence_score,
    }
    total = sum(contributions.values())
    details = {
        "steps": steps,
        "leaps": leaps,
        "consecutive_leaps": consecutive_leaps,
        "direction_changes": direction_changes,
        "strong_imperfect": strong_imperfect,
        "strong_total": strong_total,
        "asc": asc,
        "desc": desc,
    }
    return ScoreBreakdown(
        total_score=total,
        contributions=contributions,
        weights=weights,
        details=details,
    )


def rank_third_species_slots(grid: TemporalGrid, slots: list[CPNote]) -> ScoreBreakdown:
    attacks = iter_real_attacks(grid, slots)
    if len(attacks) < 2:
        return ScoreBreakdown(total_score=0.0, contributions={}, weights={}, details={})

    intervals = [attacks[i][1] - attacks[i - 1][1] for i in range(1, len(attacks))]
    abs_intervals = [abs(v) for v in intervals]
    steps = sum(1 for v in abs_intervals if v <= 2)

    weights = {
        "stepwise_motion": 35.0,
        "low_consecutive_leaps": 20.0,
        "imperfect_strong_supports": 14.0,
        "passing_bonus": 10.0,
        "lower_neighbor_bonus": 8.0,
        "cambiata_bonus": 14.0,
        "climax_uniqueness_bonus": 8.0,
        "climax_cf_coincidence_penalty": 8.0,
        "dense_cambiata_penalty": 6.0,
        "trivial_contour_penalty": 8.0,
        "circular_pattern_penalty": 10.0,
        "nontrivial_reiteration_penalty": 8.0,
        "cadence_preparation": 18.0,
    }

    step_ratio = steps / len(abs_intervals)
    stepwise_score = step_ratio * weights["stepwise_motion"]

    consecutive_leaps = 0
    for i in range(1, len(abs_intervals)):
        if abs_intervals[i] > 2 and abs_intervals[i - 1] > 2:
            consecutive_leaps += 1
    leap_penalty = (consecutive_leaps / max(1, len(abs_intervals) - 1)) * weights["low_consecutive_leaps"]
    low_leap_score = weights["low_consecutive_leaps"] - leap_penalty

    strong_imperfect = 0
    strong_total = 0
    for slot in grid.strong_slots:
        note = slots[slot.index]
        if note is None:
            continue
        strong_total += 1
        if interval_label(note, slot.cf_pitch) in {"m3", "M3", "m6", "M6"}:
            strong_imperfect += 1
    imperfect_ratio = strong_imperfect / strong_total if strong_total else 0.0
    imperfect_score = imperfect_ratio * weights["imperfect_strong_supports"]

    figure_map = collect_third_species_dissonance_figures(grid, slots)
    passing_count = sum(1 for figure in figure_map.values() if figure == "passing_tone")
    lower_count = sum(1 for figure in figure_map.values() if figure == "lower_neighbor")
    cambiata_count = sum(1 for figure in figure_map.values() if figure == "cambiata")
    passing_score = min(weights["passing_bonus"], passing_count * 2.5)
    lower_score = min(weights["lower_neighbor_bonus"], lower_count * 2.0)
    cambiata_score = min(weights["cambiata_bonus"], cambiata_count * 4.0)

    direction_changes = 0
    prev_sign = 0
    for diff in intervals:
        sign = 1 if diff > 0 else (-1 if diff < 0 else 0)
        if sign != 0 and prev_sign != 0 and sign != prev_sign:
            direction_changes += 1
        if sign != 0:
            prev_sign = sign
    contour_change_ratio = direction_changes / max(1, len(intervals) - 1)
    trivial_penalty = max(0.0, (0.25 - contour_change_ratio) / 0.25) * weights["trivial_contour_penalty"]

    attack_notes = [note for _, note in attacks]
    circular_patterns = 0
    for i in range(3, len(attack_notes)):
        if attack_notes[i] == attack_notes[i - 2] and attack_notes[i - 1] == attack_notes[i - 3]:
            circular_patterns += 1
    circular_penalty = min(weights["circular_pattern_penalty"], circular_patterns * 2.0)

    reiterations = 0
    for i in range(2, len(attack_notes)):
        if attack_notes[i] == attack_notes[i - 2]:
            reiterations += 1
    reiteration_penalty = min(weights["nontrivial_reiteration_penalty"], reiterations * 1.2)

    cp_notes = [note for _, note in attacks]
    cp_max = max(cp_notes)
    cp_climax_positions = [i for i, note in enumerate(cp_notes) if note == cp_max]
    climax_unique_bonus = (
        weights["climax_uniqueness_bonus"] if len(cp_climax_positions) == 1 else 0.0
    )

    cf_max = max(grid.cf)
    cf_climax_measures = {idx + 1 for idx, note in enumerate(grid.cf) if note == cf_max}
    cp_climax_measures = {
        attacks[pos][0].measure for pos in cp_climax_positions
    }
    climax_cf_penalty = (
        weights["climax_cf_coincidence_penalty"]
        if cp_climax_measures & cf_climax_measures
        else 0.0
    )

    cambiata_slots = sorted(idx for idx, figure in figure_map.items() if figure == "cambiata")
    dense_cambiata_pairs = 0
    for i in range(1, len(cambiata_slots)):
        if cambiata_slots[i] - cambiata_slots[i - 1] <= 8:
            dense_cambiata_pairs += 1
    dense_cambiata_penalty = min(
        weights["dense_cambiata_penalty"],
        dense_cambiata_pairs * 2.0,
    )

    cadence_score = 0.0
    if len(attacks) >= 3:
        prev = attacks[-2][1]
        final = attacks[-1][1]
        if is_step(prev, final):
            cadence_score += weights["cadence_preparation"] * 0.6
        before_prev = attacks[-3][1]
        if is_step(before_prev, prev):
            cadence_score += weights["cadence_preparation"] * 0.4

    contributions = {
        "stepwise_motion": stepwise_score,
        "low_consecutive_leaps": low_leap_score,
        "imperfect_strong_supports": imperfect_score,
        "passing_bonus": passing_score,
        "lower_neighbor_bonus": lower_score,
        "cambiata_bonus": cambiata_score,
        "climax_uniqueness_bonus": climax_unique_bonus,
        "climax_cf_coincidence_penalty": -climax_cf_penalty,
        "dense_cambiata_penalty": -dense_cambiata_penalty,
        "trivial_contour_penalty": -trivial_penalty,
        "circular_pattern_penalty": -circular_penalty,
        "nontrivial_reiteration_penalty": -reiteration_penalty,
        "cadence_preparation": cadence_score,
    }
    total = sum(contributions.values())
    details = {
        "steps": steps,
        "consecutive_leaps": consecutive_leaps,
        "direction_changes": direction_changes,
        "contour_change_ratio": contour_change_ratio,
        "strong_imperfect": strong_imperfect,
        "strong_total": strong_total,
        "passing_count": passing_count,
        "lower_neighbor_count": lower_count,
        "cambiata_count": cambiata_count,
        "cp_climax_count": len(cp_climax_positions),
        "cp_climax_measures": sorted(cp_climax_measures),
        "cf_climax_measures": sorted(cf_climax_measures),
        "dense_cambiata_pairs": dense_cambiata_pairs,
        "circular_patterns": circular_patterns,
        "nontrivial_reiterations": reiterations,
    }
    return ScoreBreakdown(
        total_score=total,
        contributions=contributions,
        weights=weights,
        details=details,
    )
