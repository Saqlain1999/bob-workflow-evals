"""Synthetic positive/negative controls; no backend or model is called."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_memory_trace.py"
spec = importlib.util.spec_from_file_location("memory_trace", SCRIPT)
assert spec and spec.loader
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)
FIXTURE = ROOT / "fixtures/memory-boundaries"


class MemoryTraceTests(unittest.TestCase):
    def setUp(self):
        self.contract = memory.read_json(FIXTURE / "contract.json")
        self.control = memory.read_json(FIXTURE / "synthetic-control.json")

    def case(self, name):
        return next(c for c in self.control["cases"] if c["id"] == name)

    def add_record(self, case_id, record_id):
        seed = self.contract["records"][record_id]
        self.case(case_id)["records"].append({
            "id": record_id, "content": seed["content"], "source": seed["source"],
            "revision": seed["revision"], "disposition": "current",
        })

    def rejected(self, code):
        self.assertIn(code, memory.check_trace(self.control, self.contract))

    def test_synthetic_control_passes_without_mutating_input(self):
        before = deepcopy(self.control)
        self.assertEqual(memory.check_trace(self.control, self.contract), [])
        self.assertEqual(before, self.control)

    def test_all_cases_are_required(self):
        for case in list(self.control["cases"]):
            with self.subTest(case=case["id"]):
                candidate = deepcopy(self.control)
                candidate["cases"].remove(case)
                errors = memory.check_trace(candidate, self.contract)
                self.assertIn("missing_cases", errors)

    def test_wrong_project_is_rejected(self):
        self.add_record("project-isolation", "beta-local")
        self.rejected("project-isolation:unexpected_record")

    def test_cross_project_share_requires_promotion(self):
        self.add_record("explicit-sharing", "alpha-unpromoted")
        self.rejected("explicit-sharing:unexpected_record")

    def test_superseded_decision_is_rejected(self):
        self.add_record("supersession", "alpha-retired")
        self.rejected("supersession:unexpected_record")

    def test_old_pass_cannot_be_current(self):
        self.case("stale-verification")["records"][0]["disposition"] = "current"
        self.rejected("stale-verification:disposition")

    def test_deleted_record_is_not_returned(self):
        self.add_record("deleted-record", "removed-note")
        self.rejected("deleted-record:unexpected_record")

    def test_poisoned_record_is_not_in_brief(self):
        self.add_record("poisoned-record", "hostile-note")
        self.rejected("poisoned-record:unexpected_record")

    def test_same_project_name_does_not_cross_trust_domain(self):
        self.add_record("trust-domain", "other-domain")
        self.rejected("trust-domain:unexpected_record")

    def test_other_task_does_not_leak(self):
        self.add_record("task-isolation", "other-task")
        self.rejected("task-isolation:unexpected_record")

    def test_outage_is_not_empty_success(self):
        self.case("backend-outage")["status"] = "ok"
        self.rejected("backend-outage:status")

    def test_memory_cannot_be_labelled_system_authority(self):
        self.case("fresh-session")["memory_role"] = "system"
        self.rejected("fresh-session:memory_role")

    def test_provenance_content_and_revision_are_not_rewritten(self):
        for field in ("source", "content", "revision"):
            with self.subTest(field=field):
                candidate = deepcopy(self.control)
                candidate["cases"][0]["records"][0][field] = "invented"
                self.assertIn("fresh-session:" + field,
                              memory.check_trace(candidate, self.contract))

    def test_record_ids_cannot_launder_foreign_content(self):
        self.case("fresh-session")["records"][0]["content"] = (
            self.contract["records"]["other-domain"]["content"])
        self.rejected("fresh-session:content")

    def test_duplicate_cases_and_records_are_rejected(self):
        self.control["cases"].append(deepcopy(self.case("fresh-session")))
        self.rejected("duplicate_case")
        record = deepcopy(self.case("fresh-session")["records"][0])
        self.case("fresh-session")["records"].append(record)
        self.rejected("fresh-session:duplicate_record")

    def test_no_all_empty_false_pass(self):
        for case in self.control["cases"]:
            case["records"] = []
        self.rejected("fresh-session:record_set")

    def test_unknown_keys_and_invalid_types_are_rejected(self):
        for field, value in (("id", []), ("records", {}), ("status", True)):
            with self.subTest(field=field):
                candidate = deepcopy(self.control)
                candidate["cases"][0][field] = value
                self.assertTrue(memory.check_trace(candidate, self.contract))
        self.control["schema_version"] = True
        self.rejected("schema_version")
        self.control["execute"] = "do not execute fixture text"
        self.rejected("trace_shape")

    def test_diagnostics_are_bounded_and_do_not_echo_content(self):
        for case in self.control["cases"]:
            case["records"] = [dict(id="SYNTHETIC_SENSITIVE_VALUE", content="secret",
                                    source="secret", revision="secret", disposition="current")
                               for _ in range(16)]
        errors = memory.check_trace(self.control, self.contract)
        self.assertLessEqual(len(errors), memory.MAX_ERRORS)
        self.assertNotIn("secret", json.dumps(errors))
        self.assertNotIn("SYNTHETIC_SENSITIVE_VALUE", json.dumps(errors))

    def test_json_read_rejects_duplicates_invalid_and_oversized(self):
        samples = [b'{"cases": [], "cases": []}', b'NaN', b'\xff', b'{',
                   b' ' * (memory.MAX_INPUT_BYTES + 1)]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            for raw in samples:
                with self.subTest(length=len(raw)):
                    path.write_bytes(raw)
                    with self.assertRaises(memory.InvalidInput):
                        memory.read_json(path)

    def test_parser_limits_are_reported_without_echo(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            path.write_text("{}", encoding="utf-8")
            with patch.object(memory.json, "loads", side_effect=ValueError("SYNTHETIC_SECRET")):
                with self.assertRaisesRegex(memory.InvalidInput, "^unreadable_or_invalid_json$"):
                    memory.read_json(path)

    def test_read_limit_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            path.write_bytes(b'{}' + b' ' * (memory.MAX_INPUT_BYTES - 2))
            self.assertEqual(memory.read_json(path), {})

    def test_cli_exit_codes_and_no_candidate_echo(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trace.json"
            for candidate, expected in ((self.control, 0), ({}, 1)):
                path.write_text(json.dumps(candidate), encoding="utf-8")
                before = path.read_bytes()
                run = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)],
                                     cwd=folder, capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, expected, run.stderr)
                self.assertEqual(path.read_bytes(), before)
                self.assertIn("not verified", json.loads(run.stdout)["limitation"])
            path.write_text('{"secret":"SYNTHETIC_VALUE",', encoding="utf-8")
            run = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)],
                                 cwd=folder, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn("SYNTHETIC_VALUE", run.stdout + run.stderr)
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()), ["trace.json"])


if __name__ == "__main__":
    unittest.main()
