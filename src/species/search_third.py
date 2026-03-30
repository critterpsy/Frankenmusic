from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from .config import CPDisposition, SearchMode, SpeciesEngineConfig
from .models import ThirdSpeciesLine, ValidationReport
from .music_core import (
    cadential_subtonic_distance,
    diatonic_interval,
    interval_label,
    is_consonant,
    is_step,
    is_white_note,
    melodic_direction,
    perfect_species,
    same_diatonic_pitch,
)
from .plans import slots_to_third_line

_THIRD_INTERACTIVE_TOPK_BUFFER = 32
_THIRD_EXHAUSTIVE_MATERIALIZATION_CAP = 20000
_IMPERFECT_CONSONANCES = {"m3", "M3", "m6", "M6"}


@dataclass(frozen=True)
class _ThirdMeasureState:
    beat1: int | None
    beat2: int | None
    beat3: int | None
    beat4: int | None

    @property
    def is_final(self) -> bool:
        return self.beat2 is None and self.beat3 is None and self.beat4 is None


def _pitch_space(cf: list[int], config: SpeciesEngineConfig) -> list[int]:
    low, high = _pitch_bounds(cf, config)
    return [pitch for pitch in range(low, high + 1) if is_white_note(pitch)]


def _pitch_bounds(cf: list[int], config: SpeciesEngineConfig) -> tuple[int, int]:
    if config.cp_range_min is not None and config.cp_range_max is not None:
        low = min(config.cp_range_min, config.cp_range_max)
        high = max(config.cp_range_min, config.cp_range_max)
    elif config.cp_disposition == CPDisposition.ABOVE:
        low = min(cf) + 3
        high = max(cf) + 19
    else:
        low = min(cf) - 19
        high = max(cf) - 3
    return low, high


def _cadential_subtonics(cf: list[int], config: SpeciesEngineConfig) -> list[int]:
    low, high = _pitch_bounds(cf, config)
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
    return sorted(set(cadential_subtonics))


def _opening_ok(note: int, cf: int, disposition: CPDisposition) -> bool:
    iv = interval_label(note, cf)
    if disposition == CPDisposition.ABOVE:
        return note > cf and iv in {"P5", "P8"}
    return note <= cf and iv in {"P1", "P8"}


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


def _strict_passing(strong_prev: int, weak: int, strong_next: int) -> bool:
    return (
        is_step(strong_prev, weak)
        and is_step(weak, strong_next)
        and melodic_direction(strong_prev, weak) == melodic_direction(weak, strong_next)
        and melodic_direction(strong_prev, weak) != 0
    )


def _lower_neighbor(strong_prev: int, weak: int, strong_next: int) -> bool:
    if strong_prev != strong_next:
        return False
    if diatonic_interval(strong_prev, weak) != -1:
        return False
    if not is_step(strong_prev, weak) or not is_step(weak, strong_next):
        return False
    dir_in = melodic_direction(strong_prev, weak)
    dir_out = melodic_direction(weak, strong_next)
    return dir_in != 0 and dir_out != 0 and dir_in == -dir_out


def _upper_neighbor(strong_prev: int, weak: int, strong_next: int) -> bool:
    if strong_prev != strong_next:
        return False
    if diatonic_interval(strong_prev, weak) != 1:
        return False
    if not is_step(strong_prev, weak) or not is_step(weak, strong_next):
        return False
    dir_in = melodic_direction(strong_prev, weak)
    dir_out = melodic_direction(weak, strong_next)
    return dir_in != 0 and dir_out != 0 and dir_in == -dir_out


def _cambiata(
    n1: int,
    n2: int,
    n3: int,
    n4: int,
    *,
    cf_n: int,
) -> bool:
    if not is_consonant(n1, cf_n):
        return False
    if is_consonant(n2, cf_n):
        return False
    if not is_consonant(n3, cf_n):
        return False
    if not is_consonant(n4, cf_n):
        return False

    entry_dir = melodic_direction(n1, n2)
    if entry_dir != -1:
        return False
    if not is_step(n1, n2):
        return False
    if melodic_direction(n2, n3) != entry_dir:
        return False
    if abs(diatonic_interval(n2, n3)) != 2:
        return False
    if not is_step(n3, n4):
        return False
    if melodic_direction(n3, n4) != -entry_dir:
        return False
    return True


