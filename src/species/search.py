from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from .config import CPDisposition, SearchMode, SpeciesEngineConfig
from .models import SecondSpeciesLine, ValidationReport
from .music_core import (
    cadential_subtonic_distance,
    interval_label,
    is_consonant,
    is_step,
    is_strong_consonance,
    is_white_note,
    melodic_direction,
    perfect_species,
)
from .plans import slots_to_line

_INTERACTIVE_TOPK_BUFFER = 16
_EXHAUSTIVE_MATERIALIZATION_CAP = 20000
_IMPERFECT_CONSONANCES = {"m3", "M3", "m6", "M6"}


@dataclass(frozen=True)
class _MeasureState:
    strong: int | None
    weak: int


def _pitch_space(cf: list[int], config: SpeciesEngineConfig) -> list[int]:
    if config.cp_range_min is not None and config.cp_range_max is not None:
        low = min(config.cp_range_min, config.cp_range_max)
        high = max(config.cp_range_min, config.cp_range_max)
    else:
        if config.cp_disposition == CPDisposition.ABOVE:
            low = min(cf) + 3
            high = max(cf) + 19
        else:
            low = min(cf) - 19
            high = max(cf) - 3
    white_space = [pitch for pitch in range(low, high + 1) if is_white_note(pitch)]
    cadence_distance = cadential_subtonic_distance(cf[-1])
    final_candidates = [
        pitch
        for pitch in range(low, high + 1)
        if interval_label(pitch, cf[-1]) in {"P1", "P8"}
    ]
    cadential_subtonics = [
        final - cadence_distance
        for final in final_candidates
        if low <= final - cadence_distance <= high
    ]
    return sorted(set(white_space + cadential_subtonics))


def _opening_ok(note: int, cf: int, disposition: CPDisposition) -> bool:
    iv = interval_label(note, cf)
    if disposition == CPDisposition.ABOVE:
        return note > cf and iv in {"P5", "P8"}
    return note <= cf and iv in {"P1", "P8"}


def _strict_passing(strong: int, weak: int, next_strong: int) -> bool:
    return (
        is_step(strong, weak)
        and is_step(weak, next_strong)
        and melodic_direction(strong, weak) == melodic_direction(weak, next_strong)
        and melodic_direction(strong, weak) != 0
    )


def _adjacent_perfect_parallel(
    cp1: int,
    cf1: int,
    cp2: int,
    cf2: int,
) -> bool:
    sp1 = perfect_species(cp1, cf1)
    sp2 = perfect_species(cp2, cf2)
    if sp1 is None or sp2 is None or sp1 != sp2:
        return False
    return (cp2 - cp1) != 0 and (cf2 - cf1) != 0


def _forbidden_melodic_interval(note1: int, note2: int) -> bool:
    size = abs(note2 - note1)
    return size in {6, 9, 10, 11} or size > 12


def _triplet_melodic_ok(previous: int, middle: int, current: int) -> bool:
    leap = middle - previous
    resolution = current - middle
    if abs(leap) > 2:
        if (leap > 0 and resolution >= 0) or (leap < 0 and resolution <= 0):
            return False
    if abs(current - previous) == 6:
        return False
    return True


def _has_required_cadential_subtonic(previous: int, final_note: int, tonic: int) -> bool:
    return previous == final_note - cadential_subtonic_distance(tonic)


