import os
import sys
import unittest
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.species.config import CPDisposition, SpeciesEngineConfig
from src.species.engine import (
    rank_third_species_solution,
    search_third_species,
    validate_third_species,
)
from src.species.music_core import cadential_subtonic_distance, is_white_note, same_diatonic_pitch
from src.species.plans import build_temporal_grid_third


CF4 = [0, 2, 4, 2]
VALID_CP_THIRD = [
    {"beat1": 7, "beat2": 9, "beat3": 12, "beat4": 11},
    {"beat1": 9, "beat2": 7, "beat3": 9, "beat4": 11},
    {"beat1": 7, "beat2": 9, "beat3": 11, "beat4": 13},
    {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
]
VALID_CP_THIRD_PASSING_LOWER = [
    {"beat1": 12, "beat2": 14, "beat3": 16, "beat4": 9},
    {"beat1": 11, "beat2": 9, "beat3": 14, "beat4": 12},
    {"beat1": 11, "beat2": 9, "beat3": 11, "beat4": 13},
    {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
]
CF3 = [0, 2, 0]
VALID_CP_THIRD_CAMBIATA = [
    {"beat1": 12, "beat2": 11, "beat3": 7, "beat4": 9},
    {"beat1": 17, "beat2": 16, "beat3": 14, "beat4": 12},
    {"beat1": 11, "beat2": 9, "beat3": 11, "beat4": 13},
    {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
]
VALID_CP_THIRD_REST_OPENING = [
    {"beat1": None, "beat2": 7, "beat3": 12, "beat4": 11},
    {"beat1": 9, "beat2": 7, "beat3": 9, "beat4": 11},
    {"beat1": 7, "beat2": 9, "beat3": 11, "beat4": 13},
    {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
]
VALID_CP_THIRD_WEAK_UNISON = [
    {"beat1": 12, "beat2": 14, "beat3": 16, "beat4": 4},
    {"beat1": 5, "beat2": 2, "beat3": 14, "beat4": 12},
    {"beat1": 11, "beat2": 9, "beat3": 11, "beat4": 13},
    {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
]


def _codes(report):
    return {e.code for e in report.errors}


class TestThirdSpeciesUnit(unittest.TestCase):
    def test_grid_is_4n_minus_3(self):
        grid = build_temporal_grid_third(CF4)
        self.assertEqual(grid.total_slots, 4 * len(CF4) - 3)
        self.assertTrue(grid.slots[-1].is_final)
        self.assertEqual(grid.slots[-1].beat, 1)

    def test_valid_line_with_passing_and_lower_neighbor(self):
        report = validate_third_species(
            CF4,
            VALID_CP_THIRD_PASSING_LOWER,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid, msg=report.errors)

    def test_valid_line_with_cambiata(self):
        report = validate_third_species(
            CF4,
            VALID_CP_THIRD_CAMBIATA,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid, msg=report.errors)

    def test_almost_cambiata_is_rejected(self):
        cp = deepcopy(VALID_CP_THIRD_CAMBIATA)
        cp[0]["beat4"] = 8
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("weak_dissonance_figure_invalid", _codes(report))

    def test_quarter_rest_opening_supported(self):
        report = validate_third_species(
            CF4,
            VALID_CP_THIRD_REST_OPENING,
            SpeciesEngineConfig(
                cp_disposition=CPDisposition.ABOVE,
                allow_half_rest_start=True,
            ),
        )
        self.assertTrue(report.valid, msg=report.errors)

    def test_interior_beat1_unison_rejected(self):
        cp = deepcopy(VALID_CP_THIRD)
        cp[1]["beat1"] = 2
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("interior_beat1_unison_forbidden", _codes(report))

    def test_non_initial_quarter_unison_allowed(self):
        report = validate_third_species(
            CF4,
            VALID_CP_THIRD_WEAK_UNISON,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid, msg=report.errors)

    def test_trivial_beat2_beat4_repetition_rejected(self):
        cp = deepcopy(VALID_CP_THIRD)
        cp[1]["beat4"] = cp[1]["beat2"]
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("trivial_weak_repetition_forbidden", _codes(report))

    def test_same_lower_neighbor_twice_is_rejected(self):
        cf = [0, 0, 2, 0]
        cp = [
            {"beat1": 12, "beat2": 9, "beat3": 12, "beat4": 11},
            {"beat1": 12, "beat2": 11, "beat3": 12, "beat4": 7},
            {"beat1": 9, "beat2": 7, "beat3": 9, "beat4": 11},
            {"beat1": 12, "beat2": None, "beat3": None, "beat4": None},
        ]
        report = validate_third_species(
            cf,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("consecutive_lower_neighbor_reuse_forbidden", _codes(report))

    def test_nontrivial_reiteration_remains_valid_and_is_ranked(self):
        report = validate_third_species(
            CF4,
            VALID_CP_THIRD_PASSING_LOWER,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid)
        breakdown = rank_third_species_solution(
            CF4,
            VALID_CP_THIRD_PASSING_LOWER,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("nontrivial_reiteration_penalty", breakdown.contributions)
        self.assertLessEqual(breakdown.contributions["nontrivial_reiteration_penalty"], 0.0)

    def test_accented_leap_must_descend(self):
        cp = deepcopy(VALID_CP_THIRD)
        cp[0]["beat4"] = 16
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("accented_leap_must_descend", _codes(report))

    def test_descending_weak_leap_requires_controlled_exception(self):
        cp = deepcopy(VALID_CP_THIRD)
        cp[1]["beat2"] = 14
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("weak_leap_direction_forbidden", _codes(report))

    def test_three_identical_perfect_supports_rejected(self):
        cp = deepcopy(VALID_CP_THIRD)
        cp[0]["beat1"] = 12
        cp[1]["beat1"] = 14
        cp[2]["beat1"] = 16
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("identical_perfect_support_streak_forbidden", _codes(report))

    def test_restricted_preceding_perfects_rejected(self):
        cp = deepcopy(VALID_CP_THIRD)
        cp[0]["beat4"] = 7
        cp[1]["beat1"] = 9
        report = validate_third_species(
            CF4,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("perfect_support_entry_prepared_by_same_perfect_forbidden", _codes(report))

    def test_modal_note_outside_cadential_slot_is_rejected(self):
        cf = [2, 4, 5, 2]
        cp = [
            {"beat1": 9, "beat2": 7, "beat3": 9, "beat4": 11},
            {"beat1": 12, "beat2": 13, "beat3": 16, "beat4": 14},
            {"beat1": 13, "beat2": 12, "beat3": 14, "beat4": 13},
            {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
        ]
        report = validate_third_species(
            cf,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("note_outside_modal_scale", _codes(report))

    def test_cadential_chromatic_at_penultimate_beat4_is_allowed(self):
        cf = [2, 5, 2]
        cp = [
            {"beat1": 14, "beat2": 12, "beat3": 11, "beat4": 9},
            {"beat1": 14, "beat2": 12, "beat3": 14, "beat4": 13},
            {"beat1": 14, "beat2": None, "beat3": None, "beat4": None},
        ]
        report = validate_third_species(
            cf,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertTrue(report.valid, msg=report.errors)

    def test_cadential_same_diatonic_inflection_is_rejected(self):
        cf = [2, 4, 2]
        cp = [
            {"beat1": 14, "beat2": 12, "beat3": 11, "beat4": 9},
            {"beat1": 19, "beat2": 17, "beat3": 24, "beat4": 25},
            {"beat1": 26, "beat2": None, "beat3": None, "beat4": None},
        ]
        report = validate_third_species(
            cf,
            cp,
            SpeciesEngineConfig(cp_disposition=CPDisposition.ABOVE),
        )
        self.assertIn("cadential_chromatic_inflection_forbidden", _codes(report))


class TestThirdSpeciesSearch(unittest.TestCase):
    def test_search_returns_only_valid_lines(self):
        cf = [0, 2, 0]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=7,
            cp_range_max=16,
            max_solutions=2,
        )
        ranked = search_third_species(cf, cfg)
        self.assertGreater(len(ranked.solutions), 0)
        for solution in ranked.solutions:
            self.assertTrue(solution.validation.valid)

    def test_search_keeps_non_modal_pitch_only_in_cadential_slot(self):
        cf = [2, 4, 5, 2]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=7,
            cp_range_max=19,
            max_solutions=8,
        )
        ranked = search_third_species(cf, cfg)
        self.assertGreater(len(ranked.solutions), 0)
        allowed_measure = len(cf) - 1
        for solution in ranked.solutions:
            final = solution.cp.measures[-1].beat1
            self.assertIsNotNone(final)
            allowed_pitch = final - cadential_subtonic_distance(cf[-1])
            for measure_index, measure in enumerate(solution.cp.measures, start=1):
                beats = [measure.beat1, measure.beat2, measure.beat3, measure.beat4]
                if measure_index == len(solution.cp.measures):
                    beats = [measure.beat1]
                for beat_index, note in enumerate(beats, start=1):
                    if note is None or is_white_note(note):
                        continue
                    self.assertEqual(measure_index, allowed_measure)
                    self.assertEqual(beat_index, 4)
                    self.assertEqual(note, allowed_pitch)

    def test_search_solves_length_11_interactive_budget(self):
        cf = [2, 4, 2, 5, 4, 9, 2, 4, 5, 4, 2]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=28,
            max_solutions=1,
        )
        ranked = search_third_species(cf, cfg)
        self.assertGreaterEqual(len(ranked.solutions), 1)
        self.assertEqual(len(ranked.solutions[0].cp.measures), 11)
        self.assertGreater(ranked.valid_candidates, 0)
        self.assertLessEqual(ranked.explored_candidates, 64)

    def test_search_avoids_same_diatonic_before_cadential_chromatic(self):
        cf = [2, 4, 2, 5, 4, 9, 2, 4, 5, 4, 2]
        cfg = SpeciesEngineConfig(
            cp_disposition=CPDisposition.ABOVE,
            cp_range_min=5,
            cp_range_max=28,
            max_solutions=3,
        )
        ranked = search_third_species(cf, cfg)
        self.assertGreaterEqual(len(ranked.solutions), 1)
        for solution in ranked.solutions:
            final_note = solution.cp.measures[-1].beat1
            self.assertIsNotNone(final_note)
            penultimate = solution.cp.measures[-2]
            if penultimate.beat4 is None or is_white_note(penultimate.beat4):
                continue
            self.assertFalse(same_diatonic_pitch(penultimate.beat3, penultimate.beat4))


if __name__ == "__main__":
    unittest.main()
