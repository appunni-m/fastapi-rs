#!/usr/bin/env python3
"""Run fresh identity-checked parity, then measure the TestClient workload."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.benchmarks import testclient_contract as contract
from scripts.parity import run_first_slice as parity_driver
from scripts.parity.contract import read_manifest, sha256_file

ROOT = Path(__file__).resolve().parents[2]


class TestClientBenchmarkError(RuntimeError):
    """A TestClient parity gate, identity, or worker failed."""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workload",
        type=Path,
        default=ROOT / "benchmarks/workloads/testclient/testclient-sync-validated.yaml",
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--fastapi-source", type=Path, default=ROOT / "../fastapi")
    parser.add_argument("--starlette-source", type=Path, default=ROOT / "../starlette")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT / "../starlette-rs")
    parser.add_argument(
        "--oracle-python", type=Path, default=ROOT / ".venv-oracle-testclient/bin/python"
    )
    parser.add_argument(
        "--target-python", type=Path, default=ROOT / "target/testclient/venv/bin/python"
    )
    return parser


def _target_parity_run(arguments: list[str]) -> dict[str, Any]:
    """Run the target through the shared parity helper without an inherited Rust wrapper."""
    old_wrapper = os.environ.get("CARGO_BUILD_RUSTC_WRAPPER")
    os.environ["CARGO_BUILD_RUSTC_WRAPPER"] = ""
    try:
        return parity_driver._run_cli("target run", arguments)
    finally:
        if old_wrapper is None:
            os.environ.pop("CARGO_BUILD_RUSTC_WRAPPER", None)
        else:
            os.environ["CARGO_BUILD_RUSTC_WRAPPER"] = old_wrapper


def _run_worker(
    kind: str,
    *,
    python: Path,
    app_workload: Path,
    factory: str,
    factory_input: dict[str, Any],
    request: dict[str, Any],
    warmups: int,
    rounds: int,
    samples_per_round: int,
    identities: dict[str, Any],
    profile_identity: dict[str, Any],
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
) -> dict[str, Any]:
    command = [
        str(python),
        "-m",
        "scripts.benchmarks.testclient_worker",
        "--kind",
        kind,
        "--request-json",
        json.dumps(request, sort_keys=True, separators=(",", ":")),
        "--factory-input-json",
        json.dumps(factory_input, sort_keys=True, separators=(",", ":")),
        "--app-workload",
        str(app_workload),
        "--factory",
        factory,
        "--warmups",
        str(warmups),
        "--rounds",
        str(rounds),
        "--samples-per-round",
        str(samples_per_round),
        "--identities-json",
        json.dumps(identities, sort_keys=True, separators=(",", ":")),
        "--profile-identity-json",
        json.dumps(profile_identity, sort_keys=True, separators=(",", ":")),
        "--fastapi-source",
        str(fastapi_source),
        "--starlette-source",
        str(starlette_source),
        "--starlette-rs-source",
        str(starlette_rs_source),
    ]
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if kind == "fastapi-rs":
        environment["CARGO_BUILD_RUSTC_WRAPPER"] = ""
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired as exc:
        raise TestClientBenchmarkError(f"{kind} TestClient worker exceeded 1800 seconds") from exc
    if completed.returncode:
        raise TestClientBenchmarkError(
            f"{kind} TestClient worker failed ({completed.returncode}):\n"
            f"{completed.stdout}{completed.stderr}"
        )
    try:
        measurement = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise TestClientBenchmarkError(
            f"{kind} TestClient worker returned invalid JSON: {exc}\n{completed.stdout}"
        ) from exc
    if not isinstance(measurement, dict):
        raise TestClientBenchmarkError(f"{kind} TestClient worker returned a non-object")
    return measurement


def _assert_clean_source(root: Path, label: str, *pathspecs: str) -> None:
    command = ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]
    if pathspecs:
        command.extend(["--", *pathspecs])
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode:
        raise TestClientBenchmarkError(
            f"could not verify a clean {label} source tree: {completed.stderr.strip()}"
        )
    if completed.stdout.strip():
        raise TestClientBenchmarkError(
            f"{label} source tree must be clean before TestClient parity/measurement:\n"
            f"{completed.stdout.strip()}"
        )


def _fresh_parity(
    *,
    input_path: Path,
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
    oracle_python: Path,
    target_python: Path,
    case_id: str,
) -> tuple[dict[str, Any], Path, dict[str, Any], dict[str, Any]]:
    parity_driver._run_cli(
        "input validation",
        [
            "validate",
            "--input",
            str(input_path),
            "--fastapi-source",
            str(fastapi_source),
            "--starlette-source",
            str(starlette_source),
        ],
    )
    oracle = parity_driver._run_cli(
        "oracle run",
        [
            "oracle",
            "--input",
            str(input_path),
            "--python",
            str(oracle_python),
            "--fastapi-source",
            str(fastapi_source),
            "--starlette-source",
            str(starlette_source),
        ],
    )
    target = _target_parity_run(
        [
            "target",
            "--input",
            str(input_path),
            "--python",
            str(target_python),
            "--target-source",
            str(ROOT),
            "--starlette-rs-source",
            str(starlette_rs_source),
        ]
    )
    comparison = parity_driver._run_cli(
        "comparison",
        [
            "compare",
            "--input",
            str(input_path),
            "--fastapi-source",
            str(fastapi_source),
            "--source-result",
            parity_driver._artifact(oracle, "oracle run"),
            "--target-result",
            parity_driver._artifact(target, "target run"),
        ],
    )
    comparison_artifact = parity_driver._artifact(comparison, "comparison")
    comparison_path = Path(comparison_artifact)
    if not comparison_path.is_absolute():
        comparison_path = ROOT / comparison_path
    comparison_path = comparison_path.resolve()
    comparison_document = json.loads(comparison_path.read_text(encoding="utf-8"))
    summary = comparison.get("summary")
    cases = comparison_document.get("cases")
    if (
        comparison.get("status") != "completed"
        or not isinstance(summary, dict)
        or summary.get("selected") != 1
        or summary.get("passed") != 1
        or summary.get("failed") != 0
        or summary.get("not_run") != 0
        or not isinstance(summary.get("parity"), dict)
        or summary["parity"].get("selected") != 1
        or summary["parity"].get("passed") != 1
        or summary["parity"].get("failed") != 0
        or not isinstance(cases, list)
        or len(cases) != 1
        or cases[0].get("case_id") != case_id
        or cases[0].get("outcome") != "pass"
    ):
        raise TestClientBenchmarkError(
            f"fresh parity did not pass exactly the selected case {case_id}: {summary}"
        )

    source_ref = comparison_document["source_result"]
    target_ref = comparison_document["target_result"]
    source = contract._artifact(source_ref["path"], "oracle", source_ref["sha256"])
    target_result = contract._artifact(target_ref["path"], "target", target_ref["sha256"])
    if (
        source.get("run_id") != source_ref.get("run_id")
        or target_result.get("run_id") != target_ref.get("run_id")
        or source.get("run_id") == target_result.get("run_id")
        or source.get("status") != "completed"
        or target_result.get("status") != "completed"
    ):
        raise TestClientBenchmarkError(
            "fresh comparison does not reference distinct completed oracle and target runs"
        )
    expected_input = {
        "path": input_path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(input_path),
        "schema": contract.WORKFLOW_SCHEMA_V12_ID,
    }
    manifest_identity = {
        "path": "tests/fixtures/manifest.yaml",
        "sha256": sha256_file(ROOT / "tests/fixtures/manifest.yaml"),
    }
    if (
        comparison_document.get("input") != expected_input
        or comparison_document.get("manifest") != manifest_identity
        or source.get("input") != expected_input
        or target_result.get("input") != expected_input
        or source.get("manifest") != manifest_identity
        or target_result.get("manifest") != manifest_identity
    ):
        raise TestClientBenchmarkError(
            "fresh parity results do not share the selected input and current manifest"
        )
    contract._expected_worker_identities(source, target_result, read_manifest())
    return comparison, comparison_path, source, target_result


def _write_immutable_result(result: dict[str, Any]) -> Path:
    result_root = contract.BENCHMARK_RESULT_ROOT / "testclient"
    result_root.mkdir(parents=True, exist_ok=True)
    artifact_path = (result_root / f"{result['run_id']}.json").resolve()
    try:
        artifact_path.relative_to(contract.BENCHMARK_RESULT_ROOT.resolve())
    except ValueError as exc:
        raise TestClientBenchmarkError("result path escapes benchmark-results") from exc
    serialized = json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    try:
        with artifact_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
    except FileExistsError as exc:
        raise TestClientBenchmarkError(
            f"refusing to replace immutable benchmark result: {artifact_path}"
        ) from exc
    return artifact_path


def main() -> int:
    args = _parser().parse_args()
    fastapi_source = args.fastapi_source.resolve()
    starlette_source = args.starlette_source.resolve()
    starlette_rs_source = args.starlette_rs_source.resolve()
    # Preserve a venv's bin/python symlink: resolving it selects the base
    # interpreter and bypasses the profile's site-packages.
    oracle_python = args.oracle_python.absolute()
    target_python = args.target_python.absolute()
    os.environ["STARLETTE_RS_SOURCE"] = str(starlette_rs_source)

    workload, workload_path, workflow, input_path, action = contract.load_workload(
        args.workload,
        validate_payload_json=False,
    )
    if args.input is not None and args.input.resolve() != input_path:
        raise TestClientBenchmarkError("command-line input differs from the TestClient workload")

    # Fail before the comparatively expensive parity gate when product source
    # identities cannot be attributed to the pinned revisions.
    _assert_clean_source(ROOT, "FastAPI-RS")
    _assert_clean_source(fastapi_source, "FastAPI", "fastapi")
    _assert_clean_source(starlette_source, "Starlette", "starlette")
    _assert_clean_source(starlette_rs_source, "Starlette-RS")
    comparison, comparison_path, source, target_result = _fresh_parity(
        input_path=input_path,
        fastapi_source=fastapi_source,
        starlette_source=starlette_source,
        starlette_rs_source=starlette_rs_source,
        oracle_python=oracle_python,
        target_python=target_python,
        case_id=workload["input"]["case_id"],
    )
    manifest = read_manifest()
    source_identity, target_parity_identity = contract._expected_worker_identities(
        source, target_result, manifest
    )
    profiles = contract._manifest_profiles(manifest)
    if source_identity["shared_packages"] != target_parity_identity["shared_packages"]:
        raise TestClientBenchmarkError(
            "oracle and target TestClient profiles have different shared packages"
        )

    case = next(
        item for item in workflow["cases"] if item["case_id"] == workload["input"]["case_id"]
    )
    payload_bytes = base64.b64decode(action["request"]["content_base64"], validate=True)
    payload = json.loads(payload_bytes.decode("utf-8"))
    request = {
        "method": action["request"]["method"],
        "path": action["request"]["url"],
        "payload": payload,
    }
    app_workload = (ROOT / workflow["workload"]["file"]).resolve()
    identity_arguments = {
        "python": workload["python_identity"],
        "fastapi_source": source_identity["fastapi_source"],
        "fastapi_version": source_identity["fastapi"],
        "starlette_source": source_identity["starlette_source"],
        "starlette_version": source_identity["starlette"],
        "starlette_rs_source": target_parity_identity["starlette_rs_source"],
        "fastapi_rs_version": target_parity_identity["fastapi_rs"],
        "starlette_rs_version": target_parity_identity["starlette_rs"],
        "shared_packages": source_identity["shared_packages"],
    }

    python_by_kind = {"fastapi": oracle_python, "fastapi-rs": target_python}
    expected_identities = {"fastapi": source_identity, "fastapi-rs": target_parity_identity}
    expected_profiles = {"fastapi": profiles["oracle"], "fastapi-rs": profiles["target"]}
    measurements: dict[str, dict[str, Any]] = {}
    for subject in workload["subjects"]:
        kind = subject["kind"]
        measurement = _run_worker(
            kind,
            python=python_by_kind[kind],
            app_workload=app_workload,
            factory=workflow["workload"]["factory"],
            factory_input=case["factory_input"],
            request=request,
            warmups=workload["timing"]["warmups"],
            rounds=workload["timing"]["rounds"],
            samples_per_round=workload["timing"]["samples_per_round"],
            identities=identity_arguments,
            profile_identity=expected_profiles[kind],
            fastapi_source=fastapi_source,
            starlette_source=starlette_source,
            starlette_rs_source=starlette_rs_source,
        )
        actual_identity = measurement.get("identity")
        if (
            measurement.get("subject") != kind
            or measurement.get("profile_identity") != expected_profiles[kind]
            or measurement.get("python_identity") != workload["python_identity"]
            or measurement.get("selected_action_id") != action["action_id"]
        ):
            raise TestClientBenchmarkError(f"{kind} worker identity differs from its parity gate")
        if kind == "fastapi":
            identity_matches = actual_identity == expected_identities[kind]
        else:
            identity_matches = isinstance(actual_identity, dict) and all(
                actual_identity.get(name) == value
                for name, value in expected_identities[kind].items()
            )
        if not identity_matches:
            raise TestClientBenchmarkError(f"{kind} worker identity differs from its parity gate")
        measurements[kind] = measurement

    observations = {
        json.dumps(row["correctness_observation"], sort_keys=True) for row in measurements.values()
    }
    hosts = {json.dumps(row["host"], sort_keys=True) for row in measurements.values()}
    if len(observations) != 1:
        raise TestClientBenchmarkError("untimed status/body observations differ across subjects")
    if len(hosts) != 1:
        raise TestClientBenchmarkError("TestClient subjects did not run on the same host")
    host = json.loads(next(iter(hosts)))
    for measurement in measurements.values():
        measurement.pop("host")

    source_latency = measurements["fastapi"]["latency_ns"]
    target_latency = measurements["fastapi-rs"]["latency_ns"]
    if any(
        samples[statistic] <= 0
        for samples in (source_latency, target_latency)
        for statistic in ("median", "p95")
    ):
        raise TestClientBenchmarkError("reported median and p95 latencies must be positive")
    target_identity = measurements["fastapi-rs"]["identity"]
    timing = workload["timing"]
    result = {
        "schema": contract.RESULT_SCHEMA_ID,
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "workload": {
            "id": workload["id"],
            "path": workload_path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(workload_path),
            "input_path": input_path.relative_to(ROOT).as_posix(),
            "input_sha256": sha256_file(input_path),
            "case_id": workload["input"]["case_id"],
            "action_id": workload["input"]["action_id"],
        },
        "parity_gate": {
            "status": comparison["status"],
            "summary": {"selected": 1, "passed": 1, "failed": 0, "not_run": 0},
            "comparison_artifact": comparison_path.relative_to(ROOT).as_posix(),
            "comparison_sha256": sha256_file(comparison_path),
        },
        "profiles": profiles,
        "python_identity": workload["python_identity"],
        "host": host,
        "boundary": timing["boundary"],
        "timing": {
            "warmups": timing["warmups"],
            "rounds": timing["rounds"],
            "samples_per_round": timing["samples_per_round"],
            "concurrency": timing["concurrency"],
        },
        "source_identity": source_identity,
        "target_identity": target_identity,
        "subjects": measurements,
        "ratios": {
            "fastapi_rs_over_fastapi_median": (target_latency["median"] / source_latency["median"]),
            "fastapi_rs_over_fastapi_p95": target_latency["p95"] / source_latency["p95"],
        },
    }
    contract.validate_result(
        result,
        workload=workload,
        workload_path=workload_path,
        input_path=input_path,
        action=action,
        comparison_path=comparison_path,
    )
    artifact_path = _write_immutable_result(result)
    print(
        json.dumps(
            {
                "status": "completed",
                "artifact": artifact_path.relative_to(ROOT).as_posix(),
                "ratios": result["ratios"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        TestClientBenchmarkError,
        contract.ContractError,
        OSError,
        RuntimeError,
        subprocess.SubprocessError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        print(f"TestClient benchmark: {error}", file=sys.stderr)
        raise SystemExit(2) from error
