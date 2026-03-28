from __future__ import annotations

from ..explainer import error
from ..models import CPNote, TemporalGrid, ValidationError
from ..music_core import cadential_subtonic_distance, interval_label, is_step
from ..plans import iter_real_attacks


def _has_required_cadential_subtonic(
    prev_note: int,
    final_note: int,
    tonic: int,
) -> bool:
    return prev_note == final_note - cadential_subtonic_distance(tonic)


def validate_final_cadence(grid: TemporalGrid, slots: list[CPNote]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    final_slot = grid.slots[-1]
    final_note = slots[final_slot.index]
    if final_note is None:
        errors.append(
            error(
                code="invalid_final_cadence",
                message="Final cadence note is missing",
                measure=final_slot.measure,
                beat=final_slot.beat,
                origin="second_species_exact",
                evidence={},
            )
        )
        return errors

    label = interval_label(final_note, final_slot.cf_pitch)
    if label not in {"P1", "P8"}:
        errors.append(
            error(
                code="invalid_final_cadence",
                message="Final vertical interval must be P1 or P8",
                measure=final_slot.measure,
                beat=final_slot.beat,
                origin="second_species_exact",
                evidence={"interval": label},
            )
        )

    attacks = iter_real_attacks(grid, slots)
    if len(attacks) < 2:
        return errors
    prev_slot, prev_note = attacks[-2]
    approached_by_step = is_step(prev_note, final_note)
    if not approached_by_step:
        errors.append(
            error(
                code="final_not_approached_by_step",
                message="Final CP note must be approached by step",
                measure=final_slot.measure,
                beat=final_slot.beat,
                origin="inherited_first_species",
                evidence={
                    "from_measure": prev_slot.measure,
                    "from_beat": prev_slot.beat,
                    "from_note": prev_note,
                    "to_note": final_note,
                },
            )
        )
    else:
        if not _has_required_cadential_subtonic(prev_note, final_note, final_slot.cf_pitch):
            errors.append(
                error(
                    code="cadential_subtonic_required",
                    message="Cadence must be subtonic -> tonic (semitone except Phrygian whole tone)",
                    measure=final_slot.measure,
                    beat=final_slot.beat,
                    origin="second_species_exact",
                    evidence={
                        "previous_note": prev_note,
                        "final_note": final_note,
                        "required_distance": cadential_subtonic_distance(final_slot.cf_pitch),
                        "tonic": final_slot.cf_pitch,
                    },
                )
            )

    return errors
