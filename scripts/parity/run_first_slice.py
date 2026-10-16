#!/usr/bin/env python3
"""Run the pinned first-slice oracle and target, then compare their results."""

from __future__ import annotations

import argparse
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
fastapi_rs_source_tree_sha256 = importlib.import_module(
    "scripts.parity.source_identity"
).fastapi_rs_source_tree_sha256

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


def _git_revision(source: Path, label: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[a-f0-9]{40}", revision) is None:
        detail = completed.stderr.strip()
        raise RuntimeError(f"cannot identify {label} source revision: {detail}")
    return revision


def _target_identity(
    result: dict[str, object],
    *,
    fastapi_revision: str,
    source_tree_sha256: str,
    starlette_rs_revision: str,
) -> dict[str, str]:
    identity = result.get("identity")
    if not isinstance(identity, dict):
        raise RuntimeError("target run did not report its runtime identity")
    repositories = identity.get("repositories")
    if not isinstance(repositories, dict):
        raise RuntimeError("target run did not report its repository identities")
    if identity.get("target_revision") != fastapi_revision:
        raise RuntimeError(
            "target result revision differs from the current FastAPI-RS checkout: "
            f"expected {fastapi_revision}, got {identity.get('target_revision')}"
        )
    if repositories.get("fastapi_rs") != fastapi_revision:
        raise RuntimeError("target result has inconsistent FastAPI-RS revision fields")
    if repositories.get("starlette_rs") != starlette_rs_revision:
        raise RuntimeError("target result Starlette-RS revision differs from its source checkout")
    if identity.get("source_tree_sha256") != source_tree_sha256:
        raise RuntimeError(
            "target result source-tree digest differs from the current "
            "FastAPI-RS/Starlette-RS trees"
        )
    binary_sha256 = identity.get("target_binary_sha256")
    if not isinstance(binary_sha256, str) or re.fullmatch(r"[a-f0-9]{64}", binary_sha256) is None:
        raise RuntimeError("target result compiled-extension digest is missing or malformed")
    return {
        "target_revision": fastapi_revision,
        "source_tree_sha256": source_tree_sha256,
        "target_binary_sha256": binary_sha256,
        "starlette_rs_revision": starlette_rs_revision,
    }


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

    expected_target_revision = _git_revision(target_source, "FastAPI-RS")
    expected_starlette_rs_revision = _git_revision(starlette_rs_source, "Starlette-RS")
    expected_source_tree_sha256 = fastapi_rs_source_tree_sha256(target_source, starlette_rs_source)

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
    target_identity = _target_identity(
        target,
        fastapi_revision=expected_target_revision,
        source_tree_sha256=expected_source_tree_sha256,
        starlette_rs_revision=expected_starlette_rs_revision,
    )
    if (
        _git_revision(target_source, "FastAPI-RS") != expected_target_revision
        or _git_revision(starlette_rs_source, "Starlette-RS") != expected_starlette_rs_revision
        or fastapi_rs_source_tree_sha256(target_source, starlette_rs_source)
        != expected_source_tree_sha256
    ):
        raise RuntimeError("FastAPI-RS or Starlette-RS source changed during the parity run")
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
                "target_identity": target_identity,
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
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        print(f"parity first slice: {error}", file=sys.stderr)
        raise SystemExit(2) from error
