from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CPDisposition(str, Enum):
    ABOVE = "above"
    BELOW = "below"


class SearchMode(str, Enum):
    EXHAUSTIVE = "exhaustive"
    EAGER = "eager"


@dataclass(frozen=True)
class SpeciesEngineConfig:
    cp_disposition: CPDisposition = CPDisposition.ABOVE
    search_mode: SearchMode = SearchMode.EAGER
    max_solutions: int | None = 1
    allow_half_rest_start: bool = False
    cp_range_min: int | None = None
    cp_range_max: int | None = None
