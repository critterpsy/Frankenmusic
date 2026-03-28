from __future__ import annotations

from .models import CPNote, ScoreBreakdown, TemporalGrid
from .music_core import interval_label, is_step
from .plans import iter_real_attacks


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
