"""Static and non-mutating controls for the pinned Engram qualification gate."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "qualifications" / "engram-v3.7.2" / "profile.json"
SCRIPT = ROOT / "scripts" / "preview_engram.py"
EXPECTED_COMMIT = "c6ba9e3c0e98ffa0d5591481d8670a575e7b70b0"
EXPECTED_SHA256 = "8db9d5db1c1574b8b830aac4ffbe86c024014aed6b9a3f0406ac3361a152cdf0"


class EngramQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        self.temporary = tempfile.TemporaryDirectory(prefix="engram-preview-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.project = root / "project-alpha"
        self.project.mkdir()
        self.binary = root / "reviewed-bin" / "engram"

    def invoke(self, project: Path | str, binary: Path | str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--project", str(project), "--binary", str(binary)],
            cwd=str(ROOT), text=True, capture_output=True, timeout=10, check=False,
        )

    def test_source_pin_license_release_and_digest_are_exact(self) -> None:
        source = self.profile["source"]
        self.assertEqual(source["tag"], "v3.7.2")
        self.assertEqual(source["commit"], EXPECTED_COMMIT)
        self.assertEqual(source["license"], "MIT")
        self.assertEqual(source["release_published_utc"], "2026-11-14T00:26:08Z")
        self.assertEqual(source["security_support"], "latest_stable_only")
        self.assertEqual(source["runtime_basis"]["tag"], "v3.7.1")
        self.assertEqual(source["asset"]["sha256"], EXPECTED_SHA256)

    def test_post_release_project_error_fix_remains_an_explicit_gate(self) -> None:
        findings = self.profile["post_release_findings"]
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["commit"], "82900dc5c61e534f4f3282ff19c211bbff3d5cd5")
        self.assertFalse(finding["included_in_v3.7.2"])
        self.assertIn("unexpected MCP project-resolution failure", finding["finding"])
        self.assertIn("independent proof of actual ambiguity", finding["gate"])
        self.assertTrue(any("not independently proven" in item for item in self.profile["stop_conditions"]))

    def test_every_backend_neutral_behavior_has_one_honest_mapping(self) -> None:
        contract = json.loads(
            (ROOT / "fixtures" / "bob-project-memory" / "contract.json").read_text(encoding="utf-8")
        )
        mappings = self.profile["contract_mapping"]
        self.assertEqual([item["behavior"] for item in mappings], contract["required_behaviors"])
        self.assertEqual(len({item["behavior"] for item in mappings}), len(mappings))
        self.assertTrue(all(item["status"] != "qualified" for item in mappings))

    def test_revision_conflict_remains_blocked_but_deletion_requires_runtime(self) -> None:
        status = {item["behavior"]: item["status"] for item in self.profile["contract_mapping"]}
        self.assertEqual(status["revision conflict refusal"], "blocked")
        self.assertEqual(status["direct and indexed deletion"], "runtime_evidence_required")
        self.assertEqual(self.profile["decision"], "adapt_after_runtime_qualification")

    def test_preview_is_project_local_disabled_and_has_no_auto_approval(self) -> None:
        result = self.invoke(self.project, self.binary)
        self.assertEqual(result.returncode, 0, result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual(preview["configuration_path"], str(self.project / ".bob" / "mcp.json"))
        server = preview["configuration"]["mcpServers"]["engram"]
        self.assertEqual(server["command"], str(self.binary))
        self.assertEqual(
            server["args"],
            [
                "mcp",
                "--project",
                "project-alpha",
                "--tools=mem_current_project,mem_context,mem_search,mem_save,mem_update,mem_delete,mem_get_observation,mem_list_projects",
            ],
        )
        self.assertEqual(server["cwd"], str(self.project))
        self.assertEqual(
            server["env"],
            {
                "ENGRAM_DATA_DIR": str(self.project / ".engram-runtime"),
                "ENGRAM_NO_UPDATE_CHECK": "1",
                "ENGRAM_CLOUD_AUTOSYNC": "0",
            },
        )
        self.assertTrue(server["disabled"])
        self.assertEqual(server["alwaysAllow"], [])
        self.assertNotIn("url", server)

    def test_preview_emits_read_only_project_discovery_first(self) -> None:
        result = self.invoke(self.project, self.binary)
        preview = json.loads(result.stdout)
        self.assertEqual(
            preview["first_tool_call"],
            {"server": "engram", "tool": "mem_current_project", "arguments": {}},
        )

    def test_preview_does_not_write_or_start_a_process(self) -> None:
        before = sorted(path.relative_to(Path(self.temporary.name)) for path in Path(self.temporary.name).rglob("*"))
        result = self.invoke(self.project, self.binary)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = sorted(path.relative_to(Path(self.temporary.name)) for path in Path(self.temporary.name).rglob("*"))
        self.assertEqual(after, before)
        preview = json.loads(result.stdout)
        self.assertFalse(preview["writes_performed"])
        self.assertFalse(preview["processes_started"])
        self.assertFalse(self.binary.exists())

    def test_relative_project_or_binary_is_rejected(self) -> None:
        relative_project = self.invoke("relative-project", self.binary)
        self.assertEqual(relative_project.returncode, 2)
        self.assertIn("project must be an absolute path", relative_project.stderr)
        relative_binary = self.invoke(self.project, "engram-alpha")
        self.assertEqual(relative_binary.returncode, 2)
        self.assertIn("binary must be an absolute path", relative_binary.stderr)

    def test_first_trial_excludes_unsafe_or_unreviewed_modes(self) -> None:
        prohibited = "\n".join(self.profile["bob_trial_contract"]["prohibited_first_trial"])
        for expected in ("global Bob", "setup", "transcript", "hook", "HTTP", "cloud", "private", "non-interactive", "paid"):
            self.assertIn(expected, prohibited)
        prerequisites = "\n".join(self.profile["bob_trial_contract"]["prerequisites"])
        self.assertIn("explicitly trusted", prerequisites)
        self.assertIn("network activity observed", prerequisites)

    def test_current_runtime_and_removal_side_effects_are_not_hidden(self) -> None:
        effects = "\n".join(self.profile["runtime_side_effects_to_observe"])
        for expected in ("SQLite", "STDIO", "initialization instructions", "network", "project resolution", "hard deletion", "removal"):
            self.assertIn(expected, effects)

    def test_alpha_cli_and_tool_contract_is_not_reused(self) -> None:
        contract_text = json.dumps(self.profile["bob_trial_contract"])
        self.assertNotIn("--db", contract_text)
        self.assertNotIn('"brief"', contract_text)
        self.assertEqual(self.profile["supersedes"], "engram-alpha-v0.11.0-source-gate")


if __name__ == "__main__":
    unittest.main()
