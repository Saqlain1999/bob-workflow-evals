#!/usr/bin/env python3
"""Validate a project-memory runtime evidence record without executing a backend."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "qualifications" / "memory-runtime-trial-v1" / "protocol.json"


class RecordError(ValueError):
    """An evidence record is malformed or overclaims its evidence."""


def reject_duplicate_names(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting ambiguous repeated names."""
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise RecordError(f"duplicate object name: {key}")
        value[key] = item
    return value


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_names,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecordError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RecordError(f"{label} must be a JSON object")
    return value


def require_object(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise RecordError(f"{key} must be an object")
    return value


def require_exact_keys(value: dict[str, Any], label: str, expected: set[str]) -> None:
    """Reject missing, misspelled, or unreviewed evidence fields."""
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing or unknown:
        details: list[str] = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unknown:
            details.append(f"unknown {', '.join(unknown)}")
        raise RecordError(f"{label} has invalid fields: {'; '.join(details)}")


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def valid_utc_timestamp(value: Any) -> bool:
    """Accept an actual second-precision RFC 3339 UTC timestamp."""
    if not isinstance(value, str) or UTC_TIMESTAMP.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def validate_record(record: dict[str, Any], root: Path = ROOT) -> str:
    protocol = load_object(root / PROTOCOL_PATH.relative_to(ROOT), "runtime protocol")
    contract = load_object(root / protocol["contract_path"], "project-memory contract")

    require_exact_keys(record, "record", {
        "schema_version", "protocol_id", "run_id", "observed_at_utc", "backend_profile",
        "backend_qualification_id", "source", "authorization", "environment",
        "safeguards", "side_effects", "behaviors", "cleanup", "decision",
        "decision_rationale", "claims", "limitations",
    })

    if record.get("schema_version") != protocol["schema_version"]:
        raise RecordError("schema_version does not match the runtime protocol")
    if record.get("protocol_id") != protocol["protocol_id"]:
        raise RecordError("protocol_id does not match the runtime protocol")

    profile_rel = record.get("backend_profile")
    if profile_rel not in protocol["allowed_backend_profiles"]:
        raise RecordError("backend_profile is not an allowed pinned profile")
    profile = load_object(root / profile_rel, "backend profile")
    if record.get("backend_qualification_id") != profile.get("qualification_id"):
        raise RecordError("backend_qualification_id does not match the profile")
    execution_block = protocol["execution_blocked_profiles"].get(profile_rel)
    if execution_block is not None:
        if profile.get("decision") != execution_block["profile_decision"]:
            raise RecordError("execution-blocked profile decision does not match the runtime protocol")
        gate = require_object(profile, execution_block["gate"])
        if gate.get("state") != execution_block["gate_state"]:
            raise RecordError("execution-blocked profile gate does not match the runtime protocol")

    source = require_object(record, "source")
    require_exact_keys(source, "source", {
        "commit", "asset_sha256", "asset_digest_verified",
    })
    profile_source = require_object(profile, "source")
    profile_asset = require_object(profile_source, "asset")
    if source.get("commit") != profile_source.get("commit"):
        raise RecordError("source commit does not match the pinned profile")
    if source.get("asset_sha256") != profile_asset.get("sha256"):
        raise RecordError("asset digest does not match the pinned profile")
    if not isinstance(source.get("asset_digest_verified"), bool):
        raise RecordError("source.asset_digest_verified must be boolean")

    authorization = require_object(record, "authorization")
    require_exact_keys(authorization, "authorization", {
        "third_party_execution_authorized", "authorization_reference",
    })
    authorized = authorization.get("third_party_execution_authorized")
    if not isinstance(authorized, bool):
        raise RecordError("authorization flag must be boolean")
    authorization_reference = authorization.get("authorization_reference")
    if authorized and not nonempty_text(authorization_reference):
        raise RecordError("authorized execution requires an authorization reference")
    if not authorized and authorization_reference is not None:
        raise RecordError("unauthorized execution cannot name an authorization reference")

    environment = require_object(record, "environment")
    require_exact_keys(environment, "environment", {
        "host_id", "operating_system", "architecture", "client", "client_mode",
        "client_version", "workspace_trust", "transport", "project_scope",
    })
    client = environment.get("client")
    if client not in protocol["allowed_clients"]:
        raise RecordError("environment.client is not allowed")
    client_mode = environment.get("client_mode")
    if client_mode not in protocol["allowed_client_modes"]:
        raise RecordError("environment.client_mode is not allowed")
    if environment.get("transport") != "stdio":
        raise RecordError("the first runtime protocol requires STDIO transport")
    if environment.get("project_scope") != "disposable_project_only":
        raise RecordError("the first runtime protocol requires disposable project scope")

    safeguards = require_object(record, "safeguards")
    require_exact_keys(safeguards, "safeguards", set(protocol["required_safeguards"]))
    for key, expected in protocol["required_safeguards"].items():
        if safeguards.get(key) is not expected:
            raise RecordError(f"required safeguard {key} must be {str(expected).lower()}")

    side_effects = require_object(record, "side_effects")
    side_effect_keys = (
        "processes", "files", "network", "model_downloads",
        "mcp_initialization_instructions",
    )
    require_exact_keys(side_effects, "side_effects", set(side_effect_keys))
    for key in side_effect_keys:
        value = side_effects.get(key)
        if not isinstance(value, list) or not all(nonempty_text(item) for item in value):
            raise RecordError(f"side_effects.{key} must be a list of non-empty strings")

    behaviors = record.get("behaviors")
    if not isinstance(behaviors, list):
        raise RecordError("behaviors must be an array")
    expected_behaviors = contract["required_behaviors"]
    names = [item.get("behavior") for item in behaviors if isinstance(item, dict)]
    if len(names) != len(behaviors) or names != expected_behaviors:
        raise RecordError("behaviors must appear exactly once in contract order")
    statuses: list[str] = []
    for item in behaviors:
        require_exact_keys(item, f"behavior {item.get('behavior')!r}", {
            "behavior", "status", "evidence",
        })
        status = item.get("status")
        if status not in protocol["allowed_behavior_statuses"]:
            raise RecordError(f"invalid status for {item['behavior']}")
        evidence = item.get("evidence")
        if status == "not_run" and evidence is not None:
            raise RecordError(f"not-run behavior {item['behavior']} cannot claim evidence")
        if status != "not_run" and not nonempty_text(evidence):
            raise RecordError(f"observed behavior {item['behavior']} requires evidence")
        statuses.append(status)

    cleanup = require_object(record, "cleanup")
    cleanup_flags = ("attempted", "processes_stopped", "project_files_removed", "machine_state_removed_or_absent")
    require_exact_keys(cleanup, "cleanup", set(cleanup_flags) | {"notes"})
    for key in cleanup_flags:
        if not isinstance(cleanup.get(key), bool):
            raise RecordError(f"cleanup.{key} must be boolean")
    if cleanup["attempted"] and not nonempty_text(cleanup.get("notes")):
        raise RecordError("attempted cleanup requires notes")
    if not cleanup["attempted"] and cleanup.get("notes") is not None:
        raise RecordError("unattempted cleanup cannot claim notes")
    if not cleanup["attempted"] and any(cleanup[key] for key in cleanup_flags[1:]):
        raise RecordError("unattempted cleanup cannot claim cleanup outcomes")

    decision = record.get("decision")
    if decision not in protocol["allowed_decisions"]:
        raise RecordError("decision is not allowed")
    if decision != "not_run" and execution_block is not None:
        raise RecordError(
            "backend profile is blocked before execution: " + execution_block["reason"]
        )
    if not nonempty_text(record.get("decision_rationale")):
        raise RecordError("decision_rationale must be non-empty")
    limitations = record.get("limitations")
    if not isinstance(limitations, list) or not limitations or not all(nonempty_text(item) for item in limitations):
        raise RecordError("limitations must contain at least one non-empty statement")

    claims = require_object(record, "claims")
    require_exact_keys(claims, "claims", {
        "backend_runtime_qualified", "live_bob_observed", "production_ready",
    })
    for key in ("backend_runtime_qualified", "live_bob_observed", "production_ready"):
        if not isinstance(claims.get(key), bool):
            raise RecordError(f"claims.{key} must be boolean")
    if claims["production_ready"]:
        raise RecordError("the first runtime protocol cannot establish production readiness")

    if decision == "not_run":
        if authorized or client != "not_run" or any(status != "not_run" for status in statuses):
            raise RecordError("not_run requires no authorization, client, or observed behavior")
        if record.get("run_id") is not None:
            raise RecordError("not_run cannot claim a run_id")
        if record.get("observed_at_utc") is not None:
            raise RecordError("not_run cannot claim observed_at_utc")
        for key in ("host_id", "operating_system", "architecture", "client_version"):
            if environment.get(key) is not None:
                raise RecordError(f"not_run cannot claim environment.{key}")
        if environment.get("workspace_trust") != "not_assessed":
            raise RecordError("not_run requires workspace trust to remain not_assessed")
        if source["asset_digest_verified"]:
            raise RecordError("not_run cannot claim verification of an unobserved trial asset")
        if any(side_effects[key] for key in side_effect_keys):
            raise RecordError("not_run cannot contain runtime side-effect observations")
        if cleanup["attempted"] or any(cleanup[key] for key in cleanup_flags[1:]):
            raise RecordError("not_run cannot claim cleanup")
    else:
        if not authorized:
            raise RecordError("an executed decision requires explicit third-party execution authorization")
        if not source["asset_digest_verified"]:
            raise RecordError("an executed decision requires exact asset-digest verification")
        if not nonempty_text(record.get("run_id")):
            raise RecordError("an executed decision requires a non-empty run_id")
        if not valid_utc_timestamp(record.get("observed_at_utc")):
            raise RecordError(
                "an executed decision requires observed_at_utc as a valid "
                "second-precision RFC 3339 UTC timestamp"
            )
        if client == "not_run":
            raise RecordError("an executed decision requires an observed client")
        for key in ("host_id", "operating_system", "architecture"):
            if not nonempty_text(environment.get(key)):
                raise RecordError(f"an executed decision requires environment.{key}")

    if client == "not_run":
        if client_mode != "not_run":
            raise RecordError("the not_run client requires not_run client_mode")
    elif client == "direct_mcp":
        if client_mode != "direct_mcp":
            raise RecordError("the direct_mcp client requires direct_mcp client_mode")
        if environment.get("workspace_trust") != "not_applicable_direct":
            raise RecordError("direct MCP requires workspace trust to be marked not applicable")
        if claims["live_bob_observed"]:
            raise RecordError("direct MCP cannot claim a live IBM Bob observation")
    else:
        if client_mode not in {"ide_interactive", "shell_interactive", "shell_non_interactive"}:
            raise RecordError("the ibm_bob client requires a named Bob client mode")
        if client_mode == "shell_non_interactive":
            raise RecordError(
                "Bob Shell non-interactive mode pre-approves tools and is outside this manual-approval protocol"
            )
        if decision != "not_run":
            if not nonempty_text(environment.get("client_version")):
                raise RecordError("an executed IBM Bob observation requires a client version")
            if environment.get("workspace_trust") != "explicit_trust":
                raise RecordError("an executed IBM Bob observation requires explicit workspace trust")
            if not claims["live_bob_observed"]:
                raise RecordError("an executed IBM Bob observation must set live_bob_observed true")

    if decision == "qualified":
        if any(status != "pass" for status in statuses):
            raise RecordError("qualified requires every contract behavior to pass")
        if any(not side_effects[key] for key in side_effect_keys):
            raise RecordError(
                "qualified requires process, file, network, model-download, "
                "and MCP-instruction observations"
            )
        if not all(cleanup[key] for key in cleanup_flags):
            raise RecordError("qualified requires complete observed cleanup")
        if not claims["backend_runtime_qualified"]:
            raise RecordError("qualified must set backend_runtime_qualified true")
    elif claims["backend_runtime_qualified"]:
        raise RecordError("only a qualified decision may claim backend runtime qualification")

    if decision == "blocked" and not any(status in {"fail", "blocked"} for status in statuses):
        raise RecordError("blocked requires at least one failed or blocked behavior")
    if decision == "incomplete" and all(status == "pass" for status in statuses):
        raise RecordError("incomplete must retain at least one non-pass behavior")

    if claims["live_bob_observed"] and (decision == "not_run" or client != "ibm_bob"):
        raise RecordError("live Bob evidence requires an executed IBM Bob trial")

    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="runtime evidence JSON record")
    args = parser.parse_args(argv)
    try:
        decision = validate_record(load_object(args.record, "runtime evidence record"))
    except RecordError as exc:
        print(f"invalid memory runtime record: {exc}", file=sys.stderr)
        return 2
    print(f"valid memory runtime record: decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
