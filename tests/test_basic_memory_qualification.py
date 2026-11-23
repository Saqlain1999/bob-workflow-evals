"""Static and non-mutating controls for the pinned Basic Memory qualification gate."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "qualifications" / "basic-memory-v1.0.0" / "profile.json"
SCRIPT = ROOT / "scripts" / "preview_basic_memory.py"
EXPECTED_COMMIT = "c9bd187b83baba549d5cd16bacc180f8023d51c8"
EXPECTED_SHA256 = "a2d2c1589616c9599aec9edd6597d508028c5af88632312fc0990dcaccf02867"


class BasicMemoryQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        self.temporary = tempfile.TemporaryDirectory(prefix="basic-memory-preview-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.project = root / "project-alpha"
        self.project.mkdir()
        self.uvx = root / "reviewed-bin" / "uvx"
        self.wheel = root / "reviewed-assets" / "basic_memory-1.0.0-py3-none-any.whl"

    def invoke(self, project: Path | str, uvx: Path | str, wheel: Path | str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--project", str(project),
             "--uvx", str(uvx), "--wheel", str(wheel)],
            cwd=str(ROOT), text=True, capture_output=True, timeout=10, check=False,
        )

    def test_source_pin_license_release_and_digest_are_exact(self) -> None:
        source = self.profile["source"]
        self.assertEqual(source["tag"], "v1.0.0")
        self.assertEqual(source["commit"], EXPECTED_COMMIT)
        self.assertEqual(source["license"], "AGPL-3.0-or-later")
        self.assertEqual(source["python_requires"], ">=3.12")
        self.assertEqual(source["release_published_utc"], "2026-10-29T23:45:31Z")
        self.assertEqual(source["asset"]["sha256"], EXPECTED_SHA256)

    def test_every_backend_neutral_behavior_has_one_honest_mapping(self) -> None:
        contract = json.loads(
            (ROOT / "fixtures" / "bob-project-memory" / "contract.json").read_text(encoding="utf-8")
        )
        mappings = self.profile["contract_mapping"]
        self.assertEqual([item["behavior"] for item in mappings], contract["required_behaviors"])
        self.assertEqual(len({item["behavior"] for item in mappings}), len(mappings))
        self.assertTrue(all(item["status"] != "qualified" for item in mappings))

    def test_checksum_conflict_is_source_supported_but_not_qualified(self) -> None:
        mapping = {item["behavior"]: item for item in self.profile["contract_mapping"]}
        conflict = mapping["revision conflict refusal"]
        self.assertIn("expected_checksum", conflict["candidate_mechanism"])
        self.assertEqual(conflict["status"], "runtime_evidence_required")
        self.assertEqual(self.profile["decision"], "defer_pending_project_confinement")

    def test_project_separation_is_blocked_by_exact_source(self) -> None:
        source = self.profile["source"]
        reviewed = source["reviewed_paths"]
        for expected in (
            "src/basic_memory/services/context_service.py",
            "src/basic_memory/api/v2/utils.py",
            "tests/services/test_context_service.py",
        ):
            self.assertIn(expected, reviewed)

        notes = "\n".join(source["source_notes"])
        self.assertIn("connected-entity project filter empty", notes)
        self.assertIn("include_cross_project=true", notes)
        self.assertIn("506305b856967da1799f530502b6d9b7e6bd9610", notes)
        self.assertIn("enabled by default for local use", notes)

        mapping = {item["behavior"]: item for item in self.profile["contract_mapping"]}
        separation = mapping["project separation"]
        self.assertEqual(separation["status"], "blocked_by_source")
        self.assertIn("explicit relations traverse", separation["candidate_mechanism"])

        gate = self.profile["project_separation_gate"]
        self.assertEqual(gate["state"], "blocked_by_source")
        self.assertEqual(gate["finding_commit"], "506305b856967da1799f530502b6d9b7e6bd9610")
        self.assertEqual(gate["finding_event_utc"], "2026-11-22T05:45:59Z")
        acceptance = "\n".join(gate["acceptance_criteria"])
        for expected in ("title", "path", "external ID", "child graph link", "body", "local STDIO MCP"):
            self.assertIn(expected, acceptance)
        self.assertIn("alpha-authored relation label", acceptance)
        resolutions = "\n".join(gate["acceptable_resolution"])
        self.assertIn("stable release", resolutions)
        self.assertIn("project-confined wrapper", resolutions)

    def test_preview_is_project_local_disabled_and_has_no_auto_approval(self) -> None:
        result = self.invoke(self.project, self.uvx, self.wheel)
        self.assertEqual(result.returncode, 0, result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual(preview["configuration_path"], str(self.project / ".bob" / "mcp.json"))
        server = preview["configuration"]["mcpServers"]["basic-memory-v1"]
        self.assertEqual(server["command"], str(self.uvx))
        self.assertEqual(server["args"], ["--from", str(self.wheel), "basic-memory", "mcp", "--project", "project-alpha"])
        self.assertEqual(server["cwd"], str(self.project))
        self.assertTrue(server["disabled"])
        self.assertEqual(server["alwaysAllow"], [])
        self.assertNotIn("url", server)

    def test_preview_isolates_state_and_disables_cloud_telemetry_and_updates(self) -> None:
        result = self.invoke(self.project, self.uvx, self.wheel)
        preview = json.loads(result.stdout)
        server = preview["configuration"]["mcpServers"]["basic-memory-v1"]
        environment = server["env"]
        self.assertEqual(environment["BASIC_MEMORY_CONFIG_DIR"], str(self.project / ".basic-memory-state"))
        self.assertEqual(environment["BASIC_MEMORY_FORCE_LOCAL"], "true")
        self.assertEqual(environment["BASIC_MEMORY_CLOUD_MODE"], "false")
        self.assertEqual(environment["BASIC_MEMORY_NO_PROMOS"], "1")
        self.assertEqual(environment["BASIC_MEMORY_LOGFIRE_SEND_TO_LOGFIRE"], "false")
        self.assertEqual(environment["BASIC_MEMORY_AUTO_UPDATE"], "false")
        self.assertEqual(environment["BASIC_MEMORY_ENABLE_PROJECT_DELETE"], "false")
        config = preview["basic_memory_config"]
        self.assertEqual(config["projects"], {"project-alpha": {"path": str(self.project), "mode": "local"}})
        self.assertIsNone(config["default_project"])
        self.assertEqual(config["project_root"], str(self.project.parent))
        self.assertEqual(config["default_search_type"], "text")
        self.assertFalse(config["logfire_send_to_logfire"])
        self.assertFalse(config["auto_update"])

    def test_preview_emits_read_only_project_inventory_first(self) -> None:
        result = self.invoke(self.project, self.uvx, self.wheel)
        preview = json.loads(result.stdout)
        self.assertEqual(preview["first_tool_call"], {
            "server": "basic-memory-v1", "tool": "bm_project", "arguments": {"command": "list"}
        })

    def test_preview_does_not_write_or_start_a_process(self) -> None:
        root = Path(self.temporary.name)
        before = sorted(path.relative_to(root) for path in root.rglob("*"))
        result = self.invoke(self.project, self.uvx, self.wheel)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = sorted(path.relative_to(root) for path in root.rglob("*"))
        self.assertEqual(after, before)
        preview = json.loads(result.stdout)
        self.assertFalse(preview["writes_performed"])
        self.assertFalse(preview["processes_started"])
        self.assertFalse(self.uvx.exists())
        self.assertFalse(self.wheel.exists())

    def test_relative_inputs_are_rejected(self) -> None:
        for label, project, uvx, wheel in (
            ("project", "relative-project", self.uvx, self.wheel),
            ("uvx", self.project, "uvx", self.wheel),
            ("wheel", self.project, self.uvx, "basic-memory.whl"),
        ):
            with self.subTest(label=label):
                result = self.invoke(project, uvx, wheel)
                self.assertEqual(result.returncode, 2)
                self.assertIn(f"{label} must be an absolute path", result.stderr)

    def test_first_trial_excludes_unreviewed_or_high_risk_modes(self) -> None:
        prohibited = "\n".join(self.profile["bob_trial_contract"]["prohibited_first_trial"])
        for expected in ("global", "unversioned", "cloud", "HTTP", "automatic", "transcript", "private", "paid"):
            self.assertIn(expected, prohibited)
        prerequisites = "\n".join(self.profile["bob_trial_contract"]["prerequisites"])
        self.assertIn("Python 3.12", prerequisites)
        self.assertIn("digest independently verified", prerequisites)
        self.assertIn("project folder explicitly trusted", prerequisites)
        self.assertIn("project-confinement layer", prerequisites)
        self.assertIn("build_context", prohibited)

    def test_dependency_and_deletion_side_effects_are_not_hidden(self) -> None:
        effects = "\n".join(self.profile["runtime_side_effects_to_observe"])
        for expected in ("dependency", "network", "SQLite", "FastEmbed", "checksum", "interrupted", "delete", "removal"):
            self.assertIn(expected, effects)
        notes = "\n".join(self.profile["source"]["source_notes"])
        self.assertIn("unpinned", notes)
        self.assertIn("0.x.x", notes)
        self.assertIn("3e8a519fa0ff406d98321af160080b74d8230c51", notes)
        self.assertIn("ignoring explicit local routing", notes)
        prerequisites = "\n".join(self.profile["bob_trial_contract"]["prerequisites"])
        self.assertIn("no Basic Memory cloud credentials", prerequisites)
        self.assertIn("network activity is observed", prerequisites)
        stop_conditions = "\n".join(self.profile["stop_conditions"])
        self.assertIn("cloud credentials", stop_conditions)
        self.assertIn("cloud discovery or any network request", stop_conditions)
        self.assertIn("project confinement is absent", stop_conditions)
        self.assertIn("project-beta title, path, external ID, child graph link or body", stop_conditions)


if __name__ == "__main__":
    unittest.main()
