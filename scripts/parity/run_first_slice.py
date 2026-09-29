#!/usr/bin/env python3
"""Run the pinned first-slice oracle and target, then compare their results."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "tests/fixtures/inputs/parity/first-asgi-request.json"


def _run_cli(step: str, arguments: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.parity.cli", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{step} failed with exit code {completed.returncode}:\n"
            f"{completed.stdout}{completed.stderr}"
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{step} returned invalid JSON: {error}") from error
    if not isinstance(result, dict):
        raise RuntimeError(f"{step} returned a non-object result")
    return result


def _artifact(result: dict[str, object], step: str) -> str:
    artifact = result.get("artifact")
    if not isinstance(artifact, str):
        raise RuntimeError(f"{step} did not report its result artifact")
    return artifact


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--fastapi-source", type=Path, default=ROOT / "../fastapi")
    parser.add_argument("--starlette-source", type=Path, default=ROOT / "../starlette")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT / "../starlette-rs")
    parser.add_argument("--target-source", type=Path, default=ROOT)
    parser.add_argument("--oracle-python", type=Path, default=ROOT / ".venv-oracle/bin/python")
    parser.add_argument("--target-python", type=Path, default=ROOT / ".venv-target/bin/python")
    return parser


def main() -> int:
    args = _parser().parse_args()
    input_path = args.input.resolve()
    fastapi_source = args.fastapi_source.resolve()
    starlette_source = args.starlette_source.resolve()
    starlette_rs_source = args.starlette_rs_source.resolve()
    target_source = args.target_source.resolve()

    oracle = _run_cli(
        "oracle run",
        [
            "oracle",
            "--input",
            str(input_path),
            "--python",
            str(args.oracle_python),
            "--fastapi-source",
            str(fastapi_source),
            "--starlette-source",
            str(starlette_source),
        ],
    )
    target = _run_cli(
        "target run",
        [
            "target",
            "--input",
            str(input_path),
            "--python",
            str(args.target_python),
            "--target-source",
            str(target_source),
            "--starlette-rs-source",
            str(starlette_rs_source),
        ],
    )
    comparison = _run_cli(
        "comparison",
        [
            "compare",
            "--input",
            str(input_path),
            "--fastapi-source",
            str(fastapi_source),
            "--source-result",
            _artifact(oracle, "oracle run"),
            "--target-result",
            _artifact(target, "target run"),
        ],
    )
    summary = comparison.get("summary")
    if (
        comparison.get("status") != "completed"
        or not isinstance(summary, dict)
        or summary.get("failed") != 0
        or summary.get("not_run") != 0
        or summary.get("passed") != summary.get("selected")
    ):
        raise RuntimeError(f"comparison did not pass every selected case: {summary}")
    print(
        json.dumps(
            {
                "status": comparison.get("status"),
                "summary": summary,
                "oracle_result": _artifact(oracle, "oracle run"),
                "target_result": _artifact(target, "target run"),
                "comparison_result": _artifact(comparison, "comparison"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"parity first slice: {error}", file=sys.stderr)
        raise SystemExit(2) from error
