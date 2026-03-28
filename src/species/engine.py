from __future__ import annotations

from .config import SpeciesEngineConfig
from .explainer import error
from .explainer import report
from .models import (
    CPNote,
    RankedSolution,
    RankedSolutions,
    ScoreBreakdown,
    SecondSpeciesLine,
    ValidationReport,
)
from .plans import build_temporal_grid, coerce_second_species_line, line_to_slots
from .ranking import rank_slots
from .rules import (
    validate_final_cadence,
    validate_melodic_constraints,
    validate_second_species_vertical_rules,
    validate_voice_independence,
)
from .search import search_candidates


def _normalize_inputs(
    cf: list[int],
    cp: SecondSpeciesLine | list | None,
    config: SpeciesEngineConfig | None,
) -> tuple[SpeciesEngineConfig, SecondSpeciesLine | None, list[CPNote] | None]:
    cfg = config or SpeciesEngineConfig()
    if cp is None:
        return cfg, None, None
    grid = build_temporal_grid(cf)
    line = coerce_second_species_line(cp, len(cf))
    slots = line_to_slots(line, grid)
    return cfg, line, slots


def validate_second_species(
    cf: list[int],
    cp: SecondSpeciesLine | list,
    config: SpeciesEngineConfig | None = None,
) -> ValidationReport:
    cfg, line, slots = _normalize_inputs(cf, cp, config)
    assert line is not None
    assert slots is not None
    grid = build_temporal_grid(cf)

    errors = []
    trace = []

    # External representation hard rule: final bar must duplicate beat1 == beat2.
    final_measure = line.measures[-1]
    if final_measure.beat1 != final_measure.beat2:
        errors.append(
            error(
                code="invalid_final_cadence",
                message="Final measure must satisfy p(N,1) = p(N,2)",
                measure=len(cf),
                beat=2,
                origin="second_species_exact",
                evidence={
                    "final_beat1": final_measure.beat1,
                    "final_beat2": final_measure.beat2,
                },
            )
        )

    second_errors, second_trace = validate_second_species_vertical_rules(grid, slots, cfg)
    errors.extend(second_errors)
    trace.extend(second_trace)

    errors.extend(validate_voice_independence(grid, slots))
    errors.extend(validate_melodic_constraints(grid, slots))
    errors.extend(validate_final_cadence(grid, slots))

    errors.sort(key=lambda e: (e.measure, e.beat, e.code))
    return report(errors, trace)


def rank_second_species_solution(
    cf: list[int],
    cp: SecondSpeciesLine | list,
    config: SpeciesEngineConfig | None = None,
) -> ScoreBreakdown:
    _, _, slots = _normalize_inputs(cf, cp, config)
    assert slots is not None
    grid = build_temporal_grid(cf)
    return rank_slots(grid, slots)


def search_second_species(
    cf: list[int],
    config: SpeciesEngineConfig | None = None,
) -> RankedSolutions:
    cfg = config or SpeciesEngineConfig()

    def _validator(line: SecondSpeciesLine) -> ValidationReport:
        return validate_second_species(cf, line, cfg)

    lines, explored, valid_count = search_candidates(cf, cfg, _validator)
    ranked: list[RankedSolution] = []
    for line in lines:
        validation = validate_second_species(cf, line, cfg)
        if not validation.valid:
            continue
        score = rank_second_species_solution(cf, line, cfg)
        ranked.append(RankedSolution(cp=line, score=score, validation=validation))
    ranked.sort(key=lambda s: s.score.total_score, reverse=True)

    if cfg.max_solutions is not None:
        ranked = ranked[: cfg.max_solutions]

    return RankedSolutions(
        solutions=ranked,
        explored_candidates=explored,
        valid_candidates=valid_count,
    )