def _build_domains(
    cf: list[int],
    config: SpeciesEngineConfig,
    pitch_space: list[int],
) -> list[list[_MeasureState]]:
    n = len(cf)
    domains: list[list[_MeasureState]] = []

    for measure in range(1, n + 1):
        cf_note = cf[measure - 1]
        is_final = measure == n
        interior = 1 < measure < n

        if is_final:
            final_states = []
            for strong in pitch_space:
                if interval_label(strong, cf_note) in {"P1", "P8"}:
                    final_states.append(_MeasureState(strong=strong, weak=strong))
            domains.append(final_states)
            continue

        if measure == 1 and config.allow_half_rest_start:
            strong_options: list[int | None] = [None, *pitch_space]
        else:
            strong_options = list(pitch_space)

        states: list[_MeasureState] = []
        for strong in strong_options:
            if strong is not None:
                if measure == 1 and not _opening_ok(strong, cf_note, config.cp_disposition):
                    continue
                if interior:
                    label = interval_label(strong, cf_note)
                    if label == "P1":
                        continue
                    if not is_strong_consonance(strong, cf_note):
                        continue

            for weak in pitch_space:
                if strong is not None:
                    if weak == strong:
                        continue
                    if _forbidden_melodic_interval(strong, weak):
                        continue

                if measure == 1 and strong is None and not _opening_ok(weak, cf_note, config.cp_disposition):
                    continue

                if interior and interval_label(weak, cf_note) == "P1":
                    continue

                # With half-rest opening, weak cannot be dissonant because strict passing
                # requires a real strong support in this metric position.
                if strong is None and not is_consonant(weak, cf_note):
                    continue

                states.append(_MeasureState(strong=strong, weak=weak))

        domains.append(states)

    return domains


def _transition_valid(
    measure: int,
    left: _MeasureState,
    right: _MeasureState,
    cf: list[int],
) -> bool:
    cf_now = cf[measure - 1]
    cf_next = cf[measure]
    n = len(cf)

    strong_now = left.strong
    weak_now = left.weak
    strong_next = right.strong
    assert strong_next is not None

    # Immediate repetition across barline is forbidden.
    if weak_now == strong_next:
        return False

    # Consecutive strong supports cannot repeat perfect species.
    if strong_now is not None:
        prev_kind = perfect_species(strong_now, cf_now)
        curr_kind = perfect_species(strong_next, cf_next)
        if prev_kind is not None and prev_kind == curr_kind:
            return False

    # Weak dissonance must be strict passing.
    if not is_consonant(weak_now, cf_now):
        if strong_now is None:
            return False
        if not _strict_passing(strong_now, weak_now, strong_next):
            return False

    # No adjacent perfect parallels between real attacks.
    if _adjacent_perfect_parallel(weak_now, cf_now, strong_next, cf_next):
        return False

    # Adjacent melodic interval constraints on barline attacks.
    if _forbidden_melodic_interval(weak_now, strong_next):
        return False

    # Triplet constraints: (s_i, w_i, s_{i+1})
    if strong_now is not None and not _triplet_melodic_ok(strong_now, weak_now, strong_next):
        return False

    # Triplet constraints: (w_i, s_{i+1}, w_{i+1}) if next measure is not final.
    if measure + 1 < n:
        if not _triplet_melodic_ok(weak_now, strong_next, right.weak):
            return False

    # Final cadence approach by step.
    if measure + 1 == n:
        if not is_step(weak_now, strong_next):
            return False
        if not _has_required_cadential_subtonic(weak_now, strong_next, cf_next):
            return False

    return True


def _canonical_cadence_bonus(
    left: _MeasureState,
    right: _MeasureState,
    cf_penultimate: int,
    cf_final: int,
) -> float:
    strong_prev = left.strong
    weak_prev = left.weak
    final_note = right.strong
    assert final_note is not None

    bonus = 0.0
    if _has_required_cadential_subtonic(weak_prev, final_note, cf_final):
        bonus += 3.0
    if strong_prev is not None:
        if interval_label(strong_prev, cf_penultimate) in _IMPERFECT_CONSONANCES:
            bonus += 1.5
    return bonus


def _state_score(
    measure: int,
    state: _MeasureState,
    cf: list[int],
) -> float:
    n = len(cf)
    cf_note = cf[measure - 1]
    score = 0.0

    if state.strong is not None:
        if interval_label(state.strong, cf_note) in _IMPERFECT_CONSONANCES:
            score += 1.0

    if measure < n and state.strong is not None:
        leap = abs(state.weak - state.strong)
        if leap <= 2:
            score += 2.0
        else:
            score += max(-2.0, 1.0 - 0.35 * leap)

    if measure == 1 and state.strong is None:
        score -= 0.25

    return score


