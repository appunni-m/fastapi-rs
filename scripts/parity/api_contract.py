"""Build and verify the per-symbol source contract embedded in the manifest."""

from __future__ import annotations

import ast
import csv
import json
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from scripts.parity.contract import (
    MATERIALIZED_INPUT_INDEX_SCHEMA_ID,
    ContractError,
    load_workflow,
    sha256_file,
)

CONTRACT_SCHEMA = "fastapi-rs/public-api-contract@9"
TARGET_PROFILE = "fastapi-rs-python-consumer"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OVERLAY_SCHEMA = "fastapi-rs/reviewed-api-contract-overlay@7"


def _read_project_metadata() -> dict[str, Any]:
    metadata_path = PROJECT_ROOT / "metadata.yaml"
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ContractError("metadata.yaml must be a mapping")
    return metadata


def _read_reviewed_overlay(metadata: dict[str, Any]) -> dict[str, Any]:
    overlay = metadata.get("reviewed_api_contract_overlay")
    if not isinstance(overlay, dict) or overlay.get("schema") != OVERLAY_SCHEMA:
        raise ContractError("metadata.yaml reviewed API contract overlay is missing or unsupported")
    return overlay


def _pointer(*parts: str | int) -> str:
    escaped = (str(part).replace("~", "~0").replace("/", "~1") for part in parts)
    return "/" + "/".join(escaped)


def _inventory_rows(inventory: dict[str, Any]) -> dict[str, list[str]]:
    pointers: dict[str, list[str]] = defaultdict(list)
    definition_pointers: dict[str, list[str]] = defaultdict(list)

    def add_definition(row: dict[str, Any], pointer: str) -> None:
        pointers[row["id"]].append(pointer)
        definition_pointers[row["id"]].append(pointer)
        for index, member in enumerate(row.get("members", [])):
            add_definition(member, f"{pointer}/members/{index}")

    for module_index, module in enumerate(inventory["modules"]):
        for definition_index, definition in enumerate(module["definitions"]):
            add_definition(
                definition,
                _pointer("modules", module_index, "definitions", definition_index),
            )
    for binding_index, binding in enumerate(inventory["import_bindings"]):
        binding_id = binding["id"]
        pointers[binding_id].append(_pointer("import_bindings", binding_index))
        target_path = binding.get("target_path")
        if isinstance(target_path, str):
            pointers[binding_id].extend(definition_pointers.get(target_path, []))
    return {symbol_id: list(dict.fromkeys(refs)) for symbol_id, refs in pointers.items()}


