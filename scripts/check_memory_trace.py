#!/usr/bin/env python3
"""Check a finite public memory trace; never run a backend or trust its claims."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

MAX_INPUT_BYTES = 65_536
MAX_ERRORS = 20
CONTRACT_PATH = Path(__file__).resolve().parents[1] / "fixtures/memory-boundaries/contract.json"
LIMITATION = "Submitted trace only; backend execution and live Bob behavior are not verified."


class InvalidInput(ValueError):
    """Malformed input. Messages intentionally contain no candidate content."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput("duplicate_json_key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise InvalidInput("nonfinite_json_number")


def read_json(path: Path) -> Any:
    """Bound file reads, reject duplicate keys and non-standard JSON numbers."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise InvalidInput("input_too_large")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=_invalid_constant)
    except InvalidInput:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise InvalidInput("unreadable_or_invalid_json") from exc


def check_trace(trace: Any, contract: dict[str, Any]) -> list[str]:
    """Validate observed brief contents against trusted fixture expectations.

    This is not a retrieval algorithm, redactor, authorization layer, or generic
    benchmark. The contract is reviewed repository input, never candidate input.
    """
    errors: list[str] = []

    def fail(code: str) -> None:
        if len(errors) < MAX_ERRORS:
            errors.append(code)

    if not isinstance(trace, dict) or set(trace) != {"schema_version", "cases"}:
        return ["trace_shape"]
    if type(trace["schema_version"]) is not int or trace["schema_version"] != 1:
        return ["schema_version"]
    if not isinstance(trace["cases"], list):
        return ["cases_shape"]

    expected = {case["id"]: case for case in contract["cases"]}
    if len(trace["cases"]) != len(expected):
        fail("case_count")
    seen: set[str] = set()
    record_keys = {"id", "content", "source", "revision", "disposition"}
    for case in trace["cases"]:
        if not isinstance(case, dict) or set(case) != {"id", "status", "memory_role", "records"}:
            fail("case_shape")
            continue
        case_id = case["id"]
        if not isinstance(case_id, str) or case_id not in expected:
            fail("unknown_case")
            continue
        if case_id in seen:
            fail("duplicate_case")
            continue
        seen.add(case_id)
        rule = expected[case_id]
        # Only public, trusted case IDs enter diagnostics; candidate content never does.
        prefix = case_id + ":"
        if case["status"] != rule["status"]:
            fail(prefix + "status")
        if case["memory_role"] != "untrusted_data":
            fail(prefix + "memory_role")
        records = case["records"]
        if not isinstance(records, list) or len(records) > 16:
            fail(prefix + "records_shape")
            continue
        wanted = set(rule["record_ids"])
        actual: set[str] = set()
        for record in records:
            if not isinstance(record, dict) or set(record) != record_keys:
                fail(prefix + "record_shape")
                continue
            if any(not isinstance(value, str) for value in record.values()):
                fail(prefix + "record_value_type")
                continue
            record_id = record["id"]
            if record_id in actual:
                fail(prefix + "duplicate_record")
            actual.add(record_id)
            if record_id not in wanted:
                fail(prefix + "unexpected_record")
                continue
            seed = contract["records"][record_id]
            for field in ("content", "source", "revision"):
                if record[field] != seed[field]:
                    fail(prefix + field)
            if record["disposition"] != rule["disposition"]:
                fail(prefix + "disposition")
        if actual != wanted:
            fail(prefix + "record_set")
    if seen != set(expected):
        fail("missing_cases")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="Public fixture trace JSON, not private memory")
    args = parser.parse_args(argv)
    try:
        contract = read_json(CONTRACT_PATH)
        errors = check_trace(read_json(args.trace), contract)
        result = {
            "status": "trace_contract_failed" if errors else "trace_contract_passed",
            "case_count": len(contract["cases"]),
            "errors": errors,
            "limitation": LIMITATION,
        }
        code = 1 if errors else 0
    except InvalidInput as exc:
        result = {"status": "invalid_input", "errors": [str(exc)], "limitation": LIMITATION}
        code = 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
