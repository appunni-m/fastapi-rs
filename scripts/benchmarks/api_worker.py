"""Measure one direct public Python API call in an isolated subject process."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import inspect
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from scripts.parity import api_worker as parity_api_worker
from scripts.parity.target_worker import TARGET_PACKAGE_ROOT, _target_identity
from scripts.parity.worker import ROOT, WorkerError, _load_workload, _oracle_identity


class ApiBenchmarkError(RuntimeError):
    """A direct API benchmark input, identity, or invocation is invalid."""


def _percentile(samples: list[int], percent: float) -> int:
    ordered = sorted(samples)
    index = round((len(ordered) - 1) * percent / 100)
    return ordered[index]


def _observation_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run(
    subject: str,
    workload_path: Path,
    input_path: Path,
    workload_json: str,
    profile_json: str,
    parity_workload_sha256: str,
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
    *,
    manifest_sha256: str,
    input_sha256: str,
    workload_sha256: str,
) -> dict[str, Any]:
    if Path.cwd().resolve() != ROOT:
        raise ApiBenchmarkError(f"benchmark worker must run from {ROOT}")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    if parity_api_worker._sha256_file(manifest_path) != manifest_sha256:
        raise ApiBenchmarkError("manifest digest changed after benchmark validation")
    try:
        workload = json.loads(workload_json)
        workflow = json.loads(input_path.read_text(encoding="utf-8"))
        profile = json.loads(profile_json)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ApiBenchmarkError(f"cannot read validated workload or workflow: {exc}") from exc
    if not isinstance(workload, dict) or not isinstance(profile, dict):
        raise ApiBenchmarkError("workload and profile inputs must be JSON objects")
    resolved_workload = workload_path.resolve()
    resolved_input = input_path.resolve()
    for path, root, label in (
        (resolved_workload, ROOT / "benchmarks/workloads/api", "benchmark workload"),
        (resolved_input, ROOT / "tests/fixtures/inputs/parity", "parity input"),
    ):
        try:
            path.relative_to(root.resolve())
        except ValueError as exc:
            raise ApiBenchmarkError(f"{label} escapes its repository lane") from exc
    if workload.get("input", {}).get("path") != resolved_input.relative_to(ROOT).as_posix():
        raise ApiBenchmarkError("benchmark workload references a different parity input")
    if parity_api_worker._sha256_file(resolved_input) != input_sha256:
        raise ApiBenchmarkError("parity input digest changed after benchmark validation")
    if parity_api_worker._sha256_file(resolved_workload) != workload_sha256:
        raise ApiBenchmarkError("benchmark workload digest changed after validation")
    if (
        not isinstance(workflow, dict)
        or workflow.get("schema") not in parity_api_worker.WORKFLOW_SCHEMA_IDS
    ):
        raise ApiBenchmarkError("parity API workflow schema is unsupported")
    workflow_workload = workflow.get("workload")
    workload_file = workflow_workload.get("file") if isinstance(workflow_workload, dict) else None
    if not isinstance(workload_file, str):
        raise ApiBenchmarkError("parity workflow workload path is malformed")
    parity_workload_path = parity_api_worker._validate_workload_path(ROOT / workload_file)
    if parity_api_worker._sha256_file(parity_workload_path) != parity_workload_sha256:
        raise ApiBenchmarkError("parity Python workload digest changed after validation")
    cases = [
        case
        for case in workflow.get("cases", [])
        if isinstance(case, dict) and case.get("case_id") == workload["input"]["case_id"]
    ]
    if len(cases) != 1:
        raise ApiBenchmarkError("benchmark parity case is missing or ambiguous")
    probes = [
        probe
        for probe in cases[0].get("probes", [])
        if isinstance(probe, dict) and probe.get("probe_id") == workload["input"]["probe_id"]
    ]
    if len(probes) != 1:
        raise ApiBenchmarkError("benchmark parity probe is missing or ambiguous")
    probe = probes[0]
    if subject not in {"fastapi", "fastapi-rs"}:
        raise ApiBenchmarkError(f"unsupported API benchmark subject: {subject}")

    if subject == "fastapi":
        identity = _oracle_identity(
            fastapi_source.resolve(),
            starlette_source.resolve(),
            profile,
        )
        import_root = fastapi_source.resolve()
    else:
        identity = _target_identity(
            ROOT,
            starlette_rs_source.resolve(),
            target_profile=profile,
        )
        import_root = TARGET_PACKAGE_ROOT.parent

    supported_symbols = parity_api_worker._trusted_supported_symbols(manifest_sha256)
    parity_api_worker._validate_workflow_callables(workflow, supported_symbols)
    factory = _load_workload(
        parity_workload_path,
        input_sha256,
        workflow["workload"]["factory"],
    )
    bundles = asyncio.run(parity_api_worker._make_bundles(factory))
    args, kwargs = parity_api_worker._get_arguments(
        bundles,
        workload["input"]["argument_bundle"],
    )
    function = parity_api_worker._resolve_public_callable(
        probe["public_callable"],
        import_root,
        supported_symbols,
    )
    cache_reset = workload["invoke"]["cache_reset"]
    receiver_index = cache_reset["receiver_argument"]
    if receiver_index >= len(args):
        raise ApiBenchmarkError("cache reset receiver argument is absent from the bundle")
    receiver = args[receiver_index]

    def invoke() -> Any:
        setattr(receiver, cache_reset["attribute"], cache_reset["value"])
        value = function(*args, **kwargs)
        if inspect.isawaitable(value):
            if inspect.iscoroutine(value):
                value.close()
            raise ApiBenchmarkError("the declared direct API benchmark must be synchronous")
        return value

    def project(value: Any) -> Any:
        return parity_api_worker._json_safe(value)

    correctness_observation = project(invoke())
    timing = workload["timing"]
    for _ in range(timing["warmups"]):
        if project(invoke()) != correctness_observation:
            raise ApiBenchmarkError("warmup observation differs from the untimed call")

    samples: list[int] = []
    for _ in range(timing["rounds"]):
        for _ in range(timing["samples_per_round"]):
            started = time.perf_counter_ns()
            value = invoke()
            elapsed = time.perf_counter_ns() - started
            if project(value) != correctness_observation:
                raise ApiBenchmarkError("measured observation differs from the untimed call")
            samples.append(elapsed)

    measurement = {
        "subject": subject,
        "identity": identity,
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
        },
        "sample_count": len(samples),
        "warmup_count": timing["warmups"],
        "rounds": timing["rounds"],
        "samples_per_round": timing["samples_per_round"],
        "latency_ns": {
            "min": min(samples),
            "median": int(statistics.median(samples)),
            "p95": _percentile(samples, 95),
            "p99": _percentile(samples, 99),
            "max": max(samples),
            "mean": statistics.fmean(samples),
        },
        "raw_latency_ns": samples,
        "untimed_observation_sha256": _observation_digest(correctness_observation),
        "correctness_observation": correctness_observation,
    }
    return measurement


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", choices=("fastapi", "fastapi-rs"), required=True)
    parser.add_argument("--workload", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--workload-json", required=True)
    parser.add_argument("--profile-json", required=True)
    parser.add_argument("--parity-workload-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--workload-sha256", required=True)
    parser.add_argument("--fastapi-source", type=Path, required=True)
    parser.add_argument("--starlette-source", type=Path, required=True)
    parser.add_argument("--starlette-rs-source", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(
            args.subject,
            args.workload,
            args.input,
            args.workload_json,
            args.profile_json,
            args.parity_workload_sha256,
            args.fastapi_source,
            args.starlette_source,
            args.starlette_rs_source,
            manifest_sha256=args.manifest_sha256,
            input_sha256=args.input_sha256,
            workload_sha256=args.workload_sha256,
        )
    except (ApiBenchmarkError, WorkerError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"API benchmark worker: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