def _adjacent_perfect_parallel(cp1: int, cf1: int, cp2: int, cf2: int) -> bool:
    sp1 = perfect_species(cp1, cf1)
    sp2 = perfect_species(cp2, cf2)
    if sp1 is None or sp2 is None or sp1 != sp2:
        return False
    return (cp2 - cp1) != 0 and (cf2 - cf1) != 0


def _direct_perfect_forbidden(cp1: int, cf1: int, cp2: int, cf2: int) -> bool:
    kind = perfect_species(cp2, cf2)
    if kind is None:
        return False
    cp_move = cp2 - cp1
    cf_move = cf2 - cf1
    if cp_move == 0 or cf_move == 0:
        return False
    same_direction = (cp_move > 0 and cf_move > 0) or (cp_move < 0 and cf_move < 0)
    return same_direction and abs(cp_move) > 2


def _third_leap_direction_ok(
    from_note: int,
    to_note: int,
    *,
    from_beat: int,
    next_note: int | None,
    cambiata_characteristic: bool,
) -> bool:
    leap = diatonic_interval(from_note, to_note)
    if abs(leap) <= 1:
        return True

    if from_beat in {1, 3}:
        return leap < 0

    if leap > 0:
        return True

    if leap != -2:
        return False
    if cambiata_characteristic:
        return True
    if next_note is None:
        return False
    return is_step(to_note, next_note) and melodic_direction(to_note, next_note) == 1


def _leap_endpoints_ok(
    from_note: int,
    from_cf: int,
    to_note: int,
    to_cf: int,
    *,
    cambiata_characteristic: bool,
) -> bool:
    if abs(diatonic_interval(from_note, to_note)) <= 1:
        return True
    if is_consonant(from_note, from_cf) and is_consonant(to_note, to_cf):
        return True
    return cambiata_characteristic


def _has_required_cadential_subtonic(previous: int, final_note: int, tonic: int) -> bool:
    return previous == final_note - cadential_subtonic_distance(tonic)


def _state_score(
    measure: int,
    state: _ThirdMeasureState,
    cf: list[int],
) -> float:
    cf_note = cf[measure - 1]
    score = 0.0

    if state.beat1 is not None and interval_label(state.beat1, cf_note) in _IMPERFECT_CONSONANCES:
        score += 1.0
    if not state.is_final and state.beat3 is not None and interval_label(state.beat3, cf_note) in _IMPERFECT_CONSONANCES:
        score += 0.75

    if state.beat1 is None:
        score -= 0.25
        return score

    if state.is_final:
        return score

    assert state.beat2 is not None
    assert state.beat3 is not None
    assert state.beat4 is not None

    melodic_pairs = (
        (state.beat1, state.beat2),
        (state.beat2, state.beat3),
        (state.beat3, state.beat4),
    )
    for left, right in melodic_pairs:
        leap = abs(right - left)
        if leap <= 2:
            score += 1.25
        else:
            score += max(-1.75, 0.6 - 0.25 * leap)

    if not is_consonant(state.beat2, cf_note):
        score -= 0.15
    if not is_consonant(state.beat4, cf_note):
        score -= 0.15

    return score


def _canonical_cadence_bonus(
    left: _ThirdMeasureState,
    right: _ThirdMeasureState,
    cf_penultimate: int,
    cf_final: int,
) -> float:
    assert left.beat3 is not None
    assert left.beat4 is not None
    final_note = right.beat1
    assert final_note is not None

    bonus = 0.0
    if _has_required_cadential_subtonic(left.beat4, final_note, cf_final):
        bonus += 3.0
    if interval_label(left.beat3, cf_penultimate) in _IMPERFECT_CONSONANCES:
        bonus += 1.0
    return bonus


def _transition_score(
    measure: int,
    left: _ThirdMeasureState,
    right: _ThirdMeasureState,
    cf: list[int],
) -> float:
    assert left.beat4 is not None
    assert right.beat1 is not None

    cp_move = right.beat1 - left.beat4
    cf_move = cf[measure] - cf[measure - 1]
    leap = abs(cp_move)

    score = 0.0
    if leap <= 2:
        score += 2.5
    else:
        score += max(-2.5, 1.0 - 0.25 * leap)

    if cp_move == 0 or cf_move == 0:
        score += 0.2
    elif (cp_move > 0 and cf_move < 0) or (cp_move < 0 and cf_move > 0):
        score += 0.45
    else:
        score -= 0.3

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
    domains: list[list[_ThirdMeasureState]],
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
    domains: list[list[_ThirdMeasureState]],
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


