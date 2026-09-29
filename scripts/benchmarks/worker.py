"""Measure one isolated product process on the shared valid ASGI input."""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import importlib
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


class BenchmarkError(RuntimeError):
    """A benchmark input, product identity, or live observation is invalid."""


def _scope(encoded: dict[str, Any]) -> dict[str, Any]:
    scope = dict(encoded)
    scope["asgi"] = dict(encoded["asgi"])
    scope["query_string"] = encoded["query_string"].encode("ascii")
    scope["headers"] = [
        (name.encode("ascii"), value.encode("utf-8")) for name, value in encoded["headers"]
    ]
    scope["client"] = tuple(encoded["client"]) if encoded["client"] is not None else None
    scope["server"] = tuple(encoded["server"]) if encoded["server"] is not None else None
    raw_path = encoded.get("raw_path_base64")
    scope["raw_path"] = (
        base64.b64decode(raw_path, validate=True) if raw_path else encoded["path"].encode("utf-8")
    )
    scope.pop("raw_path_base64", None)
    return scope


def _receive(events: list[dict[str, Any]]):
    messages = []
    for event in events:
        message = {key: value for key, value in event.items() if key != "bytes_base64"}
        if message.get("type") == "http.request":
            message["body"] = message.get("body", "").encode("utf-8")
        messages.append(message)
    offset = 0

    async def receive() -> dict[str, Any]:
        nonlocal offset
        if offset < len(messages):
            message = messages[offset]
            offset += 1
            return message
        return {"type": "http.disconnect"}

    return receive


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments], check=False, capture_output=True, text=True
    )
    if result.returncode:
        raise BenchmarkError(f"git identity lookup failed in {root}: {result.stderr.strip()}")
    return result.stdout.strip()


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _shared_package_identity(expected: dict[str, str]) -> dict[str, str]:
    packages = {name: importlib.metadata.version(name) for name in expected}
    if packages != expected:
        raise BenchmarkError(f"shared runtime package identity mismatch: {packages}")
    return packages


