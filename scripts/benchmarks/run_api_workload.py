"""Measure a direct FastAPI public API workload after a matching parity pass."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import uuid
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from scripts.benchmarks import api_contract
from scripts.parity.comparator import SHARED_ORACLE_PACKAGES
from scripts.parity.contract import ROOT, read_json, read_manifest, sha256_file
from scripts.parity.source_identity import (
    combine_digests,
    fastapi_rs_source_tree_sha256,
    source_tree_sha256,
)

PARITY_RESULTS_ROOT = (ROOT / "parity-results").resolve()
BENCHMARK_RESULTS_ROOT = ROOT / "benchmark-results/api"
TARGET_RUNTIME_PATHS = (
    "Cargo.lock",
    "Cargo.toml",
    "fastapi-rs",
    "fastapi-rs-py",
    "metadata.yaml",
    "pyproject.toml",
    "requirements/target-runtime-cpython-3.12.13.lock",
    "tests/fixtures/manifest.yaml",
    "tests/fixtures/materialized-input-index.json",
)


class ApiBenchmarkError(RuntimeError):
    """A parity gate, identity, or API benchmark worker failed."""


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _read_parity_artifact(
    path_value: str, digest: str, product: str
) -> tuple[dict[str, Any], Path]:
    path = (ROOT / path_value).resolve()
    try:
        path.relative_to(PARITY_RESULTS_ROOT)
    except ValueError as exc:
        raise ApiBenchmarkError("parity evidence must live under parity-results") from exc
    if not path.is_file() or sha256_file(path) != digest:
        raise ApiBenchmarkError(f"parity evidence is missing or stale: {path_value}")
    value = read_json(path)
    if not isinstance(value, dict) or value.get("product") != product:
        raise ApiBenchmarkError(f"parity evidence is not a {product} result: {path_value}")
    if value.get("status") != "completed" or value.get("infrastructure_errors") != []:
        raise ApiBenchmarkError(f"parity {product} evidence is incomplete")
    return value, path


def _reference_observation(result: dict[str, Any], case_id: str, probe_id: str) -> Any:
    cases = [case for case in result.get("cases", []) if case.get("case_id") == case_id]
    if len(cases) != 1 or cases[0].get("status") != "completed":
        raise ApiBenchmarkError(f"parity result lacks a completed case: {case_id}")
    probes = [probe for probe in cases[0].get("probes", []) if probe.get("probe_id") == probe_id]
    if len(probes) != 1 or probes[0].get("status") != "completed":
        raise ApiBenchmarkError(f"parity result lacks a completed probe: {probe_id}")
    observations = probes[0].get("observations", [])
    if len(observations) != 1 or observations[0].get("kind") != "python_return_value":
        raise ApiBenchmarkError("benchmark parity probe must expose one public return value")
    values = observations[0].get("values")
    if not isinstance(values, dict) or "value" not in values:
        raise ApiBenchmarkError("parity public return observation is malformed")
    return values["value"]


def _run_worker(
    python: Path,
    subject: str,
    workload_path: Path,
    input_path: Path,
    manifest_sha256: str,
    input_sha256: str,
    workload_sha256: str,
    parity_workload_sha256: str,
    workload: dict[str, Any],
    profile: dict[str, Any],
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
) -> dict[str, Any]:
    command = [
        str(python.absolute()),
        "-m",
        "scripts.benchmarks.api_worker",
        "--subject",
        subject,
        "--workload",
        str(workload_path),
        "--input",
        str(input_path),
        "--workload-json",
        json.dumps(workload, ensure_ascii=False, separators=(",", ":")),
        "--profile-json",
        json.dumps(profile, ensure_ascii=False, separators=(",", ":")),
        "--parity-workload-sha256",
        parity_workload_sha256,
        "--manifest-sha256",
        manifest_sha256,
        "--input-sha256",
        input_sha256,
        "--workload-sha256",
        workload_sha256,
        "--fastapi-source",
        str(fastapi_source.resolve()),
        "--starlette-source",
        str(starlette_source.resolve()),
        "--starlette-rs-source",
        str(starlette_rs_source.resolve()),
    ]
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    if completed.returncode:
        raise ApiBenchmarkError(
            f"{subject} API benchmark worker failed ({completed.returncode}):\n"
            f"{completed.stdout}{completed.stderr}"
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ApiBenchmarkError(f"{subject} worker emitted malformed JSON") from exc
    if not isinstance(result, dict):
        raise ApiBenchmarkError(f"{subject} worker emitted a non-object")
    return result


def _same_target_build_identity(
    live: dict[str, Any], parity: dict[str, Any], current_tree_sha256: str
) -> None:
    stable_keys = (
        "distribution",
        "version",
        "python",
        "platform",
        "target_binary_sha256",
        "packages",
    )
    if any(live.get(key) != parity.get(key) for key in stable_keys):
        raise ApiBenchmarkError("live target runtime differs from the parity-tested target build")
    if live.get("source_tree_sha256") != current_tree_sha256:
        raise ApiBenchmarkError("live target source identity differs from the clean checkout")
    live_starlette = live.get("repositories", {}).get("starlette_rs")
    parity_starlette = parity.get("repositories", {}).get("starlette_rs")
    if live_starlette != parity_starlette:
        raise ApiBenchmarkError("parity target used a different Starlette-RS source revision")


def _source_tree_sha256_at_revision(root: Path, revision: str) -> str:
    archived = subprocess.run(
        ["git", "-C", str(root), "archive", "--format=tar", revision],
        capture_output=True,
        check=False,
        timeout=120,
    )
    if archived.returncode:
        detail = archived.stderr.decode("utf-8", errors="replace").strip()
        raise ApiBenchmarkError(f"cannot read source snapshot {revision}: {detail}")
    digest = hashlib.sha256()
    try:
        with tarfile.open(fileobj=BytesIO(archived.stdout), mode="r:") as archive:
            members = sorted(
                (member for member in archive.getmembers() if not member.isdir()),
                key=lambda member: member.name.encode("utf-8"),
            )
            for member in members:
                path = member.name.encode("utf-8")
                digest.update(path)
                digest.update(b"\0")
                if member.issym():
                    digest.update(b"symlink\0")
                    digest.update(member.linkname.encode("utf-8"))
                else:
                    content = archive.extractfile(member)
                    if content is None:
                        raise ApiBenchmarkError(f"cannot read source snapshot file: {member.name}")
                    digest.update(b"file\0")
                    while chunk := content.read(1024 * 1024):
                        digest.update(chunk)
                digest.update(b"\0")
    except (OSError, tarfile.TarError) as exc:
        raise ApiBenchmarkError(f"cannot read source snapshot archive {revision}: {exc}") from exc
    return digest.hexdigest()


def _parity_source_snapshot(target_identity: dict[str, Any], starlette_rs_source: Path) -> str:
    if not isinstance(target_identity, dict):
        raise ApiBenchmarkError("parity target source identity is malformed")
    parity_revision = target_identity.get("target_revision")
    parity_tree = target_identity.get("source_tree_sha256")
    if not isinstance(parity_revision, str) or not isinstance(parity_tree, str):
        raise ApiBenchmarkError("parity target source identity is malformed")
    _git(ROOT, "merge-base", "--is-ancestor", parity_revision, "HEAD")
    revisions = [parity_revision]
    later = _git(ROOT, "rev-list", "--first-parent", "--reverse", f"{parity_revision}..HEAD")
    revisions.extend(revision for revision in later.splitlines() if revision)
    starlette_tree = source_tree_sha256(starlette_rs_source.resolve(), "Starlette-RS")
    for revision in reversed(revisions):
        fastapi_tree = _source_tree_sha256_at_revision(ROOT, revision)
        if (
            combine_digests({"fastapi-rs": fastapi_tree, "starlette-rs": starlette_tree})
            == parity_tree
        ):
            return revision
    raise ApiBenchmarkError("cannot locate the exact FastAPI-RS source snapshot used by parity")


def _require_runtime_unchanged_since(snapshot_revision: str) -> None:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "diff",
            "--quiet",
            f"{snapshot_revision}..HEAD",
            "--",
            *TARGET_RUNTIME_PATHS,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if completed.returncode == 1:
        raise ApiBenchmarkError(
            "FastAPI-RS runtime sources changed since the parity-tested source snapshot"
        )
    if completed.returncode:
        raise ApiBenchmarkError(
            f"cannot compare parity source snapshot: {completed.stderr.strip()}"
        )


def _identity_projection(identity: dict[str, Any], subject: str) -> dict[str, Any]:
    if subject == "fastapi":
        return {
            "distribution": identity["distribution"],
            "version": identity["version"],
            "python": identity["python"],
            "platform": identity["platform"],
            "fastapi_source": identity["repositories"]["fastapi_source"],
            "starlette_source": identity["repositories"]["starlette_source"],
            "packages": identity["packages"],
        }
    return {
        "distribution": identity["distribution"],
        "version": identity["version"],
        "python": identity["python"],
        "platform": identity["platform"],
        "target_revision": identity["target_revision"],
        "source_tree_sha256": identity["source_tree_sha256"],
        "target_binary_sha256": identity["target_binary_sha256"],
        "starlette_rs_source": identity["repositories"]["starlette_rs"],
        "packages": identity["packages"],
    }


def _version(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def run_benchmark(
    workload_path: Path,
    comparison_path: Path,
    *,
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
    oracle_python: Path,
    target_python: Path,
) -> tuple[dict[str, Any], Path]:
    (
        workload,
        workload_path,
        workflow,
        input_path,
        parity_workload_path,
        case,
        probe,
    ) = api_contract.load_workload(workload_path, fastapi_source=fastapi_source)
    manifest = read_manifest()
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest_digest = sha256_file(manifest_path)
    input_digest = sha256_file(input_path)
    workload_digest = sha256_file(workload_path)
    parity_workload_digest = sha256_file(parity_workload_path)
    comparison_path = comparison_path if comparison_path.is_absolute() else ROOT / comparison_path
    comparison_path = comparison_path.resolve()
    try:
        comparison_path.relative_to(PARITY_RESULTS_ROOT / "comparisons")
    except ValueError as exc:
        raise ApiBenchmarkError(
            "parity comparison must live under parity-results/comparisons"
        ) from exc
    if not comparison_path.is_file():
        raise ApiBenchmarkError(f"parity comparison does not exist: {comparison_path}")
    comparison_digest = sha256_file(comparison_path)
    comparison = read_json(comparison_path)
    if not isinstance(comparison, dict):
        raise ApiBenchmarkError("parity comparison artifact must be a JSON object")
    if (
        comparison.get("status") != "completed"
        or comparison.get("manifest", {}).get("sha256") != manifest_digest
        or comparison.get("input", {}).get("path") != _relative(input_path)
        or comparison.get("input", {}).get("sha256") != input_digest
    ):
        raise ApiBenchmarkError("parity comparison is stale or references a different input")
    summary = comparison.get("summary", {})
    if summary != {"selected": 1, "passed": 1, "failed": 0, "not_run": 0}:
        raise ApiBenchmarkError(f"single-case parity gate did not pass: {summary}")
    selected_comparisons = [
        row for row in comparison.get("cases", []) if row.get("case_id") == case["case_id"]
    ]
    if len(selected_comparisons) != 1 or selected_comparisons[0].get("outcome") != "pass":
        raise ApiBenchmarkError("selected API case is not a passing parity result")

    source_reference = comparison.get("source_result", {})
    target_reference = comparison.get("target_result", {})
    source_result, source_path = _read_parity_artifact(
        source_reference.get("path", ""), source_reference.get("sha256", ""), "oracle"
    )
    target_result, target_path = _read_parity_artifact(
        target_reference.get("path", ""), target_reference.get("sha256", ""), "target"
    )
    for label, artifact in (("source", source_result), ("target", target_result)):
        if artifact.get("manifest", {}).get("sha256") != manifest_digest:
            raise ApiBenchmarkError(f"parity {label} result uses a different manifest")
        if artifact.get("input", {}).get("sha256") != input_digest:
            raise ApiBenchmarkError(f"parity {label} result uses a different input")
        if (
            artifact.get("workload", {}).get("path")
            != parity_workload_path.relative_to(ROOT).as_posix()
            or artifact.get("workload", {}).get("sha256") != parity_workload_digest
        ):
            raise ApiBenchmarkError(f"parity {label} result uses a different workload")
    if source_result.get("run_id") != source_reference.get("run_id"):
        raise ApiBenchmarkError("parity source run ID differs from its comparison reference")
    if target_result.get("run_id") != target_reference.get("run_id"):
        raise ApiBenchmarkError("parity target run ID differs from its comparison reference")

    source_identity = source_result["identity"]
    if (
        source_identity.get("version") != manifest["oracle_profile"]["packages"]["fastapi"]
        or source_identity.get("repositories", {}).get("fastapi_source")
        != manifest["oracle_profile"]["source_commits"]["fastapi"]
        or source_identity.get("repositories", {}).get("starlette_source")
        != manifest["oracle_profile"]["source_commits"]["starlette"]
    ):
        raise ApiBenchmarkError("parity source identity differs from the pinned oracle profile")
    target_identity = target_result["identity"]
    target_profile = {
        "python": manifest["oracle_profile"]["python"],
        "shared_runtime_packages": {
            name: version
            for name, version in manifest["oracle_profile"]["packages"].items()
            if name in SHARED_ORACLE_PACKAGES
        },
        "target": dict(manifest["target"]),
    }
    current_tree = fastapi_rs_source_tree_sha256(ROOT, starlette_rs_source.resolve())
    if _git(ROOT, "status", "--porcelain"):
        raise ApiBenchmarkError("FastAPI-RS target checkout must be clean for benchmarking")
    if _git(starlette_rs_source.resolve(), "status", "--porcelain"):
        raise ApiBenchmarkError("Starlette-RS source checkout must be clean for benchmarking")
    parity_snapshot_revision = _parity_source_snapshot(target_identity, starlette_rs_source)
    _require_runtime_unchanged_since(parity_snapshot_revision)

    source = _run_worker(
        oracle_python,
        "fastapi",
        workload_path,
        input_path,
        manifest_digest,
        input_digest,
        workload_digest,
        parity_workload_digest,
        workload,
        manifest["oracle_profile"],
        fastapi_source,
        starlette_source,
        starlette_rs_source,
    )
    target = _run_worker(
        target_python,
        "fastapi-rs",
        workload_path,
        input_path,
        manifest_digest,
        input_digest,
        workload_digest,
        parity_workload_digest,
        workload,
        target_profile,
        fastapi_source,
        starlette_source,
        starlette_rs_source,
    )
    source_observation = _reference_observation(source_result, case["case_id"], probe["probe_id"])
    target_observation = _reference_observation(target_result, case["case_id"], probe["probe_id"])
    if source.get("correctness_observation") != source_observation:
        raise ApiBenchmarkError("source benchmark preflight differs from its parity observation")
    if target.get("correctness_observation") != target_observation:
        raise ApiBenchmarkError("target benchmark preflight differs from its parity observation")
    if source.get("correctness_observation") != target.get("correctness_observation"):
        raise ApiBenchmarkError("source and target benchmark preflights differ")
    if (
        source.get("python") != workload["python_identity"]
        or target.get("python") != workload["python_identity"]
    ):
        raise ApiBenchmarkError("benchmark subjects did not use the pinned Python identity")
    if source.get("identity") != source_identity:
        raise ApiBenchmarkError("live FastAPI benchmark identity differs from parity")
    _same_target_build_identity(target["identity"], target_identity, current_tree)
    if source.get("host") != target.get("host"):
        raise ApiBenchmarkError(
            "source and target benchmark subjects ran on different host identities"
        )
    host_identity = source["host"]

    for measurement in (source, target):
        measurement.pop("correctness_observation")
        measurement.pop("python")
        measurement.pop("host")
    source_measurement = {key: value for key, value in source.items() if key != "subject"}
    source_measurement["identity"] = _identity_projection(source["identity"], "fastapi")
    target_measurement = {key: value for key, value in target.items() if key != "subject"}
    target_measurement["identity"] = _identity_projection(target["identity"], "fastapi-rs")

    ratio_values = {
        "fastapi_rs_over_fastapi_median": (
            target_measurement["latency_ns"]["median"] / source_measurement["latency_ns"]["median"]
        ),
        "fastapi_rs_over_fastapi_p95": (
            target_measurement["latency_ns"]["p95"] / source_measurement["latency_ns"]["p95"]
        ),
    }
    result = {
        "schema": api_contract.RESULT_SCHEMA_ID,
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "workload": {
            "id": workload["id"],
            "path": _relative(workload_path),
            "sha256": workload_digest,
            "input_path": _relative(input_path),
            "input_sha256": input_digest,
            "case_id": case["case_id"],
            "probe_id": probe["probe_id"],
            "argument_bundle": workload["input"]["argument_bundle"],
        },
        "parity_gate": {
            "status": "completed",
            "summary": summary,
            "comparison_artifact": _relative(comparison_path),
            "comparison_sha256": comparison_digest,
            "source_result": {
                "path": _relative(source_path),
                "sha256": source_reference["sha256"],
                "run_id": source_result["run_id"],
            },
            "target_result": {
                "path": _relative(target_path),
                "sha256": target_reference["sha256"],
                "run_id": target_result["run_id"],
            },
        },
        "code": {
            "fastapi_source": _git(fastapi_source.resolve(), "rev-parse", "HEAD"),
            "starlette_source": _git(starlette_source.resolve(), "rev-parse", "HEAD"),
            "fastapi_rs_source": _git(ROOT, "rev-parse", "HEAD"),
            "fastapi_rs_tree_sha256": current_tree,
            "starlette_rs_source": _git(starlette_rs_source.resolve(), "rev-parse", "HEAD"),
            "target_binary_sha256": target_identity["target_binary_sha256"],
        },
        "host": host_identity,
        "target_build": {
            "cargo_profile": "release",
            "cargo_features": ["pyo3/extension-module"],
            "rustc": _version(["rustc", "--version", "--verbose"]),
            "cargo": _version(["cargo", "--version", "--verbose"]),
        },
        "subjects": {
            "fastapi": source_measurement,
            "fastapi-rs": target_measurement,
        },
        "ratios": ratio_values,
        "interpretation": (
            "Single-machine cold OpenAPI call baseline; not an ASGI or full-suite claim."
        ),
    }
    api_contract.validate_result(
        result,
        workload=workload,
        workload_path=workload_path,
        input_path=input_path,
        comparison_path=comparison_path,
        comparison_sha256=comparison_digest,
    )
    artifact_path = BENCHMARK_RESULTS_ROOT / f"{result['run_id']}.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result, artifact_path


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if completed.returncode:
        raise ApiBenchmarkError(
            f"Git identity lookup failed for {root}: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def _version(command: list[str]) -> str:
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workload", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--fastapi-source", type=Path, required=True)
    parser.add_argument("--starlette-source", type=Path, required=True)
    parser.add_argument("--starlette-rs-source", type=Path, required=True)
    parser.add_argument("--oracle-python", type=Path, required=True)
    parser.add_argument("--target-python", type=Path, required=True)
    args = parser.parse_args()
    try:
        result, artifact = run_benchmark(
            args.workload,
            args.comparison,
            fastapi_source=args.fastapi_source,
            starlette_source=args.starlette_source,
            starlette_rs_source=args.starlette_rs_source,
            oracle_python=args.oracle_python,
            target_python=args.target_python,
        )
    except (
        ApiBenchmarkError,
        api_contract.ApiBenchmarkContractError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"API benchmark failed: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "completed",
                "run_id": result["run_id"],
                "workload": result["workload"]["id"],
                "sample_count": result["subjects"]["fastapi"]["sample_count"],
                "fastapi_median_ns": result["subjects"]["fastapi"]["latency_ns"]["median"],
                "fastapi_rs_median_ns": result["subjects"]["fastapi-rs"]["latency_ns"]["median"],
                "ratios": result["ratios"],
                "artifact": _relative(artifact),
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
