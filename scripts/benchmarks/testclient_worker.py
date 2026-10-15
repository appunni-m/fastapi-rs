"""Measure one product process through one reused TestClient context."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.machinery
import importlib.metadata
import importlib.util
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


class TestClientBenchmarkError(RuntimeError):
    """A TestClient benchmark input, identity, or live observation is invalid."""


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise TestClientBenchmarkError(
            f"git identity lookup failed in {root}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_digest(root: Path, label: str) -> str:
    """Hash tracked and non-ignored files, including any working-tree edits."""
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        check=False,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise TestClientBenchmarkError(f"cannot enumerate {label} source files: {detail}")
    paths = sorted(set(entry for entry in completed.stdout.split(b"\0") if entry))
    digest = hashlib.sha256()
    for relative_bytes in paths:
        relative = os.fsdecode(relative_bytes)
        path = root / relative
        digest.update(relative_bytes)
        digest.update(b"\0")
        if path.is_symlink():
            digest.update(b"symlink\0")
            digest.update(os.fsencode(os.readlink(path)))
        elif path.is_file():
            digest.update(b"file\0")
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
        else:
            digest.update(b"missing\0")
        digest.update(b"\0")
    return digest.hexdigest()


def _combine_digests(entries: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(entries.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(value.encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _package_versions(expected: dict[str, str]) -> dict[str, str]:
    actual = {name: importlib.metadata.version(name) for name in expected}
    if actual != expected:
        raise TestClientBenchmarkError(
            f"TestClient runtime package identity mismatch: expected {expected}, got {actual}"
        )
    return actual


def _identity(
    kind: str,
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """Verify the selected profile and report the code actually loaded."""
    if kind == "fastapi":
        fastapi = importlib.import_module("fastapi")
        starlette = importlib.import_module("starlette")
        fastapi_revision = _git(fastapi_source, "rev-parse", "HEAD")
        starlette_revision = _git(starlette_source, "rev-parse", "HEAD")
        if fastapi_revision != expected["fastapi_source"]:
            raise TestClientBenchmarkError(
                "FastAPI oracle source revision differs from the expected identity"
            )
        if starlette_revision != expected["starlette_source"]:
            raise TestClientBenchmarkError(
                "Starlette oracle source revision differs from the expected identity"
            )
        if not Path(fastapi.__file__).resolve().is_relative_to(fastapi_source / "fastapi"):
            raise TestClientBenchmarkError("FastAPI oracle imported outside its pinned source")
        if not Path(starlette.__file__).resolve().is_relative_to(starlette_source / "starlette"):
            raise TestClientBenchmarkError("Starlette oracle imported outside its pinned source")
        fastapi_version = importlib.metadata.version("fastapi")
        starlette_version = importlib.metadata.version("starlette")
        if fastapi_version != expected["fastapi_version"]:
            raise TestClientBenchmarkError(
                "FastAPI oracle distribution version differs from its pin"
            )
        if starlette_version != expected["starlette_version"]:
            raise TestClientBenchmarkError(
                "Starlette oracle distribution version differs from its pin"
            )
        _package_versions(expected["shared_packages"])
        return {
            "fastapi": fastapi_version,
            "fastapi_source": fastapi_revision,
            "starlette": starlette_version,
            "starlette_source": starlette_revision,
            "shared_packages": expected["shared_packages"],
        }

    try:
        importlib.metadata.version("fastapi")
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        raise TestClientBenchmarkError("FastAPI-RS runtime unexpectedly contains FastAPI")

    fastapi = importlib.import_module("fastapi")
    core = importlib.import_module("fastapi_rs._core")
    starlette_rs = importlib.import_module("starlette_rs_py")
    starlette_rs_core = importlib.import_module("starlette_rs_py._core")
    target_fastapi_root = (ROOT / "fastapi-rs-py/python/fastapi").resolve()
    if not Path(fastapi.__file__).resolve().is_relative_to(target_fastapi_root):
        raise TestClientBenchmarkError("FastAPI-RS facade imported outside the target checkout")
    core_path = Path(core.__file__).resolve()
    if not core_path.is_file() or not any(
        str(core_path).endswith(suffix) for suffix in importlib.machinery.EXTENSION_SUFFIXES
    ):
        raise TestClientBenchmarkError("FastAPI-RS did not load its compiled native extension")
    starlette_rs_root = (starlette_rs_source / "starlette-rs-py/python/starlette_rs_py").resolve()
    if not Path(starlette_rs.__file__).resolve().is_relative_to(starlette_rs_root):
        raise TestClientBenchmarkError("Starlette-RS binding imported outside the pinned checkout")
    starlette_rs_core_path = Path(starlette_rs_core.__file__).resolve()
    if (
        not starlette_rs_core_path.is_file()
        or not starlette_rs_core_path.is_relative_to(starlette_rs_root)
        or not any(
            str(starlette_rs_core_path).endswith(suffix)
            for suffix in importlib.machinery.EXTENSION_SUFFIXES
        )
    ):
        raise TestClientBenchmarkError("Starlette-RS did not load its pinned compiled extension")
    fastapi_rs_version = importlib.metadata.version("fastapi-rs")
    starlette_rs_version = importlib.metadata.version("starlette-rs-py")
    if fastapi_rs_version != expected["fastapi_rs_version"]:
        raise TestClientBenchmarkError("FastAPI-RS package version differs from its pin")
    if starlette_rs_version != expected["starlette_rs_version"]:
        raise TestClientBenchmarkError("Starlette-RS package version differs from its pin")
    starlette_rs_revision = _git(starlette_rs_source, "rev-parse", "HEAD")
    if starlette_rs_revision != expected["starlette_rs_source"]:
        raise TestClientBenchmarkError("Starlette-RS source revision differs from its pin")
    _package_versions(expected["shared_packages"])
    source_tree_sha256 = _combine_digests(
        {
            "fastapi-rs": _tree_digest(ROOT, "FastAPI-RS"),
            "starlette-rs": _tree_digest(starlette_rs_source, "Starlette-RS"),
        }
    )
    fastapi_extension_sha256 = _digest(core_path)
    starlette_rs_extension_sha256 = _digest(starlette_rs_core_path)
    return {
        "fastapi_rs_source": _git(ROOT, "rev-parse", "HEAD"),
        "fastapi_rs": fastapi_rs_version,
        "fastapi_rs_extension_sha256": fastapi_extension_sha256,
        "starlette_rs_extension_sha256": starlette_rs_extension_sha256,
        "source_tree_sha256": source_tree_sha256,
        "target_binary_sha256": _combine_digests(
            {
                "fastapi_rs._core": fastapi_extension_sha256,
                "starlette_rs_py._core": starlette_rs_extension_sha256,
            }
        ),
        "starlette_rs": starlette_rs_version,
        "starlette_rs_source": starlette_rs_revision,
        "shared_packages": expected["shared_packages"],
    }


def _load_app(path: Path, factory_name: str, factory_input: dict[str, Any]) -> Any:
    spec = importlib.util.spec_from_file_location("fastapi_rs_testclient_workload", path)
    if spec is None or spec.loader is None:
        raise TestClientBenchmarkError(f"cannot load TestClient app workload: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    factory = getattr(module, factory_name, None)
    if not callable(factory):
        raise TestClientBenchmarkError(f"TestClient app factory is missing: {factory_name}")
    app = factory(factory_input, [])
    if not callable(app):
        raise TestClientBenchmarkError("TestClient app factory did not return an ASGI callable")
    return app


def _percentile(samples: list[int], percent: float) -> int:
    ordered = sorted(samples)
    return ordered[round((len(ordered) - 1) * percent / 100)]


def _response(client: Any, path: str, payload: Any) -> tuple[dict[str, Any], int]:
    start = time.perf_counter_ns()
    response = client.post(path, json=payload)
    status = response.status_code
    body = response.content
    elapsed = time.perf_counter_ns() - start
    return {"status": status, "body_hex": body.hex()}, elapsed


def _measure(
    app: Any,
    path: str,
    payload: Any,
    profile_identity: dict[str, Any],
    warmups: int,
    rounds: int,
    samples_per_round: int,
) -> dict[str, Any]:
    testclient = importlib.import_module("fastapi.testclient")
    client_type = getattr(testclient, "TestClient", None)
    if client_type is None:
        raise TestClientBenchmarkError("fastapi.testclient.TestClient is unavailable")
    with client_type(app) as client:
        baseline, _ = _response(client, path, payload)
        for _ in range(warmups):
            observation, _ = _response(client, path, payload)
            if observation != baseline:
                raise TestClientBenchmarkError(
                    "TestClient warmup differs from the baseline response"
                )

        samples: list[int] = []
        loop_start = time.perf_counter_ns()
        for _ in range(rounds):
            for _ in range(samples_per_round):
                observation, elapsed = _response(client, path, payload)
                if observation != baseline:
                    raise TestClientBenchmarkError(
                        "TestClient sample differs from baseline response"
                    )
                samples.append(elapsed)
        loop_elapsed = time.perf_counter_ns() - loop_start

    return {
        "sample_count": len(samples),
        "warmup_count": warmups,
        "rounds": rounds,
        "samples_per_round": samples_per_round,
        "latency_ns": {
            "min": min(samples),
            "median": int(statistics.median(samples)),
            "p95": _percentile(samples, 95),
            "p99": _percentile(samples, 99),
            "max": max(samples),
            "mean": statistics.fmean(samples),
        },
        "request_loop_throughput_per_second": len(samples) * 1_000_000_000 / loop_elapsed,
        "request_loop_elapsed_ns": loop_elapsed,
        "raw_latency_ns": samples,
        "correctness_observation": baseline,
        "profile_identity": profile_identity,
    }


def run(
    *,
    kind: str,
    request: dict[str, Any],
    factory_input: dict[str, Any],
    app_workload: Path,
    factory: str,
    warmups: int,
    rounds: int,
    samples_per_round: int,
    identities: dict[str, Any],
    profile_identity: dict[str, Any],
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
) -> dict[str, Any]:
    if kind not in {"fastapi", "fastapi-rs"}:
        raise TestClientBenchmarkError(f"unsupported TestClient benchmark subject: {kind}")
    if request.get("method") != "POST" or request.get("path") != "/sync/validated":
        raise TestClientBenchmarkError("request JSON differs from the pinned sync-validated POST")
    python_identity = {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
    }
    if python_identity != identities["python"]:
        raise TestClientBenchmarkError(
            "benchmark Python identity mismatch: "
            f"expected {identities['python']}, got {python_identity}"
        )
    identity = _identity(
        kind,
        fastapi_source.resolve(),
        starlette_source.resolve(),
        starlette_rs_source.resolve(),
        identities,
    )
    app = _load_app(app_workload.resolve(), factory, factory_input)
    measurement = _measure(
        app,
        request["path"],
        request["payload"],
        profile_identity,
        warmups,
        rounds,
        samples_per_round,
    )
    measurement.update(
        {
            "subject": kind,
            "selected_action_id": "sync-validated-post",
            "identity": identity,
            "python_identity": python_identity,
            "host": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": os.cpu_count(),
            },
            "generated_at": datetime.now(UTC).isoformat(),
        }
    )
    return measurement


def _object_argument(value: str, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise TestClientBenchmarkError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise TestClientBenchmarkError(f"{label} must be a JSON object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["fastapi", "fastapi-rs"], required=True)
    parser.add_argument("--request-json", required=True)
    parser.add_argument("--factory-input-json", required=True)
    parser.add_argument("--app-workload", type=Path, required=True)
    parser.add_argument("--factory", required=True)
    parser.add_argument("--warmups", type=int, required=True)
    parser.add_argument("--rounds", type=int, required=True)
    parser.add_argument("--samples-per-round", type=int, required=True)
    parser.add_argument("--identities-json", required=True)
    parser.add_argument("--profile-identity-json", required=True)
    parser.add_argument("--fastapi-source", type=Path, required=True)
    parser.add_argument("--starlette-source", type=Path, required=True)
    parser.add_argument("--starlette-rs-source", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        kind=args.kind,
        request=_object_argument(args.request_json, "request-json"),
        factory_input=_object_argument(args.factory_input_json, "factory-input-json"),
        app_workload=args.app_workload,
        factory=args.factory,
        warmups=args.warmups,
        rounds=args.rounds,
        samples_per_round=args.samples_per_round,
        identities=_object_argument(args.identities_json, "identities-json"),
        profile_identity=_object_argument(args.profile_identity_json, "profile-identity-json"),
        fastapi_source=args.fastapi_source,
        starlette_source=args.starlette_source,
        starlette_rs_source=args.starlette_rs_source,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (TestClientBenchmarkError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"TestClient benchmark worker: {error}", file=sys.stderr)
        raise SystemExit(2) from error
