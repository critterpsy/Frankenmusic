from __future__ import annotations

from ..explainer import error
from ..models import CPNote, TemporalGrid, ValidationError
from ..plans import iter_real_attacks


def validate_melodic_constraints(grid: TemporalGrid, slots: list[CPNote]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    attacks = iter_real_attacks(grid, slots)
    if len(attacks) < 2:
        return errors

    # 1) Allowed melodic intervals (legacy-compatible conservative subset).
    for i in range(1, len(attacks)):
        slot, note = attacks[i]
        _, prev_note = attacks[i - 1]
        size = abs(note - prev_note)
        if size in {6, 9, 10, 11} or size > 12:
            errors.append(
                error(
                    code="melodic_interval_forbidden",
                    message="Forbidden melodic interval",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="inherited_first_species",
                    evidence={"size_semitones": size, "from": prev_note, "to": note},
                )
            )

    # 2) Compensation after leap.
    for i in range(2, len(attacks)):
        slot, current = attacks[i]
        _, mid = attacks[i - 1]
        _, previous = attacks[i - 2]
        leap = mid - previous
        resolution = current - mid
        if abs(leap) <= 2:
            continue
        if (leap > 0 and resolution >= 0) or (leap < 0 and resolution <= 0):
            errors.append(
                error(
                    code="melodic_leap_not_compensated",
                    message="Leap must be compensated by contrary motion",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="inherited_first_species",
                    evidence={
                        "leap": leap,
                        "resolution": resolution,
                        "previous": previous,
                        "middle": mid,
                        "current": current,
                    },
                )
            )

    # 3) Melodic tritone in a 3-note span.
    for i in range(2, len(attacks)):
        slot, current = attacks[i]
        _, two_back = attacks[i - 2]
        if abs(current - two_back) == 6:
            errors.append(
                error(
                    code="melodic_tritone_forbidden",
                    message="Melodic tritone is forbidden",
                    measure=slot.measure,
                    beat=slot.beat,
                    origin="inherited_first_species",
                    evidence={"from": two_back, "to": current},
                )
            )

    return errors