def _transition_score(
    measure: int,
    left: _MeasureState,
    right: _MeasureState,
    cf: list[int],
) -> float:
    # measure is 1-based transition index: X_measure -> X_(measure+1)
    cp_move = right.strong - left.weak
    cf_move = cf[measure] - cf[measure - 1]

    score = 0.0
    leap = abs(cp_move)
    if leap <= 2:
        score += 2.5
    else:
        score += max(-2.5, 1.0 - 0.3 * leap)

    if cp_move == 0 or cf_move == 0:
        score += 0.15
    elif (cp_move > 0 and cf_move < 0) or (cp_move < 0 and cf_move > 0):
        score += 0.45
    else:
        score -= 0.25

    if measure + 1 == len(cf):
        score += _canonical_cadence_bonus(
            left,
            right,
            cf_penultimate=cf[measure - 1],
            cf_final=cf[measure],
        )

    return score


def _trim_topk(
    bucket: list[tuple[float, tuple[int, ...]]],
    item: tuple[float, tuple[int, ...]],
    k: int,
) -> None:
    bucket.append(item)
    bucket.sort(key=lambda x: x[0], reverse=True)
    if len(bucket) > k:
        del bucket[k:]


def _build_compatibility(
    domains: list[list[_MeasureState]],
    cf: list[int],
) -> list[list[list[int]]]:
    n = len(domains)
    edges: list[list[list[int]]] = []
    for measure in range(1, n):
        left_domain = domains[measure - 1]
        right_domain = domains[measure]
        outgoing: list[list[int]] = [[] for _ in left_domain]
        for left_idx, left_state in enumerate(left_domain):
            valid_right = outgoing[left_idx]
            for right_idx, right_state in enumerate(right_domain):
                if _transition_valid(measure, left_state, right_state, cf):
                    valid_right.append(right_idx)
        edges.append(outgoing)
    return edges


def _reachable_state_sets(
    domains: list[list[_MeasureState]],
    edges: list[list[list[int]]],
) -> tuple[list[set[int]], list[set[int]], list[list[list[int]]]]:
    n = len(domains)
    forward: list[set[int]] = [set() for _ in range(n)]
    backward: list[set[int]] = [set() for _ in range(n)]

    forward[0] = set(range(len(domains[0])))
    for i in range(n - 1):
        next_set: set[int] = set()
        for left_idx in forward[i]:
            next_set.update(edges[i][left_idx])
        forward[i + 1] = next_set

    backward[-1] = set(range(len(domains[-1])))
    for i in range(n - 2, -1, -1):
        current: set[int] = set()
        next_reachable = backward[i + 1]
        for left_idx, outgoing in enumerate(edges[i]):
            if left_idx not in forward[i]:
                continue
            if any(right_idx in next_reachable for right_idx in outgoing):
                current.add(left_idx)
        backward[i] = current

    viable_states = [forward[i] & backward[i] for i in range(n)]
    pruned_edges: list[list[list[int]]] = []
    for i in range(n - 1):
        right_viable = viable_states[i + 1]
        measure_edges: list[list[int]] = []
        for left_idx, outgoing in enumerate(edges[i]):
            if left_idx not in viable_states[i]:
                measure_edges.append([])
                continue
            measure_edges.append([right_idx for right_idx in outgoing if right_idx in right_viable])
        pruned_edges.append(measure_edges)

    return forward, backward, pruned_edges


def _count_valid_paths(
    viable_states: list[set[int]],
    edges: list[list[list[int]]],
) -> int:
    n = len(viable_states)
    counts: list[dict[int, int]] = [defaultdict(int) for _ in range(n)]
    for start_idx in viable_states[0]:
        counts[0][start_idx] = 1

    for i in range(n - 1):
        for left_idx, left_count in counts[i].items():
            if left_count == 0:
                continue
            for right_idx in edges[i][left_idx]:
                counts[i + 1][right_idx] += left_count

    return sum(counts[-1].values())


