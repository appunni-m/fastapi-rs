from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scripts.parity.fault_contracts import FaultContractError, verification_mode


def _fault_case_count(input_path: Path) -> int:
    workflow = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(workflow, dict):
        raise ValueError("workflow input must be a JSON object")
    cases: Any = workflow.get("cases")
    if not isinstance(cases, list):
        raise ValueError("workflow input must contain a cases list")
    if not all(isinstance(case, Mapping) for case in cases):
        raise ValueError("workflow cases must be JSON objects")
    return sum(verification_mode(case) == "fault-contract" for case in cases)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Require at least one target-only fault-contract case in a workflow."
    )
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()

    try:
        fault_cases = _fault_case_count(args.input)
    except (FaultContractError, OSError, ValueError) as exc:
        print(f"fault workflow: {exc}", file=sys.stderr)
        return 2
    if fault_cases == 0:
        print(
            f"fault workflow: {args.input} has no verification=fault-contract cases",
            file=sys.stderr,
        )
        return 2
    print(f"fault workflow valid: {args.input} ({fault_cases} fault-contract cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
