"""Strict loading and pinned-identity checks for subprocess parity workflows."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from scripts.parity.contract import (
    PROCESS_WORKFLOW_SCHEMA,
    PROCESS_WORKFLOW_SCHEMA_IDS,
    PROCESS_WORKFLOW_SCHEMA_V2,
    PROCESS_WORKFLOW_SCHEMA_V2_ID,
    ROOT,
    ContractError,
    _validate_unique_ids,
    read_json,
    sha256_file,
)

ORACLE_PROCESS_PROFILE_ID = "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-standard"
ORACLE_PROCESS_CORE_PROFILE_ID = "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-core"
ORACLE_PROCESS_PROFILE_IDS = frozenset({ORACLE_PROCESS_PROFILE_ID, ORACLE_PROCESS_CORE_PROFILE_ID})
TARGET_PROCESS_PROFILE_ID = "fastapi-rs-python-consumer"
PROCESS_TREE_MAX_FILES = 128
PROCESS_TREE_MAX_FILE_BYTES = 1_048_576
PROCESS_TREE_MAX_TOTAL_BYTES = 8_388_608
PROCESS_TREE_MAX_PATH_BYTES = 512
PROCESS_REQUEST_MAX_BODY_BYTES = 65_536
PROCESS_REQUEST_MAX_RESPONSE_BYTES = 1_048_576
PROCESS_REQUEST_MAX_HEADER_BYTES = 8_192
PROCESS_REQUEST_MAX_HEADERS = 32
PROCESS_STREAM_MAX_BYTES = 1_048_576
_PROCESS_TREE_PATH = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\Z")
_HTTP_PATH = re.compile(r"/(?!/)[A-Za-z0-9._~!$&'()*+,;=:@%/?-]*\Z")
_HTTP_HEADER_NAME = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")
_WINDOWS_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}


def process_tree_identity(cwd: dict[str, Any]) -> dict[str, Any]:
    """Validate a v2 input tree and return its stable content identity."""
    if not isinstance(cwd, dict) or cwd.get("kind") != "isolated-tree":
        raise ContractError("process v2 cwd must be an isolated input tree")
    files = cwd.get("files")
    if not isinstance(files, list) or len(files) > PROCESS_TREE_MAX_FILES:
        raise ContractError(
            f"process input tree must contain at most {PROCESS_TREE_MAX_FILES} files"
        )

    entries: dict[str, bytes] = {}
    folded_paths: dict[str, str] = {}
    folded_components: dict[str, str] = {}
    total_bytes = 0
    for item in files:
        if not isinstance(item, dict):
            raise ContractError("process input tree entries must be objects")
        relative = item.get("path")
        content = item.get("content")
        if not isinstance(relative, str) or _PROCESS_TREE_PATH.fullmatch(relative) is None:
            raise ContractError(
                f"process input tree path is not a safe relative path: {relative!r}"
            )
        try:
            path_bytes = relative.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ContractError("process input tree paths must use safe ASCII components") from exc
        if len(path_bytes) > PROCESS_TREE_MAX_PATH_BYTES:
            raise ContractError(f"process input tree path is too long: {relative!r}")
        components = relative.split("/")
        if any(
            component in {".", ".."}
            or component.endswith(".")
            or len(component.encode("ascii")) > 255
            for component in components
        ):
            raise ContractError(
                f"process input tree path contains an unsafe component: {relative!r}"
            )
        if any(
            component.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES
            for component in components
        ):
            raise ContractError(f"process input tree path uses a reserved name: {relative!r}")
        if relative in entries:
            raise ContractError(f"process input tree repeats a path: {relative}")
        folded = relative.casefold()
        if folded in folded_paths:
            raise ContractError(
                "process input tree paths collide on a case-insensitive filesystem: "
                f"{folded_paths[folded]!r} and {relative!r}"
            )
        for index in range(1, len(components) + 1):
            prefix = "/".join(components[:index])
            folded_prefix = prefix.casefold()
            previous_prefix = folded_components.get(folded_prefix)
            if previous_prefix is not None and previous_prefix != prefix:
                raise ContractError(
                    "process input tree directory components collide on a case-insensitive "
                    f"filesystem: {previous_prefix!r} and {prefix!r}"
                )
            folded_components[folded_prefix] = prefix
        if not isinstance(content, str):
            raise ContractError(f"process input tree content must be UTF-8 text: {relative}")
        try:
            content_bytes = content.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise ContractError(
                f"process input tree content is not valid UTF-8: {relative}"
            ) from exc
        if len(content_bytes) > PROCESS_TREE_MAX_FILE_BYTES:
            raise ContractError(
                f"process input tree file exceeds {PROCESS_TREE_MAX_FILE_BYTES} bytes: {relative}"
            )
        total_bytes += len(content_bytes)
        if total_bytes > PROCESS_TREE_MAX_TOTAL_BYTES:
            raise ContractError(
                f"process input tree exceeds {PROCESS_TREE_MAX_TOTAL_BYTES} total bytes"
            )
        entries[relative] = content_bytes
        folded_paths[folded] = relative

    paths = sorted(entries)
    path_set = set(paths)
    for relative in paths:
        components = relative.split("/")
        for index in range(1, len(components)):
            parent = "/".join(components[:index])
            if parent in path_set:
                raise ContractError(
                    f"process input tree file is also used as a directory: {parent}"
                )

    digest = hashlib.sha256(b"fastapi-rs-process-input-tree@1\0")
    for relative in paths:
        path_bytes = relative.encode("ascii")
        content_bytes = entries[relative]
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(content_bytes).to_bytes(8, "big"))
        digest.update(content_bytes)
    return {
        "kind": "isolated-tree",
        "tree_sha256": digest.hexdigest(),
        "file_count": len(entries),
        "total_bytes": total_bytes,
    }


def stage_process_tree(cwd: dict[str, Any], root: Path) -> dict[str, Any]:
    """Stage validated UTF-8 inputs below a fresh directory and verify its identity."""
    expected_identity = process_tree_identity(cwd)
    try:
        root_mode = root.lstat().st_mode
    except OSError as exc:
        raise ContractError(f"process input tree staging root is unavailable: {exc}") from exc
    if not stat.S_ISDIR(root_mode) or stat.S_ISLNK(root_mode):
        raise ContractError("process input tree staging root must be a fresh real directory")
    try:
        if next(root.iterdir(), None) is not None:
            raise ContractError("process input tree staging root is not empty")
    except OSError as exc:
        raise ContractError(f"cannot inspect process input tree staging root: {exc}") from exc

    expected_files: dict[str, bytes] = {}
    for item in cwd["files"]:
        relative = item["path"]
        content_bytes = item["content"].encode("utf-8", errors="strict")
        expected_files[relative] = content_bytes
        target = root
        components = relative.split("/")
        for component in components[:-1]:
            target = target / component
            try:
                mode = target.lstat().st_mode
            except FileNotFoundError:
                target.mkdir()
                mode = target.lstat().st_mode
            except OSError as exc:
                raise ContractError(
                    f"cannot stage process input directory {relative}: {exc}"
                ) from exc
            if not stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
                raise ContractError(
                    f"process input tree parent is not a real directory: {relative}"
                )
        target = target / components[-1]
        try:
            with target.open("xb") as stream:
                stream.write(content_bytes)
        except OSError as exc:
            raise ContractError(f"cannot stage process input file {relative}: {exc}") from exc

    staged_files: dict[str, bytes] = {}
    for current_text, directory_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_text)
        for name in directory_names:
            directory = current / name
            mode = directory.lstat().st_mode
            if not stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
                raise ContractError("process input tree staging created a symlink or non-directory")
        for name in file_names:
            path = current / name
            mode = path.lstat().st_mode
            if not stat.S_ISREG(mode) or stat.S_ISLNK(mode):
                raise ContractError("process input tree staging created a symlink or non-file")
            relative = path.relative_to(root).as_posix()
            try:
                staged_files[relative] = path.read_bytes()
                staged_files[relative].decode("utf-8", errors="strict")
            except (OSError, UnicodeDecodeError) as exc:
                raise ContractError(
                    f"cannot verify staged UTF-8 process input {relative}: {exc}"
                ) from exc
    if staged_files != expected_files:
        raise ContractError("staged process input files differ from the declared tree")
    staged_identity = process_tree_identity(
        {
            "kind": "isolated-tree",
            "files": [
                {"path": path, "content": content.decode("utf-8", errors="strict")}
                for path, content in sorted(staged_files.items())
            ],
        }
    )
    if staged_identity != expected_identity:
        raise ContractError("staged process input tree identity differs from the declared tree")
    return staged_identity


def _validate_http_path(value: Any, label: str) -> None:
    if not isinstance(value, str) or _HTTP_PATH.fullmatch(value) is None or "#" in value:
        raise ContractError(f"process v2 {label} must be a safe loopback HTTP path")


def _validate_v2_case(case: dict[str, Any]) -> None:
    process_tree_identity(case["cwd"])
    execution = case["execution"]
    if os.name != "posix":
        raise ContractError("process v2 requires POSIX process-group lifecycle support")
    selected = set(case["observations"])
    process_selectors = {"process.exit_code", "process.stdout", "process.stderr"}
    if execution["kind"] == "command":
        if not process_selectors <= selected:
            raise ContractError("process v2 command cases must observe exit code and both streams")
        if selected - process_selectors:
            raise ContractError("process v2 command cases cannot observe HTTP responses")
        if any("{port}" in value for value in case["argv"]):
            raise ContractError("process v2 command cases cannot use the server port placeholder")
        if any("{port}" in value for value in case["environment"]["set"].values()):
            raise ContractError("process v2 command cases cannot use the server port placeholder")
        return

    _validate_http_path(execution["readiness"]["path"], "readiness path")
    request = execution["request"]
    _validate_http_path(request["path"], "request path")
    if not {"process.exit_code", "http.status"} <= selected:
        raise ContractError("process v2 server cases must observe exit code and http.status")
    if selected & {"process.stdout", "process.stderr"}:
        raise ContractError(
            "process v2 server logs are bounded but excluded because startup output contains "
            "run-specific ports and process identifiers"
        )
    if selected - {"process.exit_code", "http.status", "http.body.bytes"}:
        raise ContractError("process v2 server case selects an unsupported observation")
    body = request["body"].encode("utf-8", errors="strict")
    if len(body) > PROCESS_REQUEST_MAX_BODY_BYTES:
        raise ContractError(
            f"process v2 request body exceeds {PROCESS_REQUEST_MAX_BODY_BYTES} bytes"
        )
    headers = request["headers"]
    if len(headers) > PROCESS_REQUEST_MAX_HEADERS:
        raise ContractError(
            f"process v2 request has more than {PROCESS_REQUEST_MAX_HEADERS} headers"
        )
    configured_budget = (
        execution["readiness"]["timeout_seconds"]
        + request["timeout_seconds"]
        + execution["shutdown"]["grace_seconds"]
    )
    if configured_budget > case["timeout_seconds"]:
        raise ContractError("process v2 server phase timeouts exceed the case timeout budget")
    header_bytes = 0
    seen_headers: set[str] = set()
    forbidden_headers = {
        "connection",
        "content-length",
        "expect",
        "host",
        "proxy-authorization",
        "proxy-connection",
        "transfer-encoding",
        "upgrade",
    }
    for name, value in headers.items():
        if _HTTP_HEADER_NAME.fullmatch(name) is None:
            raise ContractError(f"process v2 request header name is invalid: {name!r}")
        lowered = name.lower()
        if lowered in seen_headers or lowered in forbidden_headers:
            raise ContractError(f"process v2 request header is duplicate or reserved: {name}")
        seen_headers.add(lowered)
        try:
            name_bytes = name.encode("ascii")
            value_bytes = value.encode("ascii")
        except (AttributeError, UnicodeEncodeError) as exc:
            raise ContractError("process v2 request headers must use ASCII text") from exc
        if any(byte < 0x20 or byte == 0x7F for byte in value_bytes):
            raise ContractError(f"process v2 request header contains a control character: {name}")
        header_bytes += len(name_bytes) + len(value_bytes)
    if header_bytes > PROCESS_REQUEST_MAX_HEADER_BYTES:
        raise ContractError(
            f"process v2 request headers exceed {PROCESS_REQUEST_MAX_HEADER_BYTES} bytes"
        )
    server_command = case["argv"][1]
    if server_command not in {"dev", "run"}:
        raise ContractError("process v2 server command must use fastapi dev or fastapi run")
    host_positions = [index for index, value in enumerate(case["argv"]) if value == "--host"]
    explicit_loopback_host = (
        len(host_positions) == 1
        and host_positions[0] + 1 < len(case["argv"])
        and case["argv"][host_positions[0] + 1] == "127.0.0.1"
    )
    safe_default_dev_host = server_command == "dev" and not host_positions
    port_positions = [index for index, value in enumerate(case["argv"]) if value == "--port"]
    port_environment = case["environment"]["set"].get("PORT") == "{port}"
    port_argument = (
        len(port_positions) == 1
        and port_positions[0] + 1 < len(case["argv"])
        and case["argv"][port_positions[0] + 1] == "{port}"
    )
    port_placeholders = sum(value.count("{port}") for value in case["argv"])
    if port_placeholders != int(port_argument):
        raise ContractError("process v2 server argv has an unexpected port placeholder")
    if (
        not (explicit_loopback_host or safe_default_dev_host)
        or any(value.startswith("--host=") for value in case["argv"])
        or any(value.startswith("--port=") for value in case["argv"])
        or (port_argument == port_environment)
        or (not port_argument and port_positions)
        or (port_environment and "PORT" in case["environment"]["unset"])
        or ("PORT" in case["environment"]["set"] and not port_environment)
        or any(
            name != "PORT" and "{port}" in value
            for name, value in case["environment"]["set"].items()
        )
        or any(
            value in {"--uds", "--fd"} or value.startswith(("--uds=", "--fd="))
            for value in case["argv"]
        )
    ):
        raise ContractError(
            "process v2 server must use the safe fastapi dev host default or explicit "
            "--host 127.0.0.1, plus either --port {port} or environment.set.PORT={port} "
            "exclusively; fastapi run requires the explicit loopback host"
        )


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _process_selectors_for_case(case: dict[str, Any], selector_support: dict[str, str]) -> set[str]:
    """Return only requested process selectors currently implemented by the lane."""
    requested = set(case.get("observations", []))
    unknown = requested - selector_support.keys()
    if unknown:
        raise ContractError(
            "process case references unknown observation selectors: " + ", ".join(sorted(unknown))
        )
    return {
        selector
        for selector in requested
        if selector_support.get(selector) in {"supported", "partial"}
    }


def _verify_source_evidence(case: dict[str, Any], source_root: Path) -> None:
    seen: set[str] = set()
    root = source_root.resolve()
    for evidence in case["source_evidence"]:
        relative = evidence["path"]
        if relative in seen:
            raise ContractError(
                f"process case {case['case_id']} repeats source evidence: {relative}"
            )
        seen.add(relative)
        path = (root / relative).resolve()
        if not _is_under(path, root):
            raise ContractError(
                f"process source evidence resolves outside the pinned source tree: {relative}"
            )
        if not path.is_file():
            raise ContractError(f"process source evidence does not exist: {relative}")
        if sha256_file(path) != evidence["sha256"]:
            raise ContractError(f"process source evidence digest is stale: {relative}")


def _verify_profiles(workflow: dict[str, Any]) -> None:
    profiles = workflow["profiles"]
    if not isinstance(profiles, dict):
        raise ContractError("process workflow profiles must be an object")
    oracle_profile_id = profiles.get("oracle")
    if (
        oracle_profile_id not in ORACLE_PROCESS_PROFILE_IDS
        or profiles.get("target") != TARGET_PROCESS_PROFILE_ID
    ):
        raise ContractError("process workflow profiles differ from the pinned profile identities")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read process profile authority: {exc}") from exc
    artifacts = manifest.get("source_artifacts", {}) if isinstance(manifest, dict) else {}
    if not isinstance(artifacts, dict):
        raise ContractError("manifest has no source artifact identities for process profiles")
    profile_name = "core" if oracle_profile_id == ORACLE_PROCESS_CORE_PROFILE_ID else "standard"
    artifact = artifacts.get(f"runtime_api_surface_{profile_name}")
    if not isinstance(artifact, dict):
        raise ContractError(f"manifest {profile_name} runtime surface reference is malformed")
    surface_path = (ROOT / artifact.get("path", "")).resolve()
    if not _is_under(surface_path, ROOT) or not surface_path.is_file():
        raise ContractError(f"manifest {profile_name} runtime surface path is invalid")
    if sha256_file(surface_path) != artifact.get("sha256"):
        raise ContractError(f"manifest {profile_name} runtime surface digest is stale")
    surface = read_json(surface_path)
    authority = surface.get("authority", {}) if isinstance(surface, dict) else {}
    expected_authority = {
        "fastapi": {"version": "0.141.1", "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"},
        "starlette": {"version": "1.6.0", "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"},
        "python": {"implementation": "CPython", "version": "3.12.13"},
    }
    optional_versions = authority.get("optional_package_versions", {})
    if authority.get("fastapi") != expected_authority["fastapi"]:
        raise ContractError(f"{profile_name} process profile does not identify FastAPI 0.141.1")
    if authority.get("starlette") != expected_authority["starlette"]:
        raise ContractError(f"{profile_name} process profile does not identify Starlette 1.6.0")
    if authority.get("python") != expected_authority["python"]:
        raise ContractError(f"{profile_name} process profile does not identify CPython 3.12.13")
    if profile_name == "core":
        if optional_versions:
            raise ContractError("core process profile must not include optional packages")
    elif (
        optional_versions.get("fastapi-cli") != "0.0.32"
        or optional_versions.get("fastapi-cloud-cli") != "0.11.0"
    ):
        raise ContractError("standard process profile must pin fastapi-cli and fastapi-cloud-cli")


def load_process_workflow(
    input_path: Path,
    *,
    source_root: Path | None = None,
) -> tuple[dict[str, Any], Path, str]:
    """Load an input-only process workflow and verify its source/profile identities."""
    workflow_path = input_path if input_path.is_absolute() else ROOT / input_path
    workflow_path = workflow_path.resolve()
    input_root = (ROOT / "tests/fixtures/inputs/parity").resolve()
    if not _is_under(workflow_path, input_root):
        raise ContractError("process workflow inputs must live under tests/fixtures/inputs/parity")
    workflow = read_json(workflow_path)
    if not isinstance(workflow, dict):
        raise ContractError("process workflow input must be a JSON object")
    workflow_schema_id = workflow.get("schema")
    if workflow_schema_id not in PROCESS_WORKFLOW_SCHEMA_IDS:
        raise ContractError(f"unsupported process workflow schema: {workflow_schema_id!r}")
    schema_path = (
        PROCESS_WORKFLOW_SCHEMA_V2
        if workflow_schema_id == PROCESS_WORKFLOW_SCHEMA_V2_ID
        else PROCESS_WORKFLOW_SCHEMA
    )
    schema = read_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema has multiple schema error types.
        raise ContractError(f"process workflow schema is invalid: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema).iter_errors(workflow),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ContractError(f"process workflow input does not match its schema: {details}")

    _verify_profiles(workflow)
    _validate_unique_ids(workflow["cases"], "case_id", "process workflow cases")
    if source_root is None:
        source_root = (ROOT.parent / "fastapi").resolve()
    if not source_root.is_dir():
        raise ContractError(f"pinned FastAPI source checkout does not exist: {source_root}")
    selector_catalog = read_json(ROOT / "tests/fixtures/observation-selectors.json")
    selector_support = {
        row["id"]: row.get("workflow_support")
        for row in selector_catalog.get("selectors", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    for case in workflow["cases"]:
        environment = case["environment"]
        overlap = set(environment["set"]) & set(environment["unset"])
        if overlap:
            raise ContractError(
                f"process case {case['case_id']} both sets and unsets: "
                + ", ".join(sorted(overlap))
            )
        _process_selectors_for_case(case, selector_support)
        if workflow_schema_id == PROCESS_WORKFLOW_SCHEMA_V2_ID:
            _validate_v2_case(case)
        _verify_source_evidence(case, source_root)

    return workflow, workflow_path, sha256_file(workflow_path)
