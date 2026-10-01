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

from scripts.parity.contract import ContractError

CONTRACT_SCHEMA = "fastapi-rs/public-api-contract@1"
TARGET_PROFILE = "fastapi-rs-python-consumer"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OVERLAY_SCHEMA = "fastapi-rs/reviewed-api-contract-overlay@1"


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


def _starlette_rs_operation_reference(
    project_metadata: dict[str, Any], operation_id: str
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
    app_initializations = [
        node
        for node in ast.walk(factory_node)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "app" for target in node.targets)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "FastAPI"
    ]
    middleware_calls = [
        node
        for node in ast.walk(factory_node)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_middleware"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "app"
    ]
    if (
        not app_initializations
        or not middleware_calls
        or min(node.lineno for node in middleware_calls)
        <= min(node.lineno for node in app_initializations)
    ):
        raise ContractError(
            f"inherited API fixture does not call {operation_id} on FastAPI: {workload_path}"
        )

    observed_short_selectors = {
        selector
        for action in case.get("actions", [])
        if isinstance(action, dict)
        for observation in action.get("observations", [])
        if isinstance(observation, dict) and observation.get("kind") == "http_response"
        for selector in observation.get("selectors", [])
    }
    selector_aliases = {
        "http.status": "status",
        "http.headers.ordered": "headers",
        "http.body.bytes": "body",
    }
    missing_selectors = [
        selector
        for selector in expected_selectors
        if selector_aliases.get(selector) not in observed_short_selectors
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


def build_api_surface_contract(
    *,
    inventory: dict[str, Any],
    atlas: dict[str, Any],
    backlog: dict[str, Any],
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
        for field in ("feature_ids", "observation_selectors", "error_contract_ids"):
            values = operation.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ContractError(f"reviewed API {field} must be a string list: {operation_id}")
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
    duplicate_inherited_candidates = set(inherited_operations) & set(candidates_by_id)
    if duplicate_inherited_candidates:
        raise ContractError(
            "inherited API overlays must remain separate from source-declared candidates: "
            + ", ".join(sorted(duplicate_inherited_candidates))
        )
    if set(inherited_operations) != set(inherited_candidates_by_id):
        raise ContractError(
            "reviewed inherited API overlays differ from the generated atlas candidates: "
            + ", ".join(sorted(set(inherited_operations) ^ set(inherited_candidates_by_id)))
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

    def verify_source_evidence(reference: dict[str, Any], context: str) -> None:
        source_path = reference.get("path")
        if not isinstance(source_path, str):
            raise ContractError(f"reviewed source evidence has no path: {context}")
        path = (source_root / source_path).resolve()
        if source_root not in path.parents or not path.is_file():
            raise ContractError(
                f"reviewed source evidence path is missing or escapes checkout: {context}"
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
            if not any(
                isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                )
                and node.name == symbol
                for node in ast.walk(tree)
            ):
                raise ContractError(f"reviewed source symbol is missing: {source_path}:{symbol}")
        if reference.get("kind") == "source-definition":
            try:
                tree = ast.parse(source_text, filename=source_path)
            except SyntaxError as exc:
                raise ContractError(
                    f"reviewed source evidence is not valid Python: {source_path}"
                ) from exc
            definitions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == reference.get("symbol")
            ]
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
            if (
                not isinstance(line, int)
                or not isinstance(base_class, str)
                or not any(
                    node.lineno == line
                    and any(
                        (isinstance(base, ast.Name) and base.id == base_class)
                        or (isinstance(base, ast.Attribute) and base.attr == base_class)
                        for base in node.bases
                    )
                    for node in classes
                )
            ):
                raise ContractError(f"reviewed class inheritance differs: {source_path}:{symbol}")
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
    for operation_id, operation in overlay_operations.items():
        if not isinstance(operation, dict):
            raise ContractError(f"reviewed API overlay operation must be a mapping: {operation_id}")
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
        canonical_operation_id = operation.get("canonical_operation_id")
        if not isinstance(canonical_operation_id, str) or not canonical_operation_id:
            raise ContractError(
                f"inherited API operation has no canonical sibling operation: {operation_id}"
            )
        reviewed_candidate = inherited_candidates_by_id[operation_id]
        expected_overlay_ref = (
            "/reviewed_api_contract_overlay/inherited_operations/"
            + operation_id.replace("~", "~0").replace("/", "~1")
        )
        if (
            reviewed_candidate.get("kind") != "inherited_method"
            or reviewed_candidate.get("classification") != "supported"
            or reviewed_candidate.get("exposure_candidate_id") != exposure_candidate_id
            or reviewed_candidate.get("canonical_operation_id") != canonical_operation_id
            or reviewed_candidate.get("source_evidence") != operation.get("source_evidence")
            or reviewed_candidate.get("documentation_contract_refs")
            != operation.get("documentation_contract_refs")
            or reviewed_candidate.get("fixture_refs") != operation.get("fixture_refs")
            or reviewed_candidate.get("feature_ids") != operation.get("feature_ids")
            or reviewed_candidate.get("observation_selectors")
            != operation.get("observation_selectors")
            or reviewed_candidate.get("reviewed_overlay_ref") != expected_overlay_ref
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
                )
            )
        if not fixture_refs:
            raise ContractError(
                f"inherited API operation requires an input fixture: {operation_id}"
            )

        canonical_operation_ref = _starlette_rs_operation_reference(
            metadata, canonical_operation_id
        )
        inherited_operation_contracts.append(
            {
                "id": operation_id,
                "kind": "inherited_method",
                "exposure": "inherited-from-starlette",
                "reviewed_candidate_ref": _pointer(
                    "reviewed_inherited_api_candidates",
                    inherited_candidate_indexes[operation_id],
                ),
                "fastapi_exposure_candidate_ref": _pointer(
                    "api_candidates", candidate_indexes[exposure_candidate_id]
                ),
                "exposure_evidence": evidence,
                "canonical_operation_ref": canonical_operation_ref,
                "signature_contract_state": "delegated-to-canonical-starlette-rs-operation",
                "documentation_contract_refs": documentation_refs,
                "fixture_refs": fixture_refs,
                "feature_ids": sorted(feature_ids),
                "observation_selectors": sorted(selectors),
                "target_binding": {
                    "target_profile": TARGET_PROFILE,
                    "public_python_path": operation_id,
                    "implementation_owner": "starlette-rs",
                    "implementation_owner_evidence": {
                        "kind": "canonical-sibling-operation-reference",
                        "canonical_operation_ref": canonical_operation_ref,
                    },
                    "status": "full-contract-not-established",
                },
            }
        )

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
        signature = standard_symbol.get("signature")
        signature_status = signature.get("status") if isinstance(signature, dict) else None
        if signature_status == "available":
            contract_signature_state = "runtime-signature-reflected"
        elif signature_status == "unavailable":
            contract_signature_state = "runtime-signature-unavailable"
        elif standard_symbol.get("kind") == "module":
            contract_signature_state = "module-object-no-call-signature"
        elif source_signature_refs:
            contract_signature_state = "source-signature-recorded"
        elif candidate["kind"] in {"field", "value"}:
            contract_signature_state = "non-callable-surface"
        else:
            contract_signature_state = "signature-not-captured"
        signature_statuses[contract_signature_state] += 1

        implementation_owner, owner_reason, owner_source_refs = _implementation_owner_plan(
            candidate,
            candidates_by_id=candidates_by_id,
            candidate_indexes=candidate_indexes,
        )
        owner_counts[implementation_owner] += 1

        documentation_refs: list[dict[str, Any]] = []
        selectors: set[str] = set()
        feature_ids: set[str] = set()
        reviewed_operation = overlay_operations.get(symbol_id, {})
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
        rust_binding = reviewed_operation.get("rust_binding")
        if rust_binding is not None and (
            not isinstance(rust_binding, str) or not rust_binding.strip()
        ):
            raise ContractError(
                f"reviewed Rust binding for {symbol_id} must be a nonempty source path"
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
                "feature_ids": sorted(feature_ids),
                "observation_selectors": sorted(selectors),
                "behavior_contract_state": (
                    "reviewed-operation-and-documentation-links; full compatibility pending"
                    if reviewed_operation
                    else "documentation-fixture-design-linked; operation-level review pending"
                    if documentation_refs
                    else "source-evidence-only; fixture link pending"
                ),
                "target_binding": {
                    "target_profile": TARGET_PROFILE,
                    "public_python_path": symbol_id,
                    "implementation_owner": implementation_owner,
                    "implementation_owner_evidence": {
                        "kind": owner_reason,
                        "source_candidate_refs": owner_source_refs,
                    },
                    "status": "full-contract-not-established",
                    "rust_binding": rust_binding,
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
        ],
        "counts": {
            "required_public_symbols": len(symbols),
            "required_inherited_operations": len(inherited_operation_contracts),
            "required_public_api_candidates": len(symbols) + len(inherited_operation_contracts),
            "signature_contract_states": dict(sorted(signature_statuses.items())),
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
        },
        "symbols": symbols,
        "inherited_operations": inherited_operation_contracts,
    }


def validate_api_workflow_public_surface(
    workflow: dict[str, Any],
    contract: dict[str, Any],
    inventory: dict[str, Any],
) -> list[str]:
    """Require public probes and direct source-definition evidence to match the manifest."""
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
    runtime_core: dict[str, Any],
    runtime_standard: dict[str, Any],
) -> dict[str, Any]:
    """Require the active manifest block to match its current pinned evidence."""
    expected = build_api_surface_contract(
        inventory=inventory,
        atlas=atlas,
        backlog=backlog,
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
