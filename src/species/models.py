from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


CPNote = int | None

RuleOrigin = Literal[
    "second_species_exact",
    "third_species_exact",
    "inherited_first_species",
    "ranking_heuristic",
]


@dataclass(frozen=True)
class SecondSpeciesMeasure:
    beat1: CPNote
    beat2: CPNote


@dataclass(frozen=True)
class SecondSpeciesLine:
    measures: list[SecondSpeciesMeasure]

    def real_attacks(self) -> list[int]:
        notes: list[int] = []
        for measure in self.measures:
            if measure.beat1 is not None:
                notes.append(measure.beat1)
            if measure.beat2 is not None:
                notes.append(measure.beat2)
        return notes


@dataclass(frozen=True)
class ThirdSpeciesMeasure:
    beat1: CPNote
    beat2: CPNote
    beat3: CPNote
    beat4: CPNote


@dataclass(frozen=True)
class ThirdSpeciesLine:
    measures: list[ThirdSpeciesMeasure]

    def real_attacks(self) -> list[int]:
        notes: list[int] = []
        for measure_idx, measure in enumerate(self.measures, start=1):
            if measure.beat1 is not None:
                notes.append(measure.beat1)
            is_final = measure_idx == len(self.measures)
            if is_final:
                continue
            if measure.beat2 is not None:
                notes.append(measure.beat2)
            if measure.beat3 is not None:
                notes.append(measure.beat3)
            if measure.beat4 is not None:
                notes.append(measure.beat4)
        return notes


@dataclass(frozen=True)
class GridSlot:
    index: int
    measure: int
    beat: int
    is_strong: bool
    is_final: bool
    cf_index: int
    cf_pitch: int


@dataclass(frozen=True)
class TemporalGrid:
    cf: list[int]
    slots: list[GridSlot]

    @property
    def cf_length(self) -> int:
        return len(self.cf)

    @property
    def total_slots(self) -> int:
        return len(self.slots)

    @property
    def strong_slots(self) -> list[GridSlot]:
        return [slot for slot in self.slots if slot.is_strong]

    @property
    def weak_slots(self) -> list[GridSlot]:
        return [slot for slot in self.slots if not slot.is_strong]


@dataclass(frozen=True)
class LineState:
    index: int
    last_note: int | None
    previous_note: int | None
    direction: int
    leap_streak: int


@dataclass(frozen=True)
class TextureState:
    previous_strong_cp: int | None
    current_strong_cp: int | None
    previous_strong_cf: int | None
    current_strong_cf: int | None
    previous_strong_interval: int | None
    current_strong_interval: int | None


@dataclass(frozen=True)
class CadentialContext:
    final_slot_index: int
    penultimate_slot_index: int | None
    previous_strong_slot_index: int | None
    final_interval_chromatic: int
    final_interval_label: str


@dataclass(frozen=True)
class ValidationError:
    code: str
    message: str
    measure: int
    beat: int
    origin: RuleOrigin
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    errors: list[ValidationError]
    trace: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ScoreBreakdown:
    total_score: float
    contributions: dict[str, float]
    weights: dict[str, float]
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RankedSolution:
    cp: SecondSpeciesLine | ThirdSpeciesLine
    score: ScoreBreakdown
    validation: ValidationReport


@dataclass(frozen=True)
class RankedSolutions:
    solutions: list[RankedSolution]
    explored_candidates: int
    valid_candidates: int