def _load_factory(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location("fastapi_rs_benchmark_workload", path)
    if spec is None or spec.loader is None:
        raise BenchmarkError(f"cannot load benchmark app workload: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    factory = getattr(module, name, None)
    if not callable(factory):
        raise BenchmarkError(f"benchmark app factory is missing: {name}")
    app = factory()
    if not callable(app):
        raise BenchmarkError("benchmark app factory did not return an ASGI callable")
    return app


def _starlette_control() -> Any:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    async def endpoint(request: Any) -> Any:
        return JSONResponse(
            {
                "item_id": 41,
                "name": "cable",
                "quantity": 2,
                "actor": "reader",
                "color": "blue",
            },
            status_code=201,
        )

    return Starlette(routes=[Route("/items/{item_id}", endpoint, methods=["POST"])])


def _identity(
    kind: str,
    fastapi_root: Path,
    starlette_root: Path,
    starlette_rs_root: Path,
    expected: dict[str, Any],
) -> dict[str, Any]:
    if kind == "starlette-control":
        starlette = importlib.import_module("starlette")
        starlette_commit = _git(starlette_root, "rev-parse", "HEAD")
        if starlette_commit != expected["starlette_source"]:
            raise BenchmarkError("Starlette control source revision is not pinned 1.6.0")
        if not Path(starlette.__file__).resolve().is_relative_to(starlette_root / "starlette"):
            raise BenchmarkError("Starlette control imported outside the pinned 1.6.0 source")
        if importlib.metadata.version("starlette") != expected["starlette_version"]:
            raise BenchmarkError("Starlette control distribution version differs from manifest")
        return {
            "starlette": expected["starlette_version"],
            "starlette_source": starlette_commit,
            "shared_packages": _shared_package_identity(expected["shared_packages"]),
        }

    fastapi = importlib.import_module("fastapi")
    if kind == "fastapi":
        starlette = importlib.import_module("starlette")
        if _git(fastapi_root, "rev-parse", "HEAD") != expected["fastapi_source"]:
            raise BenchmarkError("FastAPI oracle source revision is not pinned 0.141.1")
        if _git(starlette_root, "rev-parse", "HEAD") != expected["starlette_source"]:
            raise BenchmarkError("Starlette oracle source revision is not pinned 1.6.0")
        if importlib.metadata.version("fastapi") != expected["fastapi_version"]:
            raise BenchmarkError("FastAPI oracle distribution version differs from manifest")
        if not Path(fastapi.__file__).resolve().is_relative_to(fastapi_root / "fastapi"):
            raise BenchmarkError("FastAPI oracle imported outside its pinned source")
        if not Path(starlette.__file__).resolve().is_relative_to(starlette_root / "starlette"):
            raise BenchmarkError("Starlette oracle imported outside its pinned source")
        return {
            "fastapi": importlib.metadata.version("fastapi"),
            "fastapi_source": expected["fastapi_source"],
            "starlette": importlib.metadata.version("starlette"),
            "starlette_source": expected["starlette_source"],
            "shared_packages": _shared_package_identity(expected["shared_packages"]),
        }

    try:
        importlib.metadata.version("fastapi")
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        raise BenchmarkError("FastAPI-RS runtime unexpectedly contains FastAPI distribution")
    core = importlib.import_module("fastapi_rs._core")
    starlette_rs = importlib.import_module("starlette_rs_py")
    target_root = ROOT / "fastapi-rs-py/python/fastapi"
    if not Path(fastapi.__file__).resolve().is_relative_to(target_root):
        raise BenchmarkError("FastAPI-RS public facade imported outside the target checkout")
    if not Path(core.__file__).resolve().is_file():
        raise BenchmarkError("FastAPI-RS native extension is missing")
    if (
        not Path(starlette_rs.__file__)
        .resolve()
        .is_relative_to(starlette_rs_root / "starlette-rs-py/python/starlette_rs_py")
    ):
        raise BenchmarkError("Starlette-RS binding imported outside the pinned checkout")
    starlette_rs_commit = _git(starlette_rs_root, "rev-parse", "HEAD")
    if starlette_rs_commit != expected["starlette_rs_source"]:
        raise BenchmarkError("Starlette-RS source revision is not the pinned clean commit")
    if _git(starlette_rs_root, "status", "--porcelain"):
        raise BenchmarkError("Starlette-RS source tree is dirty")
    target_commit = _git(ROOT, "rev-parse", "HEAD")
    if _git(ROOT, "status", "--porcelain"):
        raise BenchmarkError("FastAPI-RS source tree is dirty")
    fastapi_rs_version = importlib.metadata.version("fastapi-rs")
    starlette_rs_version = importlib.metadata.version("starlette-rs-py")
    if fastapi_rs_version != expected["fastapi_rs_version"]:
        raise BenchmarkError("FastAPI-RS package version differs from manifest")
    if starlette_rs_version != expected["starlette_rs_version"]:
        raise BenchmarkError("Starlette-RS package version differs from manifest")
    return {
        "fastapi_rs_source": target_commit,
        "fastapi_rs": fastapi_rs_version,
        "fastapi_rs_native_extension_sha256": _digest(Path(core.__file__).resolve()),
        "starlette_rs": starlette_rs_version,
        "starlette_rs_source": starlette_rs_commit,
        "shared_packages": _shared_package_identity(expected["shared_packages"]),
    }


def _signature(messages: list[dict[str, Any]]) -> dict[str, Any]:
    starts = [message for message in messages if message.get("type") == "http.response.start"]
    if len(starts) != 1:
        raise BenchmarkError(f"expected one ASGI response start; got {len(starts)}")
    start = starts[0]
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message.get("type") == "http.response.body"
    )
    headers = start.get("headers", [])
    return {
        "status": start.get("status"),
        "headers": [[bytes(name).hex(), bytes(value).hex()] for name, value in headers],
        "body_hex": body.hex(),
    }


def _percentile(samples: list[int], percent: float) -> int:
    ordered = sorted(samples)
    index = round((len(ordered) - 1) * percent / 100)
    return ordered[index]


async def _measure(app: Any, action: dict[str, Any], warmups: int, rounds: int, count: int):
    base_scope = _scope(action["scope"])
    receive_events = action["receive_events"]

    async def invoke() -> tuple[int, dict[str, Any]]:
        scope = dict(base_scope)
        messages: list[dict[str, Any]] = []
        receive = _receive(receive_events)

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        start = time.perf_counter_ns()
        await app(scope, receive, send)
        elapsed = time.perf_counter_ns() - start
        return elapsed, _signature(messages)

    baseline = (await invoke())[1]
    for _ in range(warmups):
        observation = (await invoke())[1]
        if observation != baseline:
            raise BenchmarkError("warmup response differs from the untimed correctness call")

    samples: list[int] = []
    loop_start = time.perf_counter_ns()
    for _ in range(rounds):
        for _ in range(count):
            elapsed, observation = await invoke()
            if observation != baseline:
                raise BenchmarkError("measured response differs from the untimed correctness call")
            samples.append(elapsed)
    loop_elapsed = time.perf_counter_ns() - loop_start
    summary = {
        "sample_count": len(samples),
        "warmup_count": warmups,
        "rounds": rounds,
        "samples_per_round": count,
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
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind", choices=["fastapi", "fastapi-rs", "starlette-control"], required=True
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--app-workload", type=Path, required=True)
    parser.add_argument("--factory", required=True)
    parser.add_argument("--warmups", type=int, required=True)
    parser.add_argument("--rounds", type=int, required=True)
    parser.add_argument("--samples-per-round", type=int, required=True)
    parser.add_argument("--identities-json", required=True)
    parser.add_argument("--fastapi-source", type=Path, required=True)
    parser.add_argument("--starlette-source", type=Path, required=True)
    parser.add_argument("--starlette-rs-source", type=Path, required=True)
    args = parser.parse_args()

    workload = json.loads(args.input.read_text(encoding="utf-8"))
    expected = json.loads(args.identities_json)
    selected = [case for case in workload["cases"] if case["case_id"] == args.case_id]
    if len(selected) != 1 or len(selected[0]["actions"]) != 1:
        raise BenchmarkError(f"expected one action for benchmark case {args.case_id}")
    action = selected[0]["actions"][0]

    identity = _identity(
        args.kind,
        args.fastapi_source.resolve(),
        args.starlette_source.resolve(),
        args.starlette_rs_source.resolve(),
        expected,
    )
    if args.kind == "starlette-control":
        app = _starlette_control()
    else:
        app = _load_factory(args.app_workload.resolve(), args.factory)

    result = asyncio.run(
        _measure(
            app,
            action,
            args.warmups,
            args.rounds,
            args.samples_per_round,
        )
    )
    result.update(
        {
            "subject": args.kind,
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
            "generated_at": datetime.now(UTC).isoformat(),
        }
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BenchmarkError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"benchmark worker: {error}", file=sys.stderr)
        raise SystemExit(2) from error
