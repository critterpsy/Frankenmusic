from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import CPNote, GridSlot, SecondSpeciesLine, SecondSpeciesMeasure, TemporalGrid


def build_temporal_grid(cf: list[int]) -> TemporalGrid:
    if len(cf) < 2:
        raise ValueError("Second species requires CF length >= 2")
    slots: list[GridSlot] = []
    index = 0
    for measure, cf_pitch in enumerate(cf, start=1):
        is_final_measure = measure == len(cf)
        slots.append(
            GridSlot(
                index=index,
                measure=measure,
                beat=1,
                is_strong=True,
                is_final=is_final_measure,
                cf_index=measure - 1,
                cf_pitch=cf_pitch,
            )
        )
        index += 1
        if not is_final_measure:
            slots.append(
                GridSlot(
                    index=index,
                    measure=measure,
                    beat=2,
                    is_strong=False,
                    is_final=False,
                    cf_index=measure - 1,
                    cf_pitch=cf_pitch,
                )
            )
            index += 1
    return TemporalGrid(cf=cf, slots=slots)


def coerce_second_species_line(cp: Any, cf_len: int) -> SecondSpeciesLine:
    if isinstance(cp, SecondSpeciesLine):
        return cp

    if isinstance(cp, list):
        if not cp:
            raise ValueError("CP cannot be empty")
        first = cp[0]
        if isinstance(first, SecondSpeciesMeasure):
            return SecondSpeciesLine(measures=cp)
        if isinstance(first, dict):
            measures = [
                SecondSpeciesMeasure(beat1=item.get("beat1"), beat2=item.get("beat2"))
                for item in cp
            ]
            return SecondSpeciesLine(measures=measures)
        if isinstance(first, int) or first is None:
            expected_slots = 2 * cf_len - 1
            if len(cp) != expected_slots:
                raise ValueError(
                    f"Canonical slot CP must have length {expected_slots}, got {len(cp)}"
                )
            return slots_to_line(cp)

    raise TypeError("Unsupported CP input type")


def line_to_slots(line: SecondSpeciesLine, grid: TemporalGrid) -> list[CPNote]:
    if len(line.measures) != grid.cf_length:
        raise ValueError(
            f"CP measure count must match CF length ({grid.cf_length}), got {len(line.measures)}"
        )

    slots: list[CPNote] = [None for _ in grid.slots]
    for measure_idx, measure in enumerate(line.measures, start=1):
        strong_slot = (measure_idx - 1) * 2
        if measure_idx == grid.cf_length:
            strong_slot = len(slots) - 1
        slots[strong_slot] = measure.beat1
        if measure_idx < grid.cf_length:
            slots[strong_slot + 1] = measure.beat2
    return slots


def slots_to_line(slots: list[CPNote]) -> SecondSpeciesLine:
    if len(slots) % 2 == 0:
        raise ValueError("Canonical second-species slots must have odd length (2*N-1)")
    cf_len = (len(slots) + 1) // 2
    measures: list[SecondSpeciesMeasure] = []
    for measure in range(1, cf_len + 1):
        if measure < cf_len:
            strong_slot = (measure - 1) * 2
            measures.append(
                SecondSpeciesMeasure(beat1=slots[strong_slot], beat2=slots[strong_slot + 1])
            )
        else:
            final_note = slots[-1]
            measures.append(SecondSpeciesMeasure(beat1=final_note, beat2=final_note))
    return SecondSpeciesLine(measures=measures)


def first_real_attack(grid: TemporalGrid, slots: list[CPNote]) -> tuple[GridSlot, int] | None:
    for slot in grid.slots:
        note = slots[slot.index]
        if note is not None:
            return slot, note
    return None


def iter_real_attacks(grid: TemporalGrid, slots: list[CPNote]) -> list[tuple[GridSlot, int]]:
    out: list[tuple[GridSlot, int]] = []
    for slot in grid.slots:
        note = slots[slot.index]
        if note is not None:
            out.append((slot, note))
    return out


def line_to_dict(line: SecondSpeciesLine) -> list[dict[str, CPNote]]:
    return [asdict(measure) for measure in line.measures]