def _viterbi_top_k_paths(
    domains: list[list[_MeasureState]],
    cf: list[int],
    viable_states: list[set[int]],
    edges: list[list[list[int]]],
    k: int,
) -> list[tuple[int, ...]]:
    if k <= 0:
        return []

    n = len(domains)
    layer: dict[int, list[tuple[float, tuple[int, ...]]]] = {}
    for state_idx in viable_states[0]:
        score = _state_score(1, domains[0][state_idx], cf)
        layer[state_idx] = [(score, (state_idx,))]

    for measure in range(1, n):
        next_layer: dict[int, list[tuple[float, tuple[int, ...]]]] = defaultdict(list)
        for left_idx, candidates in layer.items():
            left_state = domains[measure - 1][left_idx]
            for score, path in candidates:
                for right_idx in edges[measure - 1][left_idx]:
                    right_state = domains[measure][right_idx]
                    next_score = (
                        score
                        + _transition_score(measure, left_state, right_state, cf)
                        + _state_score(measure + 1, right_state, cf)
                    )
                    _trim_topk(next_layer[right_idx], (next_score, path + (right_idx,)), k)
        layer = next_layer

    merged: list[tuple[float, tuple[int, ...]]] = []
    for candidates in layer.values():
        merged.extend(candidates)
    merged.sort(key=lambda x: x[0], reverse=True)
    return [path for _, path in merged[:k]]


def _materialize_all_paths(
    viable_states: list[set[int]],
    edges: list[list[list[int]]],
) -> list[tuple[int, ...]]:
    n = len(viable_states)
    layer_paths: dict[int, list[tuple[int, ...]]] = {
        state_idx: [(state_idx,)] for state_idx in viable_states[0]
    }

    for measure in range(n - 1):
        next_layer_paths: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for left_idx, paths in layer_paths.items():
            outgoing = edges[measure][left_idx]
            for path in paths:
                for right_idx in outgoing:
                    next_layer_paths[right_idx].append(path + (right_idx,))
        layer_paths = next_layer_paths

    out: list[tuple[int, ...]] = []
    for paths in layer_paths.values():
        out.extend(paths)
    return out


def _path_to_line(path: tuple[int, ...], domains: list[list[_MeasureState]]) -> SecondSpeciesLine:
    n = len(domains)
    slots: list[int | None] = []
    for measure, state_idx in enumerate(path, start=1):
        state = domains[measure - 1][state_idx]
        if measure < n:
            slots.extend([state.strong, state.weak])
        else:
            slots.append(state.strong)
    return slots_to_line(slots)


def search_candidates(
    cf: list[int],
    config: SpeciesEngineConfig,
    validator: Callable[[SecondSpeciesLine], ValidationReport],
) -> tuple[list[SecondSpeciesLine], int, int]:
    pitch_space = _pitch_space(cf, config)
    domains = _build_domains(cf, config, pitch_space)
    if not all(domains):
        return [], 0, 0

    raw_edges = _build_compatibility(domains, cf)
    forward, backward, edges = _reachable_state_sets(domains, raw_edges)
    viable_states = [forward[i] & backward[i] for i in range(len(domains))]
    if not all(viable_states):
        return [], 0, 0

    valid_count = _count_valid_paths(viable_states, edges)
    if valid_count == 0:
        return [], 0, 0

    selected_paths: list[tuple[int, ...]]
    if config.search_mode == SearchMode.EXHAUSTIVE and config.max_solutions is None:
        if valid_count <= _EXHAUSTIVE_MATERIALIZATION_CAP:
            selected_paths = _materialize_all_paths(viable_states, edges)
        else:
            selected_paths = _viterbi_top_k_paths(
                domains,
                cf,
                viable_states,
                edges,
                _EXHAUSTIVE_MATERIALIZATION_CAP,
            )
    else:
        requested = config.max_solutions if config.max_solutions is not None else _INTERACTIVE_TOPK_BUFFER
        if config.search_mode == SearchMode.EAGER:
            requested = max(requested, _INTERACTIVE_TOPK_BUFFER)
        requested = min(requested, valid_count)
        selected_paths = _viterbi_top_k_paths(domains, cf, viable_states, edges, requested)

    valid_lines: list[SecondSpeciesLine] = []
    explored = 0
    for path in selected_paths:
        line = _path_to_line(path, domains)
        explored += 1
        validation = validator(line)
        if validation.valid:
            valid_lines.append(line)

    return valid_lines, explored, valid_count
