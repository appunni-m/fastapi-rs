"""Run direct public Python API probes in an identity-checked oracle process."""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import importlib
import inspect
import json
import math
import re
import sys
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scripts.parity.worker import (
    ORACLE_PROFILE_ID,
    ROOT,
    WorkerError,
    _is_under,
    _load_workload,
    _oracle_identity,
    _sha256_file,
    _validate_workload_path,
)

WORKFLOW_SCHEMA_ID = "fastapi-rs/python-api-workflow@1"
WORKFLOW_SCHEMA_V2_ID = "fastapi-rs/python-api-workflow@2"
WORKFLOW_SCHEMA_IDS = frozenset({WORKFLOW_SCHEMA_ID, WORKFLOW_SCHEMA_V2_ID})
RESULT_SCHEMA_ID = "fastapi-rs/python-api-workflow-result@2"
RESULT_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow-result@3"
RESULT_SCHEMA_IDS_BY_WORKFLOW = {
    WORKFLOW_SCHEMA_ID: RESULT_SCHEMA_ID,
    WORKFLOW_SCHEMA_V2_ID: RESULT_SCHEMA_V3_ID,
}
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
ATLAS_SCHEMA_ID = "fastapi-rs/compatibility-atlas@2"
INDEX_SCHEMA_ID = "fastapi-rs/materialized-input-index@1"
_MODULE_PATH = re.compile(r"fastapi(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
_ATTRIBUTE_PATH = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
PINNED_AUTHORITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    },
}


def _error_record(error: Exception) -> dict[str, str]:
    error_type = type(error)
    return {
        "class": f"{error_type.__module__}.{error_type.__qualname__}",
        "message": str(error),
    }


def _json_safe(value: Any) -> Any:
    """Project a Python result into strict JSON data, rejecting non-JSON values."""
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        return json.loads(encoded, parse_constant=_reject_constant)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError(
            f"public callable returned a value that is not strict JSON: {exc}"
        ) from exc


class _NonFiniteFloat:
    """Temporary marker used only while projecting non-finite JSON numbers."""

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value


def _json_safe_with_nonfinite(value: Any) -> tuple[Any, list[dict[str, str]]]:
    """Project JSON data while retaining non-finite float paths as sidecar metadata."""
    labels = {
        "NaN": "nan",
        "Infinity": "positive_infinity",
        "-Infinity": "negative_infinity",
    }
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=True,
            separators=(",", ":"),
        )
        decoded = json.loads(
            encoded,
            parse_constant=lambda token: _NonFiniteFloat(labels[token]),
        )
        sidecar: list[dict[str, str]] = []

        def replace_nonfinite(item: Any, path: str) -> Any:
            if isinstance(item, _NonFiniteFloat):
                sidecar.append({"path": path, "value": item.value})
                return None
            if isinstance(item, list):
                return [
                    replace_nonfinite(child, f"{path}/{index}") for index, child in enumerate(item)
                ]
            if isinstance(item, dict):
                return {
                    key: replace_nonfinite(
                        child, f"{path}/{key.replace('~', '~0').replace('/', '~1')}"
                    )
                    for key, child in item.items()
                }
            return item

        projected = replace_nonfinite(decoded, "")
        sidecar.sort(key=lambda record: record["path"])
        return projected, sidecar
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError(
            f"public callable returned a value that is not JSON-compatible: {exc}"
        ) from exc


def _signature_object_identity(value: Any, kind: str) -> dict[str, str] | None:
    module = getattr(value, "__module__", None)
    qualified_name = getattr(value, "__qualname__", None)
    if not isinstance(module, str) or not isinstance(qualified_name, str):
        return None
    return {"kind": kind, "qualified_name": f"{module}.{qualified_name}"}


def _is_strict_json_value(value: Any, *, depth: int = 0) -> bool:
    """Accept only values whose JSON projection preserves their Python types."""
    if value is None or type(value) in {bool, int, str}:
        return True
    if type(value) is float:
        return math.isfinite(value)
    if depth >= 64:
        return False
    if type(value) is list:
        return all(_is_strict_json_value(item, depth=depth + 1) for item in value)
    if type(value) is dict:
        return all(
            type(key) is str and _is_strict_json_value(item, depth=depth + 1)
            for key, item in value.items()
        )
    return False