def _runtime_rows(surface: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    return {
        row["id"]: (_pointer("symbols", index), row) for index, row in enumerate(surface["symbols"])
    }


def _module_id_for_inventory_ref(
    pointer: str, candidate: dict[str, Any], inventory: dict[str, Any]
) -> str:
    if isinstance(candidate.get("module"), str):
        return candidate["module"]
    parts = pointer.strip("/").split("/")
    if parts[0] == "modules":
        return inventory["modules"][int(parts[1])]["id"]
    if parts[0] == "import_bindings":
        return inventory["import_bindings"][int(parts[1])]["module"]
    raise ContractError(f"cannot identify source module for API symbol {candidate['id']}")


def _source_doc_paths(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        path = value.get("path")
        if isinstance(path, str) and path.startswith("docs/en/docs/"):
            paths.add(path)
        for child in value.values():
            paths.update(_source_doc_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.update(_source_doc_paths(child))
    return paths


def _json_pointer_value(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ContractError(f"invalid JSON pointer: {pointer!r}")
    current = document
    for token in pointer[1:].split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        current = current[int(key)] if isinstance(current, list) else current[key]
    return current


def _starlette_rs_artifact_path(starlette_rs: dict[str, Any], field: str) -> Path:
    artifact = starlette_rs.get(field)
    owner = starlette_rs.get("owner")
    if not isinstance(artifact, str) or not isinstance(owner, str):
        raise ContractError(f"pinned Starlette-RS metadata has no {field} path")
    override = os.environ.get("STARLETTE_RS_SOURCE")
    if override:
        owner_hint = Path(owner)
        artifact_hint = Path(artifact)
        try:
            artifact_relative = artifact_hint.relative_to(owner_hint)
        except ValueError as exc:
            raise ContractError(
                f"pinned Starlette-RS {field} path is outside its repository"
            ) from exc
        return Path(override).resolve() / artifact_relative
    return (PROJECT_ROOT / artifact).resolve()


def _verify_starlette_rs_checkout(starlette_rs: dict[str, Any]) -> Path:
    owner = starlette_rs.get("owner")
    expected_commit = starlette_rs.get("commit")
    if not isinstance(owner, str) or not isinstance(expected_commit, str):
        raise ContractError("pinned Starlette-RS checkout identity is incomplete")
    override = os.environ.get("STARLETTE_RS_SOURCE")
    checkout = Path(override).resolve() if override else (PROJECT_ROOT / owner).resolve()
    try:
        observed_commit = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty_state = subprocess.run(
            ["git", "-C", str(checkout), "status", "--porcelain=v1", "--untracked-files=all"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"pinned Starlette-RS checkout cannot be verified: {checkout}") from exc
    if observed_commit != expected_commit:
        raise ContractError(
            "selected Starlette-RS checkout differs from metadata.yaml pin: "
            f"expected {expected_commit}, observed {observed_commit}"
        )
    if dirty_state:
        raise ContractError(f"selected Starlette-RS checkout is dirty: {checkout}")
    return checkout


def _starlette_source_signature_reference(
    project_metadata: dict[str, Any], signature_source: dict[str, Any]
) -> dict[str, Any]:
    """Verify a method signature directly against a clean pinned Starlette source blob."""
    authority = project_metadata.get("authority", {})
    starlette = authority.get("starlette", {}) if isinstance(authority, dict) else {}
    if not isinstance(starlette, dict):
        raise ContractError("metadata.yaml has no pinned Starlette source authority")
    if signature_source.get("repository") != "starlette":
        raise ContractError("inherited source signature must identify the Starlette repository")
    checkout_text = starlette.get("checkout")
    expected_commit = starlette.get("commit")
    version = starlette.get("version")
    if not all(
        isinstance(value, str) and value for value in (checkout_text, expected_commit, version)
    ):
        raise ContractError("pinned Starlette source identity is incomplete")
    override = os.environ.get("STARLETTE_SOURCE")
    checkout = Path(override).resolve() if override else (PROJECT_ROOT / checkout_text).resolve()

    source_path_text = signature_source.get("path")
    if not isinstance(source_path_text, str) or not source_path_text:
        raise ContractError("inherited source signature has no Starlette source path")
    source_relative = Path(source_path_text)
    if source_relative.is_absolute() or ".." in source_relative.parts:
        raise ContractError("inherited Starlette source path must stay inside its checkout")
    source_path = (checkout / source_relative).resolve()
    try:
        source_path.relative_to(checkout)
    except ValueError as exc:
        raise ContractError("inherited Starlette source path escapes its checkout") from exc

    try:
        observed_commit = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        committed_source = subprocess.run(
            ["git", "-C", str(checkout), "show", f"{expected_commit}:{source_relative.as_posix()}"],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"pinned Starlette source cannot be verified: {checkout}") from exc
    if observed_commit != expected_commit:
        raise ContractError(
            "selected Starlette source checkout differs from metadata.yaml pin: "
            f"expected {expected_commit}, observed {observed_commit}"
        )
    if not source_path.is_file():
        raise ContractError(f"pinned Starlette source file is missing: {source_path}")
    source_bytes = source_path.read_bytes()
    if source_bytes != committed_source:
        raise ContractError(
            f"selected Starlette source file differs from its pinned commit blob: {source_path}"
        )

    owner = signature_source.get("owner")
    symbol = signature_source.get("symbol")
    start_line = signature_source.get("start_line")
    end_line = signature_source.get("end_line")
    if (
        not isinstance(owner, str)
        or not owner
        or not isinstance(symbol, str)
        or not symbol
        or not isinstance(start_line, int)
        or isinstance(start_line, bool)
        or not isinstance(end_line, int)
        or isinstance(end_line, bool)
        or end_line < start_line
    ):
        raise ContractError("inherited Starlette source signature identity or range is invalid")
    try:
        tree = ast.parse(source_bytes.decode("utf-8"), filename=source_path_text)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ContractError(
            f"pinned Starlette source is not valid Python: {source_path_text}"
        ) from exc
    owner_definitions = [
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == owner
    ]
    if len(owner_definitions) != 1:
        raise ContractError(
            f"pinned Starlette source class is not unique: {source_path_text}:{owner}"
        )
    method_definitions = [
        node
        for node in owner_definitions[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol
    ]
    matching_methods = [
        node
        for node in method_definitions
        if node.lineno == start_line and getattr(node, "end_lineno", None) == end_line
    ]
    if len(matching_methods) != 1:
        raise ContractError(
            f"pinned Starlette method or exact source range differs: "
            f"{source_path_text}:{owner}.{symbol}"
        )
    method = matching_methods[0]
    signature = ast.unparse(method).splitlines()[0].removesuffix(":")
    module_path = source_relative.with_suffix("").as_posix().replace("/", ".")
    return {
        "repository": "starlette",
        "version": version,
        "commit": expected_commit,
        "source_path": source_path_text,
        "source_operation_id": f"{module_path}.{owner}.{symbol}",
        "owner": owner,
        "symbol": symbol,
        "start_line": start_line,
        "end_line": end_line,
        "signature": signature,
    }


def _starlette_source_attribute_reference(
    project_metadata: dict[str, Any], attribute_source: dict[str, Any]
) -> dict[str, Any]:
    """Verify a Starlette instance-attribute assignment in the pinned source blob."""
    authority = project_metadata.get("authority", {})
    starlette = authority.get("starlette", {}) if isinstance(authority, dict) else {}
    if not isinstance(starlette, dict):
        raise ContractError("metadata.yaml has no pinned Starlette source authority")
    if attribute_source.get("repository") != "starlette":
        raise ContractError("inherited source attribute must identify the Starlette repository")
    checkout_text = starlette.get("checkout")
    expected_commit = starlette.get("commit")
    version = starlette.get("version")
    if not all(
        isinstance(value, str) and value for value in (checkout_text, expected_commit, version)
    ):
        raise ContractError("pinned Starlette source identity is incomplete")
    override = os.environ.get("STARLETTE_SOURCE")
    checkout = Path(override).resolve() if override else (PROJECT_ROOT / checkout_text).resolve()

    source_path_text = attribute_source.get("path")
    if not isinstance(source_path_text, str) or not source_path_text:
        raise ContractError("inherited source attribute has no Starlette source path")
    source_relative = Path(source_path_text)
    if source_relative.is_absolute() or ".." in source_relative.parts:
        raise ContractError("inherited Starlette source path must stay inside its checkout")
    source_path = (checkout / source_relative).resolve()
    try:
        source_path.relative_to(checkout)
    except ValueError as exc:
        raise ContractError("inherited Starlette source path escapes its checkout") from exc

    try:
        observed_commit = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        committed_source = subprocess.run(
            ["git", "-C", str(checkout), "show", f"{expected_commit}:{source_relative.as_posix()}"],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"pinned Starlette source cannot be verified: {checkout}") from exc
    if observed_commit != expected_commit:
        raise ContractError(
            "selected Starlette source checkout differs from metadata.yaml pin: "
            f"expected {expected_commit}, observed {observed_commit}"
        )
    if not source_path.is_file():
        raise ContractError(f"pinned Starlette source file is missing: {source_path}")
    source_bytes = source_path.read_bytes()
    if source_bytes != committed_source:
        raise ContractError(
            f"selected Starlette source file differs from its pinned commit blob: {source_path}"
        )

    owner = attribute_source.get("owner")
    initializer = attribute_source.get("initializer")
    attribute = attribute_source.get("attribute")
    start_line = attribute_source.get("start_line")
    end_line = attribute_source.get("end_line")
    if (
        set(attribute_source)
        != {
            "repository",
            "path",
            "owner",
            "initializer",
            "attribute",
            "start_line",
            "end_line",
        }
        or not isinstance(owner, str)
        or not owner
        or not isinstance(initializer, str)
        or not initializer
        or not isinstance(attribute, str)
        or not attribute
        or not isinstance(start_line, int)
        or isinstance(start_line, bool)
        or not isinstance(end_line, int)
        or isinstance(end_line, bool)
        or end_line < start_line
    ):
        raise ContractError("inherited Starlette attribute identity or range is invalid")
    try:
        tree = ast.parse(source_bytes.decode("utf-8"), filename=source_path_text)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ContractError(
            f"pinned Starlette source is not valid Python: {source_path_text}"
        ) from exc
    owner_definitions = [
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == owner
    ]
    if len(owner_definitions) != 1:
        raise ContractError(
            f"pinned Starlette source class is not unique: {source_path_text}:{owner}"
        )
    initializer_definitions = [
        node
        for node in owner_definitions[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == initializer
    ]
    assignments = [
        node
        for method in initializer_definitions
        for node in ast.walk(method)
        if isinstance(node, ast.Assign)
        and node.lineno == start_line
        and getattr(node, "end_lineno", None) == end_line
        and any(
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
            and target.attr == attribute
            for target in node.targets
        )
    ]
    if len(initializer_definitions) != 1 or len(assignments) != 1:
        raise ContractError(
            "pinned Starlette initializer or exact instance-attribute assignment differs: "
            f"{source_path_text}:{owner}.{initializer}.{attribute}"
        )
    module_path = source_relative.with_suffix("").as_posix().replace("/", ".")
    return {
        "repository": "starlette",
        "version": version,
        "commit": expected_commit,
        "source_path": source_path_text,
        "source_attribute_id": f"{module_path}.{owner}.{attribute}",
        "owner": owner,
        "initializer": initializer,
        "attribute": attribute,
        "start_line": start_line,
        "end_line": end_line,
        "assignment": ast.unparse(assignments[0]),
    }


def _starlette_rs_contract_gap_reference(
    project_metadata: dict[str, Any], gap: dict[str, Any]
) -> dict[str, Any]:
    """Prove a sibling operation is absent or has no canonical reviewed contract."""
    starlette_rs = project_metadata.get("starlette_rs")
    if not isinstance(starlette_rs, dict):
        raise ContractError("metadata.yaml has no pinned Starlette-RS contract")
    _verify_starlette_rs_checkout(starlette_rs)
    metadata_path = _starlette_rs_artifact_path(starlette_rs, "metadata")
    manifest_path = _starlette_rs_artifact_path(starlette_rs, "manifest")
    catalog_path = _starlette_rs_artifact_path(starlette_rs, "api_catalog")
    review_path = _starlette_rs_artifact_path(starlette_rs, "api_review")
    for path in (metadata_path, manifest_path, catalog_path, review_path):
        if not path.is_file():
            raise ContractError(f"pinned Starlette-RS API artifact is missing: {path}")

    sibling_metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    sibling_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(sibling_metadata, dict) or not isinstance(sibling_manifest, dict):
        raise ContractError("pinned Starlette-RS API metadata and manifest must be mappings")
    expected_contract_id = starlette_rs.get("contract_id")
    manifest_contract_pointer = starlette_rs.get("manifest_contract_pointer")
    if not isinstance(expected_contract_id, str) or not isinstance(manifest_contract_pointer, str):
        raise ContractError("pinned Starlette-RS contract identity is incomplete")
    if _json_pointer_value(sibling_manifest, manifest_contract_pointer) != expected_contract_id:
        raise ContractError("pinned Starlette-RS manifest contract identity differs")
    expected_operation_id = gap.get("expected_operation_id")
    reason = gap.get("reason")
    if not isinstance(expected_operation_id, str) or not expected_operation_id:
        raise ContractError("inherited sibling contract gap has no expected operation ID")
    if not isinstance(reason, str) or not reason.strip():
        raise ContractError("inherited sibling contract gap has no review rationale")
    surface_id, operation_name = expected_operation_id.rsplit(".", 1)

    sibling_authority = sibling_metadata.get("authority", {})
    starlette_authority = project_metadata.get("authority", {}).get("starlette", {})
    if sibling_authority.get("revision") != starlette_authority.get(
        "commit"
    ) or sibling_authority.get("version") != starlette_authority.get("version"):
        raise ContractError("pinned Starlette-RS API source is from another Starlette revision")

    api_sources = sibling_metadata.get("api_sources")
    if not isinstance(api_sources, list):
        raise ContractError("pinned Starlette-RS metadata has no reviewed API sources")
    source_surface_matches = [
        (source_index, source)
        for source_index, source in enumerate(api_sources)
        if isinstance(source, dict) and source.get("surface_id") == surface_id
    ]
    if len(source_surface_matches) != 1:
        raise ContractError(
            f"expected one pinned Starlette-RS API source for inherited gap: {surface_id}"
        )
    source_surface_index, source_surface = source_surface_matches[0]
    source_operations = source_surface.get("operations", [])
    if not isinstance(source_operations, list):
        raise ContractError(f"pinned Starlette-RS API source operations are invalid: {surface_id}")
    source_operation_matches = [
        operation
        for operation in source_operations
        if isinstance(operation, dict)
        and (
            operation.get("operation_id") == operation_name
            or operation.get("source_path") == expected_operation_id
        )
    ]
    if source_operation_matches:
        raise ContractError(
            "declared sibling operation gap is stale; operation now exists in API sources: "
            f"{expected_operation_id}"
        )

    surfaces = sibling_manifest.get("surfaces", [])
    if not isinstance(surfaces, list):
        raise ContractError("pinned Starlette-RS manifest surfaces are invalid")
    manifest_surface_matches = [
        (surface_index, surface)
        for surface_index, surface in enumerate(surfaces)
        if isinstance(surface, dict) and surface.get("id") == surface_id
    ]
    if len(manifest_surface_matches) != 1:
        raise ContractError(
            f"expected one pinned Starlette-RS manifest surface for inherited gap: {surface_id}"
        )
    manifest_surface_index, manifest_surface = manifest_surface_matches[0]
    manifest_operations = manifest_surface.get("operations", [])
    if not isinstance(manifest_operations, list):
        raise ContractError(f"pinned Starlette-RS manifest operations are invalid: {surface_id}")
    manifest_operation_matches = [
        operation
        for operation in manifest_operations
        if isinstance(operation, dict)
        and (
            operation.get("id") == operation_name
            or operation.get("source", {}).get("path") == expected_operation_id
        )
    ]
    if manifest_operation_matches:
        raise ContractError(
            "declared sibling operation gap is stale; operation now exists in manifest: "
            f"{expected_operation_id}"
        )

    def csv_rows(path: Path) -> list[tuple[int, dict[str, str]]]:
        with path.open(encoding="utf-8", newline="") as csv_file:
            rows = list(csv.DictReader(csv_file))
        return [(index + 2, row) for index, row in enumerate(rows)]

    catalog_rows = csv_rows(catalog_path)
    review_rows = csv_rows(review_path)

    def matching_csv_row(
        rows: list[tuple[int, dict[str, str]]],
        qualified_name: str,
        *,
        record_type: str | None = None,
        disposition: str | None = None,
    ) -> tuple[int, dict[str, str]]:
        matches = [
            (line, row)
            for line, row in rows
            if row.get("qualified_name") == qualified_name
            and (record_type is None or row.get("record_type") == record_type)
            and (disposition is None or row.get("api_disposition") == disposition)
        ]
        if len(matches) != 1:
            raise ContractError(
                "sibling contract gap must resolve to one Starlette-RS catalog/review row: "
                f"{qualified_name}"
            )
        return matches[0]

    candidate_state = gap.get("candidate_state")
    if candidate_state == "no_exact_row":
        catalog_operation_rows = [
            row for _, row in catalog_rows if row.get("qualified_name") == expected_operation_id
        ]
        review_operation_rows = [
            row for _, row in review_rows if row.get("qualified_name") == expected_operation_id
        ]
        if catalog_operation_rows or review_operation_rows:
            raise ContractError(
                "declared no-exact-row gap is stale; a sibling API catalog or review row exists: "
                f"{expected_operation_id}"
            )
        catalog_line, catalog_row = matching_csv_row(catalog_rows, surface_id, record_type="class")
        review_line, review_row = matching_csv_row(
            review_rows,
            surface_id,
            record_type="class",
            disposition="supported",
        )
        return {
            "contract_id": expected_contract_id,
            "expected_operation_id": expected_operation_id,
            "candidate_state": candidate_state,
            "reason": reason,
            "operation_absent_from_api_sources": True,
            "operation_absent_from_manifest": True,
            "operation_absent_from_api_catalog": True,
            "operation_absent_from_api_review": True,
            "api_source_surface_ref": {
                "path": starlette_rs["metadata"],
                "json_pointer": _pointer("api_sources", source_surface_index),
            },
            "manifest_surface_ref": {
                "path": starlette_rs["manifest"],
                "json_pointer": _pointer("surfaces", manifest_surface_index),
            },
            "api_catalog_surface_ref": {
                "path": starlette_rs["api_catalog"],
                "line": catalog_line,
                "qualified_name": catalog_row.get("qualified_name"),
                "record_type": catalog_row.get("record_type"),
                "audit_status": catalog_row.get("audit_status"),
            },
            "api_review_surface_ref": {
                "path": starlette_rs["api_review"],
                "line": review_line,
                "qualified_name": review_row.get("qualified_name"),
                "record_type": review_row.get("record_type"),
                "api_disposition": review_row.get("api_disposition"),
            },
        }
    if candidate_state is not None:
        raise ContractError(f"unsupported inherited sibling gap candidate_state: {candidate_state}")

    catalog_line, catalog_row = matching_csv_row(catalog_rows, expected_operation_id)
    review_line, review_row = matching_csv_row(
        review_rows, expected_operation_id, disposition="supported"
    )
    return {
        "contract_id": expected_contract_id,
        "expected_operation_id": expected_operation_id,
        "reason": reason,
        "operation_absent_from_api_sources": True,
        "operation_absent_from_manifest": True,
        "api_source_surface_ref": {
            "path": starlette_rs["metadata"],
            "json_pointer": _pointer("api_sources", source_surface_index),
        },
        "manifest_surface_ref": {
            "path": starlette_rs["manifest"],
            "json_pointer": _pointer("surfaces", manifest_surface_index),
        },
        "api_catalog_ref": {
            "path": starlette_rs["api_catalog"],
            "line": catalog_line,
            "audit_status": catalog_row.get("audit_status"),
        },
        "api_review_ref": {
            "path": starlette_rs["api_review"],
            "line": review_line,
            "api_disposition": review_row.get("api_disposition"),
        },
    }


def _starlette_rs_operation_reference(
    project_metadata: dict[str, Any], operation_id: str, *, inherited_kind: str
) -> dict[str, Any]:
    starlette_rs = project_metadata.get("starlette_rs")
    if not isinstance(starlette_rs, dict):
        raise ContractError("metadata.yaml has no pinned Starlette-RS contract")
    _verify_starlette_rs_checkout(starlette_rs)
    metadata_path = _starlette_rs_artifact_path(starlette_rs, "metadata")
    manifest_path = _starlette_rs_artifact_path(starlette_rs, "manifest")
    catalog_path = _starlette_rs_artifact_path(starlette_rs, "api_catalog")
    review_path = _starlette_rs_artifact_path(starlette_rs, "api_review")
    for path in (metadata_path, manifest_path, catalog_path, review_path):
        if not path.is_file():
            raise ContractError(f"pinned Starlette-RS API artifact is missing: {path}")

    sibling_metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    sibling_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(sibling_metadata, dict) or not isinstance(sibling_manifest, dict):
        raise ContractError("pinned Starlette-RS API metadata and manifest must be mappings")
    expected_contract_id = starlette_rs.get("contract_id")
    manifest_contract_pointer = starlette_rs.get("manifest_contract_pointer")
    if not isinstance(expected_contract_id, str) or not isinstance(manifest_contract_pointer, str):
        raise ContractError("pinned Starlette-RS contract identity is incomplete")
    if _json_pointer_value(sibling_manifest, manifest_contract_pointer) != expected_contract_id:
        raise ContractError("pinned Starlette-RS manifest contract identity differs")
    starlette_authority = project_metadata.get("authority", {}).get("starlette", {})
    sibling_authority = sibling_metadata.get("authority", {})
    if sibling_authority.get("revision") != starlette_authority.get(
        "commit"
    ) or sibling_authority.get("version") != starlette_authority.get("version"):
        raise ContractError("pinned Starlette-RS API source is from another Starlette revision")

    surface_id, operation_name = operation_id.rsplit(".", 1)
    api_sources = sibling_metadata.get("api_sources")
    if not isinstance(api_sources, list):
        raise ContractError("pinned Starlette-RS metadata has no reviewed API sources")
    source_matches: list[tuple[int, int]] = []
    for source_index, source in enumerate(api_sources):
        if not isinstance(source, dict) or source.get("surface_id") != surface_id:
            continue
        operations = source.get("operations", [])
        if not isinstance(operations, list):
            continue
        for operation_index, operation in enumerate(operations):
            if (
                isinstance(operation, dict)
                and operation.get("operation_id") == operation_name
                and operation.get("source_path") == operation_id
            ):
                source_matches.append((source_index, operation_index))
    if len(source_matches) != 1:
        raise ContractError(
            "inherited API operation must resolve to one canonical Starlette-RS API source: "
            f"{operation_id}"
        )
    manifest_matches = [
        (surface_index, operation_index, operation)
        for surface_index, surface in enumerate(sibling_manifest.get("surfaces", []))
        if isinstance(surface, dict) and surface.get("id") == surface_id
        for operation_index, operation in enumerate(surface.get("operations", []))
        if isinstance(operation, dict)
        and operation.get("id") == operation_name
        and operation.get("source", {}).get("path") == operation_id
    ]
    if len(manifest_matches) != 1:
        raise ContractError(
            "inherited API operation must resolve to one pinned Starlette-RS manifest row: "
            f"{operation_id}"
        )
    manifest_surface_index, manifest_operation_index, manifest_operation = manifest_matches[0]
    canonical_kind = manifest_operation.get("kind")
    expected_canonical_kind = {
        "inherited_method": "method",
        "inherited_property": "property_get",
    }.get(inherited_kind)
    if expected_canonical_kind is None or canonical_kind != expected_canonical_kind:
        raise ContractError(
            "canonical inherited API operation kind differs from its FastAPI exposure: "
            f"{operation_id} ({inherited_kind} -> {canonical_kind})"
        )
    manifest_targets = manifest_operation.get("targets", [])
    target_support: dict[str, dict[str, Any]] = {}
    for target_id in ("rust-native", "python-package"):
        target_matches = [
            (target_index, target)
            for target_index, target in enumerate(manifest_targets)
            if isinstance(target, dict) and target.get("target_id") == target_id
        ]
        if len(target_matches) != 1:
            raise ContractError(
                "canonical inherited API operation must declare one support row for "
                f"{target_id}: {operation_id}"
            )
        target_index, target = target_matches[0]
        support = target.get("support")
        if not isinstance(support, dict) or not isinstance(support.get("status"), str):
            raise ContractError(
                "canonical inherited API operation has no target support status for "
                f"{target_id}: {operation_id}"
            )
        target_support[target_id] = {
            "status": support["status"],
            "manifest_target_ref": {
                "path": starlette_rs["manifest"],
                "json_pointer": _pointer(
                    "surfaces",
                    manifest_surface_index,
                    "operations",
                    manifest_operation_index,
                    "targets",
                    target_index,
                ),
            },
        }
    python_support = target_support["python-package"]["status"]
    if python_support != "supported":
        raise ContractError(
            "canonical inherited API operation is not supported by the pinned Starlette-RS "
            f"Python package contract: {operation_id}"
        )

    def matching_csv_row(path: Path, *, disposition: str | None = None) -> int:
        with path.open(encoding="utf-8", newline="") as csv_file:
            rows = list(csv.DictReader(csv_file))
        matches = [
            (index + 2, row)
            for index, row in enumerate(rows)
            if row.get("qualified_name") == operation_id
            and (disposition is None or row.get("api_disposition") == disposition)
        ]
        if len(matches) != 1:
            raise ContractError(
                "inherited API operation must resolve to one pinned Starlette-RS catalog row: "
                f"{operation_id}"
            )
        return matches[0][0]

    catalog_line = matching_csv_row(catalog_path)
    review_line = matching_csv_row(review_path, disposition="supported")
    source_index, operation_index = source_matches[0]
    return {
        "contract_id": expected_contract_id,
        "manifest_path": starlette_rs["manifest"],
        "manifest_contract_pointer": manifest_contract_pointer,
        "canonical_operation_id": operation_id,
        "canonical_operation_kind": canonical_kind,
        "target_support": target_support,
        "manifest_operation_ref": {
            "path": starlette_rs["manifest"],
            "json_pointer": _pointer(
                "surfaces", manifest_surface_index, "operations", manifest_operation_index
            ),
        },
        "source_operation_ref": {
            "path": starlette_rs["metadata"],
            "json_pointer": _pointer("api_sources", source_index, "operations", operation_index),
        },
        "api_catalog_ref": {"path": starlette_rs["api_catalog"], "line": catalog_line},
        "api_review_ref": {"path": starlette_rs["api_review"], "line": review_line},
    }


def _validate_inherited_fixture_reference(
    fixture_reference: dict[str, Any],
    *,
    expected_doc_paths: set[str],
    expected_selectors: list[str],
    operation_id: str,
    inherited_kind: str,
) -> dict[str, Any]:
    recipe_path = fixture_reference.get("recipe_path")
    case_id = fixture_reference.get("case_id")
    if not isinstance(recipe_path, str) or not isinstance(case_id, str):
        raise ContractError(f"inherited API fixture reference is incomplete: {operation_id}")
    recipe = (PROJECT_ROOT / recipe_path).resolve()
    input_root = (PROJECT_ROOT / "tests/fixtures/input-recipes").resolve()
    if input_root not in recipe.parents or not recipe.is_file():
        raise ContractError(
            f"inherited API fixture recipe is missing or outside inputs: {recipe_path}"
        )
    workflow = yaml.safe_load(recipe.read_text(encoding="utf-8"))
    if not isinstance(workflow, dict):
        raise ContractError(f"inherited API fixture recipe must be a mapping: {recipe_path}")
    cases = workflow.get("cases", [])
    matching_cases = [
        case for case in cases if isinstance(case, dict) and case.get("case_id") == case_id
    ]
    if len(matching_cases) != 1:
        raise ContractError(
            f"inherited API fixture must select one input case: {recipe_path}::{case_id}"
        )
    case = matching_cases[0]
    case_doc_paths = {
        evidence.get("path")
        for evidence in case.get("source_evidence", [])
        if isinstance(evidence, dict)
    }
    if not expected_doc_paths <= case_doc_paths:
        raise ContractError(
            f"inherited API fixture lacks its reviewed documentation evidence: {recipe_path}"
        )

    workload = workflow.get("workload", {})
    workload_path = workload.get("file")
    factory = workload.get("factory")
    if not isinstance(workload_path, str) or not isinstance(factory, str):
        raise ContractError(f"inherited API fixture workload is incomplete: {recipe_path}")
    workload_file = (PROJECT_ROOT / workload_path).resolve()
    try:
        workload_file.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise ContractError(f"inherited API workload escapes the project: {workload_path}") from exc
    if not workload_file.is_file():
        raise ContractError(f"inherited API workload is missing: {workload_path}")
    try:
        tree = ast.parse(workload_file.read_text(encoding="utf-8"), filename=workload_path)
    except SyntaxError as exc:
        raise ContractError(f"inherited API workload is not valid Python: {workload_path}") from exc
    imports_fastapi = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "fastapi"
        and any(alias.name == "FastAPI" for alias in node.names)
        for node in ast.walk(tree)
    )
    if not imports_fastapi:
        raise ContractError(f"inherited API workload does not import FastAPI: {workload_path}")
    factories = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == factory
    ]
    if len(factories) != 1:
        raise ContractError(
            f"inherited API workload factory is not unique: {workload_path}:{factory}"
        )
    factory_node = factories[0]
    exposure_class = operation_id.rsplit(".", 2)[-2]
    receiver_names = {
        target.id
        for node in ast.walk(factory_node)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == exposure_class
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    method_name = operation_id.rsplit(".", 1)[-1]
    if inherited_kind == "inherited_method":
        operation_usages = [
            node
            for node in ast.walk(factory_node)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == method_name
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in receiver_names
        ]
    elif inherited_kind == "inherited_property":
        operation_usages = [
            node
            for node in ast.walk(factory_node)
            if isinstance(node, ast.Attribute)
            and node.attr == method_name
            and isinstance(node.value, ast.Name)
            and node.value.id in receiver_names
        ]
    else:
        raise ContractError(
            f"inherited API fixture kind is unsupported: {operation_id} ({inherited_kind})"
        )
    if (
        not receiver_names
        or not operation_usages
        or min(node.lineno for node in operation_usages)
        <= min(
            node.lineno
            for node in ast.walk(factory_node)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == exposure_class
        )
    ):
        raise ContractError(
            f"inherited API fixture does not use {exposure_class}.{method_name}: {workload_path}"
        )

    observed_short_selectors = {
        selector
        for action in case.get("actions", [])
        if isinstance(action, dict)
        for observation in action.get("observations", [])
        if isinstance(observation, dict) and observation.get("kind") == "http_response"
        for selector in observation.get("selectors", [])
    }
    observed_short_selectors.update(
        "asgi.send." + observation["selector"]
        for action in case.get("actions", [])
        if isinstance(action, dict)
        for observation in action.get("observations", [])
        if isinstance(observation, dict)
        and observation.get("kind") == "asgi_send"
        and isinstance(observation.get("selector"), str)
    )
    selector_aliases = {
        "http.status": "status",
        "http.headers.ordered": "headers",
        "http.body.bytes": "body",
    }
    missing_selectors = [
        selector
        for selector in expected_selectors
        if selector_aliases.get(selector, selector) not in observed_short_selectors
    ]
    if missing_selectors:
        raise ContractError(
            "inherited API fixture observations do not cover reviewed selectors: "
            f"{recipe_path}::{case_id} -> {', '.join(missing_selectors)}"
        )
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "workload_path": workload_path,
        "observation_selectors": sorted(expected_selectors),
    }


def _validate_reviewed_operation_fixture_reference(
    fixture_reference: dict[str, Any],
    *,
    materialized_workflows: list[dict[str, Any]],
    operation_id: str,
) -> dict[str, Any]:
    """Resolve one reviewed operation fixture link through the materialized index."""
    recipe_path = fixture_reference.get("recipe_path")
    case_id = fixture_reference.get("case_id")
    if not isinstance(recipe_path, str) or not isinstance(case_id, str):
        raise ContractError(
            f"reviewed API operation fixture reference is incomplete: {operation_id}"
        )

    matching_workflows = [
        workflow
        for workflow in materialized_workflows
        if isinstance(workflow, dict) and workflow.get("recipe_path") == recipe_path
    ]
    if len(matching_workflows) != 1:
        raise ContractError(
            "reviewed API operation fixture must resolve to one materialized recipe: "
            f"{operation_id}: {recipe_path}"
        )
    workflow = matching_workflows[0]
    case_ids = workflow.get("case_ids")
    if not isinstance(case_ids, list) or case_ids.count(case_id) != 1:
        raise ContractError(
            "reviewed API operation fixture must resolve to one materialized recipe case: "
            f"{operation_id}: {recipe_path}::{case_id}"
        )

    input_root = (PROJECT_ROOT / "tests/fixtures/inputs").resolve()
    recipe_root = (PROJECT_ROOT / "tests/fixtures/input-recipes").resolve()
    workload_root = (PROJECT_ROOT / "tests/fixtures/workloads").resolve()
    resolved_paths: dict[str, Path] = {}
    for field, root, label in (
        ("input_path", input_root, "materialized API operation input"),
        ("recipe_path", recipe_root, "API operation fixture recipe"),
        ("workload_path", workload_root, "API operation fixture workload"),
    ):
        relative_path = workflow.get(field)
        if not isinstance(relative_path, str):
            raise ContractError(
                f"materialized API operation workflow has no {field}: {recipe_path}"
            )
        path = (PROJECT_ROOT / relative_path).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ContractError(
                f"API operation fixture {label} is outside its project area: {relative_path}"
            ) from exc
        if not path.is_file():
            raise ContractError(f"API operation fixture {label} is missing: {relative_path}")
        digest_field = f"{field.removesuffix('_path')}_sha256"
        expected_digest = workflow.get(digest_field)
        if not isinstance(expected_digest, str) or sha256_file(path) != expected_digest:
            raise ContractError(
                f"materialized API operation workflow has a stale {field} digest: {relative_path}"
            )
        resolved_paths[field] = path

    recipe = yaml.safe_load(resolved_paths["recipe_path"].read_text(encoding="utf-8"))
    materialized_input = json.loads(resolved_paths["input_path"].read_text(encoding="utf-8"))
    materialized_case: dict[str, Any] | None = None
    for document, label in ((recipe, "recipe"), (materialized_input, "materialized input")):
        cases = document.get("cases", []) if isinstance(document, dict) else None
        matching_cases = [
            case
            for case in cases or []
            if isinstance(case, dict) and case.get("case_id") == case_id
        ]
        if not isinstance(cases, list) or len(matching_cases) != 1:
            raise ContractError(
                f"reviewed API operation fixture case is absent or duplicated in {label}: "
                f"{recipe_path}::{case_id}"
            )
        if label == "materialized input":
            materialized_case = matching_cases[0]

    from scripts.parity.materialized import _selected_selectors

    observation_selectors = sorted(
        _selected_selectors(materialized_case, workflow_schema=materialized_input["schema"])
    )
    if not observation_selectors:
        raise ContractError(
            f"reviewed API operation fixture case has no observable selectors: "
            f"{recipe_path}::{case_id}"
        )

    return {
        "workflow_id": workflow["id"],
        "input_path": workflow["input_path"],
        "input_sha256": workflow["input_sha256"],
        "recipe_path": recipe_path,
        "recipe_sha256": workflow["recipe_sha256"],
        "workload_path": workflow["workload_path"],
        "workload_sha256": workflow["workload_sha256"],
        "case_id": case_id,
        "observation_selectors": observation_selectors,
    }


def _implementation_owner_plan(
    candidate: dict[str, Any],
    *,
    candidates_by_id: dict[str, dict[str, Any]],
    candidate_indexes: dict[str, int],
) -> tuple[str, str, list[str]]:
    """Follow source identity aliases to the implementation that owns the object."""
    current = candidate
    visited: set[str] = set()
    source_refs: list[str] = []
    while True:
        candidate_id = current["id"]
        if candidate_id in visited:
            break
        visited.add(candidate_id)
        source_refs.append(_pointer("api_candidates", candidate_indexes[candidate_id]))
        if current.get("starlette_delegation") == "direct_reexport":
            reason = (
                "direct_starlette_reexport"
                if len(source_refs) == 1
                else "identity_alias_chain_to_starlette"
            )
            return "starlette-rs", reason, source_refs
        if current.get("identity_alias") is not True:
            break
        target = current.get("target_path")
        if not isinstance(target, str):
            break
        target_candidate = candidates_by_id.get(target)
        if target_candidate is None:
            break
        current = target_candidate
    return "fastapi-rs", "fastapi_owned_or_adapter", source_refs


def _reviewed_deprecation_references(
    rules: list[Any],
    *,
    atlas_deprecations: list[dict[str, Any]],
    candidates_by_id: dict[str, dict[str, Any]],
    supported_symbol_ids: set[str],
) -> dict[str, list[str]]:
    """Map reviewed method rules to exact source deprecation records."""
    rule_ids: set[str] = set()
    method_ids: set[str] = set()
    references: dict[str, list[str]] = defaultdict(list)

    for rule in rules:
        if not isinstance(rule, dict):
            raise ContractError("reviewed deprecation reference rule must be a mapping")
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            raise ContractError("reviewed deprecation reference rules require stable IDs")
        if rule_id in rule_ids:
            raise ContractError(f"reviewed deprecation reference rule ID is duplicated: {rule_id}")
        rule_ids.add(rule_id)

        method_id = rule.get("symbol_id")
        record_symbol_id = rule.get("deprecation_symbol_id")
        source_path = rule.get("source_path")
        source_line = rule.get("source_line")
        source_end_line = rule.get("source_end_line")
        if not all(
            isinstance(value, str) and value for value in (method_id, record_symbol_id, source_path)
        ):
            raise ContractError(f"reviewed deprecation reference identity is invalid: {rule_id}")
        if (
            not isinstance(source_line, int)
            or isinstance(source_line, bool)
            or not isinstance(source_end_line, int)
            or isinstance(source_end_line, bool)
            or source_line < 1
            or source_end_line < source_line
        ):
            raise ContractError(f"reviewed deprecation source range is invalid: {rule_id}")
        if method_id in method_ids:
            raise ContractError(f"method has multiple reviewed deprecation rules: {method_id}")
        method_ids.add(method_id)
        if method_id not in supported_symbol_ids:
            raise ContractError(
                f"deprecation rule references an unsupported API symbol: {method_id}"
            )
        candidate = candidates_by_id[method_id]
        if candidate.get("kind") != "method" or not method_id.startswith(record_symbol_id + "."):
            raise ContractError(
                f"deprecation rule does not identify a method of its record: {rule_id}"
            )
        method_source_rows = candidate.get("source_evidence", [])
        if not isinstance(method_source_rows, list) or not any(
            isinstance(row, dict)
            and row.get("path") == source_path
            and row.get("line") == source_end_line + 1
            for row in method_source_rows
        ):
            raise ContractError(
                f"deprecation evidence is not adjacent to the method definition: {rule_id}"
            )

        matching_evidence: list[tuple[int, dict[str, Any]]] = []
        for record_index, record in enumerate(atlas_deprecations):
            evidence_rows = record.get("evidence", [])
            if not isinstance(evidence_rows, list):
                raise ContractError(
                    f"atlas deprecation evidence must be a list: {record.get('symbol_id')}"
                )
            for evidence in evidence_rows:
                if not isinstance(evidence, dict):
                    raise ContractError(
                        "atlas deprecation evidence row must be a mapping: "
                        f"{record.get('symbol_id')}"
                    )
                source_ref = evidence.get("source_ref")
                if (
                    evidence.get("kind") == "typing_extensions.deprecated"
                    and isinstance(source_ref, dict)
                    and source_ref.get("path") == source_path
                    and source_ref.get("line") == source_line
                    and source_ref.get("end_line") == source_end_line
                ):
                    matching_evidence.append((record_index, record))
        if len(matching_evidence) != 1:
            raise ContractError(
                "reviewed deprecation rule must match exactly one pinned atlas evidence row: "
                f"{rule_id}"
            )
        record_index, record = matching_evidence[0]
        if record.get("symbol_id") != record_symbol_id:
            raise ContractError(
                f"reviewed deprecation rule matched the wrong source record: {rule_id}"
            )
        references[method_id].append(_pointer("deprecations", record_index))

    return dict(references)


def _reviewed_identity_workflow_references(
    reviewed_refs: Any,
    *,
    candidates_by_id: dict[str, dict[str, Any]],
    candidate_indexes: dict[str, int],
    atlas_aliases: list[dict[str, Any]],
    alias_refs: dict[str, list[str]],
    materialized_input_index: dict[str, Any],
    runtime_core: dict[str, Any],
    selector_support: dict[str, str],
) -> dict[str, list[dict[str, Any]]]:
    """Link reviewed root and module import identity checks to current ASGI inputs."""
    if not isinstance(reviewed_refs, dict):
        raise ContractError("reviewed identity workflow references must be a mapping")
    from scripts.parity.materialized import _selected_selectors

    root_aliases: dict[str, dict[str, Any]] = {}
    module_aliases: dict[str, dict[str, Any]] = {}
    for alias in atlas_aliases:
        if not isinstance(alias, dict) or not isinstance(alias.get("id"), str):
            raise ContractError("source identity aliases must be mappings with stable IDs")
        if alias.get("identity_alias") is not True:
            continue
        if alias.get("root_export") is True:
            symbol_id = alias["id"]
            if symbol_id in root_aliases:
                raise ContractError(f"root identity alias is duplicated: {symbol_id}")
            root_aliases[symbol_id] = alias
        elif alias["id"].startswith("fastapi."):
            if alias["id"] in module_aliases:
                raise ContractError(f"FastAPI module identity alias is duplicated: {alias['id']}")
            module_aliases[alias["id"]] = alias

    core_module_rows = runtime_core.get("modules", [])
    if not isinstance(core_module_rows, list):
        raise ContractError("core runtime modules are invalid for identity references")
    core_modules = {
        row["id"]: row
        for row in core_module_rows
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    optional_unavailable_modules = {
        module_id
        for module_id, module in core_modules.items()
        if module.get("status") == "optional_feature_unavailable"
    }
    # Optional imports remain explicit runtime-profile gaps until their own workflow is added.
    supported_module_aliases = {
        symbol_id: alias
        for symbol_id, alias in module_aliases.items()
        if candidates_by_id.get(symbol_id, {}).get("classification") == "supported"
        and symbol_id.rpartition(".")[0] not in optional_unavailable_modules
    }
    expected_aliases = set(root_aliases) | set(supported_module_aliases)
    if set(reviewed_refs) != expected_aliases:
        missing = sorted(expected_aliases - set(reviewed_refs))
        extra = sorted(set(reviewed_refs) - expected_aliases)
        raise ContractError(
            "reviewed identity workflow references must cover every supported root and module "
            "identity alias "
            f"exactly once (missing={missing}, extra={extra})"
        )

    workflow_rows_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for workflow_ref in materialized_input_index.get("workflows", []):
        if not isinstance(workflow_ref, dict):
            raise ContractError("materialized workflow row is invalid for identity references")
        for case_id in workflow_ref.get("case_ids", []):
            workflow_rows_by_case[case_id].append(workflow_ref)
    source_mappings = materialized_input_index.get("mappings", [])
    workflow_cache: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]] = {}
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for symbol_id, rows in reviewed_refs.items():
        candidate = candidates_by_id.get(symbol_id)
        is_root_alias = symbol_id in root_aliases
        root_alias = root_aliases.get(symbol_id)
        source_alias = root_alias if root_alias is not None else supported_module_aliases[symbol_id]
        if (
            not isinstance(candidate, dict)
            or candidate.get("classification") != "supported"
            or candidate.get("kind") != "import_binding"
            or candidate.get("root_export") is not is_root_alias
            or candidate.get("identity_alias") is not True
            or candidate.get("target_path") != source_alias.get("target_path")
            or candidate.get("local_name") != source_alias.get("local_name")
            or source_alias.get("source_module") != candidate.get("imported_module")
            or source_alias.get("source_name") != candidate.get("imported_name")
        ):
            raise ContractError(
                f"reviewed identity reference lacks a matching supported source alias: {symbol_id}"
            )
        if not isinstance(rows, list) or not rows:
            raise ContractError(f"reviewed identity workflow references are empty: {symbol_id}")

        target_path = source_alias.get("target_path")
        if not is_root_alias:
            module_alias = source_alias
            imported_module = candidate.get("imported_module")
            imported_name = candidate.get("imported_name")
            if (
                not isinstance(imported_module, str)
                or not imported_module.startswith("starlette.")
                or not isinstance(imported_name, str)
                or target_path != f"{imported_module}.{imported_name}"
            ):
                raise ContractError(
                    f"direct FastAPI module alias has an invalid Starlette target: {symbol_id}"
                )
            expected_relations = {"public_module_to_starlette"}
        else:
            module_candidate = (
                candidates_by_id.get(target_path) if isinstance(target_path, str) else None
            )
            module_alias = module_aliases.get(target_path) if isinstance(target_path, str) else None
            if candidate.get("imported_module") == "starlette":
                if (
                    not isinstance(target_path, str)
                    or candidate.get("imported_name") is None
                    or target_path != f"starlette.{candidate['imported_name']}"
                ):
                    raise ContractError(
                        f"direct Starlette root alias has an invalid target: {symbol_id}"
                    )
                expected_relations = {"root_to_starlette_module"}
            else:
                expected_module_path = (
                    f"fastapi.{candidate['imported_module']}.{candidate['imported_name']}"
                )
                if target_path != expected_module_path or not isinstance(module_candidate, dict):
                    raise ContractError(
                        f"root alias does not resolve to its public FastAPI module source: "
                        f"{symbol_id}"
                    )
                if module_candidate.get("classification") != "supported":
                    raise ContractError(
                        f"root alias module source is not a supported API candidate: {symbol_id}"
                    )
                module_candidate_target = module_candidate.get("target_path")
                module_targets_starlette = isinstance(
                    module_candidate_target, str
                ) and module_candidate_target.startswith("starlette.")
                if module_targets_starlette and not isinstance(module_alias, dict):
                    raise ContractError(
                        f"FastAPI module Starlette target has no reviewed identity alias: "
                        f"{symbol_id}"
                    )
                expected_relations = {"root_to_public_module"}
                if isinstance(module_alias, dict):
                    if (
                        module_candidate.get("kind") != "import_binding"
                        or module_alias.get("id") != target_path
                        or module_alias.get("local_name") != module_candidate.get("local_name")
                        or module_alias.get("source_module")
                        != module_candidate.get("imported_module")
                        or module_alias.get("source_name") != module_candidate.get("imported_name")
                        or module_alias.get("target_path") != module_candidate.get("target_path")
                    ):
                        raise ContractError(
                            "FastAPI module import candidate differs from its source alias: "
                            f"{symbol_id}"
                        )
                if module_targets_starlette and isinstance(module_alias, dict):
                    imported_module = module_candidate.get("imported_module")
                    imported_name = module_candidate.get("imported_name")
                    if (
                        not isinstance(imported_module, str)
                        or not imported_module.startswith("starlette.")
                        or not isinstance(imported_name, str)
                        or module_alias.get("target_path") != module_candidate_target
                        or module_candidate_target != f"{imported_module}.{imported_name}"
                    ):
                        raise ContractError(
                            f"FastAPI module alias has an inconsistent Starlette target: "
                            f"{symbol_id}"
                        )
                    expected_relations.update(
                        {"root_to_starlette_module", "public_module_to_starlette"}
                    )
        relation_rows: dict[str, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict) or set(row) != {
                "case_id",
                "relation",
                "observation_selector",
                "projection",
            }:
                raise ContractError(
                    f"reviewed identity workflow row has unsupported fields: {symbol_id}"
                )
            relation = row.get("relation")
            if not isinstance(relation, str) or relation in relation_rows:
                raise ContractError(
                    f"reviewed identity workflow relation is invalid or duplicated: {symbol_id}"
                )
            relation_rows[relation] = row
        if set(relation_rows) != expected_relations:
            raise ContractError(
                f"reviewed identity relations differ from the source alias chain: {symbol_id}; "
                f"expected={sorted(expected_relations)}, found={sorted(relation_rows)}"
            )

        is_websocket = candidate.get("imported_module") in {
            "websockets",
            "starlette.websockets",
        }
        expected_case = (
            "fastapi.root-alias-identity.websocket-reexports"
            if is_websocket
            else "fastapi.root-alias-identity.http-reexports"
        )
        expected_selector = "websocket.messages" if is_websocket else "http.body.bytes"
        expected_projection = (
            "websocket_send_text_json_boolean" if is_websocket else "http_json_body_boolean"
        )

        for relation, row in relation_rows.items():
            if row.get("case_id") != expected_case:
                raise ContractError(
                    f"identity alias mapped to the wrong source case: {symbol_id}::{relation}"
                )
            selector = row.get("observation_selector")
            if selector != expected_selector or selector_support.get(selector) not in {
                "supported",
                "partial",
            }:
                raise ContractError(
                    f"identity alias uses an unsupported or incorrect selector: "
                    f"{symbol_id}::{relation} -> {selector}"
                )
            if row.get("projection") != expected_projection:
                raise ContractError(
                    f"identity alias projection differs from its transport observation: "
                    f"{symbol_id}::{relation}"
                )

            matching_workflows = workflow_rows_by_case.get(expected_case, [])
            if len(matching_workflows) != 1:
                raise ContractError(
                    f"identity alias case is missing or ambiguous in the materialized index: "
                    f"{expected_case}"
                )
            workflow_ref = matching_workflows[0]
            workflow_id = workflow_ref.get("id")
            if not isinstance(workflow_id, str):
                raise ContractError("identity workflow index row has no stable ID")
            if workflow_id not in workflow_cache:
                workflow_path = PROJECT_ROOT / workflow_ref["input_path"]
                workflow, resolved_path, input_digest, workload_path = load_workflow(workflow_path)
                if (
                    input_digest != workflow_ref.get("input_sha256")
                    or resolved_path.relative_to(PROJECT_ROOT).as_posix()
                    != workflow_ref.get("input_path")
                    or workflow["workload"].get("file") != workflow_ref.get("workload_path")
                    or sha256_file(workload_path) != workflow_ref.get("workload_sha256")
                    or sha256_file(PROJECT_ROOT / workflow_ref["recipe_path"])
                    != workflow_ref.get("recipe_sha256")
                ):
                    raise ContractError(
                        f"identity workflow differs from its materialized index row: {workflow_id}"
                    )
                cases_by_id = {case["case_id"]: case for case in workflow["cases"]}
                if len(cases_by_id) != len(workflow["cases"]):
                    raise ContractError(f"identity workflow repeats a case ID: {workflow_id}")
                workflow_cache[workflow_id] = (
                    workflow,
                    cases_by_id,
                    {
                        selector
                        for case in workflow["cases"]
                        for selector in _selected_selectors(
                            case, workflow_schema=workflow["schema"]
                        )
                    },
                )

            workflow, cases_by_id, workflow_selectors = workflow_cache[workflow_id]
            case = cases_by_id.get(expected_case)
            if case is None:
                raise ContractError(f"identity workflow is missing case {expected_case}")
            case_selectors = _selected_selectors(case, workflow_schema=workflow["schema"])
            if selector not in case_selectors or selector not in workflow_selectors:
                raise ContractError(
                    f"identity workflow case does not observe its declared selector: "
                    f"{expected_case} -> {selector}"
                )
            expected_action_kind = "websocket_session" if is_websocket else "http_request"
            if not any(
                action.get("kind") == expected_action_kind for action in case.get("actions", [])
            ):
                raise ContractError(
                    f"identity workflow case has no matching transport action: {expected_case}"
                )
            if not any(
                mapping.get("workflow_id") == workflow_id
                and expected_case in mapping.get("case_ids", [])
                and selector in mapping.get("observation_selectors", [])
                for mapping in source_mappings
            ):
                raise ContractError(
                    f"identity workflow case has no current source mapping for selector: "
                    f"{expected_case} -> {selector}"
                )

            pointer_key = {
                "root_to_public_module": "root_to_public_module",
                "root_to_starlette_module": "root_to_starlette_module",
                "public_module_to_starlette": "public_module_to_starlette",
            }[relation]
            pointer_name = (
                module_alias.get("local_name")
                if relation == "public_module_to_starlette" and module_alias
                else candidate.get("local_name")
            )
            if not isinstance(pointer_name, str):
                raise ContractError(
                    f"identity alias has no source-backed output name: {symbol_id}::{relation}"
                )
            source_alias_ids = [symbol_id]
            if (
                is_root_alias
                and relation == "public_module_to_starlette"
                and target_path != symbol_id
            ):
                source_alias_ids = [target_path]
            elif relation == "root_to_starlette_module" and module_alias:
                source_alias_ids.append(target_path)
            source_alias_ids = list(dict.fromkeys(source_alias_ids))
            source_alias_pointers: list[str] = []
            for source_alias_id in source_alias_ids:
                pointers = alias_refs.get(source_alias_id, [])
                if not pointers:
                    raise ContractError(
                        f"identity workflow source alias is absent from the atlas: "
                        f"{source_alias_id}"
                    )
                source_alias_pointers.extend(pointers)

            source_candidate_ids = [symbol_id]
            if isinstance(target_path, str) and target_path in candidate_indexes:
                source_candidate_ids.append(target_path)
            source_candidate_pointers = [
                _pointer("api_candidates", candidate_indexes[source_id])
                for source_id in dict.fromkeys(source_candidate_ids)
            ]
            result[symbol_id].append(
                {
                    "workflow_id": workflow_id,
                    "input_path": workflow_ref["input_path"],
                    "input_sha256": workflow_ref["input_sha256"],
                    "recipe_path": workflow_ref["recipe_path"],
                    "recipe_sha256": workflow_ref["recipe_sha256"],
                    "workload_path": workflow_ref["workload_path"],
                    "workload_sha256": workflow_ref["workload_sha256"],
                    "case_id": expected_case,
                    "relation": relation,
                    "observation_selector": selector,
                    "projection": {
                        "kind": row["projection"],
                        "pointer": f"/{pointer_key}/{pointer_name}",
                    },
                    "source_candidate_refs": source_candidate_pointers,
                    "source_alias_refs": list(dict.fromkeys(source_alias_pointers)),
                }
            )

    return {
        symbol_id: sorted(
            references,
            key=lambda reference: (
                reference["case_id"],
                reference["relation"],
                reference["observation_selector"],
            ),
        )
        for symbol_id, references in result.items()
    }


def build_api_surface_contract(
    *,
    inventory: dict[str, Any],
    atlas: dict[str, Any],
    backlog: dict[str, Any],
    materialized_input_index: dict[str, Any],
    runtime_core: dict[str, Any],
    runtime_standard: dict[str, Any],
    reviewed_overlay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return exact source/runtime references for every source-supported API symbol."""
    metadata = _read_project_metadata()
    overlay = reviewed_overlay if reviewed_overlay is not None else _read_reviewed_overlay(metadata)
    if overlay.get("schema") != OVERLAY_SCHEMA:
        raise ContractError("reviewed API contract overlay schema is unsupported")
    overlay_operations = overlay.get("operations")
    if not isinstance(overlay_operations, dict):
        raise ContractError("reviewed API contract overlay operations must be a mapping")
    inherited_operations = overlay.get("inherited_operations", {})
    if not isinstance(inherited_operations, dict):
        raise ContractError("reviewed inherited API operations must be a mapping")
    inherited_candidate_reviews = overlay.get("inherited_candidate_reviews", {})
    if not isinstance(inherited_candidate_reviews, dict):
        raise ContractError("reviewed inherited API candidate reviews must be a mapping")
    error_selector_rules = overlay.get("error_selector_rules", [])
    if not isinstance(error_selector_rules, list) or any(
        not isinstance(rule, dict) for rule in error_selector_rules
    ):
        raise ContractError("reviewed API error selector rules must be a list of mappings")
    deprecation_reference_rules = overlay.get("deprecation_reference_rules", [])
    if not isinstance(deprecation_reference_rules, list):
        raise ContractError("reviewed API deprecation reference rules must be a list")
    warning_reviews = overlay.get("warning_classification_reviews", {})
    if not isinstance(warning_reviews, dict):
        raise ContractError("reviewed warning classification overlays must be a mapping")
    for warning_id, review in warning_reviews.items():
        if not isinstance(review, dict):
            raise ContractError(f"reviewed warning classification must be a mapping: {warning_id}")
        evidence = review.get("evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(row, dict) for row in evidence):
            raise ContractError(
                f"reviewed warning evidence must be a list of mappings: {warning_id}"
            )
    for operation_id, operation in overlay_operations.items():
        if not isinstance(operation, dict):
            raise ContractError(f"reviewed API overlay operation must be a mapping: {operation_id}")
        evidence = operation.get("source_evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(row, dict) for row in evidence):
            raise ContractError(
                f"reviewed API source evidence must be a list of mappings: {operation_id}"
            )
        docs = operation.get("documentation_contract_refs", [])
        if not isinstance(docs, list) or any(not isinstance(row, dict) for row in docs):
            raise ContractError(
                f"reviewed API documentation references must be a list of mappings: {operation_id}"
            )
        fixtures = operation.get("fixture_refs", [])
        if not isinstance(fixtures, list) or any(not isinstance(row, dict) for row in fixtures):
            raise ContractError(
                f"reviewed API fixture references must be a list of mappings: {operation_id}"
            )
        supported_slice = operation.get("supported_slice")
        if supported_slice is not None and (
            not isinstance(supported_slice, str) or not supported_slice.strip()
        ):
            raise ContractError(
                f"reviewed API supported_slice must be a nonempty string: {operation_id}"
            )
        for field in ("feature_ids", "observation_selectors", "error_contract_ids"):
            values = operation.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ContractError(f"reviewed API {field} must be a string list: {operation_id}")
        target_binding = operation.get("target_binding")
        if target_binding is not None:
            known_gaps = (
                target_binding.get("known_gaps") if isinstance(target_binding, dict) else None
            )
            rust_binding = (
                target_binding.get("rust_binding") if isinstance(target_binding, dict) else None
            )
            if (
                not isinstance(target_binding, dict)
                or set(target_binding)
                - {
                    "implementation_owner",
                    "status",
                    "known_gaps",
                    "rust_binding",
                }
                or target_binding.get("implementation_owner") != "fastapi-rs"
                or target_binding.get("status") not in {"partial-contract", "unimplemented"}
                or not isinstance(known_gaps, list)
                or not known_gaps
                or any(not isinstance(value, str) or not value.strip() for value in known_gaps)
                or len(known_gaps) != len(set(known_gaps))
                or (
                    rust_binding is not None
                    and (not isinstance(rust_binding, str) or not rust_binding.strip())
                )
            ):
                raise ContractError(
                    "reviewed API target binding must declare FastAPI-RS ownership, "
                    "partial-contract or unimplemented status, and unique known gaps: "
                    f"{operation_id}"
                )
        for documentation_ref in docs:
            doc_selectors = documentation_ref.get("observation_selectors", [])
            if not isinstance(doc_selectors, list) or any(
                not isinstance(value, str) for value in doc_selectors
            ):
                raise ContractError(
                    f"reviewed API docs selectors must be a string list: {operation_id}"
                )
    for operation_id, operation in inherited_operations.items():
        if not isinstance(operation, dict):
            raise ContractError(
                f"reviewed inherited API operation must be a mapping: {operation_id}"
            )
        if any(field in operation for field in ("signature", "parameters", "requirements")):
            raise ContractError(
                "inherited API overlays must point to the canonical sibling contract without "
                f"copying its signature or requirements: {operation_id}"
            )
        inherited_kind = operation.get("kind", "inherited_method")
        if inherited_kind not in {"inherited_method", "inherited_property"}:
            raise ContractError(
                f"reviewed inherited API kind is unsupported: {operation_id} ({inherited_kind})"
            )
        has_gap = "sibling_contract_gap" in operation
        if has_gap:
            if "canonical_operation_id" in operation:
                raise ContractError(
                    "inherited API sibling-gap rows must omit canonical_operation_id: "
                    f"{operation_id}"
                )
            signature_source = operation.get("signature_source")
            attribute_source = operation.get("attribute_source")
            gap = operation.get("sibling_contract_gap")
            target_binding = operation.get("target_binding")
            has_signature_source = isinstance(signature_source, dict)
            has_attribute_source = isinstance(attribute_source, dict)
            if (
                has_signature_source == has_attribute_source
                or ("signature_source" in operation and not has_signature_source)
                or ("attribute_source" in operation and not has_attribute_source)
                or not isinstance(gap, dict)
            ):
                raise ContractError(
                    "inherited API sibling-gap row needs exactly one source mapping and a gap: "
                    f"{operation_id}"
                )
            if has_attribute_source and gap.get("candidate_state") != "no_exact_row":
                raise ContractError(
                    "inherited attribute sibling gap must explicitly state no_exact_row: "
                    f"{operation_id}"
                )
            if has_signature_source and gap.get("candidate_state") == "no_exact_row":
                raise ContractError(
                    "no_exact_row sibling gaps are reserved for instance attributes: "
                    f"{operation_id}"
                )
            if not isinstance(target_binding, dict):
                raise ContractError(
                    "inherited API sibling-gap row needs an explicit target binding: "
                    f"{operation_id}"
                )
            known_gaps = target_binding.get("known_gaps")
            rust_binding = target_binding.get("rust_binding")
            if (
                target_binding.get("status") != "partial-contract"
                or target_binding.get("implementation_owner") != "fastapi-rs"
                or not isinstance(known_gaps, list)
                or not known_gaps
                or any(not isinstance(value, str) or not value.strip() for value in known_gaps)
                or len(known_gaps) != len(set(known_gaps))
                or (
                    rust_binding is not None
                    and (not isinstance(rust_binding, str) or not rust_binding.strip())
                )
            ):
                raise ContractError(
                    "inherited API sibling-gap target binding must declare partial-contract, "
                    f"fastapi-rs ownership, and unique known gaps: {operation_id}"
                )
        elif "signature_source" in operation or "attribute_source" in operation:
            raise ContractError(
                "inherited API source references are reserved for explicit sibling gaps: "
                f"{operation_id}"
            )
        elif "target_binding" in operation:
            target_binding = operation.get("target_binding")
            known_gaps = (
                target_binding.get("known_gaps") if isinstance(target_binding, dict) else None
            )
            rust_binding = (
                target_binding.get("rust_binding") if isinstance(target_binding, dict) else None
            )
            if (
                not isinstance(target_binding, dict)
                or target_binding.get("implementation_owner") != "fastapi-rs"
                or target_binding.get("status") not in {"partial-contract", "unimplemented"}
                or not isinstance(known_gaps, list)
                or not known_gaps
                or any(not isinstance(value, str) or not value.strip() for value in known_gaps)
                or len(known_gaps) != len(set(known_gaps))
                or (
                    rust_binding is not None
                    and (not isinstance(rust_binding, str) or not rust_binding.strip())
                )
            ):
                raise ContractError(
                    "inherited canonical target binding must declare FastAPI-RS ownership, "
                    "partial-contract or unimplemented status, and unique known gaps: "
                    f"{operation_id}"
                )
        evidence = operation.get("source_evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(row, dict) for row in evidence):
            raise ContractError(
                f"reviewed inherited API evidence must be a list of mappings: {operation_id}"
            )
        docs = operation.get("documentation_contract_refs", [])
        fixtures = operation.get("fixture_refs", [])
        if (
            not isinstance(docs, list)
            or any(not isinstance(row, dict) for row in docs)
            or not isinstance(fixtures, list)
            or any(not isinstance(row, dict) for row in fixtures)
        ):
            raise ContractError(
                f"reviewed inherited API documentation and fixture refs must be mappings: "
                f"{operation_id}"
            )
        for field in ("feature_ids", "observation_selectors"):
            values = operation.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ContractError(
                    f"reviewed inherited API {field} must be a string list: {operation_id}"
                )
        for documentation_ref in docs:
            doc_selectors = documentation_ref.get("observation_selectors", [])
            if not isinstance(doc_selectors, list) or any(
                not isinstance(value, str) for value in doc_selectors
            ):
                raise ContractError(
                    f"reviewed inherited API docs selectors must be a string list: {operation_id}"
                )
    inherited_operation_only_fields = {
        "canonical_operation_id",
        "sibling_contract_gap",
        "signature_source",
        "attribute_source",
        "target_binding",
        "documentation_contract_refs",
        "fixture_refs",
        "feature_ids",
        "observation_selectors",
        "signature",
        "parameters",
        "requirements",
    }
    for candidate_id, review in inherited_candidate_reviews.items():
        if not isinstance(review, dict):
            raise ContractError(
                f"reviewed inherited API candidate review must be a mapping: {candidate_id}"
            )
        if review.get("kind", "inherited_method") not in {
            "inherited_method",
            "inherited_property",
        }:
            raise ContractError(
                f"reviewed inherited API candidate kind is unsupported: {candidate_id}"
            )
        if review.get("classification") not in {"private/internal", "uncertain"}:
            raise ContractError(
                "classification-only inherited API candidate must be private/internal or "
                f"uncertain: {candidate_id}"
            )
        rationale = review.get("classification_evidence_rule")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ContractError(
                f"reviewed inherited API candidate has no classification rationale: {candidate_id}"
            )
        if inherited_operation_only_fields & set(review):
            raise ContractError(
                "classification-only inherited API candidate declares operation fields: "
                f"{candidate_id}"
            )
        evidence = review.get("source_evidence")
        sibling_review = review.get("starlette_rs_review")
        if (
            not isinstance(evidence, list)
            or not evidence
            or any(not isinstance(reference, dict) for reference in evidence)
            or not isinstance(sibling_review, dict)
            or not isinstance(sibling_review.get("qualified_name"), str)
            or sibling_review.get("api_disposition") != review.get("classification")
        ):
            raise ContractError(
                f"reviewed inherited API candidate has incomplete source/review evidence: "
                f"{candidate_id}"
            )
    inventory_refs = _inventory_rows(inventory)
    core_refs = _runtime_rows(runtime_core)
    standard_refs = _runtime_rows(runtime_standard)
    core_modules = {
        row["id"]: (_pointer("modules", index), row)
        for index, row in enumerate(runtime_core["modules"])
    }
    atlas_candidates = atlas["api_candidates"]
    candidates_by_id = {candidate["id"]: candidate for candidate in atlas_candidates}
    candidate_indexes = {candidate["id"]: index for index, candidate in enumerate(atlas_candidates)}
    atlas_inherited_candidates = atlas.get("reviewed_inherited_api_candidates", [])
    if not isinstance(atlas_inherited_candidates, list):
        raise ContractError("atlas reviewed inherited API candidates must be a list")
    inherited_candidates_by_id = {
        candidate["id"]: candidate
        for candidate in atlas_inherited_candidates
        if isinstance(candidate, dict) and isinstance(candidate.get("id"), str)
    }
    inherited_candidate_indexes = {
        candidate["id"]: index for index, candidate in enumerate(atlas_inherited_candidates)
    }
    if set(inherited_candidates_by_id) != set(inherited_candidate_indexes):
        raise ContractError("atlas inherited API candidate IDs must be unique")
    aliases: dict[str, list[str]] = defaultdict(list)
    for index, alias in enumerate(atlas["aliases"]):
        aliases[alias["id"]].append(_pointer("aliases", index))
    deprecations: dict[str, list[str]] = defaultdict(list)
    for index, item in enumerate(atlas["deprecations"]):
        deprecations[item["symbol_id"]].append(_pointer("deprecations", index))
    errors: dict[str, list[str]] = defaultdict(list)
    for index, item in enumerate(atlas["errors"]):
        errors[item["id"]].append(_pointer("errors", index))

    coverage_by_doc_path: dict[str, tuple[str, dict[str, Any]]] = {}
    for index, row in enumerate(atlas["coverage_matrix"]):
        if row["kind"] == "documented_feature_page":
            coverage_by_doc_path[row["source_path"]] = (_pointer("coverage_matrix", index), row)
    backlog_by_id = {
        fixture["id"]: _pointer("fixture_designs", index)
        for index, fixture in enumerate(backlog["fixture_designs"])
    }

    api_symbol_ids = [
        candidate["id"]
        for candidate in atlas_candidates
        if candidate["classification"] == "supported"
    ]
    if len(api_symbol_ids) != len(set(api_symbol_ids)):
        raise ContractError("source API contract has duplicate supported symbol IDs")
    unsupported_overlay_operations = set(overlay_operations) - set(api_symbol_ids)
    if unsupported_overlay_operations:
        raise ContractError(
            "reviewed API overlay references operations outside the supported source contract: "
            + ", ".join(sorted(unsupported_overlay_operations))
        )
    duplicate_inherited_candidates = (
        set(inherited_operations) | set(inherited_candidate_reviews)
    ) & set(candidates_by_id)
    if duplicate_inherited_candidates:
        raise ContractError(
            "inherited API overlays must remain separate from source-declared candidates: "
            + ", ".join(sorted(duplicate_inherited_candidates))
        )
    if set(inherited_operations) & set(inherited_candidate_reviews):
        raise ContractError(
            "inherited operation overlays and classification reviews must be disjoint"
        )
    supported_inherited_candidate_ids = {
        candidate_id
        for candidate_id, candidate in inherited_candidates_by_id.items()
        if candidate.get("classification") == "supported"
    }
    classification_only_candidate_ids = set(inherited_candidates_by_id) - (
        supported_inherited_candidate_ids
    )
    if set(inherited_operations) != supported_inherited_candidate_ids:
        raise ContractError(
            "reviewed inherited API operations differ from supported atlas candidates: "
            + ", ".join(sorted(set(inherited_operations) ^ supported_inherited_candidate_ids))
        )
    if set(inherited_candidate_reviews) != classification_only_candidate_ids:
        raise ContractError(
            "reviewed inherited API candidate reviews differ from non-supported atlas "
            "candidates: "
            + ", ".join(
                sorted(set(inherited_candidate_reviews) ^ classification_only_candidate_ids)
            )
        )
    reviewed_deprecation_refs = _reviewed_deprecation_references(
        deprecation_reference_rules,
        atlas_deprecations=atlas["deprecations"],
        candidates_by_id=candidates_by_id,
        supported_symbol_ids=set(api_symbol_ids),
    )
    for symbol_id, references in reviewed_deprecation_refs.items():
        if deprecations.get(symbol_id):
            raise ContractError(
                f"reviewed deprecation rule duplicates a direct source record: {symbol_id}"
            )
        deprecations[symbol_id].extend(references)

    selector_catalog = json.loads(
        (PROJECT_ROOT / "tests/fixtures/observation-selectors.json").read_text(encoding="utf-8")
    )
    known_selectors = {
        row["id"]
        for row in selector_catalog.get("selectors", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    selector_support = {
        row["id"]: row.get("workflow_support")
        for row in selector_catalog.get("selectors", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    identity_workflow_refs_by_symbol = _reviewed_identity_workflow_references(
        overlay.get("identity_workflow_refs"),
        candidates_by_id=candidates_by_id,
        candidate_indexes=candidate_indexes,
        atlas_aliases=atlas["aliases"],
        alias_refs=aliases,
        materialized_input_index=materialized_input_index,
        runtime_core=runtime_core,
        selector_support=selector_support,
    )
    matched_error_rules: set[str] = set()
    rule_ids: set[str] = set()
    for rule in error_selector_rules:
        if not isinstance(rule, dict) or not isinstance(rule.get("id"), str):
            raise ContractError("reviewed error selector rules require stable IDs")
        if rule["id"] in rule_ids:
            raise ContractError(f"reviewed error selector rule ID is duplicated: {rule['id']}")
        rule_ids.add(rule["id"])
        rule_selectors = rule.get("observation_selectors", [])
        if (
            not isinstance(rule_selectors, list)
            or any(not isinstance(value, str) for value in rule_selectors)
            or not set(rule_selectors) <= known_selectors
        ):
            raise ContractError(f"reviewed error selector rule has unknown selectors: {rule['id']}")
        for field in ("candidate_ids", "target_paths"):
            values = rule.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ContractError(
                    f"reviewed error selector {field} must be a string list: {rule['id']}"
                )
        if not (rule.get("candidate_ids") or rule.get("target_paths")):
            raise ContractError(
                f"reviewed error selector rule has no source identity: {rule['id']}"
            )
    for candidate in atlas_candidates:
        matching_rules = [
            rule
            for rule in error_selector_rules
            if candidate["id"] in rule.get("candidate_ids", [])
            or candidate.get("target_path") in rule.get("target_paths", [])
        ]
        if len(matching_rules) > 1:
            raise ContractError(
                f"source API candidate matches multiple error selector rules: {candidate['id']}"
            )
        if matching_rules:
            matched_error_rules.add(matching_rules[0]["id"])
    if matched_error_rules != rule_ids:
        raise ContractError(
            "reviewed error selector rules do not match pinned source candidates: "
            + ", ".join(sorted(rule_ids - matched_error_rules))
        )

    authority = metadata.get("authority", {})
    source_root = (PROJECT_ROOT / authority.get("checkout", "../fastapi")).resolve()
    starlette_authority = authority.get("starlette", {})
    starlette_checkout_text = starlette_authority.get("checkout", "../starlette")
    starlette_source_root = Path(
        os.environ.get("STARLETTE_SOURCE", str(PROJECT_ROOT / starlette_checkout_text))
    ).resolve()

    def verify_source_evidence(reference: dict[str, Any], context: str) -> None:
        source_path = reference.get("path")
        if not isinstance(source_path, str):
            raise ContractError(f"reviewed source evidence has no path: {context}")
        source_authority = reference.get("source_authority")
        if source_authority is not None:
            expected_authority = f"Starlette {starlette_authority.get('version')}"
            if source_authority != expected_authority:
                raise ContractError(f"reviewed Starlette source authority differs: {context}")
            evidence_root = starlette_source_root
        else:
            evidence_root = source_root
        path = (evidence_root / source_path).resolve()
        if evidence_root not in path.parents or not path.is_file():
            raise ContractError(
                f"reviewed source evidence path is missing or escapes checkout: {context}"
            )
        if source_authority is not None:
            expected_commit = starlette_authority.get("commit")
            try:
                observed_commit = subprocess.run(
                    ["git", "-C", str(evidence_root), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                committed_source = subprocess.run(
                    ["git", "-C", str(evidence_root), "show", f"{expected_commit}:{source_path}"],
                    check=True,
                    capture_output=True,
                ).stdout
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ContractError(
                    f"reviewed Starlette source identity cannot be verified: {context}"
                ) from exc
            if observed_commit != expected_commit or path.read_bytes() != committed_source:
                raise ContractError(
                    f"reviewed Starlette source differs from its pinned commit: {context}"
                )
        source_text = path.read_text(encoding="utf-8")
        symbol = reference.get("symbol")
        if symbol is not None:
            try:
                tree = ast.parse(source_text, filename=source_path)
            except SyntaxError as exc:
                raise ContractError(
                    f"reviewed source evidence is not valid Python: {source_path}"
                ) from exc
            if reference.get("kind") == "import-binding":
                line = reference.get("line")
                imported_module = reference.get("imported_module")
                relative_level = reference.get("relative_level")
                imported_name = reference.get("imported_name")
                alias_spelling = reference.get("alias_spelling")
                local_name = reference.get("local_name")
                target_path = reference.get("target_path")
                if (
                    not isinstance(line, int)
                    or not isinstance(imported_module, str)
                    or not isinstance(relative_level, int)
                    or relative_level < 0
                    or not isinstance(imported_name, str)
                    or not isinstance(alias_spelling, str)
                    or not isinstance(local_name, str)
                    or not isinstance(target_path, str)
                    or symbol != local_name
                ):
                    raise ContractError(
                        f"reviewed source import binding differs: {source_path}:{line}:{symbol}"
                    )
                matching_bindings = [
                    alias
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                    and node.lineno == line
                    and node.module == imported_module
                    and node.level == relative_level
                    for alias in node.names
                    if alias.name == imported_name
                    and alias.asname == alias_spelling
                    and (alias.asname or alias.name) == local_name
                ]
                if not matching_bindings:
                    raise ContractError(
                        f"reviewed source import binding differs: {source_path}:{line}:{symbol}"
                    )
                source_parts = list(Path(source_path).with_suffix("").parts)
                package_parts = source_parts[:-1]
                if relative_level > len(package_parts):
                    raise ContractError(
                        f"reviewed source import level is invalid: {source_path}:{line}"
                    )
                resolved_parts = package_parts[: len(package_parts) - relative_level + 1]
                resolved_module_parts = (
                    resolved_parts + imported_module.split(".")
                    if relative_level
                    else imported_module.split(".")
                )
                observed_target_path = ".".join(resolved_module_parts + [imported_name])
                if observed_target_path != target_path:
                    raise ContractError(
                        f"reviewed source import target differs: {source_path}:{line}:{target_path}"
                    )
            elif reference.get("kind") != "module-value" and not any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and node.name == symbol
                for node in ast.walk(tree)
            ):
                raise ContractError(f"reviewed source symbol is missing: {source_path}:{symbol}")
        if reference.get("kind") == "module-value":
            try:
                tree = ast.parse(source_text, filename=source_path)
            except SyntaxError as exc:
                raise ContractError(
                    f"reviewed source evidence is not valid Python: {source_path}"
                ) from exc
            symbol = reference.get("symbol")
            start_line = reference.get("start_line")
            end_line = reference.get("end_line")
            definitions = [
                node
                for node in tree.body
                if (
                    isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == symbol
                )
                or (
                    isinstance(node, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == symbol
                        for target in node.targets
                    )
                )
            ]
            if not any(
                node.lineno == start_line and getattr(node, "end_lineno", None) == end_line
                for node in definitions
            ):
                raise ContractError(
                    f"reviewed module value line range differs: {source_path}:{symbol}"
                )
        if reference.get("kind") == "source-definition":
            try:
                tree = ast.parse(source_text, filename=source_path)
            except SyntaxError as exc:
                raise ContractError(
                    f"reviewed source evidence is not valid Python: {source_path}"
                ) from exc
            owner = reference.get("owner")
            owner_nodes = (
                [
                    node
                    for node in tree.body
                    if isinstance(node, ast.ClassDef) and node.name == owner
                ]
                if isinstance(owner, str)
                else []
            )
            definitions = (
                [
                    node
                    for owner_node in owner_nodes
                    for node in owner_node.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == reference.get("symbol")
                ]
                if isinstance(owner, str)
                else [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == reference.get("symbol")
                ]
            )
            if not any(
                node.lineno == reference.get("start_line")
                and getattr(node, "end_lineno", None) == reference.get("end_line")
                for node in definitions
            ):
                raise ContractError(f"reviewed source line range differs: {source_path}:{symbol}")
        if reference.get("kind") == "release-note":
            lines = source_text.splitlines()
            line = reference.get("line")
            if not isinstance(line, int) or line < 1 or line > len(lines):
                raise ContractError(f"reviewed release-note line is out of range: {source_path}")
            observed = lines[line - 1].replace("`", "")
            if reference.get("statement") not in observed:
                raise ContractError(
                    f"reviewed release-note statement differs: {source_path}:{line}"
                )
            if reference.get("section") not in source_text:
                raise ContractError(f"reviewed release-note section is missing: {source_path}")
        if reference.get("kind") == "class-inheritance":
            try:
                tree = ast.parse(source_text, filename=source_path)
            except SyntaxError as exc:
                raise ContractError(
                    f"reviewed source evidence is not valid Python: {source_path}"
                ) from exc
            line = reference.get("line")
            base_class = reference.get("base_class")
            classes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and node.name == symbol
            ]
            matching_bases = [
                base
                for node in classes
                if node.lineno == line
                for base in node.bases
                if (isinstance(base, ast.Name) and base.id == base_class)
                or (isinstance(base, ast.Attribute) and base.attr == base_class)
            ]
            if not isinstance(line, int) or not isinstance(base_class, str) or not matching_bases:
                raise ContractError(f"reviewed class inheritance differs: {source_path}:{symbol}")
            binding_fields = {
                "base_expression",
                "base_import_module",
                "base_import_name",
                "base_import_alias",
                "base_import_line",
            }
            supplied_binding_fields = binding_fields & set(reference)
            if supplied_binding_fields or reference.get("symbol") == "APIRouter":
                if supplied_binding_fields != binding_fields:
                    raise ContractError(
                        f"reviewed class base import binding is incomplete: {source_path}:{symbol}"
                    )
                expression = reference.get("base_expression")
                import_module = reference.get("base_import_module")
                import_name = reference.get("base_import_name")
                import_alias = reference.get("base_import_alias")
                import_line = reference.get("base_import_line")
                expression_bases = [
                    base for base in matching_bases if ast.unparse(base) == expression
                ]
                root_names = []
                for base in expression_bases:
                    root = base
                    while isinstance(root, ast.Attribute):
                        root = root.value
                    if isinstance(root, ast.Name):
                        root_names.append(root.id)
                imported_aliases = [
                    alias.asname or alias.name
                    for node in tree.body
                    if isinstance(node, ast.ImportFrom)
                    and node.level == 0
                    and node.module == import_module
                    and node.lineno == import_line
                    for alias in node.names
                    if alias.name == import_name
                ]
                if (
                    not isinstance(expression, str)
                    or not isinstance(import_module, str)
                    or not isinstance(import_name, str)
                    or not isinstance(import_alias, str)
                    or not isinstance(import_line, int)
                    or isinstance(import_line, bool)
                    or not expression_bases
                    or root_names != [import_alias]
                    or imported_aliases != [import_alias]
                ):
                    raise ContractError(
                        f"reviewed class base does not resolve through its source import: "
                        f"{source_path}:{symbol}"
                    )
        if reference.get("kind") == "documentation-text":
            lines = source_text.splitlines()
            start_line = reference.get("start_line")
            end_line = reference.get("end_line")
            required_text = reference.get("required_text")
            if (
                not isinstance(start_line, int)
                or not isinstance(end_line, int)
                or start_line < 1
                or end_line < start_line
                or end_line > len(lines)
                or not isinstance(required_text, list)
                or any(not isinstance(value, str) or not value for value in required_text)
            ):
                raise ContractError(f"reviewed documentation evidence range is invalid: {context}")
            excerpt = "\n".join(lines[start_line - 1 : end_line])
            if any(value not in excerpt for value in required_text):
                raise ContractError(
                    f"reviewed documentation evidence text differs: {source_path}:{start_line}"
                )

    for operation_id, operation in overlay_operations.items():
        evidence = operation.get("source_evidence", [])
        if not isinstance(evidence, list) or not evidence:
            raise ContractError(f"reviewed API operation requires source evidence: {operation_id}")
        for reference in evidence:
            verify_source_evidence(reference, operation_id)
    for warning_id, review in warning_reviews.items():
        for reference in review.get("evidence", []):
            verify_source_evidence(reference, warning_id)

    known_features = {
        feature_id
        for row in coverage_by_doc_path.values()
        for feature_id in row[1].get("feature_ids", [])
    }
    known_error_ids = set(errors)
    if materialized_input_index.get("schema") != MATERIALIZED_INPUT_INDEX_SCHEMA_ID:
        raise ContractError("materialized input index schema is unsupported for the API contract")
    api_input_refs_by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_api_probe_refs: set[tuple[str, str, str, str]] = set()
    for workflow_ref in materialized_input_index.get("workflows", []):
        if not isinstance(workflow_ref, dict):
            raise ContractError("materialized input index contains an invalid workflow row")
        for probe_ref in workflow_ref.get("api_probes", []):
            if not isinstance(probe_ref, dict):
                raise ContractError("materialized input index contains an invalid API probe row")
            symbol_id = probe_ref.get("symbol_id")
            case_id = probe_ref.get("case_id")
            probe_id = probe_ref.get("probe_id")
            workflow_id = workflow_ref.get("id")
            selectors = probe_ref.get("observation_selectors")
            if (
                not isinstance(symbol_id, str)
                or symbol_id not in api_symbol_ids
                or not isinstance(case_id, str)
                or case_id not in workflow_ref.get("case_ids", [])
                or not isinstance(probe_id, str)
                or not isinstance(workflow_id, str)
                or not isinstance(selectors, list)
                or not selectors
                or any(not isinstance(selector, str) for selector in selectors)
                or not set(selectors) <= known_selectors
            ):
                raise ContractError(
                    f"materialized direct API probe has an invalid source or selector link: "
                    f"{workflow_id}::{case_id}::{probe_id}"
                )
            key = (workflow_id, case_id, probe_id, symbol_id)
            if key in seen_api_probe_refs:
                raise ContractError(f"materialized direct API probe is duplicated: {key}")
            seen_api_probe_refs.add(key)
            api_input_refs_by_symbol[symbol_id].append(
                {
                    "workflow_id": workflow_id,
                    "input_path": workflow_ref["input_path"],
                    "input_sha256": workflow_ref["input_sha256"],
                    "recipe_path": workflow_ref["recipe_path"],
                    "recipe_sha256": workflow_ref["recipe_sha256"],
                    "workload_path": workflow_ref["workload_path"],
                    "workload_sha256": workflow_ref["workload_sha256"],
                    "case_id": case_id,
                    "probe_id": probe_id,
                    "probe_kind": probe_ref["probe_kind"],
                    "observation_selectors": sorted(set(selectors)),
                }
            )
    for references in api_input_refs_by_symbol.values():
        references.sort(
            key=lambda reference: (
                reference["workflow_id"],
                reference["case_id"],
                reference["probe_id"],
            )
        )
    operation_fixture_refs_by_symbol: dict[str, list[dict[str, Any]]] = {}
    for operation_id, operation in overlay_operations.items():
        if not isinstance(operation, dict):
            raise ContractError(f"reviewed API overlay operation must be a mapping: {operation_id}")
        fixture_refs: list[dict[str, Any]] = []
        seen_fixture_refs: set[tuple[str, str]] = set()
        for fixture_reference in operation.get("fixture_refs", []):
            recipe_path = fixture_reference.get("recipe_path")
            case_id = fixture_reference.get("case_id")
            if not isinstance(recipe_path, str) or not isinstance(case_id, str):
                raise ContractError(
                    f"reviewed API operation fixture reference is incomplete: {operation_id}"
                )
            key = (recipe_path, case_id)
            if key in seen_fixture_refs:
                raise ContractError(
                    f"reviewed API operation fixture reference is duplicated: "
                    f"{operation_id}: {recipe_path}::{case_id}"
                )
            seen_fixture_refs.add(key)
            fixture_refs.append(
                _validate_reviewed_operation_fixture_reference(
                    fixture_reference,
                    materialized_workflows=materialized_input_index["workflows"],
                    operation_id=operation_id,
                )
            )
        operation_fixture_refs_by_symbol[operation_id] = fixture_refs
        operation_features = operation.get("feature_ids", [])
        operation_selectors = operation.get("observation_selectors", [])
        operation_errors = operation.get("error_contract_ids", [])
        if (
            not isinstance(operation_features, list)
            or not set(operation_features) <= known_features
        ):
            raise ContractError(f"reviewed API overlay has unknown feature IDs: {operation_id}")
        if (
            not isinstance(operation_selectors, list)
            or not set(operation_selectors) <= known_selectors
        ):
            raise ContractError(f"reviewed API overlay has unknown selectors: {operation_id}")
        if not isinstance(operation_errors, list) or not set(operation_errors) <= known_error_ids:
            raise ContractError(
                f"reviewed API overlay has unknown error references: {operation_id}"
            )
        for documentation_ref in operation.get("documentation_contract_refs", []):
            if not isinstance(documentation_ref, dict):
                raise ContractError(
                    "reviewed API overlay documentation reference must be a mapping: "
                    f"{operation_id}"
                )
            source_path = documentation_ref.get("source_path")
            coverage_ref = coverage_by_doc_path.get(source_path)
            if coverage_ref is None:
                raise ContractError(
                    f"reviewed API overlay references an unreviewed docs page: {source_path}"
                )
            coverage_row = coverage_ref[1]
            if documentation_ref.get("fixture_id") != coverage_row.get("fixture_id"):
                raise ContractError(
                    f"reviewed API overlay docs fixture identity differs: {source_path}"
                )
            doc_selectors = documentation_ref.get("observation_selectors", [])
            if not isinstance(doc_selectors, list) or not set(doc_selectors) <= set(
                coverage_row.get("observation_selectors", [])
            ):
                raise ContractError(
                    f"reviewed API overlay docs selectors exceed page evidence: {source_path}"
                )

    inherited_operation_contracts: list[dict[str, Any]] = []
    for candidate_id, review in inherited_candidate_reviews.items():
        reviewed_candidate = inherited_candidates_by_id[candidate_id]
        exposure_candidate_id = review.get("fastapi_exposure_candidate_id")
        exposure_candidate = candidates_by_id.get(exposure_candidate_id)
        if (
            reviewed_candidate.get("classification") != review.get("classification")
            or reviewed_candidate.get("kind") != review.get("kind", "inherited_method")
            or reviewed_candidate.get("classification_evidence_rule")
            != review.get("classification_evidence_rule")
            or reviewed_candidate.get("exposure_candidate_id") != exposure_candidate_id
            or not isinstance(exposure_candidate, dict)
            or exposure_candidate.get("classification") != "supported"
            or exposure_candidate.get("kind") != "class"
            or reviewed_candidate.get("source_evidence") != review.get("source_evidence")
            or reviewed_candidate.get("starlette_rs_review_ref", {}).get("qualified_name")
            != review.get("starlette_rs_review", {}).get("qualified_name")
            or reviewed_candidate.get("starlette_rs_review_ref", {}).get("api_disposition")
            != review.get("starlette_rs_review", {}).get("api_disposition")
            or reviewed_candidate.get("reviewed_overlay_ref")
            != (
                "/reviewed_api_contract_overlay/inherited_candidate_reviews/"
                + candidate_id.replace("~", "~0").replace("/", "~1")
            )
        ):
            raise ContractError(
                f"atlas inherited API classification differs from reviewed metadata: {candidate_id}"
            )
        evidence = review.get("source_evidence", [])
        evidence_kinds = {reference.get("kind") for reference in evidence}
        if not {"class-inheritance", "source-definition"} <= evidence_kinds:
            raise ContractError(
                f"inherited API candidate lacks source evidence kinds: {candidate_id}"
            )
        inheritance_refs = [
            reference for reference in evidence if reference.get("kind") == "class-inheritance"
        ]
        starlette_refs = [
            reference for reference in evidence if reference.get("kind") == "source-definition"
        ]
        if len(inheritance_refs) != 1 or len(starlette_refs) != 1:
            raise ContractError(
                f"inherited API candidate must have one FastAPI base and Starlette member ref: "
                f"{candidate_id}"
            )
        inheritance_ref = inheritance_refs[0]
        starlette_ref = starlette_refs[0]
        if inheritance_ref.get("symbol") == "APIRouter" and not {
            "base_expression",
            "base_import_module",
            "base_import_name",
            "base_import_alias",
            "base_import_line",
        } <= set(inheritance_ref):
            raise ContractError(
                f"inherited APIRouter candidate does not document its Starlette base binding: "
                f"{candidate_id}"
            )
        fastapi_module = (
            Path(str(inheritance_ref.get("path", ""))).with_suffix("").as_posix().replace("/", ".")
        )
        starlette_module = (
            Path(str(starlette_ref.get("path", ""))).with_suffix("").as_posix().replace("/", ".")
        )
        expected_exposure_id = f"{fastapi_module}.{inheritance_ref.get('symbol')}"
        expected_candidate_id = f"{expected_exposure_id}.{starlette_ref.get('symbol')}"
        expected_starlette_name = (
            f"{starlette_module}.{starlette_ref.get('owner')}.{starlette_ref.get('symbol')}"
        )
        if (
            exposure_candidate_id != expected_exposure_id
            or candidate_id != expected_candidate_id
            or inheritance_ref.get("base_class") != starlette_ref.get("owner")
            or review.get("starlette_rs_review", {}).get("qualified_name")
            != expected_starlette_name
        ):
            raise ContractError(
                f"inherited API candidate ID or sibling review does not match its evidence: "
                f"{candidate_id}"
            )
        for reference in evidence:
            verify_source_evidence(reference, candidate_id)
        if not starlette_refs or any(
            reference.get("source_authority") != f"Starlette {starlette_authority.get('version')}"
            for reference in starlette_refs
        ):
            raise ContractError(
                f"inherited API candidate has no exact Starlette source definition: {candidate_id}"
            )
        sibling_review = review.get("starlette_rs_review", {})
        if sibling_review.get("api_disposition") != review.get(
            "classification"
        ) or reviewed_candidate.get("starlette_rs_review_ref", {}).get("path") != atlas.get(
            "authorities", {}
        ).get("starlette_rs", {}).get("api_review_path"):
            raise ContractError(
                f"inherited API candidate Starlette-RS review reference differs: {candidate_id}"
            )

    for operation_id, operation in inherited_operations.items():
        if operation_id in overlay_operations or operation_id in candidates_by_id:
            raise ContractError(
                f"inherited API operation duplicates another public-surface record: {operation_id}"
            )
        exposure_candidate_id = operation.get("fastapi_exposure_candidate_id")
        exposure_candidate = candidates_by_id.get(exposure_candidate_id)
        if (
            not isinstance(exposure_candidate_id, str)
            or exposure_candidate is None
            or exposure_candidate.get("classification") != "supported"
            or exposure_candidate.get("kind") != "class"
        ):
            raise ContractError(
                "inherited API operation must point to a supported FastAPI class candidate: "
                f"{operation_id}"
            )
        sibling_gap = operation.get("sibling_contract_gap")
        has_sibling_gap = isinstance(sibling_gap, dict)
        canonical_operation_id = operation.get("canonical_operation_id")
        if not has_sibling_gap and (
            not isinstance(canonical_operation_id, str) or not canonical_operation_id
        ):
            raise ContractError(
                f"inherited API operation has no canonical sibling operation: {operation_id}"
            )
        reviewed_candidate = inherited_candidates_by_id[operation_id]
        expected_overlay_ref = (
            "/reviewed_api_contract_overlay/inherited_operations/"
            + operation_id.replace("~", "~0").replace("/", "~1")
        )
        inherited_kind = operation.get("kind", "inherited_method")
        if (
            reviewed_candidate.get("kind") != inherited_kind
            or reviewed_candidate.get("classification") != "supported"
            or reviewed_candidate.get("exposure_candidate_id") != exposure_candidate_id
            or reviewed_candidate.get("source_evidence") != operation.get("source_evidence")
            or reviewed_candidate.get("documentation_contract_refs")
            != operation.get("documentation_contract_refs")
            or reviewed_candidate.get("fixture_refs") != operation.get("fixture_refs")
            or reviewed_candidate.get("feature_ids") != operation.get("feature_ids")
            or reviewed_candidate.get("observation_selectors")
            != operation.get("observation_selectors")
            or reviewed_candidate.get("reviewed_overlay_ref") != expected_overlay_ref
            or (
                has_sibling_gap
                and (
                    "canonical_operation_id" in reviewed_candidate
                    or reviewed_candidate.get("signature_source")
                    != operation.get("signature_source")
                    or reviewed_candidate.get("attribute_source")
                    != operation.get("attribute_source")
                    or reviewed_candidate.get("sibling_contract_gap") != sibling_gap
                    or reviewed_candidate.get("target_binding") != operation.get("target_binding")
                )
            )
            or (
                not has_sibling_gap
                and (
                    reviewed_candidate.get("canonical_operation_id") != canonical_operation_id
                    or reviewed_candidate.get("target_binding") != operation.get("target_binding")
                )
            )
        ):
            raise ContractError(
                f"atlas inherited API candidate differs from reviewed metadata: {operation_id}"
            )
        evidence = operation.get("source_evidence", [])
        if not evidence:
            raise ContractError(
                f"inherited API operation requires exposure evidence: {operation_id}"
            )
        for reference in evidence:
            verify_source_evidence(reference, operation_id)
        inheritance_refs = [
            reference for reference in evidence if reference.get("kind") == "class-inheritance"
        ]
        class_source_refs = exposure_candidate.get("source_evidence", [])
        class_name = exposure_candidate_id.rsplit(".", 1)[-1]
        if (
            len(inheritance_refs) != 1
            or not isinstance(class_source_refs, list)
            or inheritance_refs[0].get("symbol") != class_name
            or not any(
                isinstance(source_ref, dict)
                and source_ref.get("path") == inheritance_refs[0].get("path")
                and source_ref.get("line") == inheritance_refs[0].get("line")
                for source_ref in class_source_refs
            )
        ):
            raise ContractError(
                f"inherited API operation class evidence does not match its exposure candidate: "
                f"{operation_id}"
            )
        evidence_kinds = {reference.get("kind") for reference in evidence}
        if not {"class-inheritance", "documentation-text"} <= evidence_kinds:
            raise ContractError(
                "inherited API exposure requires both class inheritance and documentation text: "
                f"{operation_id}"
            )

        operation_features = operation.get("feature_ids", [])
        operation_selectors = operation.get("observation_selectors", [])
        if (
            not isinstance(operation_features, list)
            or not set(operation_features) <= known_features
        ):
            raise ContractError(f"inherited API operation has unknown feature IDs: {operation_id}")
        if (
            not isinstance(operation_selectors, list)
            or not set(operation_selectors) <= known_selectors
        ):
            raise ContractError(f"inherited API operation has unknown selectors: {operation_id}")

        documentation_refs: list[dict[str, Any]] = []
        documentation_paths: set[str] = set()
        selectors = set(operation_selectors)
        feature_ids = set(operation_features)
        for documentation_ref in operation.get("documentation_contract_refs", []):
            source_path = documentation_ref.get("source_path")
            coverage_reference = coverage_by_doc_path.get(source_path)
            if coverage_reference is None:
                raise ContractError(
                    f"inherited API operation references an unreviewed docs page: {source_path}"
                )
            coverage_pointer, coverage_row = coverage_reference
            if documentation_ref.get("fixture_id") != coverage_row.get("fixture_id"):
                raise ContractError(f"inherited API docs fixture identity differs: {source_path}")
            doc_selectors = documentation_ref.get("observation_selectors", [])
            if not set(doc_selectors) <= set(coverage_row.get("observation_selectors", [])):
                raise ContractError(
                    f"inherited API docs selectors exceed page evidence: {source_path}"
                )
            if not set(doc_selectors) <= set(operation_selectors):
                raise ContractError(
                    f"inherited API docs selectors exceed operation observations: {source_path}"
                )
            documentation_paths.add(source_path)
            fixture_id = coverage_row.get("fixture_id")
            documentation_refs.append(
                {
                    "coverage_matrix_ref": coverage_pointer,
                    "source_path": source_path,
                    "mapping_status": coverage_row["mapping_status"],
                    "fixture_id": fixture_id,
                    "fixture_design_ref": backlog_by_id.get(fixture_id) if fixture_id else None,
                    "observation_selectors": sorted(set(doc_selectors)),
                }
            )
            selectors.update(doc_selectors)
            feature_ids.update(coverage_row.get("feature_ids", []))
        if not documentation_refs:
            raise ContractError(
                f"inherited API operation requires a reviewed documentation mapping: {operation_id}"
            )
        evidenced_doc_paths = {
            reference.get("path")
            for reference in evidence
            if reference.get("kind") == "documentation-text"
        }
        if not documentation_paths <= evidenced_doc_paths:
            raise ContractError(
                f"inherited API documentation mapping lacks source evidence: {operation_id}"
            )

        fixture_refs: list[dict[str, Any]] = []
        for fixture_reference in operation.get("fixture_refs", []):
            fixture_refs.append(
                _validate_inherited_fixture_reference(
                    fixture_reference,
                    expected_doc_paths=documentation_paths,
                    expected_selectors=operation_selectors,
                    operation_id=operation_id,
                    inherited_kind=inherited_kind,
                )
            )
        if not fixture_refs:
            raise ContractError(
                f"inherited API operation requires an input fixture: {operation_id}"
            )

        inherited_contract = {
            "id": operation_id,
            "kind": inherited_kind,
            "exposure": "inherited-from-starlette",
            "reviewed_candidate_ref": _pointer(
                "reviewed_inherited_api_candidates",
                inherited_candidate_indexes[operation_id],
            ),
            "fastapi_exposure_candidate_ref": _pointer(
                "api_candidates", candidate_indexes[exposure_candidate_id]
            ),
            "exposure_evidence": evidence,
            "documentation_contract_refs": documentation_refs,
            "fixture_refs": fixture_refs,
            "feature_ids": sorted(feature_ids),
            "observation_selectors": sorted(selectors),
        }
        if has_sibling_gap:
            signature_source = operation.get("signature_source")
            sibling_gap_ref = _starlette_rs_contract_gap_reference(metadata, sibling_gap)
            target_binding = operation.get("target_binding", {})
            if isinstance(signature_source, dict):
                source_signature_ref = _starlette_source_signature_reference(
                    metadata, signature_source
                )
                expected_operation_id = sibling_gap.get("expected_operation_id")
                if expected_operation_id != source_signature_ref["source_operation_id"]:
                    raise ContractError(
                        "inherited sibling gap does not identify the pinned source method: "
                        f"{operation_id}"
                    )
                inherited_contract.update(
                    {
                        "signature": source_signature_ref["signature"],
                        "signature_source_ref": source_signature_ref,
                        "signature_contract_state": (
                            "source-signature-linked; sibling-operation-missing"
                        ),
                        "sibling_contract_gap": sibling_gap_ref,
                        "target_binding": {
                            "target_profile": TARGET_PROFILE,
                            "public_python_path": operation_id,
                            "implementation_owner": target_binding["implementation_owner"],
                            "implementation_owner_evidence": {
                                "kind": "pinned-source-signature-with-sibling-operation-gap",
                                "signature_source_ref": source_signature_ref,
                                "sibling_contract_gap_ref": sibling_gap_ref,
                            },
                            "status": target_binding["status"],
                            "known_gaps": target_binding["known_gaps"],
                        },
                    }
                )
            else:
                attribute_source = operation.get("attribute_source")
                if not isinstance(attribute_source, dict):
                    raise ContractError(
                        f"inherited sibling-gap row has no pinned source reference: {operation_id}"
                    )
                source_attribute_ref = _starlette_source_attribute_reference(
                    metadata, attribute_source
                )
                expected_operation_id = sibling_gap.get("expected_operation_id")
                if expected_operation_id != source_attribute_ref["source_attribute_id"]:
                    raise ContractError(
                        "inherited sibling gap does not identify the pinned source attribute: "
                        f"{operation_id}"
                    )
                inherited_contract.update(
                    {
                        "attribute_source_ref": source_attribute_ref,
                        "attribute_contract_state": (
                            "source-assignment-linked; sibling-accessor-missing"
                        ),
                        "sibling_contract_gap": sibling_gap_ref,
                        "target_binding": {
                            "target_profile": TARGET_PROFILE,
                            "public_python_path": operation_id,
                            "implementation_owner": target_binding["implementation_owner"],
                            "implementation_owner_evidence": {
                                "kind": (
                                    "pinned-source-attribute-assignment-with-sibling-accessor-gap"
                                ),
                                "attribute_source_ref": source_attribute_ref,
                                "sibling_contract_gap_ref": sibling_gap_ref,
                            },
                            "status": target_binding["status"],
                            "known_gaps": target_binding["known_gaps"],
                            "rust_binding": target_binding.get("rust_binding"),
                        },
                    }
                )
        else:
            canonical_operation_ref = _starlette_rs_operation_reference(
                metadata, canonical_operation_id, inherited_kind=inherited_kind
            )
            target_binding = operation.get("target_binding")
            if target_binding is None:
                target_binding = {
                    "implementation_owner": "starlette-rs",
                    "status": "full-contract-not-established",
                }
            rendered_target_binding = {
                "target_profile": TARGET_PROFILE,
                "public_python_path": operation_id,
                "implementation_owner": target_binding["implementation_owner"],
                "implementation_owner_evidence": {
                    "kind": "canonical-sibling-operation-reference",
                    "canonical_operation_ref": canonical_operation_ref,
                },
                "status": target_binding["status"],
            }
            if "known_gaps" in target_binding:
                rendered_target_binding["known_gaps"] = target_binding["known_gaps"]
            if "rust_binding" in target_binding:
                rendered_target_binding["rust_binding"] = target_binding["rust_binding"]
            inherited_contract.update(
                {
                    "canonical_operation_ref": canonical_operation_ref,
                    "signature_contract_state": "delegated-to-canonical-starlette-rs-operation",
                    "target_binding": rendered_target_binding,
                }
            )
        inherited_operation_contracts.append(inherited_contract)

    for warning_id, review in warning_reviews.items():
        candidate = candidates_by_id.get(warning_id)
        if candidate is None or candidate.get("classification") != review.get("classification"):
            raise ContractError(
                f"reviewed warning evidence must preserve source classification: {warning_id}"
            )
        if review.get("classification") != "uncertain":
            raise ContractError(
                f"warning evidence alone cannot promote a candidate classification: {warning_id}"
            )

    signature_statuses: Counter[str] = Counter()
    owner_counts: Counter[str] = Counter()
    symbols: list[dict[str, Any]] = []
    for atlas_index, candidate in enumerate(atlas_candidates):
        if candidate["classification"] != "supported":
            continue
        symbol_id = candidate["id"]
        if symbol_id not in standard_refs:
            raise ContractError(
                f"supported API symbol is missing the standard runtime reflection: {symbol_id}"
            )
        if symbol_id not in inventory_refs:
            raise ContractError(f"supported API symbol is missing source inventory: {symbol_id}")
        inventory_rows = _resolve_inventory_refs(inventory, inventory_refs[symbol_id])
        source_signature_refs = [
            pointer
            for pointer, row in zip(inventory_refs[symbol_id], inventory_rows, strict=True)
            if row.get("signature_source")
        ]
        source_constructor_definition_refs = sorted(
            {
                f"{pointer}/members/{member_index}"
                for pointer, row in zip(inventory_refs[symbol_id], inventory_rows, strict=True)
                if row.get("kind") == "class"
                for member_index, member in enumerate(row.get("members", []))
                if member.get("id", "").rsplit(".", 1)[-1] in {"__init__", "__new__"}
                and member.get("signature_source")
            }
        )
        source_signature_state = "recorded" if source_signature_refs else "not-recorded"

        if symbol_id in core_refs:
            core_pointer, core_symbol = core_refs[symbol_id]
            core_runtime_ref = {
                "ref": core_pointer,
                "status": "reflected",
                "object_identity": core_symbol.get("object_identity"),
                "kind": core_symbol.get("kind"),
                "signature_status": _signature_status(core_symbol),
            }
        else:
            module_id = _module_id_for_inventory_ref(
                inventory_refs[symbol_id][0], candidate, inventory
            )
            module_row = core_modules.get(module_id)
            if module_row is None or module_row[1].get("status") != "optional_feature_unavailable":
                raise ContractError(
                    "supported symbol lacks runtime reflection outside optional profile gap: "
                    f"{symbol_id}"
                )
            core_symbol = {}
            core_runtime_ref = {
                "ref": None,
                "module_ref": module_row[0],
                "status": "optional_feature_unavailable",
                "object_identity": None,
                "kind": None,
                "signature_status": "unavailable",
            }
        standard_pointer, standard_symbol = standard_refs[symbol_id]
        signature_status = _signature_status(standard_symbol)
        if signature_status == "available":
            contract_signature_state = "runtime-signature-reflected"
        elif signature_status == "unavailable":
            contract_signature_state = "runtime-signature-unavailable"
        elif standard_symbol.get("kind") == "module":
            contract_signature_state = "module-object-no-call-signature"
        elif source_signature_refs:
            contract_signature_state = "source-signature-recorded"
        elif signature_status == "not-applicable" or candidate["kind"] in {"field", "value"}:
            contract_signature_state = "non-callable-surface"
        else:
            contract_signature_state = "signature-not-captured"
        signature_statuses[contract_signature_state] += 1

        reviewed_operation = overlay_operations.get(symbol_id, {})
        implementation_owner, owner_reason, owner_source_refs = _implementation_owner_plan(
            candidate,
            candidates_by_id=candidates_by_id,
            candidate_indexes=candidate_indexes,
        )
        reviewed_target_binding = reviewed_operation.get("target_binding")
        if (
            reviewed_target_binding is not None
            and reviewed_target_binding["implementation_owner"] != implementation_owner
        ):
            raise ContractError(
                f"reviewed API target binding owner differs from the source ownership plan: "
                f"{symbol_id}"
            )
        owner_counts[implementation_owner] += 1

        documentation_refs: list[dict[str, Any]] = []
        selectors: set[str] = set()
        feature_ids: set[str] = set()
        input_workflow_refs = api_input_refs_by_symbol.get(symbol_id, [])
        identity_workflow_refs = identity_workflow_refs_by_symbol.get(symbol_id, [])
        for source_path in sorted(_source_doc_paths(candidate.get("public_evidence", []))):
            row_ref = coverage_by_doc_path.get(source_path)
            if row_ref is None:
                continue
            coverage_pointer, coverage_row = row_ref
            fixture_id = coverage_row.get("fixture_id")
            backlog_pointer = backlog_by_id.get(fixture_id) if fixture_id else None
            documentation_refs.append(
                {
                    "coverage_matrix_ref": coverage_pointer,
                    "source_path": source_path,
                    "mapping_status": coverage_row["mapping_status"],
                    "fixture_id": fixture_id,
                    "fixture_design_ref": backlog_pointer,
                    "observation_selectors": coverage_row["observation_selectors"],
                }
            )
            selectors.update(coverage_row["observation_selectors"])
            feature_ids.update(coverage_row["feature_ids"])

        feature_ids.update(reviewed_operation.get("feature_ids", []))
        selectors.update(reviewed_operation.get("observation_selectors", []))
        for input_workflow_ref in input_workflow_refs:
            selectors.update(input_workflow_ref["observation_selectors"])
        rust_binding = reviewed_operation.get("rust_binding")
        if rust_binding is not None and (
            not isinstance(rust_binding, str) or not rust_binding.strip()
        ):
            raise ContractError(
                f"reviewed Rust binding for {symbol_id} must be a nonempty source path"
            )
        supported_slice = reviewed_operation.get("supported_slice")
        operation_scope = {
            "status": "slice-described" if supported_slice else "scope-review-pending",
        }
        if supported_slice:
            operation_scope["metadata_ref"] = _pointer(
                "reviewed_api_contract_overlay", "operations", symbol_id, "supported_slice"
            )
        for documentation_ref in reviewed_operation.get("documentation_contract_refs", []):
            coverage_pointer, coverage_row = coverage_by_doc_path[documentation_ref["source_path"]]
            fixture_id = coverage_row.get("fixture_id")
            backlog_pointer = backlog_by_id.get(fixture_id) if fixture_id else None
            documentation_refs.append(
                {
                    "coverage_matrix_ref": coverage_pointer,
                    "source_path": documentation_ref["source_path"],
                    "mapping_status": coverage_row["mapping_status"],
                    "fixture_id": fixture_id,
                    "fixture_design_ref": backlog_pointer,
                    "observation_selectors": sorted(
                        set(documentation_ref["observation_selectors"])
                    ),
                }
            )
            selectors.update(documentation_ref["observation_selectors"])

        target_binding = {
            "target_profile": TARGET_PROFILE,
            "public_python_path": symbol_id,
            "implementation_owner": implementation_owner,
            "implementation_owner_evidence": {
                "kind": owner_reason,
                "source_candidate_refs": owner_source_refs,
            },
            "status": (
                reviewed_target_binding["status"]
                if reviewed_target_binding is not None
                else "full-contract-not-established"
            ),
            "rust_binding": rust_binding,
        }
        if reviewed_target_binding is not None:
            if "known_gaps" in reviewed_target_binding:
                target_binding["known_gaps"] = reviewed_target_binding["known_gaps"]
            if "rust_binding" in reviewed_target_binding:
                target_binding["rust_binding"] = reviewed_target_binding["rust_binding"]

        error_refs = list(errors.get(symbol_id, []))
        for error_id in reviewed_operation.get("error_contract_ids", []):
            error_refs.extend(errors[error_id])
        error_refs = list(dict.fromkeys(error_refs))
        for error_pointer in error_refs:
            error_index = int(error_pointer.rsplit("/", 1)[1])
            selectors.update(atlas["errors"][error_index]["observation_selectors"])

        symbols.append(
            {
                "id": symbol_id,
                "kind": candidate["kind"],
                "source_candidate_ref": _pointer("api_candidates", atlas_index),
                "source_inventory_refs": inventory_refs[symbol_id],
                "source_signature_state": source_signature_state,
                "source_signature_refs": source_signature_refs,
                **(
                    {"source_constructor_definition_refs": source_constructor_definition_refs}
                    if source_constructor_definition_refs
                    else {}
                ),
                "runtime_reflections": {
                    "core": core_runtime_ref,
                    "standard": {
                        "ref": standard_pointer,
                        "object_identity": standard_symbol.get("object_identity"),
                        "kind": standard_symbol.get("kind"),
                        "signature_status": _signature_status(standard_symbol),
                    },
                },
                "signature_contract_state": contract_signature_state,
                "alias_refs": aliases.get(symbol_id, []),
                "deprecation_refs": deprecations.get(symbol_id, []),
                "error_contract_refs": error_refs,
                "documentation_contract_refs": documentation_refs,
                "input_workflow_refs": input_workflow_refs,
                **(
                    {"operation_fixture_refs": operation_fixture_refs_by_symbol[symbol_id]}
                    if operation_fixture_refs_by_symbol.get(symbol_id)
                    else {}
                ),
                "identity_workflow_refs": identity_workflow_refs,
                "feature_ids": sorted(feature_ids),
                "observation_selectors": sorted(selectors),
                "operation_scope": operation_scope,
                "behavior_contract_state": (
                    "reviewed-operation-and-documentation-links; full compatibility pending"
                    if reviewed_operation
                    else "documentation-fixture-design-linked; operation-level review pending"
                    if documentation_refs
                    else "direct-api-input-fixture-linked; behavior review pending"
                    if input_workflow_refs
                    else "source-evidence-only; fixture link pending"
                ),
                "target_binding": {
                    **target_binding,
                },
            }
        )

    return {
        "schema": CONTRACT_SCHEMA,
        "status": "source-api-linked; behavior-and-target-contract-incomplete",
        "authority": {
            "fastapi": {
                "version": atlas["authorities"]["fastapi"]["version"],
                "commit": atlas["authorities"]["fastapi"]["commit"],
            },
            "starlette": {
                "version": "1.6.0",
                "commit": atlas["authorities"]["starlette"]["commit"],
            },
            "python": runtime_standard["authority"]["python"],
            "pydantic": runtime_standard["authority"]["pydantic"],
        },
        "target_profile": TARGET_PROFILE,
        "public_import": "fastapi",
        "classification_source": "source_artifacts.compatibility_atlas.api_candidates",
        "reviewed_operation_overlay_source": "metadata.yaml:/reviewed_api_contract_overlay",
        "identity_workflow_source": (
            "metadata.yaml:/reviewed_api_contract_overlay/identity_workflow_refs"
        ),
        "inherited_operation_source": (
            "metadata.yaml:/reviewed_api_contract_overlay/inherited_operations"
        ),
        "signature_source": [
            "source_artifacts.api_inventory",
            "source_artifacts.runtime_api_surface_core",
            "source_artifacts.runtime_api_surface_standard",
        ],
        "alias_deprecation_error_source": "source_artifacts.compatibility_atlas",
        "coverage_source": [
            "source_artifacts.compatibility_atlas.coverage_matrix",
            "source_artifacts.fixture_backlog",
            "source_artifacts.materialized_input_index.api_probes",
            "source_artifacts.materialized_input_index.workflows",
            "source_artifacts.materialized_input_index.mappings",
        ],
        "counts": {
            "required_public_symbols": len(symbols),
            "required_inherited_operations": len(inherited_operation_contracts),
            "required_public_api_candidates": len(symbols) + len(inherited_operation_contracts),
            "signature_contract_states": dict(sorted(signature_statuses.items())),
            "symbols_with_constructor_definition_refs": sum(
                bool(symbol.get("source_constructor_definition_refs")) for symbol in symbols
            ),
            "unique_source_constructor_definitions": len(
                {
                    reference
                    for symbol in symbols
                    for reference in symbol.get("source_constructor_definition_refs", [])
                }
            ),
            "operation_scope_statuses": dict(
                sorted(Counter(symbol["operation_scope"]["status"] for symbol in symbols).items())
            ),
            "implementation_owner_plans": dict(sorted(owner_counts.items())),
            "inherited_implementation_owner_plans": dict(
                sorted(
                    Counter(
                        operation["target_binding"]["implementation_owner"]
                        for operation in inherited_operation_contracts
                    ).items()
                )
            ),
            "symbols_with_documented_feature_refs": sum(
                bool(symbol["documentation_contract_refs"]) for symbol in symbols
            ),
            "symbols_with_alias_refs": sum(bool(symbol["alias_refs"]) for symbol in symbols),
            "symbols_with_deprecation_refs": sum(
                bool(symbol["deprecation_refs"]) for symbol in symbols
            ),
            "symbols_with_error_contract_refs": sum(
                bool(symbol["error_contract_refs"]) for symbol in symbols
            ),
            "symbols_with_direct_api_input_workflow_refs": sum(
                bool(symbol["input_workflow_refs"]) for symbol in symbols
            ),
            "symbols_with_operation_fixture_refs": sum(
                bool(symbol.get("operation_fixture_refs")) for symbol in symbols
            ),
            "operation_fixture_refs": sum(
                len(symbol.get("operation_fixture_refs", [])) for symbol in symbols
            ),
            "symbols_with_identity_workflow_refs": sum(
                bool(symbol["identity_workflow_refs"]) for symbol in symbols
            ),
            "identity_workflow_refs": sum(
                len(symbol["identity_workflow_refs"]) for symbol in symbols
            ),
        },
        "symbols": symbols,
        "inherited_operations": inherited_operation_contracts,
    }


def validate_api_workflow_public_surface(
    workflow: dict[str, Any],
    contract: dict[str, Any],
    inventory: dict[str, Any],
    *,
    input_path: str,
) -> list[str]:
    """Require each direct API probe to match a manifest input-workflow link."""
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise ContractError("direct Python API workflow requires the generated public API contract")
    symbols = [
        symbol
        for symbol in contract.get("symbols", [])
        if isinstance(symbol, dict) and isinstance(symbol.get("id"), str)
    ]
    symbols_by_id = {symbol["id"]: symbol for symbol in symbols}
    selected: set[str] = set()
    for case in workflow.get("cases", []):
        selected_in_case: set[str] = set()
        for probe in case.get("probes", []):
            public_symbol = probe.get("public_callable", probe.get("public_attribute", {}))
            module = public_symbol.get("module")
            attribute = public_symbol.get("attribute")
            symbol_id = f"{module}.{attribute}"
            symbol = symbols_by_id.get(symbol_id)
            if symbol is None:
                raise ContractError(
                    "direct Python API workflow references a symbol outside the supported "
                    f"source API contract: {symbol_id}"
                )
            runtime_kinds = {
                reflection.get("kind")
                for reflection in symbol.get("runtime_reflections", {}).values()
                if isinstance(reflection, dict)
            }
            callable_kinds = {
                "class",
                "function",
                "callable",
                "async_function",
                "method",
                "protocol_method",
            }
            manifest_callable = symbol.get("kind") in callable_kinds or bool(
                runtime_kinds & callable_kinds
            )
            is_callable_probe = "public_callable" in probe
            if is_callable_probe != manifest_callable:
                probe_kind = "callable" if is_callable_probe else "non-callable attribute"
                manifest_kind = "callable" if manifest_callable else "non-callable"
                raise ContractError(
                    f"direct API {probe_kind} probe disagrees with manifest {manifest_kind} "
                    f"kind: {symbol_id}"
                )
            input_refs = symbol.get("input_workflow_refs", [])
            matches = [
                reference
                for reference in input_refs
                if isinstance(reference, dict)
                and reference.get("input_path") == input_path
                and reference.get("case_id") == case.get("case_id")
                and reference.get("probe_id") == probe.get("probe_id")
                and reference.get("symbol_id", symbol_id) == symbol_id
            ]
            if len(matches) != 1:
                raise ContractError(
                    "direct Python API probe has no unique manifest input-workflow link: "
                    f"{input_path}::{case.get('case_id')}::{probe.get('probe_id')} -> {symbol_id}"
                )
            selected.add(symbol_id)
            selected_in_case.add(symbol_id)

        definition_symbols: set[str] = set()
        for evidence in case.get("source_evidence", []):
            if evidence.get("kind") != "upstream_api_definition":
                continue
            symbol_id = evidence.get("symbol_id")
            symbol = symbols_by_id.get(symbol_id)
            if not isinstance(symbol_id, str) or symbol is None:
                raise ContractError(
                    f"API definition evidence references a symbol outside the manifest: {symbol_id}"
                )
            if symbol_id not in selected_in_case:
                raise ContractError(
                    "API definition evidence is not bound to a probe in its case: "
                    f"{case.get('case_id')} -> {symbol_id}"
                )
            source_refs = symbol.get("source_inventory_refs")
            if not isinstance(source_refs, list) or any(
                not isinstance(reference, str) for reference in source_refs
            ):
                raise ContractError(f"manifest symbol has no source inventory refs: {symbol_id}")
            inventory_rows = _resolve_inventory_refs(inventory, source_refs)
            if not any(row.get("id") == symbol_id for row in inventory_rows):
                raise ContractError(
                    "API definition evidence inventory refs do not resolve the manifest symbol: "
                    f"{symbol_id}"
                )
            source_paths = {
                source_ref.get("path")
                for row in inventory_rows
                if isinstance((source_ref := row.get("source_ref")), dict)
            }
            if evidence.get("path") not in source_paths:
                raise ContractError(
                    "API definition evidence path differs from the manifest symbol source: "
                    f"{symbol_id} -> {evidence.get('path')}"
                )
            definition_symbols.add(symbol_id)

        for probe in case.get("probes", []):
            if "public_attribute" not in probe:
                continue
            public_attribute = probe["public_attribute"]
            symbol_id = f"{public_attribute['module']}.{public_attribute['attribute']}"
            if symbol_id not in definition_symbols:
                raise ContractError(
                    "direct public attribute probe lacks its source definition evidence: "
                    f"{case.get('case_id')} -> {symbol_id}"
                )
    if not selected:
        raise ContractError("direct Python API workflow contains no public symbol probes")
    return sorted(selected)


def _resolve_inventory_refs(inventory: dict[str, Any], pointers: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pointer in pointers:
        current: Any = inventory
        for part in pointer.strip("/").split("/"):
            key = part.replace("~1", "/").replace("~0", "~")
            current = current[int(key)] if isinstance(current, list) else current[key]
        if isinstance(current, dict):
            rows.append(current)
    return rows


def _signature_status(symbol: dict[str, Any]) -> str:
    signature = symbol.get("signature")
    return (
        signature.get("status", "not-applicable")
        if isinstance(signature, dict)
        else "not-applicable"
    )


def validate_api_surface_contract(
    actual: dict[str, Any] | None,
    *,
    inventory: dict[str, Any],
    atlas: dict[str, Any],
    backlog: dict[str, Any],
    materialized_input_index: dict[str, Any],
    runtime_core: dict[str, Any],
    runtime_standard: dict[str, Any],
) -> dict[str, Any]:
    """Require the active manifest block to match its current pinned evidence."""
    expected = build_api_surface_contract(
        inventory=inventory,
        atlas=atlas,
        backlog=backlog,
        materialized_input_index=materialized_input_index,
        runtime_core=runtime_core,
        runtime_standard=runtime_standard,
    )
    if actual != expected:
        if not isinstance(actual, dict):
            raise ContractError("manifest per-symbol API contract is missing")
        if actual.get("schema") != CONTRACT_SCHEMA:
            raise ContractError("manifest per-symbol API contract schema is unsupported")
        if actual.get("symbols") != expected["symbols"]:
            raise ContractError(
                "manifest per-symbol API contracts are stale or do not cover the supported source "
                "surface"
            )
        raise ContractError("manifest API contract summary differs from source evidence")
    return expected["counts"]