def _count_candidate_paths(
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
    domains: list[list[_ThirdMeasureState]],
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
            for path in paths:
                for right_idx in edges[measure][left_idx]:
                    next_layer_paths[right_idx].append(path + (right_idx,))
        layer_paths = next_layer_paths

    out: list[tuple[int, ...]] = []
    for paths in layer_paths.values():
        out.extend(paths)
    return out


def _build_domains(
    cf: list[int],
    config: SpeciesEngineConfig,
    pitch_space: list[int],
    cadential_subtonics: list[int],
) -> list[list[_ThirdMeasureState]]:
    n = len(cf)
    domains: list[list[_ThirdMeasureState]] = []
    for measure in range(1, n + 1):
        cf_note = cf[measure - 1]
        is_final = measure == n
        if is_final:
            final_states: list[_ThirdMeasureState] = []
            for beat1 in pitch_space:
                if interval_label(beat1, cf_note) in {"P1", "P8"}:
                    final_states.append(_ThirdMeasureState(beat1=beat1, beat2=None, beat3=None, beat4=None))
            domains.append(final_states)
            continue

        if measure == 1 and config.allow_half_rest_start:
            beat1_options: list[int | None] = [None, *pitch_space]
        else:
            beat1_options = list(pitch_space)

        states: list[_ThirdMeasureState] = []
        for beat1 in beat1_options:
            if beat1 is not None:
                if measure == 1 and not _opening_ok(beat1, cf_note, config.cp_disposition):
                    continue
                if measure > 1 and not is_consonant(beat1, cf_note):
                    continue
                if 1 < measure < n and interval_label(beat1, cf_note) == "P1":
                    continue

            for beat3 in pitch_space:
                if not is_consonant(beat3, cf_note):
                    continue
                for beat2 in pitch_space:
                    if beat1 is not None:
                        if beat1 == beat2:
                            continue
                        if _forbidden_melodic_interval(beat1, beat2):
                            continue
                    elif measure == 1 and not _opening_ok(beat2, cf_note, config.cp_disposition):
                        continue

                    if beat2 == beat3:
                        continue
                    if _forbidden_melodic_interval(beat2, beat3):
                        continue
                    if beat1 is not None and not _triplet_melodic_ok(beat1, beat2, beat3):
                        continue

                    beat2_dissonant = not is_consonant(beat2, cf_note)
                    if beat2_dissonant:
                        if beat1 is None:
                            continue
                        in_step = is_step(beat1, beat2)
                        if not in_step:
                            continue
                        direct_ok = _strict_passing(beat1, beat2, beat3)
                        lower_ok = _lower_neighbor(beat1, beat2, beat3)
                        candidate_cambiata = (
                            is_step(beat1, beat2)
                            and melodic_direction(beat1, beat2) == -1
                            and melodic_direction(beat2, beat3) == -1
                            and abs(diatonic_interval(beat2, beat3)) == 2
                        )
                        if not (direct_ok or lower_ok or candidate_cambiata):
                            continue

                    beat4_options = pitch_space if measure != n - 1 else sorted(set(pitch_space + cadential_subtonics))
                    for beat4 in beat4_options:
                        if beat3 == beat4:
                            continue
                        if beat2 == beat4:
                            continue
                        if _forbidden_melodic_interval(beat3, beat4):
                            continue
                        if not _triplet_melodic_ok(beat2, beat3, beat4):
                            continue
                        if beat1 is None:
                            if _forbidden_melodic_interval(beat2, beat4):
                                continue
                        if not is_consonant(beat4, cf_note):
                            if not is_step(beat3, beat4):
                                continue
                        if measure == n - 1 and beat4 in cadential_subtonics and same_diatonic_pitch(beat3, beat4):
                            continue

                        beat2_cambiata = (
                            beat1 is not None and _cambiata(beat1, beat2, beat3, beat4, cf_n=cf_note)
                        )

                        if beat1 is not None:
                            if not _third_leap_direction_ok(
                                beat1,
                                beat2,
                                from_beat=1,
                                next_note=beat3,
                                cambiata_characteristic=False,
                            ):
                                continue
                            if not _leap_endpoints_ok(
                                beat1,
                                cf_note,
                                beat2,
                                cf_note,
                                cambiata_characteristic=False,
                            ):
                                continue

                        if not _third_leap_direction_ok(
                            beat2,
                            beat3,
                            from_beat=2,
                            next_note=beat4,
                            cambiata_characteristic=beat2_cambiata,
                        ):
                            continue
                        if not _leap_endpoints_ok(
                            beat2,
                            cf_note,
                            beat3,
                            cf_note,
                            cambiata_characteristic=beat2_cambiata,
                        ):
                            continue

                        if not _third_leap_direction_ok(
                            beat3,
                            beat4,
                            from_beat=3,
                            next_note=None,
                            cambiata_characteristic=False,
                        ):
                            continue
                        if not _leap_endpoints_ok(
                            beat3,
                            cf_note,
                            beat4,
                            cf_note,
                            cambiata_characteristic=False,
                        ):
                            continue

                        states.append(
                            _ThirdMeasureState(
                                beat1=beat1,
                                beat2=beat2,
                                beat3=beat3,
                                beat4=beat4,
                            )
                        )
        domains.append(states)
    return domains


def _left_measure_dissonance_valid(
    left: _ThirdMeasureState,
    right: _ThirdMeasureState,
    *,
    cf_now: int,
    cf_next: int,
) -> bool:
    assert left.beat2 is not None
    assert left.beat3 is not None
    assert left.beat4 is not None
    assert right.beat1 is not None

    if not is_consonant(left.beat2, cf_now):
        if left.beat1 is None:
            return False
        if _upper_neighbor(left.beat1, left.beat2, left.beat3):
            return False
        beat2_ok = (
            _strict_passing(left.beat1, left.beat2, left.beat3)
            or _lower_neighbor(left.beat1, left.beat2, left.beat3)
            or _cambiata(
                left.beat1,
                left.beat2,
                left.beat3,
                left.beat4,
                cf_n=cf_now,
            )
        )
        if not beat2_ok:
            return False

    if not is_consonant(left.beat4, cf_now):
        if _upper_neighbor(left.beat3, left.beat4, right.beat1):
            return False
        beat4_ok = _strict_passing(left.beat3, left.beat4, right.beat1) or _lower_neighbor(
            left.beat3,
            left.beat4,
            right.beat1,
        )
        if not beat4_ok:
            return False

    return True


def _transition_valid(
    measure: int,
    left: _ThirdMeasureState,
    right: _ThirdMeasureState,
    cf: list[int],
) -> bool:
    cf_now = cf[measure - 1]
    cf_next = cf[measure]
    n = len(cf)
    assert left.beat2 is not None
    assert left.beat3 is not None
    assert left.beat4 is not None
    assert right.beat1 is not None

    if left.beat4 == right.beat1:
        return False
    if _forbidden_melodic_interval(left.beat4, right.beat1):
        return False
    if not _triplet_melodic_ok(left.beat3, left.beat4, right.beat1):
        return False
    if not right.is_final:
        assert right.beat2 is not None
        if not _triplet_melodic_ok(left.beat4, right.beat1, right.beat2):
            return False

    if _adjacent_perfect_parallel(left.beat4, cf_now, right.beat1, cf_next):
        return False
    if _adjacent_perfect_parallel(left.beat3, cf_now, right.beat1, cf_next):
        return False
    if _direct_perfect_forbidden(left.beat4, cf_now, right.beat1, cf_next):
        return False
    if not _restricted_preceding_perfects_ok(left, right, cf_now, cf_next):
        return False

    if not _left_measure_dissonance_valid(left, right, cf_now=cf_now, cf_next=cf_next):
        return False

    next_note_after_right = None if right.is_final else right.beat2
    if not _third_leap_direction_ok(
        left.beat4,
        right.beat1,
        from_beat=4,
        next_note=next_note_after_right,
        cambiata_characteristic=False,
    ):
        return False
    if not _leap_endpoints_ok(
        left.beat4,
        cf_now,
        right.beat1,
        cf_next,
        cambiata_characteristic=False,
    ):
        return False

    if measure + 1 == n:
        if not is_step(left.beat4, right.beat1):
            return False
        if not _has_required_cadential_subtonic(left.beat4, right.beat1, cf_next):
            return False

    return True


def _restricted_preceding_perfects_ok(
    left: _ThirdMeasureState,
    right: _ThirdMeasureState,
    cf_now: int,
    cf_next: int,
) -> bool:
    assert left.beat2 is not None
    assert left.beat3 is not None
    assert left.beat4 is not None
    assert right.beat1 is not None

    curr_kind = perfect_species(right.beat1, cf_next)
    if curr_kind is None:
        return True

    if curr_kind == "P5":
        return not (
            perfect_species(left.beat3, cf_now) == "P5"
            or perfect_species(left.beat4, cf_now) == "P5"
        )

    return not (
        perfect_species(left.beat2, cf_now) == "P1/P8"
        or perfect_species(left.beat3, cf_now) == "P1/P8"
        or perfect_species(left.beat4, cf_now) == "P1/P8"
    )


def _path_to_line(path: tuple[int, ...], domains: list[list[_ThirdMeasureState]]) -> ThirdSpeciesLine:
    n = len(domains)
    slots: list[int | None] = []
    for measure, state_idx in enumerate(path, start=1):
        state = domains[measure - 1][state_idx]
        if measure < n:
            assert state.beat2 is not None
            assert state.beat3 is not None
            assert state.beat4 is not None
            slots.extend([state.beat1, state.beat2, state.beat3, state.beat4])
        else:
            assert state.beat1 is not None
            slots.append(state.beat1)
    return slots_to_third_line(slots)


def search_third_candidates(
    cf: list[int],
    config: SpeciesEngineConfig,
    validator: Callable[[ThirdSpeciesLine], ValidationReport],
) -> tuple[list[ThirdSpeciesLine], int, int]:
    pitch_space = _pitch_space(cf, config)
    cadential_subtonics = _cadential_subtonics(cf, config)
    domains = _build_domains(cf, config, pitch_space, cadential_subtonics)
    if not all(domains):
        return [], 0, 0

    raw_edges = _build_compatibility(domains, cf)
    forward, backward, edges = _reachable_state_sets(domains, raw_edges)
    viable_states = [forward[i] & backward[i] for i in range(len(domains))]
    if not all(viable_states):
        return [], 0, 0

    candidate_count = _count_candidate_paths(viable_states, edges)
    if candidate_count == 0:
        return [], 0, 0

    if config.max_solutions is None:
        requested_valid = _THIRD_INTERACTIVE_TOPK_BUFFER
    else:
        requested_valid = max(config.max_solutions, 1)

    if config.search_mode == SearchMode.EXHAUSTIVE and config.max_solutions is None:
        if candidate_count <= _THIRD_EXHAUSTIVE_MATERIALIZATION_CAP:
            selected_paths = _materialize_all_paths(viable_states, edges)
        else:
            selected_paths = _viterbi_top_k_paths(
                domains,
                cf,
                viable_states,
                edges,
                _THIRD_EXHAUSTIVE_MATERIALIZATION_CAP,
            )
    else:
        requested_paths = max(requested_valid, _THIRD_INTERACTIVE_TOPK_BUFFER)
        requested_paths = min(requested_paths, candidate_count)
        valid_lines: list[ThirdSpeciesLine] = []
        explored = 0
        seen_paths: set[tuple[int, ...]] = set()
        while True:
            selected_paths = _viterbi_top_k_paths(domains, cf, viable_states, edges, requested_paths)
            new_paths = [path for path in selected_paths if path not in seen_paths]
            for path in new_paths:
                seen_paths.add(path)
                line = _path_to_line(path, domains)
                explored += 1
                validation = validator(line)
                if validation.valid:
                    valid_lines.append(line)
                    if config.max_solutions is not None and len(valid_lines) >= config.max_solutions:
                        return valid_lines, explored, len(valid_lines)
            if requested_paths >= candidate_count:
                return valid_lines, explored, len(valid_lines)
            requested_paths = min(candidate_count, max(requested_paths + 1, requested_paths * 2))

    valid_lines = []
    explored = 0
    valid_count = 0
    for path in selected_paths:
        line = _path_to_line(path, domains)
        explored += 1
        validation = validator(line)
        if validation.valid:
            valid_count += 1
            valid_lines.append(line)

    return valid_lines, explored, valid_count
