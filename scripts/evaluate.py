#!/usr/bin/env python3
"""Prepare the Tiny Ledger fixture and collect offline public-test evidence."""

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "tiny-ledger"
TASK_ID = "tiny-ledger-atomicity-v1"
EXPECTED_TEST_COUNT = 9
EXPECTED_FAILURE = (
    "test_ledger.LedgerTests.test_unknown_destination_leaves_balances_unchanged"
)


def _inside(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _file_hash(path: Path) -> Optional[str]:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _test_hash(directory: Path) -> Optional[str]:
    if not directory.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*.py")):
        digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def prepare(output: Path) -> Dict[str, Any]:
    output = output.resolve()
    if _inside(output, FIXTURE.resolve()):
        raise ValueError("Prepare a workspace outside the original fixture")
    if output.exists():
        raise ValueError("Output already exists; choose a new run directory")
    shutil.copytree(FIXTURE, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return {
        "schema_version": 1,
        "task_id": TASK_ID,
        "status": "workspace_prepared",
        "workspace": str(output),
        "source_sha256": _file_hash(output / "ledger.py"),
        "public_tests_sha256": _test_hash(FIXTURE / "tests"),
        "model_calls_made_by_helper": 0,
    }


def _worker(workspace: Path, report_path: Path) -> None:
    """Run trusted tests against the candidate in a separate Python process."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(workspace.resolve()))
    suite = unittest.TestLoader().discover(str(FIXTURE / "tests"), pattern="test_*.py")
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    report = {
        "tests_run": result.testsRun,
        "failures": [test.id() for test, _ in result.failures],
        "errors": [test.id() for test, _ in result.errors],
        "skipped": [test.id() for test, _ in result.skipped],
        "expected_failures": [test.id() for test, _ in result.expectedFailures],
        "unexpected_successes": [test.id() for test in result.unexpectedSuccesses],
        "successful": result.wasSuccessful(),
        "output": output.getvalue(),
    }
    report_path.write_text(json.dumps(report), encoding="utf-8")


def check(workspace: Path, phase: str, timeout: float) -> Tuple[Dict[str, Any], int]:
    workspace = workspace.resolve()
    if not workspace.is_dir() or not (workspace / "ledger.py").is_file():
        raise ValueError("Workspace must contain the Tiny Ledger ledger.py file")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be finite and positive")

    canonical_source = _file_hash(FIXTURE / "ledger.py")
    source = _file_hash(workspace / "ledger.py")
    canonical_tests = _test_hash(FIXTURE / "tests")
    workspace_tests = _test_hash(workspace / "tests")
    report: Dict[str, Any] = {
        "schema_version": 1,
        "record_type": "offline_public_test_check",
        "task_id": TASK_ID,
        "phase": phase,
        "status": "runner_error",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "fingerprints": {
            "original_source_sha256": canonical_source,
            "candidate_source_sha256": source,
            "trusted_public_tests_sha256": canonical_tests,
            "workspace_tests_sha256": workspace_tests,
            "source_matches_original": source == canonical_source,
            "workspace_tests_match_original": workspace_tests == canonical_tests,
        },
        "test_duration_seconds": None,
        "tests": None,
        "manual_acceptance": "not_assessed",
        "model_calls_made_by_helper": 0,
    }
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="bob-eval-") as temporary:
        worker_report = Path(temporary) / "tests.json"
        command = [
            sys.executable, "-B", str(Path(__file__).resolve()), "_run-tests",
            str(workspace), str(worker_report),
        ]
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment.pop("PYTHONPATH", None)
        try:
            completed = subprocess.run(
                command, cwd=str(workspace), env=environment,
                capture_output=True, text=True, timeout=timeout, check=False,
            )
            if completed.returncode != 0 or not worker_report.is_file():
                report["error"] = "Public-test worker did not produce a valid result"
                report["worker_stdout"] = completed.stdout
                report["worker_stderr"] = completed.stderr
                return report, 2
            tests = json.loads(worker_report.read_text(encoding="utf-8"))
            report["tests"] = tests
            if completed.stdout:
                report["candidate_stdout"] = completed.stdout
            if completed.stderr:
                report["candidate_stderr"] = completed.stderr
        except subprocess.TimeoutExpired:
            report["error"] = "Public-test worker exceeded the configured timeout"
            return report, 2
        except (OSError, ValueError) as error:
            report["error"] = "Public-test worker failed: " + str(error)
            return report, 2
        finally:
            report["test_duration_seconds"] = round(time.perf_counter() - started, 6)

    complete_suite = (
        tests["tests_run"] == EXPECTED_TEST_COUNT
        and not tests["errors"]
        and not tests["skipped"]
        and not tests["expected_failures"]
        and not tests["unexpected_successes"]
    )
    if phase == "baseline":
        valid = (
            complete_suite
            and tests["failures"] == [EXPECTED_FAILURE]
            and source == canonical_source
            and workspace_tests == canonical_tests
        )
        report["status"] = "expected_baseline_failure" if valid else "unexpected_baseline"
    else:
        valid = complete_suite and not tests["failures"] and tests["successful"]
        report["status"] = "public_tests_passed" if valid else "public_tests_failed"
    return report, 0 if valid else 1


def _validate_output(path: Optional[Path]) -> Optional[Path]:
    if path is None:
        return None
    resolved = path.resolve()
    if _inside(resolved, FIXTURE.resolve()):
        raise ValueError("Result output must be outside the original fixture")
    if resolved.exists():
        raise ValueError("Result file already exists; choose a new filename")
    return resolved


def main(argv: Optional[List[str]] = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments and arguments[0] == "_run-tests":
        if len(arguments) != 3:
            return 2
        _worker(Path(arguments[1]), Path(arguments[2]))
        return 0

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="Copy the original to a new workspace")
    prepare_parser.add_argument("--output", required=True, type=Path)
    for phase in ("baseline", "candidate"):
        subparser = commands.add_parser(phase, help="Collect " + phase + " public-test evidence")
        subparser.add_argument("--workspace", required=True, type=Path)
        subparser.add_argument("--result", type=Path)
        subparser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(arguments)
    try:
        if args.command == "prepare":
            report = prepare(args.output)
            result_path = None
            exit_code = 0
        else:
            result_path = _validate_output(args.result)
            report, exit_code = check(args.workspace, args.command, args.timeout)
        encoded = json.dumps(report, indent=2) + "\n"
        if result_path is not None:
            result_path.parent.mkdir(parents=True, exist_ok=True)
            with result_path.open("x", encoding="utf-8") as output:
                output.write(encoded)
            print(json.dumps({"status": report["status"], "result_file": str(result_path)}))
        else:
            print(encoded, end="")
        return exit_code
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "helper_error", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
