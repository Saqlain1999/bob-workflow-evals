"""Integration checks for the offline helper, separate from fixture tests."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate.py"
FIXTURE = ROOT / "fixtures" / "tiny-ledger"


class EvaluationHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="bob-eval-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.workspace = self.directory / "candidate"

    def invoke(self, *arguments: str) -> subprocess.CompletedProcess:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *map(str, arguments)],
            cwd=str(ROOT), env=environment, text=True, capture_output=True,
            timeout=10, check=False,
        )

    def copy_fixture(self) -> None:
        shutil.copytree(FIXTURE, self.workspace)

    def test_prepare_copies_fixture_and_refuses_overwrite(self) -> None:
        first = self.invoke("prepare", "--output", self.workspace)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(
            (self.workspace / "ledger.py").read_bytes(),
            (FIXTURE / "ledger.py").read_bytes(),
        )
        marker = self.workspace / "my-work.txt"
        marker.write_text("preserve this", encoding="utf-8")
        second = self.invoke("prepare", "--output", self.workspace)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve this")

    def test_prepare_refuses_a_directory_inside_original_fixture(self) -> None:
        destination = FIXTURE / "must-not-be-created"
        self.assertFalse(destination.exists())
        result = self.invoke("prepare", "--output", destination)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(destination.exists())

    def test_baseline_confirms_known_failure_and_writes_report(self) -> None:
        self.copy_fixture()
        destination = self.directory / "baseline.json"
        result = self.invoke(
            "baseline", "--workspace", self.workspace, "--result", destination
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "expected_baseline_failure")
        self.assertEqual(report["tests"]["tests_run"], 9)
        self.assertEqual(len(report["tests"]["failures"]), 1)
        self.assertEqual(report["tests"]["errors"], [])
        self.assertEqual(report["manual_acceptance"], "not_assessed")
        self.assertEqual(report["model_calls_made_by_helper"], 0)

    def test_faulty_candidate_fails_public_checks(self) -> None:
        self.copy_fixture()
        result = self.invoke("candidate", "--workspace", self.workspace)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "public_tests_failed")
        self.assertIn("FAIL:", report["tests"]["output"])

    def test_focused_repair_passes_but_does_not_claim_manual_acceptance(self) -> None:
        self.copy_fixture()
        source = self.workspace / "ledger.py"
        text = source.read_text(encoding="utf-8")
        old = (
            "        self._balances[source] = source_balance - cents\n"
            "        destination_balance = self.balance(destination)\n"
        )
        new = (
            "        destination_balance = self.balance(destination)\n"
            "        self._balances[source] = source_balance - cents\n"
        )
        self.assertEqual(text.count(old), 1)
        source.write_text(text.replace(old, new), encoding="utf-8")
        candidate = self.invoke("candidate", "--workspace", self.workspace)
        self.assertEqual(candidate.returncode, 0, candidate.stderr)
        report = json.loads(candidate.stdout)
        self.assertEqual(report["status"], "public_tests_passed")
        self.assertEqual(report["tests"]["tests_run"], 9)
        self.assertEqual(report["tests"]["failures"], [])
        self.assertFalse(report["fingerprints"]["source_matches_original"])
        self.assertTrue(report["fingerprints"]["workspace_tests_match_original"])
        self.assertEqual(report["manual_acceptance"], "not_assessed")
        baseline = self.invoke("baseline", "--workspace", self.workspace)
        self.assertEqual(baseline.returncode, 1)
        self.assertEqual(json.loads(baseline.stdout)["status"], "unexpected_baseline")
        self.assertIn(old, (FIXTURE / "ledger.py").read_text(encoding="utf-8"))

    def test_weakened_workspace_tests_do_not_hide_the_bug(self) -> None:
        self.copy_fixture()
        tests = self.workspace / "tests" / "test_ledger.py"
        tests.write_text("# Removed by the candidate\n", encoding="utf-8")
        result = self.invoke("candidate", "--workspace", self.workspace)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["tests"]["tests_run"], 9)
        self.assertEqual(len(report["tests"]["failures"]), 1)
        self.assertFalse(report["fingerprints"]["workspace_tests_match_original"])

    def test_result_file_is_never_overwritten(self) -> None:
        self.copy_fixture()
        destination = self.directory / "existing.json"
        destination.write_text("keep prior evidence", encoding="utf-8")
        result = self.invoke(
            "baseline", "--workspace", self.workspace, "--result", destination
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(destination.read_text(encoding="utf-8"), "keep prior evidence")

    def test_timeout_reports_execution_problem_not_a_test_pass(self) -> None:
        self.copy_fixture()
        source = self.workspace / "ledger.py"
        source.write_text("while True:\n    pass\n", encoding="utf-8")
        result = self.invoke(
            "candidate", "--workspace", self.workspace, "--timeout", "0.5"
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "runner_error")
        self.assertIsNone(report["tests"])
        self.assertIn("timeout", report["error"])

    def test_invalid_timeout_does_not_disable_the_execution_bound(self) -> None:
        self.copy_fixture()
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(timeout=value):
                result = self.invoke(
                    "candidate", "--workspace", self.workspace, "--timeout", value
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("finite and positive", result.stderr)


if __name__ == "__main__":
    unittest.main()