def _signature_component(value: Any, *, depth: int = 0) -> Any:
    """Keep JSON defaults exact and encode FastAPI wrapper/type/callable defaults by identity."""
    if value is inspect.Signature.empty:
        return None
    if depth > 8:
        raise WorkerError("signature default projection exceeded its nesting limit")
    if _is_strict_json_value(value):
        return _json_safe(value)
    value_type = type(value)
    qualified_type = f"{value_type.__module__}.{value_type.__qualname__}"

    if qualified_type == "fastapi.datastructures.DefaultPlaceholder":
        return {
            "kind": "fastapi_default_placeholder",
            "value": _signature_component(value.value, depth=depth + 1),
        }
    if inspect.isclass(value):
        identity = _signature_object_identity(value, "class")
        if identity is not None:
            return identity
    elif inspect.isroutine(value):
        identity = _signature_object_identity(value, "callable")
        if identity is not None:
            return identity

    raise WorkerError(
        f"signature default cannot be represented as strict JSON without loss: {qualified_type}"
    ) from None


def _signature_value(function: Any) -> dict[str, Any]:
    signature = inspect.signature(function)
    return {
        "parameters": [
            {
                "name": parameter.name,
                "kind": parameter.kind.name,
                "has_default": parameter.default is not inspect.Parameter.empty,
                "default": _signature_component(parameter.default),
                "annotation": (
                    None
                    if parameter.annotation is inspect.Parameter.empty
                    else str(parameter.annotation)
                ),
            }
            for parameter in signature.parameters.values()
        ],
        "return_annotation": (
            None
            if signature.return_annotation is inspect.Signature.empty
            else str(signature.return_annotation)
        ),
    }


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite number is not strict JSON: {value}")


def _resolve_public_callable(
    spec: dict[str, str], fastapi_root: Path, supported_symbols: frozenset[str]
) -> Any:
    _require_supported_callable(spec, supported_symbols)
    module_name = spec["module"]
    module = importlib.import_module(module_name)
    module_file = getattr(module, "__file__", None)
    if module_file is None or not _is_under(Path(module_file), fastapi_root / "fastapi"):
        raise WorkerError(f"public module is outside the pinned FastAPI source: {module_name}")
    value: Any = module
    for segment in spec["attribute"].split("."):
        value = getattr(value, segment)
    if not callable(value):
        raise TypeError(f"public attribute is not callable: {module_name}.{spec['attribute']}")
    return value


def _require_supported_callable(spec: dict[str, str], supported_symbols: frozenset[str]) -> str:
    if not isinstance(spec, dict):
        raise WorkerError("direct Python API callable reference is malformed")
    module_name = spec.get("module")
    attribute = spec.get("attribute")
    if (
        not isinstance(module_name, str)
        or not isinstance(attribute, str)
        or _MODULE_PATH.fullmatch(module_name) is None
        or _ATTRIBUTE_PATH.fullmatch(attribute) is None
    ):
        raise WorkerError("direct Python API callable reference is malformed")
    symbol_id = f"{module_name}.{attribute}"
    if symbol_id not in supported_symbols:
        raise WorkerError(
            "direct Python API workflow references a symbol outside the supported "
            f"pinned API atlas: {symbol_id}"
        )
    return symbol_id


def _validate_workflow_callables(
    workflow: dict[str, Any], supported_symbols: frozenset[str]
) -> None:
    cases = workflow.get("cases")
    if not isinstance(cases, list) or not cases:
        raise WorkerError("direct Python API workflow has no valid case list")
    selected: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("probes"), list):
            raise WorkerError("direct Python API workflow case has no valid probe list")
        for probe in case["probes"]:
            if not isinstance(probe, dict):
                raise WorkerError("direct Python API workflow probe is malformed")
            selected.add(
                _require_supported_callable(probe.get("public_callable", {}), supported_symbols)
            )
    if not selected:
        raise WorkerError("direct Python API workflow contains no supported callable probes")


