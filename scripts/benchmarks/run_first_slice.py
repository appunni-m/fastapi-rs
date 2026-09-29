#!/usr/bin/env python3
"""Run fresh parity first, then measure three isolated ASGI products."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


class BenchmarkError(RuntimeError):
    """A benchmark gate, identity, or worker failed."""


def _run(label: str, command: list[str]) -> dict[str, Any]:
    process = subprocess.run(
        command, cwd=ROOT, check=False, capture_output=True, text=True, timeout=1800
    )
    if process.returncode:
        raise BenchmarkError(
            f"{label} failed ({process.returncode}):\n{process.stdout}{process.stderr}"
        )
    try:
        value = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise BenchmarkError(f"{label} did not return JSON: {error}\n{process.stdout}") from error
    if not isinstance(value, dict):
        raise BenchmarkError(f"{label} returned a non-object")
    return value


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator


def _version(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    parity_driver = importlib.import_module("scripts.parity.run_first_slice")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workload", type=Path, default=ROOT / "benchmarks/workloads/first-slice-valid-asgi.yaml"
    )
    parser.add_argument(
        "--input", type=Path, default=ROOT / "tests/fixtures/inputs/parity/first-asgi-request.json"
    )
    parser.add_argument("--fastapi-source", type=Path, default=ROOT / "../fastapi")
    parser.add_argument("--starlette-source", type=Path, default=ROOT / "../starlette")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT / "../starlette-rs")
    parser.add_argument("--oracle-python", type=Path, default=ROOT / ".venv-oracle/bin/python")
    parser.add_argument("--target-python", type=Path, default=ROOT / ".venv-target/bin/python")
    args = parser.parse_args()
    workload_path = args.workload.resolve()
    input_path = args.input.resolve()
    workload = yaml.safe_load(workload_path.read_text(encoding="utf-8"))
    input_workflow = json.loads(input_path.read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "tests/fixtures/manifest.yaml").read_text(encoding="utf-8"))
    case_id = workload["input"]["case_id"]
    app_workload = ROOT / input_workflow["workload"]["file"]
    factory = input_workflow["workload"]["factory"]
    oracle_profile = manifest["oracle_profile"]
    target_contract = manifest["target"]
    expected_identity = {
        "fastapi_source": oracle_profile["source_commits"]["fastapi"],
        "fastapi_version": oracle_profile["packages"]["fastapi"],
        "starlette_source": oracle_profile["source_commits"]["starlette"],
        "starlette_version": oracle_profile["packages"]["starlette"],
        "starlette_rs_source": target_contract["starlette_rs_distribution"]["commit"],
        "fastapi_rs_version": target_contract["version"],
        "starlette_rs_version": target_contract["starlette_rs_distribution"]["version"],
        "shared_packages": {
            name: version
            for name, version in oracle_profile["packages"].items()
            if name not in {"fastapi", "starlette"}
        },
    }

    oracle = parity_driver._run_cli(
        "oracle run",
        [
            "oracle",
            "--input",
            str(input_path),
            "--python",
            str(args.oracle_python.resolve()),
            "--fastapi-source",
            str(args.fastapi_source.resolve()),
            "--starlette-source",
            str(args.starlette_source.resolve()),
        ],
    )
    target = parity_driver._run_cli(
        "target run",
        [
            "target",
            "--input",
            str(input_path),
            "--python",
            str(args.target_python.resolve()),
            "--target-source",
            str(ROOT),
            "--starlette-rs-source",
            str(args.starlette_rs_source.resolve()),
        ],
    )
    comparison = parity_driver._run_cli(
        "comparison",
        [
            "compare",
            "--input",
            str(input_path),
            "--fastapi-source",
            str(args.fastapi_source.resolve()),
            "--source-result",
            parity_driver._artifact(oracle, "oracle run"),
            "--target-result",
            parity_driver._artifact(target, "target run"),
        ],
    )
    parity = {
        "status": comparison.get("status"),
        "summary": comparison.get("summary"),
        "comparison_result": parity_driver._artifact(comparison, "comparison"),
    }
    summary = parity.get("summary", {})
    if (
        summary.get("failed") != 0
        or summary.get("not_run") != 0
        or summary.get("passed") != summary.get("selected")
    ):
        raise BenchmarkError(f"full selected parity gate did not pass: {summary}")

    subject_python = {
        "fastapi": args.oracle_python.resolve(),
        "starlette-control": args.oracle_python.resolve(),
        "fastapi-rs": args.target_python.resolve(),
    }
    measurements: dict[str, dict[str, Any]] = {}
    for subject in workload["subjects"]:
        kind = subject["kind"]
        measurements[kind] = _run(
            f"{kind} benchmark",
            [
                str(subject_python[kind]),
                str(ROOT / "scripts/benchmarks/worker.py"),
                "--kind",
                kind,
                "--input",
                str(input_path),
                "--case-id",
                case_id,
                "--app-workload",
                str(app_workload),
                "--factory",
                factory,
                "--warmups",
                str(workload["timing"]["warmups"]),
                "--rounds",
                str(workload["timing"]["rounds"]),
                "--samples-per-round",
                str(workload["timing"]["samples_per_round"]),
                "--identities-json",
                json.dumps(expected_identity, sort_keys=True, separators=(",", ":")),
                "--fastapi-source",
                str(args.fastapi_source.resolve()),
                "--starlette-source",
                str(args.starlette_source.resolve()),
                "--starlette-rs-source",
                str(args.starlette_rs_source.resolve()),
            ],
        )

    observations = {
        json.dumps(value["correctness_observation"], sort_keys=True)
        for value in measurements.values()
    }
    if len(observations) != 1:
        raise BenchmarkError("untimed live observations differ across benchmark subjects")

    oracle = measurements["fastapi"]["latency_ns"]
    target = measurements["fastapi-rs"]["latency_ns"]
    comparison_path = Path(parity["comparison_result"])
    if not comparison_path.is_absolute():
        comparison_path = ROOT / comparison_path
    result = {
        "schema": "fastapi-rs/benchmark-result@1",
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "workload": {
            "id": workload["id"],
            "path": str(workload_path.relative_to(ROOT)),
            "sha256": _sha256(workload_path),
            "input_path": str(input_path.relative_to(ROOT)),
            "input_sha256": _sha256(input_path),
            "case_id": case_id,
        },
        "parity_gate": {
            "status": parity["status"],
            "summary": summary,
            "comparison_artifact": str(comparison_path),
            "comparison_sha256": _sha256(comparison_path),
        },
        "code": {
            "fastapi_source": _git(args.fastapi_source.resolve(), "rev-parse", "HEAD"),
            "starlette_source": _git(args.starlette_source.resolve(), "rev-parse", "HEAD"),
            "fastapi_rs_source": _git(ROOT, "rev-parse", "HEAD"),
            "starlette_rs_source": _git(args.starlette_rs_source.resolve(), "rev-parse", "HEAD"),
        },
        "host": {"platform": platform.platform(), "machine": platform.machine()},
        "target_build": {
            "cargo_profile": "release",
            "cargo_features": ["pyo3/extension-module"],
            "rustc": _version(["rustc", "--version", "--verbose"]),
            "cargo": _version(["cargo", "--version", "--verbose"]),
        },
        "subjects": measurements,
        "ratios": {
            "fastapi_rs_over_fastapi_median": _ratio(target["median"], oracle["median"]),
            "fastapi_rs_over_fastapi_p95": _ratio(target["p95"], oracle["p95"]),
        },
        "interpretation": (
            "Single-machine first-slice direct-ASGI baseline; not a network or full-suite claim."
        ),
    }
    results_dir = ROOT / "benchmark-results"
    results_dir.mkdir(exist_ok=True)
    artifact = (
        results_dir / f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{result['run_id']}.json"
    )
    with artifact.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(
        json.dumps(
            {"status": "completed", "artifact": str(artifact), "ratios": result["ratios"]}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        BenchmarkError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        print(f"first-slice benchmark: {error}", file=sys.stderr)
        raise SystemExit(2) from error
