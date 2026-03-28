import os
import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import generate_counterpoint as cli

from src.species.models import (
    RankedSolution,
    RankedSolutions,
    ScoreBreakdown,
    SecondSpeciesLine,
    SecondSpeciesMeasure,
    ValidationReport,
)


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "generate_counterpoint.py")


class TestGenerateCounterpointCLI(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_second_species_cli_with_explicit_cf(self):
        result = self.run_cli(
            "--species", "2",
            "--cf", "0,2,0",
            "--cp_disposition", "above",
            "--max_solutions", "1",
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Especie    : 2", result.stdout)
        self.assertIn("Compás | CF", result.stdout)
        self.assertIn("CP beat1", result.stdout)
        self.assertIn("CP beat2", result.stdout)
        self.assertIn("C0 (  0)", result.stdout)
        self.assertIn("D0 (  2)", result.stdout)
        self.assertIn("Soluciones válidas   : 1", result.stdout)

    def test_second_species_rejects_num_voices_other_than_two(self):
        result = self.run_cli(
            "--species", "2",
            "--cf", "0,2,4",
            "--num_voices", "3",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactamente 2 voces", result.stdout)


class TestSecondSpeciesAutoCFSelection(unittest.TestCase):
    def _ranked(self, score=None):
        solutions = []
        if score is not None:
            solutions.append(
                RankedSolution(
                    cp=SecondSpeciesLine(
                        measures=[
                            SecondSpeciesMeasure(beat1=7, beat2=9),
                            SecondSpeciesMeasure(beat1=5, beat2=5),
                        ]
                    ),
                    score=ScoreBreakdown(
                        total_score=score,
                        contributions={},
                        weights={},
                    ),
                    validation=ValidationReport(valid=True, errors=[]),
                )
            )
        return RankedSolutions(
            solutions=solutions,
            explored_candidates=10,
            valid_candidates=len(solutions),
        )

    def test_search_second_species_from_cli_returns_first_solvable_generated_cf(self):
        args = SimpleNamespace(
            cf="",
            cp_disposition="above",
            max_solutions=3,
            exhaustive_search=False,
            exhaustive_species=False,
        )
        candidates = [[0, 2, 4], [0, 4, 2], [0, 2, 5]]
        ranked_map = {
            tuple(candidates[0]): self._ranked(),
            tuple(candidates[1]): self._ranked(55.0),
            tuple(candidates[2]): self._ranked(91.5),
        }

        with patch.object(cli, "collect_cf_candidates", return_value=candidates):
            with patch.object(cli, "search_second_species", side_effect=lambda cf, config: ranked_map[tuple(cf)]):
                selected_cf, ranked, selected_index, candidate_count = cli.search_second_species_from_cli(args, cli.Notes.C)

        self.assertEqual(selected_cf, candidates[1])
        self.assertEqual(selected_index, 2)
        self.assertEqual(candidate_count, 3)
        self.assertEqual(ranked.solutions[0].score.total_score, 55.0)

    def test_collect_cf_candidates_retries_multiple_legacy_runs(self):
        args = SimpleNamespace(
            cf="",
            length=4,
            plagal=False,
            debug=False,
            sequential=False,
            exhaustive_search=False,
        )

        pools = iter([
            [[0, 7, 2, 0]],
            [[0, 7, 2, 0]],
            [[0, 5, 2, 0]],
        ])

        class FakeTreeSearch:
            def __init__(self, **kwargs):
                self.voices = [SimpleNamespace(pool=[SimpleNamespace(sequence=seq) for seq in next(pools)])]

            def generate_voices(self):
                return None

        with patch.object(cli, "SECOND_SPECIES_CF_ATTEMPTS", 3):
            with patch.object(cli, "SECOND_SPECIES_CF_CANDIDATES", 2):
                with patch.object(cli, "TreeSearch", FakeTreeSearch):
                    candidates = cli.collect_cf_candidates(args, cli.Notes.C)

        self.assertEqual(candidates, [[0, 7, 2, 0], [0, 5, 2, 0]])


class TestMuseScoreLaunch(unittest.TestCase):
    def test_open_in_musescore_uses_launchservices_on_macos(self):
        midi_path = "/tmp/example.mid"

        with patch.object(cli.sys, "platform", "darwin"):
            with patch.object(cli.os.path, "exists", side_effect=lambda p: p == "/Applications/MuseScore 4.app"):
                with patch.object(cli.subprocess, "Popen") as popen:
                    cli.open_in_musescore(midi_path)

        popen.assert_called_once_with(["open", "-a", "MuseScore 4", midi_path])


if __name__ == "__main__":
    unittest.main()