def _validate_argument_bundles(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise WorkerError("workload factory must return a non-empty mapping of argument bundles")
    if any(not isinstance(name, str) for name in value):
        raise WorkerError("argument bundle names must be strings")
    return value


def _get_arguments(
    bundles: Mapping[str, Any], name: str
) -> tuple[list[Any] | tuple[Any, ...], dict[str, Any]]:
    if name not in bundles:
        raise WorkerError(f"workload does not provide argument bundle: {name}")
    bundle = bundles[name]
    if not isinstance(bundle, Mapping) or set(bundle) != {"args", "kwargs"}:
        raise WorkerError(f"argument bundle must contain exactly args and kwargs: {name}")
    args = bundle["args"]
    kwargs = bundle["kwargs"]
    if not isinstance(args, (list, tuple)):
        raise WorkerError(f"argument bundle args must be a list or tuple: {name}")
    if not isinstance(kwargs, Mapping) or any(not isinstance(key, str) for key in kwargs):
        raise WorkerError(f"argument bundle kwargs must be a mapping with string keys: {name}")
    return args, dict(kwargs)


async def _make_bundles(factory: Any) -> Mapping[str, Any]:
    bundles = factory()
    if inspect.isawaitable(bundles):
        bundles = await bundles
    return _validate_argument_bundles(bundles)


async def _run_probe(
    probe: dict[str, Any],
    bundles: Mapping[str, Any],
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    *,
    allow_nonfinite_floats: bool = False,
) -> dict[str, Any]:
    try:
        function = _resolve_public_callable(
            probe["public_callable"], fastapi_root, supported_symbols
        )
        has_signature_observation = any(
            observation["kind"] == "python_signature" for observation in probe["observations"]
        )
        has_return_value_observation = any(
            observation["kind"] == "python_return_value" for observation in probe["observations"]
        )
        has_call_outcome_observation = any(
            observation["kind"] == "python_call_outcome" for observation in probe["observations"]
        )
        signature = _signature_value(function) if has_signature_observation else None
        result = None
        call_outcome = None
        if has_return_value_observation:
            args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
            result = function(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
        elif has_call_outcome_observation:
            args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
            try:
                result = function(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
            except Exception as exc:
                call_outcome = {"status": "raised", "error": _error_record(exc)}
            else:
                call_outcome = {"status": "returned"}

        observations = []
        for index, observation in enumerate(probe["observations"]):
            if observation["kind"] == "python_signature":
                values = {"signature": signature}
            elif observation["kind"] == "python_return_value":
                if allow_nonfinite_floats:
                    projected, nonfinite_floats = _json_safe_with_nonfinite(result)
                    values = {"value": projected}
                    if nonfinite_floats:
                        values["nonfinite_floats"] = nonfinite_floats
                else:
                    values = {"value": _json_safe(result)}
            elif observation["kind"] == "python_call_outcome":
                values = {"outcome": call_outcome}
            else:
                raise WorkerError(f"unsupported direct API observation: {observation['kind']}")
            observations.append({"index": index, "kind": observation["kind"], "values": values})
        return {"probe_id": probe["probe_id"], "status": "completed", "observations": observations}
    except WorkerError:
        raise
    except Exception as exc:
        return {
            "probe_id": probe["probe_id"],
            "status": "product_error",
            "error": _error_record(exc),
            "observations": [],
        }


async def _run_case(
    case: dict[str, Any],
    factory: Any,
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    *,
    allow_nonfinite_floats: bool = False,
) -> dict[str, Any]:
    bundles = await _make_bundles(factory)
    probes = []
    for probe in case["probes"]:
        probes.append(
            await _run_probe(
                probe,
                bundles,
                fastapi_root,
                supported_symbols,
                allow_nonfinite_floats=allow_nonfinite_floats,
            )
        )
    errors = [probe["error"] for probe in probes if probe["status"] == "product_error"]
    result: dict[str, Any] = {
        "case_id": case["case_id"],
        "status": "product_error" if errors else "completed",
        "probes": probes,
    }
    if errors:
        result["error"] = errors[0]
    return result


async def _run_cases(
    workflow: dict[str, Any],
    factory: Any,
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    *,
    allow_nonfinite_floats: bool = False,
) -> list[dict[str, Any]]:
    cases = []
    for case in workflow["cases"]:
        cases.append(
            await _run_case(
                case,
                factory,
                fastapi_root,
                supported_symbols,
                allow_nonfinite_floats=allow_nonfinite_floats,
            )
        )
    return cases


def _strict_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise WorkerError(f"duplicate object key in pinned API atlas: {key}")
        result[key] = value
    return result


def _manifest_artifact_ref(
    manifest_text: str, artifact_name: str, schema_id: str
) -> tuple[str, str]:
    """Read one narrow, fixed YAML artifact reference without oracle-only packages."""
    lines = manifest_text.splitlines()
    section_headers = [index for index, line in enumerate(lines) if line == "source_artifacts:"]
    if len(section_headers) != 1:
        raise WorkerError("manifest must contain exactly one source_artifacts mapping")
    section_start = section_headers[0] + 1
    section_end = next(
        (
            index
            for index in range(section_start, len(lines))
            if lines[index] and not lines[index][0].isspace()
        ),
        len(lines),
    )
    artifact_headers = [
        index
        for index in range(section_start, section_end)
        if lines[index] == f"  {artifact_name}:"
    ]
    if len(artifact_headers) != 1:
        raise WorkerError(f"manifest must contain exactly one {artifact_name} reference")
    artifact_start = artifact_headers[0] + 1
    atlas_end = next(
        (
            index
            for index in range(artifact_start, section_end)
            if lines[index] and not lines[index].startswith("    ")
        ),
        section_end,
    )
    fields: dict[str, str] = {}
    for line in lines[artifact_start:atlas_end]:
        match = re.fullmatch(r"    (path|schema|sha256): ([^\s#]+)", line)
        if match:
            key, value = match.groups()
            if key in fields:
                raise WorkerError(f"duplicate {artifact_name} field: {key}")
            fields[key] = value
    if (
        not fields.get("path")
        or fields.get("schema") != schema_id
        or re.fullmatch(r"[a-f0-9]{64}", fields.get("sha256", "")) is None
    ):
        raise WorkerError(f"manifest {artifact_name} reference is missing or unsupported")
    return fields["path"], fields["sha256"]


def _read_pinned_artifact(manifest_text: str, artifact_name: str, schema_id: str) -> dict[str, Any]:
    artifact_relative_path, artifact_digest = _manifest_artifact_ref(
        manifest_text, artifact_name, schema_id
    )
    artifact_path = (ROOT / artifact_relative_path).resolve()
    if not _is_under(artifact_path, ROOT) or _sha256_file(artifact_path) != artifact_digest:
        raise WorkerError(f"{artifact_name} digest differs from its manifest pin")
    try:
        artifact = json.loads(
            artifact_path.read_text(encoding="utf-8"), object_pairs_hook=_strict_json_pairs
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkerError(f"cannot read pinned {artifact_name}: {exc}") from exc
    if not isinstance(artifact, dict) or artifact.get("schema") != schema_id:
        raise WorkerError(f"{artifact_name} schema identity is unsupported")
    return artifact


def _trusted_supported_symbols(manifest_sha256: str) -> frozenset[str]:
    """Load the allowlist only from the manifest-digested, pinned FastAPI atlas."""
    if re.fullmatch(r"[a-f0-9]{64}", manifest_sha256) is None:
        raise WorkerError("manifest digest is malformed")
    if _sha256_file(MANIFEST_PATH) != manifest_sha256:
        raise WorkerError("manifest changed after host-side API workflow validation")
    try:
        manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkerError(f"cannot read pinned contract manifest: {exc}") from exc
    atlas = _read_pinned_artifact(manifest_text, "compatibility_atlas", ATLAS_SCHEMA_ID)
    authorities = atlas.get("authorities")
    if not isinstance(authorities, dict):
        raise WorkerError("compatibility atlas has no source authorities")
    for name, expected in PINNED_AUTHORITIES.items():
        authority = authorities.get(name)
        if not isinstance(authority, dict) or any(
            authority.get(key) != value for key, value in expected.items()
        ):
            raise WorkerError(
                f"compatibility atlas does not select pinned {name} {expected['version']}"
            )
    candidates = atlas.get("api_candidates")
    if not isinstance(candidates, list):
        raise WorkerError("compatibility atlas API candidates are malformed")
    supported = {
        candidate["id"]
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("classification") == "supported"
        and isinstance(candidate.get("id"), str)
    }
    if not supported:
        raise WorkerError("compatibility atlas has no supported API candidates")
    return frozenset(supported)


def _validate_indexed_workflow(
    manifest_sha256: str,
    workflow: dict[str, Any],
    workflow_path: Path,
    input_sha256: str,
    workload_sha256: str,
    fastapi_root: Path,
) -> None:
    """Require the worker input, callable evidence, and workload to be indexed."""
    if _sha256_file(MANIFEST_PATH) != manifest_sha256:
        raise WorkerError("manifest changed after host-side API workflow validation")
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    index = _read_pinned_artifact(manifest_text, "materialized_input_index", INDEX_SCHEMA_ID)
    if index.get("authority") != {"fastapi": "0.141.1", "starlette": "1.6.0"}:
        raise WorkerError("materialized input index does not select the pinned source contract")
    relative_input = workflow_path.relative_to(ROOT).as_posix()
    matching = [
        row for row in index.get("workflows", []) if row.get("input_path") == relative_input
    ]
    if len(matching) != 1:
        raise WorkerError("direct API workflow is not uniquely indexed as a materialized input")
    indexed = matching[0]
    workload_path = workflow["workload"]["file"]
    if (
        indexed.get("input_sha256") != input_sha256
        or indexed.get("workload_path") != workload_path
        or indexed.get("workload_sha256") != workload_sha256
        or set(indexed.get("case_ids", [])) != {case.get("case_id") for case in workflow["cases"]}
    ):
        raise WorkerError("direct API workflow differs from its materialized input index entry")

    atlas = _read_pinned_artifact(manifest_text, "compatibility_atlas", ATLAS_SCHEMA_ID)
    coverage_by_id = {
        row.get("id"): row for row in atlas.get("coverage_matrix", []) if isinstance(row, dict)
    }
    mappings = [
        row for row in index.get("mappings", []) if row.get("workflow_id") == indexed.get("id")
    ]
    for case in workflow["cases"]:
        evidence = {(row.get("path"), row.get("kind")) for row in case["source_evidence"]}
        for source_evidence in case["source_evidence"]:
            source_path = (fastapi_root / source_evidence["path"]).resolve()
            if (
                not _is_under(source_path, fastapi_root)
                or not source_path.is_file()
                or _sha256_file(source_path) != source_evidence["sha256"]
            ):
                raise WorkerError(
                    f"direct API source evidence digest is stale: {source_evidence['path']}"
                )
        mapped: set[tuple[str, str]] = set()
        for mapping in mappings:
            if case["case_id"] not in mapping.get("case_ids", []):
                continue
            source = coverage_by_id.get(mapping.get("source_item_id"))
            if not isinstance(source, dict):
                raise WorkerError("materialized API mapping references missing source evidence")
            kind = (
                "upstream_documentation"
                if source.get("kind") == "documented_feature_page"
                else "upstream_test"
            )
            mapped.add((source.get("source_path"), kind))
        if not mapped or not mapped <= evidence:
            raise WorkerError(
                f"direct API workflow case lacks indexed source evidence: {case['case_id']}"
            )


def _validate_result_consistency(cases: list[dict[str, Any]]) -> None:
    """Ensure status, error, and observation fields agree before emitting results."""
    for case in cases:
        probe_errors = [
            probe.get("error") for probe in case["probes"] if probe.get("status") == "product_error"
        ]
        for probe in case["probes"]:
            status = probe.get("status")
            error_present = "error" in probe
            observations = probe.get("observations")
            if status == "completed" and (error_present or not isinstance(observations, list)):
                raise WorkerError("completed API probe has contradictory error status fields")
            if status == "product_error" and (not error_present or observations != []):
                raise WorkerError("failed API probe must have an error and no observations")
        expected_status = "product_error" if probe_errors else "completed"
        if case.get("status") != expected_status:
            raise WorkerError("API case status does not match its probe statuses")
        if probe_errors:
            if case.get("error") != probe_errors[0]:
                raise WorkerError("failed API case must expose its first probe error")
        elif "error" in case:
            raise WorkerError("completed API case must not expose an error")


def run_oracle(
    input_path: Path,
    fastapi_root: Path,
    starlette_root: Path,
    *,
    input_sha256: str,
    workload_sha256: str,
    manifest_sha256: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    if Path.cwd().resolve() != ROOT:
        raise WorkerError(f"worker must run from the repository root: {ROOT}")
    workflow_path = input_path.resolve()
    try:
        workflow_path.relative_to(ROOT)
    except ValueError as exc:
        raise WorkerError("workflow input must live inside the repository") from exc
    if _sha256_file(workflow_path) != input_sha256:
        raise WorkerError("workflow input changed after host-side validation")
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    if not isinstance(workflow, dict) or workflow.get("schema") not in WORKFLOW_SCHEMA_IDS:
        raise WorkerError("workflow schema identity changed after host-side validation")

    fastapi_root = fastapi_root.resolve()
    starlette_root = starlette_root.resolve()
    workload_path = _validate_workload_path(ROOT / workflow["workload"]["file"])
    try:
        workload_path.relative_to(ROOT)
    except ValueError as exc:
        raise WorkerError("validated workload file resolves outside the repository") from exc
    if _sha256_file(workload_path) != workload_sha256:
        raise WorkerError("workload file changed after host-side validation")

    started = dt.datetime.now(dt.UTC)
    supported_symbols = _trusted_supported_symbols(manifest_sha256)
    _validate_workflow_callables(workflow, supported_symbols)
    _validate_indexed_workflow(
        manifest_sha256,
        workflow,
        workflow_path,
        input_sha256,
        workload_sha256,
        fastapi_root,
    )
    identity = _oracle_identity(fastapi_root, starlette_root, profile)
    factory = _load_workload(workload_path, input_sha256, workflow["workload"]["factory"])
    cases = asyncio.run(
        _run_cases(
            workflow,
            factory,
            fastapi_root,
            supported_symbols,
            allow_nonfinite_floats=workflow["schema"] == WORKFLOW_SCHEMA_V2_ID,
        )
    )
    _validate_result_consistency(cases)
    finished = dt.datetime.now(dt.UTC)
    manifest_path = MANIFEST_PATH
    result = {
        "schema": RESULT_SCHEMA_IDS_BY_WORKFLOW[workflow["schema"]],
        "run_id": str(uuid.uuid4()),
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "product": "oracle",
        "identity": identity,
        "manifest": {"path": manifest_path.relative_to(ROOT).as_posix(), "sha256": manifest_sha256},
        "input": {
            "path": workflow_path.relative_to(ROOT).as_posix(),
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "workload": {
            "path": workload_path.relative_to(ROOT).as_posix(),
            "sha256": workload_sha256,
            "factory": workflow["workload"]["factory"],
        },
        "command": {
            "argv": [sys.executable, "-m", "scripts.parity.api_worker", *sys.argv[1:]],
            "cwd": ".",
        },
        "status": "completed",
        "cases": cases,
        "infrastructure_errors": [],
    }
    expected_cases = [case["case_id"] for case in workflow["cases"]]
    actual_cases = [case["case_id"] for case in cases]
    if actual_cases != expected_cases:
        raise WorkerError("worker case result order or cardinality differs from input")
    for specification, result_case in zip(workflow["cases"], cases, strict=True):
        expected_probes = [probe["probe_id"] for probe in specification["probes"]]
        actual_probes = [probe["probe_id"] for probe in result_case["probes"]]
        if actual_probes != expected_probes:
            raise WorkerError(
                f"worker probe result order or cardinality differs: {result_case['case_id']}"
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--fastapi-source", required=True, type=Path)
    parser.add_argument("--starlette-source", required=True, type=Path)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--workload-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--oracle-profile", required=True)
    args = parser.parse_args()
    try:
        profile = json.loads(args.oracle_profile)
        if not isinstance(profile, dict) or profile.get("id") != ORACLE_PROFILE_ID:
            raise WorkerError("worker received an unsupported oracle profile")
        result = run_oracle(
            args.input,
            args.fastapi_source,
            args.starlette_source,
            input_sha256=args.input_sha256,
            workload_sha256=args.workload_sha256,
            manifest_sha256=args.manifest_sha256,
            profile=profile,
        )
    except (WorkerError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
