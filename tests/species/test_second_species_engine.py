import os
import sys
import unittest
from copy import deepcopy
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.species.config import CPDisposition, SearchMode, SpeciesEngineConfig
from src.species.engine import (
    rank_second_species_solution,
    search_second_species,
    validate_second_species,
)
from src.species.music_core import (
    cadential_subtonic_distance,
    interval_label,
    is_step,
    is_white_note,
)
from src.species.plans import build_temporal_grid


CF4 = [0, 2, 4, 2]
VALID_CP_ABOVE = [
    {"beat1": 12, "beat2": 11},
    {"beat1": 9, "beat2": 11},
    {"beat1": 12, "beat2": 13},
    {"beat1": 14, "beat2": 14},
]
VALID_CP_BELOW = [
    {"beat1": 0, "beat2": 12},
    {"beat1": 11, "beat2": -1},
    {"beat1": 0, "beat2": 1},
    {"beat1": 2, "beat2": 2},
]


def _codes(report):
    return {e.code for e in report.errors}


class TestSecondSpeciesUnit(unittest.TestCase):
    def test_grid_is_2n_minus_1(self):
        grid = build_temporal_grid(CF4)
        self.assertEqual(grid.total_slots, 2 * len(CF4) - 1)
        self.assertTrue(grid.slots[-1].is_final)
        self.assertTrue(grid.slots[-1].is_strong)

    def test_valid_opening_above(self):
        report = validate_second_species(
            CF4,
            VALID_CP_ABOVE,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid)

    def test_valid_opening_below(self):
        report = validate_second_species(
            CF4,
            VALID_CP_BELOW,
            SpeciesEngineConfig(cp_disposition=CPDisposition.BELOW),
        )
        self.assertTrue(report.valid)

    def test_first_measure_weak_dissonant_passing_is_valid(self):
        report = validate_second_species(
            CF4,
            VALID_CP_ABOVE,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid)

    def test_strong_beat_dissonance_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[1]["beat1"] = 0
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("strong_beat_dissonance", _codes(report))

    def test_weak_dissonance_without_strict_passing_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[0]["beat2"] = 13
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("weak_dissonance_not_strict_passing", _codes(report))

    def test_invalid_opening_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[0]["beat1"] = 0
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("invalid_opening_interval", _codes(report))

    def test_invalid_final_cadence_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[-1]["beat1"] = 6
        cp[-1]["beat2"] = 6
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("invalid_final_cadence", _codes(report))

    def test_final_measure_must_duplicate_beat1_and_beat2(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[-1]["beat1"] = 5
        cp[-1]["beat2"] = 17
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("invalid_final_cadence", _codes(report))

    def test_final_not_approached_by_step_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[2]["beat2"] = 10
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("final_not_approached_by_step", _codes(report))

    def test_final_requires_cadential_subtonic(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[2]["beat2"] = 12
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("cadential_subtonic_required", _codes(report))

    def test_phrygian_cadence_uses_whole_tone_subtonic(self):
        cf = [0, 2, 4, 5, 4]
        cp_valid = [
            {"beat1": 12, "beat2": 11},
            {"beat1": 9, "beat2": 11},
            {"beat1": 16, "beat2": 14},
            {"beat1": 12, "beat2": 14},
            {"beat1": 16, "beat2": 16},
        ]
        valid_report = validate_second_species(
            cf, cp_valid, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertTrue(valid_report.valid)

        cp_invalid = deepcopy(cp_valid)
        cp_invalid[-2]["beat2"] = 15
        invalid_report = validate_second_species(
            cf, cp_invalid, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("cadential_subtonic_required", _codes(invalid_report))

    def test_interior_unison_strong_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[1]["beat1"] = 2
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("interior_unison_forbidden", _codes(report))

    def test_interior_unison_weak_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[1]["beat2"] = 2
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("interior_unison_forbidden", _codes(report))

    def test_repetition_beat1_equals_beat2_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[1]["beat2"] = cp[1]["beat1"]
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("immediate_repetition_forbidden", _codes(report))

    def test_repetition_beat2_equals_next_beat1_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[1]["beat2"] = cp[2]["beat1"]
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("immediate_repetition_forbidden", _codes(report))

    def test_adjacent_perfect_parallel_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[0]["beat2"] = 7
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("adjacent_perfect_parallel", _codes(report))

    def test_strong_support_perfect_parallel_rejected(self):
        cp = deepcopy(VALID_CP_ABOVE)
        cp[1]["beat1"] = 14
        report = validate_second_species(
            CF4, cp, SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE)
        )
        self.assertIn("strong_support_perfect_parallel", _codes(report))

    def test_half_rest_start_with_invalid_first_attack_rejected(self):
        cp = deepcopy(VALID_CP_BELOW)
        cp[0]["beat1"] = None
        cp[0]["beat2"] = 2
        report = validate_second_species(
            CF4,
            cp,
            SpeciesEngineConfig(
                cp_disposition=CPDisposition.BELOW,
                allow_half_rest_start=True,
            ),
        )
        self.assertIn("invalid_opening_interval", _codes(report))


class TestSecondSpeciesIntegration(unittest.TestCase):
    def test_exhaustive_search_returns_only_valid_solutions(self):
        cf = [0, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=18,
            max_solutions=3,
        )
        ranked = search_second_species(cf, cfg)
        self.assertGreater(len(ranked.solutions), 0)
        for solution in ranked.solutions:
            self.assertTrue(solution.validation.valid)

    def test_ranking_orders_valid_solutions_without_changing_validity(self):
        cf = [0, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=18,
            max_solutions=3,
        )
        ranked = search_second_species(cf, cfg)
        self.assertGreaterEqual(len(ranked.solutions), 2)
        scores = [s.score.total_score for s in ranked.solutions]
        self.assertGreaterEqual(scores[0], scores[1])
        for solution in ranked.solutions[:2]:
            report = validate_second_species(cf, solution.cp, cfg)
            self.assertTrue(report.valid)
            breakdown = rank_second_species_solution(cf, solution.cp, cfg)
            self.assertIsInstance(breakdown.total_score, float)

    def test_max_solutions_truncates_output_not_exploration(self):
        cf = [0, 2, 0]
        cfg_all = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=18,
            max_solutions=None,
        )
        cfg_one = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=18,
            max_solutions=1,
        )
        all_results = search_second_species(cf, cfg_all)
        one_result = search_second_species(cf, cfg_one)
        self.assertEqual(all_results.explored_candidates, one_result.explored_candidates)
        self.assertEqual(all_results.valid_candidates, one_result.valid_candidates)
        self.assertLessEqual(len(one_result.solutions), 1)
        self.assertGreaterEqual(len(all_results.solutions), len(one_result.solutions))

    def test_search_final_interval_is_perfect_for_both_dispositions(self):
        cf = [0, 2, 4, 2]
        for cfg in (
            SpeciesEngineConfig(
                cp_disposition=CPDisposition.ABOVE,
                cp_range_min=5,
                cp_range_max=18,
                max_solutions=3,
            ),
            SpeciesEngineConfig(
                cp_disposition=CPDisposition.BELOW,
                cp_range_min=-8,
                cp_range_max=6,
                max_solutions=2,
            ),
        ):
            ranked = search_second_species(cf, cfg)
            self.assertGreater(len(ranked.solutions), 0)
            for solution in ranked.solutions:
                final_note = solution.cp.measures[-1].beat1
                self.assertIsNotNone(final_note)
                iv = interval_label(final_note, cf[-1])
                self.assertIn(iv, {"P1", "P8"})


class TestSecondSpeciesDPSolver(unittest.TestCase):
    def test_dp_valid_count_matches_bruteforce_validator_on_small_case(self):
        cf = [0, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            search_mode=SearchMode.EXHAUSTIVE,
            cp_range_min=5,
            cp_range_max=12,
            max_solutions=None,
        )
        ranked = search_second_species(cf, cfg)

        pitch_space = [p for p in range(cfg.cp_range_min, cfg.cp_range_max + 1) if is_white_note(p)]
        brute_valid = 0
        for s1, w1, s2, w2, sf in product(pitch_space, repeat=5):
            cp = [
                {"beat1": s1, "beat2": w1},
                {"beat1": s2, "beat2": w2},
                {"beat1": sf, "beat2": sf},
            ]
            if validate_second_species(cf, cp, cfg).valid:
                brute_valid += 1

        self.assertEqual(ranked.valid_candidates, brute_valid)
        self.assertEqual(len(ranked.solutions), brute_valid)

    def test_dp_candidates_stay_equivalent_to_validator(self):
        cf = [0, 2, 4, 5, 4]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=20,
            max_solutions=5,
        )
        ranked = search_second_species(cf, cfg)
        self.assertGreater(len(ranked.solutions), 0)
        for solution in ranked.solutions:
            self.assertTrue(solution.validation.valid)
            report = validate_second_species(cf, solution.cp, cfg)
            self.assertTrue(report.valid)

    def test_dp_solves_length_11_interactive_budget(self):
        cf = [0, 2, 4, 5, 7, 5, 4, 2, 4, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=22,
            max_solutions=1,
        )
        ranked = search_second_species(cf, cfg)
        self.assertGreaterEqual(len(ranked.solutions), 1)
        self.assertEqual(len(ranked.solutions[0].cp.measures), 11)
        self.assertGreater(ranked.valid_candidates, 0)

    def test_dp_length_11_has_valid_cadence(self):
        cf = [0, 2, 4, 5, 7, 5, 4, 2, 4, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=22,
            max_solutions=1,
        )
        ranked = search_second_species(cf, cfg)
        self.assertGreaterEqual(len(ranked.solutions), 1)
        cp_line = ranked.solutions[0].cp
        final_note = cp_line.measures[-1].beat1
        prev_attack = cp_line.measures[-2].beat2
        self.assertIsNotNone(final_note)
        self.assertIsNotNone(prev_attack)
        self.assertIn(interval_label(final_note, cf[-1]), {"P1", "P8"})
        self.assertTrue(is_step(prev_attack, final_note))
        required = cadential_subtonic_distance(cf[-1])
        self.assertEqual(prev_attack, final_note - required)

    def test_dp_length_11_has_no_parallel_errors(self):
        cf = [0, 2, 4, 5, 7, 5, 4, 2, 4, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=22,
            max_solutions=1,
        )
        ranked = search_second_species(cf, cfg)
        self.assertGreaterEqual(len(ranked.solutions), 1)
        report = validate_second_species(cf, ranked.solutions[0].cp, cfg)
        codes = _codes(report)
        self.assertNotIn("adjacent_perfect_parallel", codes)
        self.assertNotIn("strong_support_perfect_parallel", codes)


if __name__ == "__main__":
    unittest.main()
