"""Validate the pinned-source API atlas and input-only fixture backlog."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.parity.contract import ROOT, ContractError, read_json, sha256_file

API_CLASSIFICATIONS = {"supported", "private/internal", "uncertain"}
OUTPUT_KEYS = {
    "actual_output",
    "expected",
    "expected_body",
    "expected_error",
    "expected_errors",
    "expected_output",
    "expected_response",
    "expected_status",
    "oracle_observation",
    "oracle_observations",
    "oracle_output",
    "oracle_result",
    "oracle_results",
    "pass_fail",
    "timing",
    "timings",
}
FIXTURE_KINDS = {"upstream_test_module", "documented_feature_page"}
REVIEWED_CALLABLE_KINDS = {
    "classmethod",
    "function",
    "async_function",
    "method",
    "property_getter",
    "protocol_method",
}
FIXTURE_BACKLOG_SCHEMA_ID = "fastapi-rs/fixture-backlog@2"
QUERY_VALIDATION_ALIAS_FUNCTION_CASES = {
    "test_required_list_validation_alias_schema": (
        "fastapi.request-parameters.query.validation-alias-list.validation-only.openapi",
        ("openapi-validation-only-parameters",),
        ("openapi.document", "openapi.paths"),
    ),
    "test_required_list_validation_alias_missing": (
        "fastapi.request-parameters.query.validation-alias-list.validation-only.missing",
        ("direct-missing", "model-missing"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_validation_alias_by_name": (
        "fastapi.request-parameters.query.validation-alias-list.validation-only.rejects-field-name",
        ("direct-field-name", "model-field-name"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_validation_alias_by_validation_alias": (
        "fastapi.request-parameters.query.validation-alias-list.validation-only.accepts-wire-name",
        ("direct-wire-name", "model-wire-name"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_alias_and_validation_alias_schema": (
        "fastapi.request-parameters.query.validation-alias-list.both-aliases.openapi",
        ("openapi-both-aliases-parameters",),
        ("openapi.document", "openapi.paths"),
    ),
    "test_required_list_alias_and_validation_alias_missing": (
        "fastapi.request-parameters.query.validation-alias-list.both-aliases.missing",
        ("direct-missing", "model-missing"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_alias_and_validation_alias_by_name": (
        "fastapi.request-parameters.query.validation-alias-list.both-aliases.rejects-field-name",
        ("direct-field-name", "model-field-name"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_alias_and_validation_alias_by_alias": (
        "fastapi.request-parameters.query.validation-alias-list.both-aliases.rejects-declared-alias",
        ("direct-declared-alias", "model-declared-alias"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_alias_and_validation_alias_by_validation_alias": (
        "fastapi.request-parameters.query.validation-alias-list.both-aliases.accepts-validation-alias",
        ("direct-wire-name", "model-wire-name"),
        ("http.body.bytes", "http.status"),
    ),
}
QUERY_VALIDATION_ALIAS_RECIPE_PATH = (
    "tests/fixtures/input-recipes/parity/query-validation-alias-list-cases.yaml"
)
QUERY_VALIDATION_ALIAS_WORKFLOW_ID = "query-validation-alias-list-cases"
QUERY_REQUIRED_LIST_FUNCTION_CASES = {
    "test_required_list_str_schema": (
        "fastapi.request-parameters.query.required-list.plain",
        ("inspect-openapi",),
        ("openapi.document", "openapi.paths"),
    ),
    "test_required_list_str_missing": (
        "fastapi.request-parameters.query.required-list.plain",
        ("plain-direct-missing", "plain-model-missing"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_str": (
        "fastapi.request-parameters.query.required-list.plain",
        ("plain-direct-repeated", "plain-model-repeated"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_str_alias_schema": (
        "fastapi.request-parameters.query.required-list.declared-alias",
        ("inspect-openapi",),
        ("openapi.document", "openapi.paths"),
    ),
    "test_required_list_alias_missing": (
        "fastapi.request-parameters.query.required-list.declared-alias",
        ("alias-direct-missing", "alias-model-missing"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_alias_by_name": (
        "fastapi.request-parameters.query.required-list.declared-alias",
        ("alias-direct-field-name", "alias-model-field-name"),
        ("http.body.bytes", "http.status"),
    ),
    "test_required_list_alias_by_alias": (
        "fastapi.request-parameters.query.required-list.declared-alias",
        ("alias-direct-wire-name", "alias-model-wire-name"),
        ("http.body.bytes", "http.status"),
    ),
}
QUERY_REQUIRED_LIST_RECIPE_PATH = (
    "tests/fixtures/input-recipes/parity/query-required-list-aliases.yaml"
)
QUERY_REQUIRED_LIST_WORKFLOW_ID = "query-required-list-aliases"
REVIEWED_DIRECT_FUNCTION_WORKFLOW_LINKS = {
    (
        "tests/test_router_include_context.py",
        "test_url_path_for_uses_effective_context_for_live_included_route",
    ): (
        "inherited-app-url-path-for",
        "tests/fixtures/input-recipes/parity/inherited-app-url-path-for.yaml",
        "fastapi.applications.url-path-for.included-router-context",
        ("reverse-included-route",),
        ("http.status", "http.headers.ordered", "http.body.bytes"),
    ),
    (
        "tests/test_router_include_context.py",
        "test_url_path_for_uses_distinct_repeated_inclusion_contexts",
    ): (
        "inherited-apirouter-url-path-for",
        "tests/fixtures/input-recipes/parity/inherited-apirouter-url-path-for.yaml",
        "fastapi.apirouter.url-path-for.repeated-inclusion-context",
        ("reverse-parent-router-route",),
        ("http.status", "http.headers.ordered", "http.body.bytes"),
    ),
    (
        "tests/test_router_include_context.py",
        "test_openapi_cache_updates_after_live_route_addition",
    ): (
        "router-openapi-cache-after-include",
        "tests/fixtures/input-recipes/parity/router-openapi-cache-after-include.yaml",
        "fastapi.router.include-context.openapi-cache-after-live-route",
        (
            "observe-openapi-before-child-route",
            "add-child-route-after-openapi-cache",
            "observe-openapi-after-child-route",
        ),
        ("http.status", "openapi.document", "openapi.paths"),
    ),
    (
        "tests/test_additional_responses_response_class.py",
        "test_openapi_schema",
    ): (
        "additional-responses-response-class",
        "tests/fixtures/input-recipes/parity/additional-responses-response-class.yaml",
        "fastapi.additional-responses-response-class.openapi",
        ("inspect-paired-response-classes",),
        ("docs.response.status", "http.status", "openapi.document"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_app",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-app",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_app_override",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-app-override",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_a",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-a",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_a_override",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-a-override",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_a_a",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-a-a",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_a_a_override",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-a-a-override",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_a_b",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-a-b",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_a_b_override",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-a-b-override",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_b",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-b",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
    (
        "tests/test_default_response_class_router.py",
        "test_router_b_override",
    ): (
        "default-response-class-router-upstream",
        "tests/fixtures/input-recipes/parity/default-response-class-router-upstream.yaml",
        "fastapi.test.test-default-response-class-router.test-router-b-override",
        ("dispatch",),
        ("http.body.bytes", "http.headers.ordered", "http.status"),
    ),
}


def _fail(message: str) -> None:
    raise ContractError(f"compatibility atlas: {message}")


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _merge_page_selector_evidence(
    evidence_groups: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    selectors_by_feature: dict[str | None, set[str]] = {}
    extensions_by_feature: dict[str | None, set[str]] = {}
    for evidence_group in evidence_groups:
        for evidence in evidence_group:
            feature_id = evidence["feature_id"]
            selectors_by_feature.setdefault(feature_id, set()).update(evidence["selectors"])
            extensions_by_feature.setdefault(feature_id, set()).update(
                evidence.get("schema_extension_required", [])
            )

    merged = []
    for feature_id in sorted(selectors_by_feature, key=lambda value: (value is None, value or "")):
        evidence = {
            "feature_id": feature_id,
            "selectors": sorted(selectors_by_feature[feature_id]),
        }
        if extensions_by_feature[feature_id]:
            evidence["schema_extension_required"] = sorted(extensions_by_feature[feature_id])
        merged.append(evidence)
    return merged


def _source_path(root: Path, value: Any, label: str) -> Path:
    _require(isinstance(value, str) and bool(value), f"{label} has no source path")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError(f"compatibility atlas: {label} escapes its pinned source tree") from exc
    _require(candidate.is_file(), f"{label} source does not exist: {value}")
    return candidate


def _verify_source_ref(
    root: Path,
    reference: dict[str, Any],
    label: str,
    *,
    digest_key: str | None = None,
) -> None:
    path = _source_path(root, reference.get("path"), label)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = reference.get("line")
    end = reference.get("end_line", start)
    if start is not None:
        _require(
            isinstance(start, int) and 1 <= start <= len(lines), f"{label} line is out of range"
        )
        _require(
            isinstance(end, int) and start <= end <= len(lines),
            f"{label} end line is out of range",
        )
    if digest_key is not None:
        expected = reference.get(digest_key)
        _require(isinstance(expected, str) and bool(expected), f"{label} has no {digest_key}")
        _require(sha256_file(path) == expected, f"{label} source digest is stale")


def _validate_starlette_behavior_crosswalks(
    atlas: dict[str, Any], fastapi_source: Path, edges: list[dict[str, Any]]
) -> None:
    _require(
        isinstance(edges, list) and all(isinstance(edge, dict) for edge in edges),
        "Starlette integration edges must be a list of mappings",
    )
    expected_kinds = {
        "fastapi.routing.get_route_path": "private-helper-behavior",
        "fastapi.routing.is_async_callable": "private-helper-behavior",
        "fastapi.routing.wrap_app_handling_exceptions": "private-helper-behavior",
        "fastapi.routing.routing": "module-namespace-reference",
    }
    selected_contract = atlas.get("authorities", {}).get("starlette_rs", {})
    contract_id = selected_contract.get("current_contract_id")
    crosswalk_edges = {
        edge.get("fastapi_binding"): edge
        for edge in edges
        if isinstance(edge.get("starlette_rs_behavior_crosswalk"), dict)
    }
    _require(
        set(crosswalk_edges) == set(expected_kinds),
        "Starlette behavior crosswalks must cover the exact four reviewed bindings",
    )

    for binding_id, expected_kind in expected_kinds.items():
        edge = crosswalk_edges[binding_id]
        crosswalk = edge["starlette_rs_behavior_crosswalk"]
        kind = crosswalk.get("kind")
        _require(
            kind == expected_kind
            and isinstance(crosswalk.get("scope_note"), str)
            and bool(crosswalk["scope_note"].strip()),
            f"Starlette behavior crosswalk kind or scope is invalid: {binding_id}",
        )
        source_uses = crosswalk.get("fastapi_source_uses")
        _require(
            isinstance(source_uses, dict) and source_uses.get("path") == "fastapi/routing.py",
            f"Starlette behavior crosswalk source path is invalid: {binding_id}",
        )
        source_path = _source_path(fastapi_source, source_uses.get("path"), binding_id)
        source_tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

        if kind == "private-helper-behavior":
            _require(
                set(source_uses) == {"path", "call_lines"}
                and isinstance(source_uses.get("call_lines"), list)
                and bool(source_uses["call_lines"]),
                f"private helper call-line evidence is malformed: {binding_id}",
            )
            helper_name = crosswalk.get("starlette_symbol", "").rsplit(".", 1)[-1]
            call_lines = source_uses["call_lines"]
            _require(
                all(isinstance(line, int) and not isinstance(line, bool) for line in call_lines)
                and call_lines == sorted(set(call_lines)),
                f"private helper call lines must be sorted and unique: {binding_id}",
            )
            actual_call_lines = sorted(
                {
                    node.lineno
                    for node in ast.walk(source_tree)
                    if isinstance(node, ast.Call)
                    and (
                        (isinstance(node.func, ast.Name) and node.func.id == helper_name)
                        or (isinstance(node.func, ast.Attribute) and node.func.attr == helper_name)
                    )
                }
            )
            _require(
                actual_call_lines == call_lines,
                f"private helper call lines do not match pinned FastAPI: {binding_id}",
            )
            _require(
                crosswalk.get("resolution") == "existing-sibling-behavior-requirements"
                and not crosswalk.get("namespace_catalog_reference"),
                f"private helper crosswalk has the wrong resolution: {binding_id}",
            )
            operation_refs = crosswalk.get("target_operation_refs")
            _require(
                isinstance(operation_refs, list) and bool(operation_refs),
                f"private helper has no sibling behavior links: {binding_id}",
            )
            for reference in operation_refs:
                _require(
                    isinstance(reference, dict)
                    and reference.get("contract_id") == contract_id
                    and isinstance(reference.get("surface_id"), str)
                    and isinstance(reference.get("operation_id"), str)
                    and isinstance(reference.get("requirement_ids"), list)
                    and bool(reference["requirement_ids"])
                    and all(
                        isinstance(requirement_id, str) and bool(requirement_id)
                        for requirement_id in reference["requirement_ids"]
                    )
                    and isinstance(reference.get("target_support"), dict),
                    f"private helper sibling behavior link is incomplete: {binding_id}",
                )
        else:
            _require(
                set(source_uses) == {"path", "import_line", "alias", "consumed_members"}
                and isinstance(source_uses.get("import_line"), int)
                and not isinstance(source_uses.get("import_line"), bool)
                and isinstance(source_uses.get("alias"), str)
                and isinstance(source_uses.get("consumed_members"), list)
                and all(
                    isinstance(member, str) and bool(member)
                    for member in source_uses["consumed_members"]
                )
                and source_uses["consumed_members"] == sorted(set(source_uses["consumed_members"])),
                f"Starlette module namespace source evidence is malformed: {binding_id}",
            )
            alias = source_uses["alias"]
            imports = [
                node.lineno
                for node in source_tree.body
                if isinstance(node, ast.ImportFrom)
                and node.module == "starlette"
                and any(
                    item.name == "routing" and (item.asname or item.name) == alias
                    for item in node.names
                )
            ]
            members = sorted(
                {
                    node.attr
                    for node in ast.walk(source_tree)
                    if isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == alias
                }
            )
            _require(
                imports == [source_uses["import_line"]]
                and members == source_uses["consumed_members"],
                f"Starlette module namespace usage differs from pinned FastAPI: {binding_id}",
            )
            catalog_refs = [
                item
                for item in edge.get("starlette_rs_catalog_evidence", [])
                if isinstance(item, dict)
                and item.get("record_type") == "external_module_namespace_reference"
                and item.get("module") == crosswalk.get("starlette_symbol")
            ]
            namespace_ref = crosswalk.get("namespace_catalog_reference")
            _require(
                crosswalk.get("resolution") == "external-sibling-module-namespace-reference"
                and not crosswalk.get("target_operation_refs")
                and len(catalog_refs) == 1
                and namespace_ref == catalog_refs[0]
                and namespace_ref.get("contract_id") == contract_id
                and namespace_ref.get("catalog_path") == "docs/api-surface.csv"
                and isinstance(namespace_ref.get("catalog_sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", namespace_ref["catalog_sha256"]) is not None,
                f"Starlette module namespace catalog link is invalid: {binding_id}",
            )


def _validate_starlette_operation_aliases(edges: list[dict[str, Any]]) -> None:
    expected_aliases = {
        f"fastapi.concurrency.{name}": f"starlette.concurrency.{name}"
        for name in (
            "iterate_in_threadpool",
            "run_in_threadpool",
            "run_until_first_complete",
        )
    }
    alias_edges = {
        edge.get("fastapi_binding"): edge
        for edge in edges
        if isinstance(edge.get("starlette_rs_operation_aliases"), dict)
    }
    _require(
        set(alias_edges) == set(expected_aliases),
        "Starlette operation aliases must cover the reviewed FastAPI concurrency bindings",
    )
    for binding_id, expected_symbol in expected_aliases.items():
        edge = alias_edges[binding_id]
        alias = edge["starlette_rs_operation_aliases"]
        _require(
            edge.get("relation") == "direct_reexport"
            and edge.get("starlette_symbol") == expected_symbol
            and edge.get("fastapi_source", {}).get("path") == "fastapi/concurrency.py"
            and alias.get("resolution") == "direct-reexport-operation-alias"
            and alias.get("starlette_symbol") == expected_symbol
            and isinstance(alias.get("scope_note"), str)
            and bool(alias["scope_note"].strip()),
            f"Starlette operation alias source binding is invalid: {binding_id}",
        )
        refs = alias.get("target_operation_refs")
        operation_id = expected_symbol.rsplit(".", 1)[-1]
        _require(
            isinstance(refs, list) and bool(refs),
            f"Starlette operation alias has no sibling operation reference: {binding_id}",
        )
        for reference in refs:
            _require(
                isinstance(reference, dict)
                and reference.get("surface_id") == "starlette.concurrency"
                and reference.get("operation_id") == operation_id
                and isinstance(reference.get("contract_id"), str)
                and bool(reference["contract_id"])
                and isinstance(reference.get("requirement_ids"), list)
                and bool(reference["requirement_ids"])
                and all(
                    isinstance(requirement_id, str) and bool(requirement_id)
                    for requirement_id in reference["requirement_ids"]
                )
                and reference.get("source_path") == expected_symbol
                and isinstance(reference.get("target_support"), dict),
                f"Starlette operation alias reference is incomplete: {binding_id}",
            )


def _walk_source_references(
    value: Any,
    fastapi_root: Path,
    starlette_root: Path,
    label: str,
) -> None:
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and value.get("line") is not None:
            authority = value.get("source_authority")
            root = (
                starlette_root
                if isinstance(authority, str) and authority.startswith("Starlette")
                else fastapi_root
            )
            _verify_source_ref(root, value, label)
        for key, item in value.items():
            _walk_source_references(item, fastapi_root, starlette_root, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_source_references(item, fastapi_root, starlette_root, f"{label}[{index}]")


def _reject_output_values(value: Any, context: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _require(
                key not in OUTPUT_KEYS
                and not key.startswith("expected_")
                and key not in {"output", "outputs", "result", "results"},
                f"{context} contains forbidden output field {key!r}",
            )
            _reject_output_values(child, f"{context}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_output_values(child, f"{context}[{index}]")


def _inventory_symbol_rows(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    symbols: dict[str, dict[str, Any]] = {}
    for module in inventory.get("modules", []):
        for definition in module.get("definitions", []):
            for row in [definition, *definition.get("members", [])]:
                symbols[row["id"]] = {
                    "module": module["id"],
                    "kind": row.get("kind"),
                    "visibility": row.get("visibility"),
                }
    for binding in inventory.get("import_bindings", []):
        symbols[binding["id"]] = {
            "module": binding["module"],
            "kind": "import_binding",
            "visibility": "import_binding",
        }
    return symbols


def _reject_runtime_addresses(value: Any, context: str) -> None:
    if isinstance(value, str):
        _require(
            re.search(r"0x[0-9a-fA-F]{6,}", value) is None,
            f"{context} contains a process-specific memory address",
        )
    elif isinstance(value, dict):
        for key, child in value.items():
            _reject_runtime_addresses(child, f"{context}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_runtime_addresses(child, f"{context}[{index}]")


def validate_runtime_api_surfaces(
    api_inventory: dict[str, Any],
    core_surface: dict[str, Any],
    standard_surface: dict[str, Any],
) -> dict[str, Any]:
    """Verify that runtime reflection covers each statically inventoried symbol."""
    source_symbols = _inventory_symbol_rows(api_inventory)
    _require(
        len(source_symbols)
        == len(api_inventory.get("import_bindings", []))
        + sum(
            1 + len(row.get("members", []))
            for module in api_inventory.get("modules", [])
            for row in module.get("definitions", [])
        ),
        "source API inventory contains duplicate symbol IDs",
    )
    expected_modules = {row["id"] for row in api_inventory.get("modules", [])}
    expected_inventory_digest = hashlib.sha256(
        json.dumps(api_inventory, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    expected_authorities = {
        "fastapi": {"version": "0.141.1", "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"},
        "starlette": {"version": "1.6.0", "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"},
        "python": {"implementation": "CPython", "version": "3.12.13"},
        "pydantic": {"version": "2.13.4", "pydantic_core_version": "2.46.4"},
    }
    expected_standard_packages = {
        "email-validator": "2.3.0",
        "fastapi-cli": "0.0.32",
        "fastapi-cloud-cli": "0.11.0",
        "fastar": "0.11.0",
        "httpx": "0.28.1",
        "httpx2": "2.5.0",
        "jinja2": "3.1.6",
        "pydantic-extra-types": "2.11.0",
        "pydantic-settings": "2.14.2",
        "python-multipart": "0.0.32",
        "uvicorn": "0.40.0",
    }
    expected_profile_extras = {"core": [], "standard": ["docs-tests", "standard"]}
    surfaces = {"core": core_surface, "standard": standard_surface}
    stats = {}
    for profile_name, surface in surfaces.items():
        _reject_runtime_addresses(surface, f"{profile_name} runtime API surface")
        _require(
            surface.get("schema") == "fastapi-rs/runtime-api-surface@1",
            f"{profile_name} runtime API surface has an unsupported schema",
        )
        authority = surface.get("authority", {})
        for authority_name, expected in expected_authorities.items():
            _require(
                authority.get(authority_name) == expected,
                f"{profile_name} runtime API surface has the wrong {authority_name} identity",
            )
        _require(
            authority.get("optional_extras") == expected_profile_extras[profile_name],
            f"{profile_name} runtime profile has the wrong optional extras",
        )
        _require(
            authority.get("source_inventory_sha256") == expected_inventory_digest,
            f"{profile_name} runtime API surface refers to a different source inventory",
        )
        modules = surface.get("modules")
        _require(isinstance(modules, list), f"{profile_name} runtime module table is missing")
        module_ids = [row.get("id") for row in modules]
        _require(
            len(module_ids) == len(set(module_ids)) and set(module_ids) == expected_modules,
            f"{profile_name} runtime module table does not match FastAPI's source modules",
        )
        statuses = {row["id"]: row.get("status") for row in modules}
        _require(
            statuses.get("fastapi.__main__") == "entrypoint_import_skipped",
            f"{profile_name} profile must record the executable CLI entrypoint exclusion",
        )
        _require(
            all(
                status not in {"import_error", "optional_feature_unavailable"}
                for status in statuses.values()
            )
            if profile_name == "standard"
            else True,
            "standard runtime profile has an unaccounted import failure",
        )
        if profile_name == "core":
            unavailable = {
                module_id
                for module_id, status in statuses.items()
                if status == "optional_feature_unavailable"
            }
            _require(
                unavailable == {"fastapi.templating", "fastapi.testclient"},
                "core profile optional-feature import gaps changed",
            )
            _require(
                authority.get("optional_package_versions") == {},
                "core profile must not include optional FastAPI packages",
            )
        else:
            _require(
                authority.get("optional_package_versions") == expected_standard_packages,
                "standard profile optional package versions differ from the pinned lock",
            )

        reflected = surface.get("symbols")
        _require(isinstance(reflected, list), f"{profile_name} runtime symbol table is missing")
        reflected_by_id = {row.get("id"): row for row in reflected}
        _require(
            len(reflected_by_id) == len(reflected),
            f"{profile_name} runtime symbols contain duplicate IDs",
        )
        _require(
            all(identifier in source_symbols for identifier in reflected_by_id),
            f"{profile_name} runtime surface includes a non-source symbol as a source symbol",
        )
        for identifier, row in reflected_by_id.items():
            source = source_symbols[identifier]
            _require(
                (row.get("source_kind"), row.get("source_visibility"))
                == (source["kind"], source["visibility"]),
                f"{profile_name} runtime symbol {identifier} disagrees with source metadata",
            )
        unavailable_ids = {
            identifier
            for module in modules
            if module.get("status") in {"entrypoint_import_skipped", "optional_feature_unavailable"}
            for identifier in module.get("source_declared_symbol_ids", [])
        }
        unresolved_ids = {
            missing.get("id")
            for module in modules
            for missing in module.get("source_declared_names_missing_at_runtime", [])
        }
        _require(
            not unresolved_ids, f"{profile_name} has unresolved symbols: {sorted(unresolved_ids)}"
        )
        _require(
            set(reflected_by_id) | unavailable_ids == set(source_symbols),
            f"{profile_name} reflection does not account for every source API candidate",
        )
        _require(
            not (set(reflected_by_id) & unavailable_ids),
            f"{profile_name} marks a source symbol both reflected and unavailable",
        )
        model_count = sum("pydantic_model_fields" in row for row in reflected)
        _require(
            model_count == 49, f"{profile_name} profile has an unexpected Pydantic model count"
        )
        stats[profile_name] = {
            "imported_modules": sum(status == "imported" for status in statuses.values()),
            "optional_feature_unavailable_modules": sum(
                status == "optional_feature_unavailable" for status in statuses.values()
            ),
            "entrypoint_modules_skipped": sum(
                status == "entrypoint_import_skipped" for status in statuses.values()
            ),
            "source_symbols_reflected": len(reflected_by_id),
            "pydantic_model_classes": model_count,
        }

    _require(
        stats["standard"]["imported_modules"] > stats["core"]["imported_modules"],
        "standard optional profile did not expand the reflected FastAPI surface",
    )
    return stats


def validate_compatibility_artifacts(
    atlas: dict[str, Any],
    backlog: dict[str, Any],
    selector_catalog: dict[str, Any],
    *,
    materialized_input_index: dict[str, Any],
    fastapi_source: Path,
    starlette_source: Path,
) -> dict[str, Any]:
    """Check source evidence, complete module/page links, and input-only designs."""
    _require(atlas.get("schema") == "fastapi-rs/compatibility-atlas@11", "unsupported atlas schema")
    starlette_edges = atlas.get("starlette_integration_edges")
    _require(isinstance(starlette_edges, list), "Starlette integration edges are missing")
    edge_by_id = {
        edge.get("id"): edge
        for edge in starlette_edges
        if isinstance(edge, dict) and isinstance(edge.get("id"), str)
    }
    _require(
        len(edge_by_id) == len(starlette_edges),
        "Starlette integration edge identities must be unique",
    )

    canonical_kind_rank = {
        "surface-alias": 0,
        "operation-alias": 1,
        "subclass-base-contract": 2,
        "surface-gap": 3,
    }

    def canonical_kind(edge: dict[str, Any]) -> str | None:
        if edge.get("relation") == "direct_reexport":
            if edge.get("starlette_rs_surface_aliases"):
                return "surface-alias"
            if edge.get("starlette_rs_operation_aliases"):
                return "operation-alias"
            if edge.get("starlette_rs_surface_gap"):
                return "surface-gap"
        if edge.get("relation") == "subclass_edge" and edge.get(
            "starlette_rs_subclass_contract_refs"
        ):
            return "subclass-base-contract"
        return None

    canonical_by_symbol: dict[str, list[tuple[int, str, str]]] = {}
    for edge in starlette_edges:
        if not isinstance(edge, dict) or not isinstance(edge.get("starlette_symbol"), str):
            continue
        kind = canonical_kind(edge)
        if kind is not None:
            canonical_by_symbol.setdefault(edge["starlette_symbol"], []).append(
                (canonical_kind_rank[kind], edge["id"], kind)
            )

    canonical_link_count = 0
    specific_link_count = 0
    type_only_link_count = 0
    unresolved_link_count = 0
    for edge in starlette_edges:
        if not isinstance(edge, dict) or edge.get("relation") != "internal_dependency":
            _require(
                not isinstance(edge, dict) or "starlette_rs_canonical_edge_refs" not in edge,
                "canonical Starlette edge references are allowed only on internal dependencies",
            )
            _require(
                not isinstance(edge, dict) or "starlette_rs_type_only_ref" not in edge,
                "type-only Starlette references are allowed only on internal dependencies",
            )
            continue
        type_only = edge.get("starlette_rs_type_only_ref")
        if type_only is not None:
            _require(
                isinstance(type_only, dict)
                and set(type_only)
                == {"resolution", "starlette_symbol", "target_support", "scope_note"}
                and type_only.get("resolution") == "python-typing-only"
                and type_only.get("starlette_symbol") == edge.get("starlette_symbol")
                and isinstance(type_only.get("scope_note"), str)
                and bool(type_only["scope_note"].strip()),
                "type-only Starlette reference has invalid identity or scope",
            )
            target_support = type_only.get("target_support")
            _require(
                isinstance(target_support, dict)
                and set(target_support) == {"python-package", "rust-native"},
                "type-only Starlette reference must declare both target states",
            )
            python_support = target_support.get("python-package")
            rust_support = target_support.get("rust-native")
            _require(
                isinstance(python_support, dict)
                and set(python_support) == {"status", "reason"}
                and python_support.get("status") in {"supported", "private/internal", "uncertain"}
                and isinstance(python_support.get("reason"), str)
                and bool(python_support["reason"].strip()),
                "type-only Starlette Python state is invalid",
            )
            _require(
                isinstance(rust_support, dict)
                and set(rust_support) == {"status", "reason"}
                and rust_support.get("status") == "out_of_scope"
                and isinstance(rust_support.get("reason"), str)
                and bool(rust_support["reason"].strip()),
                "type-only Starlette Rust-native state is invalid",
            )
        candidates = canonical_by_symbol.get(edge.get("starlette_symbol"), [])
        supplied = edge.get("starlette_rs_canonical_edge_refs")
        if not candidates:
            _require(
                supplied is None,
                "internal dependency without a same-symbol contract edge has a canonical reference",
            )
        else:
            best_rank = min(rank for rank, _, _ in candidates)
            expected = sorted(
                (edge_id, kind) for rank, edge_id, kind in candidates if rank == best_rank
            )
            _require(
                isinstance(supplied, dict),
                "same-symbol internal dependency lacks canonical references",
            )
            _require(
                set(supplied)
                == {"resolution", "starlette_symbol", "canonical_edges", "scope_note"},
                "canonical Starlette edge reference has unsupported fields",
            )
            _require(
                supplied.get("resolution") == "same-starlette-symbol"
                and supplied.get("starlette_symbol") == edge.get("starlette_symbol")
                and isinstance(supplied.get("scope_note"), str)
                and bool(supplied["scope_note"].strip()),
                "canonical Starlette edge reference has invalid identity or scope",
            )
            refs = supplied.get("canonical_edges")
            _require(isinstance(refs, list), "canonical Starlette edge references must be a list")
            _require(
                refs == [{"edge_id": edge_id, "contract_kind": kind} for edge_id, kind in expected],
                "canonical Starlette edge references differ from exact same-symbol contracts",
            )
            for edge_id, kind in expected:
                canonical = edge_by_id.get(edge_id)
                _require(canonical is not None, "canonical Starlette edge reference points nowhere")
                _require(
                    canonical.get("starlette_symbol") == edge.get("starlette_symbol")
                    and canonical_kind(canonical) == kind,
                    "canonical Starlette edge reference target changed identity",
                )
        has_specific_links = isinstance(
            edge.get("starlette_rs_integration_operation_refs"), dict
        ) or isinstance(edge.get("starlette_rs_behavior_crosswalk"), dict)
        _require(
            not (type_only is not None and (supplied is not None or has_specific_links)),
            "type-only Starlette reference overlaps a behavior or canonical resolution",
        )
        if supplied is not None:
            canonical_link_count += 1
        elif has_specific_links:
            specific_link_count += 1
        elif type_only is not None:
            type_only_link_count += 1
        else:
            unresolved_link_count += 1

    internal_edge_count = sum(
        isinstance(edge, dict) and edge.get("relation") == "internal_dependency"
        for edge in starlette_edges
    )
    atlas_counts = atlas.get("counts", {})
    _require(
        atlas_counts.get("starlette_internal_edges_with_canonical_refs") == canonical_link_count,
        "canonical Starlette internal-edge count differs from the edge map",
    )
    _require(
        atlas_counts.get("starlette_internal_edges_with_specific_refs_without_canonical")
        == specific_link_count,
        "specific Starlette internal-edge count differs from the edge map",
    )
    _require(
        atlas_counts.get("starlette_internal_edges_with_type_only_refs") == type_only_link_count,
        "type-only Starlette internal-edge count differs from the edge map",
    )
    _require(
        atlas_counts.get("starlette_internal_edges_unresolved") == unresolved_link_count,
        "unresolved Starlette internal-edge count differs from the edge map",
    )
    _require(
        canonical_link_count + specific_link_count + type_only_link_count + unresolved_link_count
        == internal_edge_count,
        "Starlette internal-edge resolutions do not partition the inventory",
    )
    _require(unresolved_link_count == 0, "Starlette internal edges remain unresolved")
    _require(
        backlog.get("schema") == FIXTURE_BACKLOG_SCHEMA_ID,
        "unsupported fixture backlog schema",
    )
    fastapi_authority = atlas.get("authorities", {}).get("fastapi", {})
    _require(
        (fastapi_authority.get("version"), fastapi_authority.get("commit"))
        == ("0.141.1", "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"),
        "FastAPI 0.141.1 must remain the pinned source authority",
    )
    starlette_authority = atlas.get("authorities", {}).get("starlette", {})
    _require(
        starlette_authority.get("version") == "1.6.0",
        "Starlette 1.6.0 must be the sole selected Starlette contract",
    )
    _require(
        starlette_authority.get("commit") == "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "Starlette authority commit does not match the pinned 1.6.0 source",
    )
    review_ref = atlas.get("api_classification_review")
    _require(isinstance(review_ref, dict), "callable classification review reference is missing")
    review_path = (ROOT / review_ref.get("path", "")).resolve()
    try:
        review_path.relative_to(ROOT)
    except ValueError as exc:
        raise ContractError("compatibility atlas: callable review escapes the repository") from exc
    _require(review_path.is_file(), "callable classification review file is missing")
    review_digest = review_ref.get("sha256")
    _require(
        isinstance(review_digest, str) and sha256_file(review_path) == review_digest,
        "callable classification review digest is stale",
    )
    review = read_json(review_path)
    _require(
        review.get("schema")
        == review_ref.get("schema")
        == "fastapi-callable-classification-review/v1",
        "callable classification review schema is unsupported",
    )
    review_identity = review.get("source_identity", {})
    _require(
        isinstance(review_identity, dict)
        and review_identity.get("source_commit") == fastapi_authority.get("commit")
        and review_identity.get("selected_starlette_profile") == "1.6.0",
        "callable classification review has a different source authority",
    )
    review_rows = review.get("rows", [])
    review_by_id = {row.get("id"): row for row in review_rows if isinstance(row, dict)}
    reviewed_candidates = {
        row["id"]: row
        for row in atlas.get("api_candidates", [])
        if isinstance(row.get("classification_review"), dict)
        and row.get("visibility") in {"public", "public_protocol"}
        and row.get("kind") in REVIEWED_CALLABLE_KINDS
    }
    _require(
        len(review_by_id) == len(review_rows) and set(review_by_id) == set(reviewed_candidates),
        "callable classification review rows do not match reviewed atlas candidates",
    )
    review_counts = Counter(row.get("recommendation") for row in review_rows)
    _require(
        review.get("scope", {}).get("candidate_count") == len(review_rows)
        and review.get("scope", {}).get("recommendation_counts") == dict(review_counts),
        "callable classification review summary differs from its rows",
    )
    for identifier, row in review_by_id.items():
        candidate = reviewed_candidates[identifier]
        candidate_review = candidate["classification_review"]
        _require(
            row.get("recommendation") == candidate.get("classification")
            and row.get("source") == candidate_review.get("source")
            and row.get("evidence_basis") == candidate_review.get("evidence_basis")
            and row.get("evidence") == candidate_review.get("evidence")
            and row.get("reason") == candidate_review.get("reason"),
            f"reviewed API classification differs from its source review: {identifier}",
        )
        source_path = _source_path(fastapi_source, row.get("source", {}).get("path"), identifier)
        source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        line = row.get("source", {}).get("line")
        _require(
            isinstance(line, int) and 1 <= line <= len(source_lines),
            f"reviewed API source line is stale: {identifier}",
        )
        for reference in row.get("evidence", []):
            match = re.fullmatch(r"(.+):(\d+)(?:-(\d+))?", reference)
            evidence_path = match.group(1) if match else reference
            evidence_line = int(match.group(2)) if match else None
            evidence_end = int(match.group(3) or match.group(2)) if match else None
            evidence_file = _source_path(fastapi_source, evidence_path, identifier)
            if evidence_line is not None:
                evidence_lines = evidence_file.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines()
                _require(
                    1 <= evidence_line <= evidence_end <= len(evidence_lines),
                    f"reviewed API evidence line is stale: {identifier}",
                )
    python_authority = atlas.get("authorities", {}).get("python", {})
    _require(
        python_authority.get("requires_python") == ">=3.10"
        and {"3.10", "3.11", "3.12", "3.13", "3.14"}.issubset(
            python_authority.get("project_classifiers", [])
        ),
        "FastAPI Python version requirements or classifiers are incomplete",
    )
    pydantic_authority = atlas.get("authorities", {}).get("pydantic", {})
    _require(
        pydantic_authority.get("selected_version") == "2.13.4",
        "Pydantic 2.13.4 must remain the selected source-lock baseline",
    )
    _require(
        selector_catalog.get("schema") == "fastapi-rs/observation-selector-catalog@1",
        "unsupported observation selector catalog schema",
    )
    _require(
        selector_catalog.get("authority") == {"fastapi": "0.141.1", "starlette": "1.6.0"},
        "observation selector catalog does not match the pinned source contracts",
    )
    _require(
        isinstance(selector_catalog.get("comparison_policy"), str)
        and bool(selector_catalog["comparison_policy"].strip()),
        "selector comparison policy is missing",
    )
    selector_specs = selector_catalog.get("selectors")
    _require(
        isinstance(selector_specs, list) and bool(selector_specs),
        "selector definitions are missing",
    )
    selector_ids: set[str] = set()
    selector_patterns: list[re.Pattern[str]] = []
    for selector in selector_specs:
        _require(
            isinstance(selector.get("projection"), str) and bool(selector["projection"].strip()),
            "selector projection is missing",
        )
        _require(
            selector.get("comparison")
            in {
                "exact",
                "exact-bytes",
                "exact-json-value",
                "exact-identity-relation",
                "ordered-exact",
            },
            f"selector {selector.get('id', selector.get('id_pattern'))} has an unknown comparison",
        )
        _require(
            selector.get("workflow_support") in {"supported", "partial", "planned"},
            f"selector {selector.get('id', selector.get('id_pattern'))} has no workflow "
            "support state",
        )
        if "id" in selector:
            identifier = selector["id"]
            _require(
                isinstance(identifier, str) and identifier not in selector_ids,
                "selector IDs must be unique",
            )
            selector_ids.add(identifier)
        else:
            _require(
                isinstance(selector.get("id_pattern"), str)
                and isinstance(selector.get("pattern"), str),
                "parameterized selector requires an ID template and pattern",
            )
            try:
                selector_patterns.append(re.compile(selector["pattern"]))
            except re.error as exc:
                raise ContractError("compatibility atlas: invalid selector pattern") from exc

    def selector_is_defined(identifier: str) -> bool:
        return identifier in selector_ids or any(
            pattern.fullmatch(identifier) for pattern in selector_patterns
        )

    used_selectors: set[str] = set()

    def register_selectors(values: Any, context: str) -> None:
        _require(isinstance(values, list), f"{context} selectors must be a list")
        for identifier in values:
            _require(
                isinstance(identifier, str) and selector_is_defined(identifier),
                f"{context} uses undefined observation selector {identifier!r}",
            )
            used_selectors.add(identifier)
        if "http.body.json" in values:
            _require(
                "http.body.bytes" in values,
                f"{context} selects JSON without the exact HTTP body bytes",
            )

    for family in atlas.get("feature_families", []):
        register_selectors(family.get("observations", []), f"feature {family.get('id')}")

    api_rows = atlas.get("api_candidates")
    _require(isinstance(api_rows, list) and bool(api_rows), "API candidate inventory is missing")
    api_ids: set[str] = set()
    classifications: Counter[str] = Counter()
    for row in api_rows:
        identifier = row.get("id")
        _require(
            isinstance(identifier, str) and identifier not in api_ids,
            "API candidate IDs must be unique",
        )
        api_ids.add(identifier)
        classification = row.get("classification")
        _require(classification in API_CLASSIFICATIONS, f"{identifier} has no valid classification")
        classifications[classification] += 1
        _require(
            isinstance(row.get("classification_evidence_rule"), str)
            and bool(row["classification_evidence_rule"].strip()),
            f"{identifier} has no classification rationale",
        )
        source_evidence = row.get("source_evidence")
        _require(
            isinstance(source_evidence, list) and bool(source_evidence),
            f"{identifier} has no source evidence",
        )
        for evidence in source_evidence:
            _verify_source_ref(
                fastapi_source,
                evidence,
                f"{identifier} source evidence",
                digest_key="module_sha256",
            )
        if classification == "supported":
            _require(
                bool(row.get("public_evidence")),
                f"{identifier} is supported without public API evidence",
            )
        _walk_source_references(
            row.get("public_evidence", []), fastapi_source, starlette_source, identifier
        )

    inherited_rows = atlas.get("reviewed_inherited_api_candidates")
    _require(
        isinstance(inherited_rows, list), "reviewed inherited API candidate inventory is missing"
    )
    inherited_ids: set[str] = set()
    inherited_classifications: Counter[str] = Counter()
    api_indexes = {row["id"]: index for index, row in enumerate(api_rows)}
    for row in inherited_rows:
        identifier = row.get("id")
        _require(
            isinstance(identifier, str)
            and identifier not in inherited_ids
            and identifier not in api_ids,
            "inherited API candidate IDs must be unique and separate from source candidates",
        )
        inherited_ids.add(identifier)
        classification = row.get("classification")
        inherited_classifications[classification] += 1
        _require(
            row.get("kind") in {"inherited_method", "inherited_property"}
            and classification in {"supported", "private/internal", "uncertain"}
            and isinstance(row.get("classification_evidence_rule"), str)
            and bool(row["classification_evidence_rule"].strip()),
            f"{identifier} must have an inherited kind, reviewed classification, and rationale",
        )
        exposure_candidate_id = row.get("exposure_candidate_id")
        _require(
            exposure_candidate_id in api_indexes
            and api_rows[api_indexes[exposure_candidate_id]].get("kind") == "class"
            and api_rows[api_indexes[exposure_candidate_id]].get("classification") == "supported"
            and row.get("exposure_candidate_ref")
            == f"/api_candidates/{api_indexes[exposure_candidate_id]}",
            f"{identifier} does not point to its supported FastAPI class candidate",
        )
        evidence = row.get("source_evidence")
        _require(
            isinstance(evidence, list) and bool(evidence), f"{identifier} has no exposure evidence"
        )
        _walk_source_references(evidence, fastapi_source, starlette_source, identifier)
        inheritance_refs = [
            item
            for item in evidence
            if isinstance(item, dict) and item.get("kind") == "class-inheritance"
        ]
        class_source_refs = api_rows[api_indexes[exposure_candidate_id]].get("source_evidence", [])
        class_name = exposure_candidate_id.rsplit(".", 1)[-1]
        _require(
            len(inheritance_refs) == 1
            and isinstance(class_source_refs, list)
            and inheritance_refs[0].get("symbol") == class_name
            and any(
                isinstance(source_ref, dict)
                and source_ref.get("path") == inheritance_refs[0].get("path")
                and source_ref.get("line") == inheritance_refs[0].get("line")
                for source_ref in class_source_refs
            ),
            f"{identifier} class evidence does not match its exposure candidate",
        )
        for inheritance_ref in (
            item
            for item in evidence
            if isinstance(item, dict)
            and item.get("kind") == "class-inheritance"
            and item.get("symbol") == "APIRouter"
        ):
            _require(
                inheritance_ref.get("base_class") == "Router"
                and inheritance_ref.get("base_expression") == "routing.Router"
                and inheritance_ref.get("base_import_module") == "starlette"
                and inheritance_ref.get("base_import_name") == "routing"
                and inheritance_ref.get("base_import_alias") == "routing"
                and inheritance_ref.get("base_import_line") == 91,
                f"{identifier} does not bind APIRouter's Router base through Starlette",
            )
        if classification != "supported":
            _require(
                not any(
                    field in row
                    for field in (
                        "canonical_operation_id",
                        "sibling_contract_gap",
                        "signature_source",
                        "attribute_source",
                        "target_binding",
                        "documentation_contract_refs",
                        "fixture_refs",
                        "feature_ids",
                        "observation_selectors",
                    )
                ),
                f"{identifier} classification-only candidate must not imply an operation contract",
            )
            _require(
                {item.get("kind") for item in evidence if isinstance(item, dict)}
                >= {"class-inheritance", "source-definition"},
                f"{identifier} lacks FastAPI inheritance or Starlette method source evidence",
            )
            inheritance_refs = [
                item
                for item in evidence
                if isinstance(item, dict) and item.get("kind") == "class-inheritance"
            ]
            starlette_refs = [
                item
                for item in evidence
                if isinstance(item, dict) and item.get("kind") == "source-definition"
            ]
            _require(
                len(inheritance_refs) == 1 and len(starlette_refs) == 1,
                f"{identifier} must have one FastAPI inheritance and one Starlette method ref",
            )
            inheritance_ref = inheritance_refs[0]
            starlette_ref = starlette_refs[0]
            fastapi_module = (
                Path(str(inheritance_ref.get("path", "")))
                .with_suffix("")
                .as_posix()
                .replace("/", ".")
            )
            starlette_module = (
                Path(str(starlette_ref.get("path", "")))
                .with_suffix("")
                .as_posix()
                .replace("/", ".")
            )
            _require(
                exposure_candidate_id == f"{fastapi_module}.{inheritance_ref.get('symbol')}"
                and identifier == f"{exposure_candidate_id}.{starlette_ref.get('symbol')}"
                and inheritance_ref.get("base_class") == starlette_ref.get("owner"),
                f"{identifier} candidate ID does not match its FastAPI and Starlette source refs",
            )
            sibling_review = row.get("starlette_rs_review_ref")
            _require(
                isinstance(sibling_review, dict)
                and isinstance(sibling_review.get("qualified_name"), str)
                and sibling_review.get("qualified_name")
                == (
                    f"{starlette_module}.{starlette_ref.get('owner')}.{starlette_ref.get('symbol')}"
                )
                and sibling_review.get("api_disposition") == classification
                and sibling_review.get("path")
                == atlas.get("authorities", {}).get("starlette_rs", {}).get("api_review_path"),
                f"{identifier} lacks matching pinned Starlette-RS classification evidence",
            )
            continue
        sibling_gap = row.get("sibling_contract_gap")
        if sibling_gap is None:
            _require(
                isinstance(row.get("canonical_operation_id"), str)
                and bool(row["canonical_operation_id"]),
                f"{identifier} has no canonical delegated operation",
            )
            _require(
                all(field not in row for field in ("signature", "parameters", "requirements")),
                f"{identifier} must leave its canonical signature and requirements to its owner",
            )
            if row.get("target_binding") is not None:
                target_binding = row.get("target_binding")
                known_gaps = (
                    target_binding.get("known_gaps") if isinstance(target_binding, dict) else None
                )
                _require(
                    isinstance(target_binding, dict)
                    and target_binding.get("implementation_owner") in {"fastapi-rs", "starlette-rs"}
                    and target_binding.get("status")
                    in {"partial-contract", "unimplemented", "unresolved"}
                    and isinstance(known_gaps, list)
                    and bool(known_gaps)
                    and all(isinstance(gap, str) and gap.strip() for gap in known_gaps),
                    f"{identifier} canonical target binding must state FastAPI-RS ownership "
                    "and known gaps",
                )
        else:
            _require(
                "canonical_operation_id" not in row,
                f"{identifier} sibling-gap candidate must not claim a canonical operation",
            )
            _require(
                isinstance(sibling_gap, dict)
                and isinstance(sibling_gap.get("expected_operation_id"), str)
                and bool(sibling_gap.get("expected_operation_id"))
                and isinstance(sibling_gap.get("reason"), str)
                and bool(sibling_gap["reason"].strip()),
                f"{identifier} has an incomplete sibling contract gap",
            )
            signature_source = row.get("signature_source")
            attribute_source = row.get("attribute_source")
            has_signature_source = isinstance(signature_source, dict)
            has_attribute_source = isinstance(attribute_source, dict)
            _require(
                has_signature_source != has_attribute_source
                and ("signature_source" not in row or has_signature_source)
                and ("attribute_source" not in row or has_attribute_source),
                f"{identifier} must identify exactly one sibling method or instance attribute",
            )
            if has_signature_source:
                _require(
                    signature_source.get("repository") == "starlette"
                    and isinstance(signature_source.get("path"), str)
                    and signature_source.get("owner")
                    and signature_source.get("symbol")
                    and isinstance(signature_source.get("start_line"), int)
                    and isinstance(signature_source.get("end_line"), int),
                    f"{identifier} has no pinned Starlette source signature reference",
                )
                source_path = signature_source["path"]
                start_line = signature_source["start_line"]
                end_line = signature_source["end_line"]
                _verify_source_ref(
                    starlette_source,
                    {"path": source_path, "line": start_line, "end_line": end_line},
                    f"{identifier} Starlette signature source",
                )
                try:
                    source_tree = ast.parse(
                        _source_path(
                            starlette_source, source_path, f"{identifier} signature source"
                        ).read_text(encoding="utf-8"),
                        filename=source_path,
                    )
                except SyntaxError as exc:
                    raise ContractError(
                        f"compatibility atlas: {identifier} Starlette signature source is invalid"
                    ) from exc
                owners = [
                    node
                    for node in source_tree.body
                    if isinstance(node, ast.ClassDef) and node.name == signature_source["owner"]
                ]
                methods = [
                    node
                    for owner in owners
                    for node in owner.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == signature_source["symbol"]
                    and node.lineno == start_line
                    and getattr(node, "end_lineno", None) == end_line
                ]
                module_id = Path(source_path).with_suffix("").as_posix().replace("/", ".")
                expected_operation_id = (
                    f"{module_id}.{signature_source['owner']}.{signature_source['symbol']}"
                )
                _require(
                    len(owners) == 1
                    and len(methods) == 1
                    and sibling_gap["expected_operation_id"] == expected_operation_id,
                    f"{identifier} signature source does not resolve to the "
                    "reviewed sibling method",
                )
            else:
                _require(
                    set(attribute_source)
                    == {
                        "repository",
                        "path",
                        "owner",
                        "initializer",
                        "attribute",
                        "start_line",
                        "end_line",
                    }
                    and attribute_source.get("repository") == "starlette"
                    and isinstance(attribute_source.get("path"), str)
                    and isinstance(attribute_source.get("owner"), str)
                    and isinstance(attribute_source.get("initializer"), str)
                    and isinstance(attribute_source.get("attribute"), str)
                    and isinstance(attribute_source.get("start_line"), int)
                    and not isinstance(attribute_source.get("start_line"), bool)
                    and isinstance(attribute_source.get("end_line"), int)
                    and not isinstance(attribute_source.get("end_line"), bool)
                    and sibling_gap.get("candidate_state") == "no_exact_row",
                    f"{identifier} has an incomplete instance-attribute source reference",
                )
                source_path = attribute_source["path"]
                start_line = attribute_source["start_line"]
                end_line = attribute_source["end_line"]
                _verify_source_ref(
                    starlette_source,
                    {"path": source_path, "line": start_line, "end_line": end_line},
                    f"{identifier} Starlette attribute source",
                )
                try:
                    source_tree = ast.parse(
                        _source_path(
                            starlette_source, source_path, f"{identifier} attribute source"
                        ).read_text(encoding="utf-8"),
                        filename=source_path,
                    )
                except SyntaxError as exc:
                    raise ContractError(
                        f"compatibility atlas: {identifier} Starlette attribute source is invalid"
                    ) from exc
                owners = [
                    node
                    for node in source_tree.body
                    if isinstance(node, ast.ClassDef) and node.name == attribute_source["owner"]
                ]
                matching_assignments = [
                    node
                    for owner in owners
                    for method in owner.body
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and method.name == attribute_source["initializer"]
                    for node in ast.walk(method)
                    if isinstance(node, ast.Assign)
                    and node.lineno == start_line
                    and getattr(node, "end_lineno", None) == end_line
                    and any(
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                        and target.attr == attribute_source["attribute"]
                        for target in node.targets
                    )
                ]
                module_id = Path(source_path).with_suffix("").as_posix().replace("/", ".")
                expected_operation_id = (
                    f"{module_id}.{attribute_source['owner']}.{attribute_source['attribute']}"
                )
                _require(
                    len(owners) == 1
                    and len(matching_assignments) == 1
                    and sibling_gap.get("expected_operation_id") == expected_operation_id,
                    f"{identifier} attribute source does not resolve to the pinned assignment",
                )
            target_binding = row.get("target_binding")
            _require(
                isinstance(target_binding, dict)
                and target_binding.get("implementation_owner") == "fastapi-rs"
                and target_binding.get("status") == "partial-contract"
                and isinstance(target_binding.get("known_gaps"), list)
                and bool(target_binding["known_gaps"])
                and all(
                    isinstance(gap, str) and gap.strip() for gap in target_binding["known_gaps"]
                ),
                f"{identifier} sibling-gap candidate has no explicit partial target binding",
            )
            _require(
                all(field not in row for field in ("signature", "parameters", "requirements")),
                f"{identifier} must link its source signature without copying an operation "
                "contract",
            )
        _require(
            {item.get("kind") for item in evidence if isinstance(item, dict)}
            >= {"class-inheritance", "documentation-text"},
            f"{identifier} lacks class-inheritance or documentation exposure evidence",
        )
        _require(
            isinstance(row.get("documentation_contract_refs"), list)
            and bool(row["documentation_contract_refs"])
            and isinstance(row.get("fixture_refs"), list)
            and bool(row["fixture_refs"]),
            f"{identifier} has no reviewed docs or input-fixture mapping",
        )
    _require(
        atlas.get("counts", {}).get("reviewed_inherited_api_candidates") == len(inherited_rows),
        "reviewed inherited API candidate count differs from its rows",
    )
    _require(
        atlas.get("counts", {}).get("inherited_api_classifications")
        == {
            classification: inherited_classifications.get(classification, 0)
            for classification in ("supported", "private/internal", "uncertain")
        },
        "reviewed inherited API classification counts differ from their rows",
    )

    for group, rows in (
        ("aliases", atlas.get("aliases")),
        ("deprecations", atlas.get("deprecations")),
        ("errors", atlas.get("errors")),
    ):
        _require(isinstance(rows, list), f"{group} evidence is missing")
        for row in rows:
            _walk_source_references(
                row,
                fastapi_source,
                starlette_source,
                f"{group}:{row.get('id', row.get('symbol_id', 'unknown'))}",
            )
            if group == "errors":
                _require(
                    bool(row.get("source_evidence")),
                    f"error {row.get('id')} has no source evidence",
                )
                _require(
                    bool(row.get("observation_selectors")),
                    f"error {row.get('id')} has no observation selectors",
                )
                register_selectors(row["observation_selectors"], f"error {row.get('id')}")
    for feature in atlas.get("optional_features", []):
        _require(
            bool(feature.get("extra"))
            and bool(feature.get("requirements"))
            and bool(feature.get("source")),
            "optional feature lacks requirement evidence",
        )

    coverage_rows = atlas.get("coverage_matrix")
    _require(isinstance(coverage_rows, list) and bool(coverage_rows), "coverage matrix is missing")
    coverage_by_id: dict[str, dict[str, Any]] = {}
    for row in coverage_rows:
        identifier = row.get("id")
        _require(
            isinstance(identifier, str) and identifier not in coverage_by_id,
            "coverage matrix IDs must be unique",
        )
        coverage_by_id[identifier] = row
        _verify_source_ref(
            fastapi_source,
            {
                "path": row.get("source_path"),
                "source_sha256": row.get("source_sha256"),
            },
            f"coverage source {identifier}",
            digest_key="source_sha256",
        )
        register_selectors(row.get("observation_selectors", []), identifier)
        if row.get("kind") == "upstream_test_module" and row.get("mapping_status") == "excluded":
            mapping = row.get("mapping_evidence", {})
            function_count = mapping.get("test_function_count")
            explicit_exclusions = mapping.get("excluded_test_functions")
            inherited_exclusions = mapping.get("module_excluded_test_functions")
            _require(
                isinstance(function_count, int)
                and not isinstance(function_count, bool)
                and function_count >= 0,
                f"excluded test module {identifier} has no valid function count",
            )
            _require(
                isinstance(explicit_exclusions, list) and isinstance(inherited_exclusions, list),
                f"excluded test module {identifier} has no per-function dispositions",
            )
            _require(
                all(isinstance(item, dict) for item in explicit_exclusions)
                and all(isinstance(item, dict) for item in inherited_exclusions),
                f"excluded test module {identifier} has malformed per-function dispositions",
            )
            explicit_names = [item.get("name") for item in explicit_exclusions]
            inherited_names = [item.get("name") for item in inherited_exclusions]
            all_disposition_names = explicit_names + inherited_names
            _require(
                all(isinstance(name, str) and bool(name) for name in all_disposition_names)
                and len(all_disposition_names) == len(set(all_disposition_names))
                and len(all_disposition_names) == function_count,
                f"excluded test module {identifier} does not disposition every function "
                "exactly once",
            )
            for disposition in explicit_exclusions:
                function_name = disposition["name"]
                _require(
                    isinstance(disposition.get("line"), int)
                    and not isinstance(disposition.get("line"), bool)
                    and isinstance(disposition.get("end_line"), int)
                    and not isinstance(disposition.get("end_line"), bool),
                    f"excluded test function {identifier}::{function_name} has an invalid "
                    "source span",
                )
                evidence = disposition.get("source_evidence")
                _require(
                    bool(disposition.get("reason"))
                    and isinstance(evidence, list)
                    and bool(evidence)
                    and all(isinstance(source, dict) for source in evidence),
                    f"excluded test function {identifier}::{function_name} "
                    "has no individual evidence",
                )
                exact_function_source = False
                for source in evidence:
                    source_root = (
                        starlette_source
                        if str(source.get("source_authority", "")).startswith("Starlette")
                        else fastapi_source
                    )
                    _verify_source_ref(
                        source_root,
                        {
                            "path": source.get("path"),
                            "line": source.get("start_line"),
                            "end_line": source.get("end_line"),
                            "sha256": source.get("sha256"),
                        },
                        f"excluded test function {identifier}::{function_name} source",
                        digest_key="sha256",
                    )
                    exact_function_source = exact_function_source or (
                        source.get("path") == row.get("source_path")
                        and source.get("start_line") == disposition.get("line")
                        and source.get("end_line") == disposition.get("end_line")
                        and source.get("sha256") == row.get("source_sha256")
                    )
                _require(
                    exact_function_source,
                    f"excluded test function {identifier}::{function_name} does not link its "
                    "exact source span",
                )
            for disposition in inherited_exclusions:
                function_name = disposition["name"]
                _require(
                    disposition.get("disposition") == "inherited_module_exclusion"
                    and disposition.get("reason") == row.get("exclusion_reason")
                    and isinstance(disposition.get("line"), int)
                    and not isinstance(disposition.get("line"), bool)
                    and isinstance(disposition.get("end_line"), int)
                    and not isinstance(disposition.get("end_line"), bool),
                    f"excluded test function {identifier}::{function_name} has an invalid "
                    "inherited disposition",
                )
                evidence = disposition.get("source_evidence")
                _require(
                    isinstance(evidence, list)
                    and bool(evidence)
                    and all(isinstance(source, dict) for source in evidence),
                    f"excluded test function {identifier}::{function_name} has no source evidence",
                )
                exact_function_source = False
                for source in evidence:
                    source_root = (
                        starlette_source
                        if str(source.get("source_authority", "")).startswith("Starlette")
                        else fastapi_source
                    )
                    _verify_source_ref(
                        source_root,
                        {
                            "path": source.get("path"),
                            "line": source.get("start_line"),
                            "end_line": source.get("end_line"),
                            "sha256": source.get("sha256"),
                        },
                        f"excluded test function {identifier}::{function_name} source",
                        digest_key="sha256",
                    )
                    exact_function_source = exact_function_source or (
                        source.get("path") == row.get("source_path")
                        and source.get("start_line") == disposition.get("line")
                        and source.get("end_line") == disposition.get("end_line")
                        and source.get("sha256") == row.get("source_sha256")
                    )
                _require(
                    exact_function_source,
                    f"excluded test function {identifier}::{function_name} does not link its "
                    "exact source span",
                )
        if row.get("kind") in FIXTURE_KINDS:
            if row.get("mapping_status") == "excluded":
                _require(
                    row.get("review_status") == "excluded",
                    f"excluded source {identifier} has an inconsistent review status",
                )
                _require(
                    bool(row.get("exclusion_reason")), f"excluded source {identifier} has no reason"
                )
                _require(
                    row.get("fixture_id") is None,
                    f"excluded source {identifier} unexpectedly has a fixture",
                )
            else:
                review_status = row.get("review_status")
                _require(
                    review_status in {"pending", "reviewed_partial"},
                    f"source {identifier} has no valid review status",
                )
                _require(bool(row.get("fixture_id")), f"source {identifier} has no fixture mapping")
                _require(
                    bool(row.get("observation_selectors")),
                    f"source {identifier} has no observation selectors",
                )
                mapping = row.get("mapping_evidence", {})
                workflow_mappings = mapping.get("independent_workflow_mappings", [])
                _require(
                    isinstance(workflow_mappings, list),
                    f"source {identifier} workflow mappings are malformed",
                )
                for workflow_mapping in workflow_mappings:
                    _require(
                        isinstance(workflow_mapping, dict)
                        and bool(workflow_mapping.get("recipe_path"))
                        and bool(workflow_mapping.get("case_ids"))
                        and bool(workflow_mapping.get("observation_selectors")),
                        f"source {identifier} has an incomplete workflow mapping",
                    )
                    register_selectors(
                        workflow_mapping["observation_selectors"],
                        f"source {identifier} workflow mapping",
                    )
                if review_status == "reviewed_partial":
                    _require(
                        bool(workflow_mappings),
                        f"source {identifier} marks review complete without an indexed workflow",
                    )
                if row["kind"] == "upstream_test_module":
                    _require(
                        not mapping.get("unmatched_test_functions"),
                        f"source {identifier} has unmapped test functions",
                    )
                    if review_status == "reviewed_partial":
                        module_review = mapping.get("reviewed_module_mapping") or {}
                        module_sources = module_review.get("supporting_sources", [])
                        module_notes = module_review.get("stimulus_notes", "")
                        explicit_module_review = bool(
                            module_review.get("rationale")
                            and module_sources
                            and (
                                module_review.get("workflow_cases")
                                or (
                                    "tests/fixtures/input-recipes/" in module_notes
                                    and "::" in module_notes
                                )
                            )
                        )
                        functions = mapping.get("matched_test_functions", [])
                        all_functions_reviewed = bool(functions) and all(
                            function.get("mapping_status")
                            in {
                                "reviewed_source_candidate",
                                "contract_gated_source_candidate",
                                "excluded",
                            }
                            for function in functions
                        )
                        _require(
                            explicit_module_review or all_functions_reviewed,
                            f"source {identifier} has no source-backed function or module review",
                        )
                elif review_status == "reviewed_partial":
                    page_review = mapping.get("reviewed_source_mapping") or {}
                    _require(
                        bool(page_review.get("rationale"))
                        and bool(page_review.get("source_evidence")),
                        f"documented source {identifier} has no reviewed source evidence",
                    )

    excluded_test_modules = [
        row
        for row in coverage_rows
        if row.get("kind") == "upstream_test_module" and row.get("mapping_status") == "excluded"
    ]
    inherited_module_exclusion_count = sum(
        len(row.get("mapping_evidence", {}).get("module_excluded_test_functions", []))
        for row in excluded_test_modules
    )
    _require(
        atlas.get("counts", {}).get("test_functions_in_excluded_modules")
        == sum(
            row.get("mapping_evidence", {}).get("test_function_count", 0)
            for row in excluded_test_modules
        )
        and atlas.get("counts", {}).get("test_functions_with_individual_exclusion")
        == sum(
            len(row.get("mapping_evidence", {}).get("excluded_test_functions", []))
            for row in excluded_test_modules
        )
        and atlas.get("counts", {}).get("test_functions_with_inherited_module_exclusion")
        == inherited_module_exclusion_count,
        "excluded test-function disposition counts differ from the coverage matrix",
    )

    fixture_rows = backlog.get("fixture_designs")
    _require(isinstance(fixture_rows, list) and bool(fixture_rows), "fixture designs are missing")
    indexed_workflows = {
        row.get("id"): row for row in materialized_input_index.get("workflows", [])
    }
    indexed_mappings = {
        (row.get("source_item_id"), row.get("workflow_id")): row
        for row in materialized_input_index.get("mappings", [])
    }
    fixture_by_source: dict[str, dict[str, Any]] = {}
    fixture_ids: set[str] = set()
    case_ids: set[str] = set()
    for fixture in fixture_rows:
        fixture_id = fixture.get("id")
        source_id = fixture.get("source_item_id")
        _require(
            isinstance(fixture_id, str) and fixture_id not in fixture_ids,
            "fixture IDs must be unique",
        )
        _require(
            isinstance(source_id, str) and source_id not in fixture_by_source,
            "fixture source IDs must be unique",
        )
        fixture_ids.add(fixture_id)
        fixture_by_source[source_id] = fixture
        _require(
            fixture.get("input_only") is True, f"fixture {fixture_id} is not marked input-only"
        )
        _require(
            bool(fixture.get("stimulus_design")), f"fixture {fixture_id} has no stimulus design"
        )
        _require(
            bool(fixture.get("observation_selectors")),
            f"fixture {fixture_id} has no observation selectors",
        )
        _require(
            bool(fixture.get("selector_evidence")), f"fixture {fixture_id} has no selector evidence"
        )
        register_selectors(fixture["observation_selectors"], f"fixture {fixture_id}")
        _reject_output_values(fixture, f"fixture {fixture_id}")

        source_row = coverage_by_id.get(source_id)
        _require(
            source_row is not None, f"fixture {fixture_id} references unknown source {source_id}"
        )
        _require(
            source_row.get("fixture_id") == fixture_id,
            f"fixture {fixture_id} does not match its coverage row",
        )
        _require(
            source_row.get("mapping_status") != "excluded",
            f"fixture {fixture_id} belongs to an excluded source",
        )
        evidence = fixture.get("source_evidence")
        evidence_rows = [evidence] if isinstance(evidence, dict) else evidence
        _require(
            isinstance(evidence_rows, list) and bool(evidence_rows),
            f"fixture {fixture_id} has no source evidence",
        )
        _require(
            any(
                row.get("path") == source_row.get("source_path")
                and row.get("sha256") == source_row.get("source_sha256")
                for row in evidence_rows
                if isinstance(row, dict)
            ),
            f"fixture {fixture_id} does not carry its primary source digest",
        )
        for evidence_row in evidence_rows:
            _require(
                isinstance(evidence_row, dict),
                f"fixture {fixture_id} has malformed source evidence",
            )
            evidence_root = (
                starlette_source
                if str(evidence_row.get("source_authority", "")).startswith("Starlette")
                else fastapi_source
            )
            _verify_source_ref(
                evidence_root,
                evidence_row,
                f"fixture {fixture_id} source evidence",
                digest_key="sha256" if evidence_row.get("sha256") else None,
            )

        if source_row.get("kind") == "upstream_test_module":
            designs = fixture.get("case_designs")
            _require(
                isinstance(designs, list) and bool(designs),
                f"test module {fixture_id} has no case designs",
            )
            design_ids = set()
            for design in designs:
                case_id = design.get("id")
                _require(
                    isinstance(case_id, str) and case_id not in case_ids,
                    "test case fixture IDs must be unique",
                )
                case_ids.add(case_id)
                design_ids.add(case_id)
                _require(
                    bool(design.get("stimulus_design")), f"case {case_id} has no stimulus design"
                )
                _require(
                    bool(design.get("observation_selectors")),
                    f"case {case_id} has no observation selectors",
                )
                _require(
                    bool(design.get("selector_evidence")),
                    f"case {case_id} has no selector evidence",
                )
                register_selectors(design["observation_selectors"], f"case {case_id}")
                _reject_output_values(design, f"case {case_id}")
            matched_ids = {
                row.get("case_id")
                for row in source_row.get("mapping_evidence", {}).get("matched_test_functions", [])
            }
            _require(
                design_ids == matched_ids,
                f"test module {fixture_id} case designs disagree with its function map",
            )
            matched_by_case = {
                row.get("case_id"): row
                for row in source_row.get("mapping_evidence", {}).get("matched_test_functions", [])
            }
            linked_functions: dict[str, str] = {}
            for design in designs:
                function_name = design.get("source_function")
                workflow_case = design.get("workflow_case")
                function_source_ref = design.get("function_source_ref")
                inventory_row = matched_by_case.get(design.get("id"), {})
                _require(
                    inventory_row.get("workflow_case") == workflow_case
                    and inventory_row.get("function_source_ref") == function_source_ref,
                    f"case {design.get('id')} direct function links differ "
                    "from the atlas inventory",
                )
                if workflow_case is None:
                    _require(
                        function_source_ref is None,
                        f"case {design.get('id')} has a source span without a direct workflow link",
                    )
                    continue
                _require(
                    isinstance(workflow_case, dict)
                    and set(workflow_case)
                    == {
                        "workflow_id",
                        "recipe_path",
                        "case_id",
                        "action_ids",
                        "observation_selectors",
                    },
                    f"case {design.get('id')} has an invalid direct workflow link",
                )
                workflow_id = workflow_case.get("workflow_id")
                recipe_path = workflow_case.get("recipe_path")
                linked_case_id = workflow_case.get("case_id")
                action_ids = workflow_case.get("action_ids")
                link_selectors = workflow_case.get("observation_selectors")
                _require(
                    isinstance(workflow_id, str)
                    and isinstance(recipe_path, str)
                    and isinstance(linked_case_id, str)
                    and isinstance(action_ids, list)
                    and bool(action_ids)
                    and all(isinstance(value, str) and value for value in action_ids)
                    and len(action_ids) == len(set(action_ids))
                    and isinstance(link_selectors, list)
                    and bool(link_selectors)
                    and all(isinstance(value, str) and value for value in link_selectors)
                    and len(link_selectors) == len(set(link_selectors)),
                    f"case {design.get('id')} has malformed direct workflow selectors or actions",
                )
                expected_link = QUERY_VALIDATION_ALIAS_FUNCTION_CASES.get(function_name)
                expected_workflow_id = QUERY_VALIDATION_ALIAS_WORKFLOW_ID
                expected_recipe_path = QUERY_VALIDATION_ALIAS_RECIPE_PATH
                if expected_link is None:
                    expected_link = QUERY_REQUIRED_LIST_FUNCTION_CASES.get(function_name)
                    expected_workflow_id = QUERY_REQUIRED_LIST_WORKFLOW_ID
                    expected_recipe_path = QUERY_REQUIRED_LIST_RECIPE_PATH
                if expected_link is None:
                    direct_review = REVIEWED_DIRECT_FUNCTION_WORKFLOW_LINKS.get(
                        (source_row.get("source_path"), function_name)
                    )
                    if direct_review is not None:
                        (
                            expected_workflow_id,
                            expected_recipe_path,
                            expected_case_id,
                            expected_action_ids,
                            expected_selectors,
                        ) = direct_review
                        expected_link = (
                            expected_case_id,
                            expected_action_ids,
                            expected_selectors,
                        )
                _require(
                    expected_link is not None
                    and workflow_case
                    == {
                        "workflow_id": expected_workflow_id,
                        "recipe_path": expected_recipe_path,
                        "case_id": expected_link[0],
                        "action_ids": list(expected_link[1]),
                        "observation_selectors": list(expected_link[2]),
                    },
                    f"case {design.get('id')} direct link differs from its reviewed mapping",
                )
                workflow = indexed_workflows.get(workflow_id)
                _require(
                    isinstance(workflow, dict) and workflow.get("recipe_path") == recipe_path,
                    f"case {design.get('id')} references an unknown workflow or recipe",
                )
                source_mapping = indexed_mappings.get((source_id, workflow_id), {})
                _require(
                    linked_case_id in source_mapping.get("case_ids", [])
                    and set(link_selectors) <= set(source_mapping.get("observation_selectors", [])),
                    f"case {design.get('id')} direct link exceeds its indexed source mapping",
                )
                input_path = (ROOT / workflow.get("input_path", "")).resolve()
                _require(
                    input_path.is_relative_to(ROOT.resolve()) and input_path.is_file(),
                    f"case {design.get('id')} linked workflow input is missing or escapes the repo",
                )
                workflow_document = read_json(input_path)
                materialized_cases = [
                    case
                    for case in workflow_document.get("cases", [])
                    if isinstance(case, dict) and case.get("case_id") == linked_case_id
                ]
                _require(
                    len(materialized_cases) == 1,
                    f"case {design.get('id')} linked workflow case is missing or ambiguous",
                )
                materialized_case = materialized_cases[0]
                actions = materialized_case.get("actions")
                _require(
                    isinstance(actions, list)
                    and all(isinstance(action, dict) for action in actions),
                    f"case {design.get('id')} linked workflow actions are malformed",
                )
                action_by_id = {
                    action.get("action_id"): action
                    for action in actions
                    if isinstance(action.get("action_id"), str)
                }
                _require(
                    len(action_by_id) == len(actions) and set(action_ids) <= action_by_id.keys(),
                    f"case {design.get('id')} link references an unknown or duplicate "
                    "workflow action",
                )
                selected_case = dict(materialized_case)
                selected_case["actions"] = [action_by_id[action_id] for action_id in action_ids]
                from scripts.parity.materialized import _selected_selectors

                projected_selectors = _selected_selectors(
                    selected_case, workflow_schema=workflow_document.get("schema")
                )
                _require(
                    set(link_selectors) == projected_selectors
                    and set(link_selectors) == set(design.get("observation_selectors", [])),
                    f"case {design.get('id')} direct selectors do not match selected actions",
                )
                register_selectors(link_selectors, f"case {design.get('id')} direct workflow")

                _require(
                    isinstance(function_source_ref, dict)
                    and set(function_source_ref) == {"path", "line", "end_line", "sha256"}
                    and function_source_ref.get("path") == source_row.get("source_path")
                    and function_source_ref.get("line") == design.get("source_line")
                    and function_source_ref.get("end_line") == design.get("source_end_line")
                    and function_source_ref.get("sha256") == source_row.get("source_sha256"),
                    f"case {design.get('id')} has a missing or mismatched function source span",
                )
                _verify_source_ref(
                    fastapi_source,
                    function_source_ref,
                    f"case {design.get('id')} direct function source",
                    digest_key="sha256",
                )
                source_path = _source_path(
                    fastapi_source, function_source_ref.get("path"), f"case {design.get('id')}"
                )
                source_tree = ast.parse(source_path.read_text(encoding="utf-8"))
                source_functions = [
                    node
                    for node in source_tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == function_name
                ]
                _require(
                    len(source_functions) == 1
                    and source_functions[0].lineno == function_source_ref.get("line")
                    and source_functions[0].end_lineno == function_source_ref.get("end_line"),
                    f"case {design.get('id')} source span does not identify its exact function",
                )
                linked_functions[function_name] = linked_case_id
            if source_row.get("source_path") == "tests/test_request_params/test_query/test_list.py":
                _require(
                    linked_functions
                    == {
                        function_name: mapping[0]
                        for function_name, mapping in {
                            **QUERY_VALIDATION_ALIAS_FUNCTION_CASES,
                            **QUERY_REQUIRED_LIST_FUNCTION_CASES,
                        }.items()
                    },
                    "query-list functions lost or changed direct workflow links",
                )
            if source_row.get("source_path") == "tests/test_router_include_context.py":
                expected_direct_links = {
                    function_name: row[2]
                    for (
                        source_path,
                        function_name,
                    ), row in REVIEWED_DIRECT_FUNCTION_WORKFLOW_LINKS.items()
                    if source_path == source_row.get("source_path")
                }
                _require(
                    linked_functions == expected_direct_links,
                    "router-include-context functions lost or changed direct workflow links",
                )
        elif source_row.get("kind") == "documented_feature_page":
            sections = fixture.get("documented_sections")
            _require(isinstance(sections, list), f"documented page {fixture_id} has no section map")
            for section in sections:
                section_status = section.get("review_status")
                feature_ids = section.get("feature_ids")
                observation_selectors = section.get("observation_selectors")
                if section_status == "excluded" and not feature_ids:
                    _require(
                        not observation_selectors,
                        f"featureless excluded section in {fixture_id} cannot claim selectors",
                    )
                else:
                    _require(
                        bool(feature_ids),
                        f"documented section in {fixture_id} has no feature mapping",
                    )
                    _require(
                        bool(observation_selectors),
                        f"documented section in {fixture_id} has no selectors",
                    )
                    register_selectors(observation_selectors, f"documented section in {fixture_id}")
                _reject_output_values(section, f"documented section in {fixture_id}")
                _require(
                    section_status in {"pending", "reviewed_partial", "excluded"},
                    f"documented section in {fixture_id} has no explicit review status",
                )
                section_mappings = section.get("independent_workflow_mappings")
                _require(
                    isinstance(section_mappings, list),
                    f"documented section in {fixture_id} has no workflow mapping list",
                )
                if section_status == "reviewed_partial":
                    _require(
                        bool(section_mappings)
                        and bool(section.get("review_rationale"))
                        and not section.get("exclusion_reason"),
                        f"reviewed documented section in {fixture_id} lacks mapping evidence",
                    )
                    for mapping in section_mappings:
                        _require(
                            isinstance(mapping.get("workflow_id"), str)
                            and bool(mapping.get("recipe_path"))
                            and isinstance(mapping.get("case_ids"), list)
                            and bool(mapping.get("case_ids"))
                            and bool(mapping.get("scope_note")),
                            f"reviewed documented section in {fixture_id} "
                            "has an incomplete workflow link",
                        )
                        register_selectors(
                            mapping.get("observation_selectors"),
                            f"documented section workflow in {fixture_id}",
                        )
                        workflow = indexed_workflows.get(mapping.get("workflow_id"))
                        _require(
                            isinstance(workflow, dict)
                            and workflow.get("recipe_path") == mapping.get("recipe_path"),
                            f"documented section in {fixture_id} references an unknown workflow",
                        )
                        page_mapping = indexed_mappings.get(
                            (source_id, mapping.get("workflow_id")), {}
                        )
                        _require(
                            set(mapping.get("case_ids", []))
                            <= set(page_mapping.get("case_ids", []))
                            and set(mapping.get("observation_selectors", []))
                            <= set(page_mapping.get("observation_selectors", [])),
                            f"documented section in {fixture_id} exceeds its indexed page workflow",
                        )
                elif section_status == "excluded":
                    _require(
                        bool(section.get("exclusion_reason")) and not section_mappings,
                        f"excluded documented section in {fixture_id} needs a reason "
                        "and no workflow links",
                    )
                else:
                    _require(
                        not section_mappings and not section.get("exclusion_reason"),
                        f"pending documented section in {fixture_id} cannot claim "
                        "coverage or exclusion",
                    )
        elif source_row.get("kind") == "documented_python_example_source":
            source_mapping = source_row.get("mapping_evidence", {})
            _require(
                fixture.get("independent_workflow_mappings")
                == source_mapping.get("independent_workflow_mappings"),
                (
                    f"documentation example {fixture_id} workflow mappings differ "
                    "from its coverage row"
                ),
            )
            _require(
                fixture.get("observation_selectors")
                == source_mapping.get("example_observation_selectors"),
                (
                    f"documentation example {fixture_id} selectors differ from "
                    "its direct case mappings"
                ),
            )
            _require(
                fixture.get("selector_evidence") == source_mapping.get("example_selector_evidence"),
                (
                    f"documentation example {fixture_id} selector evidence differs "
                    "from its direct case mappings"
                ),
            )
            _require(
                bool(fixture.get("independent_workflow_mappings")),
                f"documentation example {fixture_id} has no exact workflow cases",
            )
            _require(
                source_row.get("review_status") == "reviewed_partial",
                f"documentation example {fixture_id} is not reviewed partial",
            )

    active_page_rows_by_fixture = {
        row["fixture_id"]: row
        for row in coverage_rows
        if row.get("kind") == "documented_feature_page"
        and row.get("mapping_status") != "excluded"
        and row.get("fixture_id")
    }
    documentation_examples = [
        row for row in coverage_rows if row.get("kind") == "documented_python_example_source"
    ]
    for example in documentation_examples:
        example_id = example.get("id")
        status = example.get("mapping_status")
        if status == "excluded":
            reason = example.get("exclusion_reason")
            _require(
                isinstance(reason, str) and bool(reason.strip()),
                f"excluded documentation example {example_id} has no reason",
            )
            _require(
                example.get("review_status") == "excluded",
                f"excluded documentation example {example_id} has an inconsistent review status",
            )
            continue

        _require(
            status == "supporting_source",
            f"documentation example {example_id} is neither mapped nor explicitly excluded",
        )
        independent_workflow_mappings = example.get("mapping_evidence", {}).get(
            "independent_workflow_mappings", []
        )
        if example.get("fixture_id") is None:
            _require(
                not independent_workflow_mappings and example.get("review_status") == "pending",
                f"unmapped documentation example {example_id} claims reviewed independent coverage",
            )
        else:
            example_design = fixture_by_source.get(example_id)
            _require(
                example.get("review_status") == "reviewed_partial"
                and bool(independent_workflow_mappings)
                and example_design is not None
                and example_design.get("id") == example.get("fixture_id"),
                f"documentation example {example_id} has an incomplete independent mapping",
            )
            review_mapping = example.get("mapping_evidence", {}).get("reviewed_example_mapping")
            _require(
                isinstance(review_mapping, dict)
                and bool(review_mapping.get("rationale"))
                and any(
                    evidence.get("path") == example.get("source_path")
                    and evidence.get("sha256") == example.get("source_sha256")
                    for evidence in review_mapping.get("source_evidence", [])
                ),
                f"documentation example {example_id} has no source-backed mapping review",
            )
            direct_selectors = sorted(
                {
                    selector
                    for mapping in independent_workflow_mappings
                    for selector in mapping.get("observation_selectors", [])
                }
            )
            _require(
                example.get("mapping_evidence", {}).get("example_observation_selectors")
                == direct_selectors,
                (
                    f"documentation example {example_id} direct selectors differ "
                    "from its case mappings"
                ),
            )
        _require(
            example.get("review_status") in {"pending", "reviewed_partial"},
            f"supporting documentation example {example_id} has no valid review status",
        )
        mapped_fixture_ids = example.get("mapped_fixture_ids")
        _require(
            isinstance(mapped_fixture_ids, list)
            and bool(mapped_fixture_ids)
            and all(
                isinstance(fixture_id, str) and bool(fixture_id)
                for fixture_id in mapped_fixture_ids
            )
            and len(mapped_fixture_ids) == len(set(mapped_fixture_ids)),
            f"supporting documentation example {example_id} has no unique page fixture references",
        )
        page_references = example.get("mapping_evidence", {}).get("mapped_documented_pages")
        _require(
            isinstance(page_references, list) and bool(page_references),
            f"supporting documentation example {example_id} has no page selector evidence",
        )
        _require(
            all(
                isinstance(reference, dict)
                and isinstance(reference.get("fixture_id"), str)
                and bool(reference.get("fixture_id"))
                for reference in page_references
            ),
            f"supporting documentation example {example_id} has malformed page references",
        )
        page_references_by_fixture = {
            reference.get("fixture_id"): reference
            for reference in page_references
            if isinstance(reference, dict)
        }
        _require(
            len(page_references_by_fixture) == len(page_references)
            and set(page_references_by_fixture) == set(mapped_fixture_ids),
            f"supporting documentation example {example_id} has inconsistent page references",
        )

        inherited_selectors: set[str] = set()
        page_selector_evidence_groups: list[list[dict[str, Any]]] = []
        for fixture_id in mapped_fixture_ids:
            page_row = active_page_rows_by_fixture.get(fixture_id)
            _require(
                page_row is not None,
                f"supporting documentation example {example_id} references inactive page "
                f"fixture {fixture_id}",
            )
            page_workflows = page_row.get("mapping_evidence", {}).get(
                "independent_workflow_mappings", []
            )
            _require(
                bool(page_workflows),
                f"supporting documentation example {example_id} references an unmapped page "
                f"fixture {fixture_id}",
            )
            page_reference = page_references_by_fixture[fixture_id]
            _require(
                page_reference.get("source_path") == page_row.get("source_path")
                and page_reference.get("feature_ids") == page_row.get("feature_ids")
                and page_reference.get("observation_selectors")
                == page_row.get("observation_selectors")
                and page_reference.get("selector_evidence") == page_row.get("selector_evidence"),
                f"supporting documentation example {example_id} has stale page selectors "
                f"for {fixture_id}",
            )
            page_feature_ids = set(page_row.get("feature_ids", []))
            page_selector_evidence = page_row.get("selector_evidence")
            _require(
                isinstance(page_selector_evidence, list) and bool(page_selector_evidence),
                f"supporting documentation example {example_id} references page {fixture_id} "
                "without feature-selector evidence",
            )
            _require(
                all(
                    isinstance(evidence, dict)
                    and (
                        evidence.get("feature_id") is None
                        or evidence.get("feature_id") in page_feature_ids
                    )
                    and isinstance(evidence.get("selectors"), list)
                    and bool(evidence.get("selectors"))
                    and all(
                        isinstance(selector, str) and bool(selector)
                        for selector in evidence["selectors"]
                    )
                    and (
                        "schema_extension_required" not in evidence
                        or (
                            isinstance(evidence["schema_extension_required"], list)
                            and all(
                                isinstance(selector, str) and bool(selector)
                                for selector in evidence["schema_extension_required"]
                            )
                        )
                    )
                    for evidence in page_selector_evidence
                ),
                f"supporting documentation example {example_id} references malformed "
                f"feature-selector evidence on page {fixture_id}",
            )
            evidence_selectors = {
                selector
                for evidence in page_selector_evidence
                for selector in evidence["selectors"]
            }
            _require(
                evidence_selectors == set(page_row.get("observation_selectors", [])),
                f"page {fixture_id} feature-selector evidence does not match its selectors",
            )
            page_design = fixture_by_source.get(page_row.get("id"))
            _require(
                page_design is not None
                and page_design.get("id") == fixture_id
                and bool(page_design.get("independent_workflow_mappings"))
                and page_design.get("selector_evidence") == page_selector_evidence
                and page_design.get("observation_selectors")
                == page_row.get("observation_selectors"),
                f"supporting documentation example {example_id} references a page without "
                "an input design",
            )
            inherited_selectors.update(page_row.get("observation_selectors", []))
            page_selector_evidence_groups.append(page_selector_evidence)

        _require(
            example.get("observation_selectors") == sorted(inherited_selectors),
            f"supporting documentation example {example_id} selectors do not inherit "
            "its page fixtures",
        )
        _require(
            example.get("selector_evidence")
            == _merge_page_selector_evidence(page_selector_evidence_groups),
            f"supporting documentation example {example_id} feature-selector evidence does not "
            "inherit its page fixtures",
        )

    for row in coverage_rows:
        if row.get("kind") in FIXTURE_KINDS and row.get("mapping_status") != "excluded":
            _require(
                row.get("id") in fixture_by_source,
                f"mapped source {row.get('id')} has no fixture design",
            )

    indexed_workflows = materialized_input_index.get("workflows")
    _require(isinstance(indexed_workflows, list), "materialized API workflow index is missing")
    for workflow in indexed_workflows:
        _require(isinstance(workflow, dict), "materialized workflow entry is malformed")
        probes = workflow.get("api_probes", [])
        _require(
            isinstance(probes, list), f"workflow {workflow.get('id')} API probes are malformed"
        )
        for probe in probes:
            _require(isinstance(probe, dict), "materialized API probe entry is malformed")
            register_selectors(
                probe.get("observation_selectors", []),
                f"direct API workflow {workflow.get('id')} probe {probe.get('probe_id')}",
            )

    unused_definitions = selector_ids - used_selectors
    _require(
        not unused_definitions,
        f"selector catalog contains unused definitions: {sorted(unused_definitions)}",
    )

    integration_edges = atlas.get("starlette_integration_edges", [])
    _validate_starlette_behavior_crosswalks(atlas, fastapi_source, integration_edges)
    _validate_starlette_operation_aliases(integration_edges)
    for edge in integration_edges:
        _require(
            bool(edge.get("starlette_rs_planning_areas")),
            f"Starlette edge {edge.get('id')} has no FastAPI-RS planning area",
        )
        _require(
            bool(
                edge.get("starlette_rs_catalog_evidence")
                or edge.get("starlette_rs_review_evidence")
            ),
            f"Starlette edge {edge.get('id')} has no Starlette-RS contract "
            "mapping or explicit review",
        )
        starlette_source_ref = edge.get("starlette_source", {})
        _verify_source_ref(
            starlette_source, starlette_source_ref, f"Starlette edge {edge.get('id')}"
        )

    selected_starlette_rs = atlas.get("authorities", {}).get("starlette_rs", {})
    for row in coverage_rows:
        mappings = row.get("starlette_rs_contract_mappings")
        _require(
            isinstance(mappings, list),
            f"coverage row {row.get('id')} has no FastAPI-to-Starlette-RS contract mapping",
        )
        mapped_features = {mapping.get("feature_id") for mapping in mappings}
        _require(
            mapped_features == set(row.get("feature_ids", [])),
            f"coverage row {row.get('id')} contract mappings do not match its feature IDs",
        )
        for mapping in mappings:
            _require(
                mapping.get("contract_id") == selected_starlette_rs.get("current_contract_id"),
                f"coverage row {row.get('id')} selects another Starlette-RS contract",
            )
            operation_refs = mapping.get("operation_refs", [])
            if mapping.get("status") == "linked-to-current-contract-slice":
                _require(
                    bool(operation_refs),
                    f"coverage row {row.get('id')} marks a contract link without "
                    "operation references",
                )
            else:
                _require(
                    mapping.get("status") == "out-of-current-contract-slice" and not operation_refs,
                    f"coverage row {row.get('id')} has an invalid out-of-slice mapping",
                )
            for operation_ref in operation_refs:
                _require(
                    operation_ref.get("contract_id")
                    == selected_starlette_rs.get("current_contract_id")
                    and bool(operation_ref.get("surface_id"))
                    and bool(operation_ref.get("operation_id"))
                    and bool(operation_ref.get("requirement_ids")),
                    f"coverage row {row.get('id')} has an incomplete Starlette-RS "
                    "requirement reference",
                )

    backlog_ref = atlas.get("fixture_backlog_ref", {})
    _require(
        backlog_ref.get("item_count") == len(fixture_rows),
        "atlas fixture count does not match backlog",
    )
    _require(
        backlog_ref.get("path") == "tests/fixtures/fixture-backlog.json",
        "atlas fixture backlog path is unexpected",
    )
    _require(
        backlog_ref.get("schema") == backlog.get("schema") == FIXTURE_BACKLOG_SCHEMA_ID,
        "atlas fixture backlog schema differs from the backlog artifact",
    )

    kinds = Counter(row.get("kind") for row in coverage_rows)
    documented_sections = [
        section
        for row in coverage_rows
        if row.get("kind") == "documented_feature_page"
        for section in row.get("mapping_evidence", {}).get("documented_sections", [])
    ]
    section_statuses = Counter(section.get("review_status") for section in documented_sections)
    _require(
        atlas.get("counts", {}).get("documentation_section_candidates") == len(documented_sections)
        and atlas.get("counts", {}).get("documentation_sections_with_reviewed_partial_mapping")
        == section_statuses["reviewed_partial"]
        and atlas.get("counts", {}).get("documentation_sections_pending_behavior_review")
        == section_statuses["pending"]
        and atlas.get("counts", {}).get("documentation_sections_excluded")
        == section_statuses["excluded"],
        "documentation-section status counts differ from the coverage matrix",
    )
    statuses = Counter(
        row.get("mapping_status") for row in coverage_rows if row.get("kind") in FIXTURE_KINDS
    )
    from scripts.atlas_source_wave_b_review_mappings import (
        validate_source_wave_b_review_mappings,
    )

    source_wave_b_review = validate_source_wave_b_review_mappings()
    return {
        "starlette_contract": "1.6.0",
        "api_candidates": len(api_rows),
        "reviewed_inherited_api_candidates": len(inherited_rows),
        "api_classifications": dict(sorted(classifications.items())),
        "upstream_test_modules": kinds["upstream_test_module"],
        "documented_feature_pages": kinds["documented_feature_page"],
        "documented_sections": len(documented_sections),
        "documented_sections_with_reviewed_partial_mapping": section_statuses["reviewed_partial"],
        "documented_sections_pending_behavior_review": section_statuses["pending"],
        "documented_sections_excluded": section_statuses["excluded"],
        "documentation_python_examples": len(documentation_examples),
        "documentation_python_examples_grouped_with_page": sum(
            row.get("mapping_status") == "supporting_source" for row in documentation_examples
        ),
        "documentation_python_examples_with_independent_input_workflow_link": sum(
            bool(row.get("mapping_evidence", {}).get("independent_workflow_mappings"))
            for row in documentation_examples
        ),
        "documentation_python_examples_with_reviewed_partial_mapping": sum(
            row.get("review_status") == "reviewed_partial" for row in documentation_examples
        ),
        "documentation_python_examples_excluded": sum(
            row.get("mapping_status") == "excluded" for row in documentation_examples
        ),
        "fixture_designs": len(fixture_rows),
        "test_case_designs": len(case_ids),
        "selector_definitions": len(selector_specs),
        "selectors_used": len(used_selectors),
        "reviewed_callable_candidates": len(review_rows),
        "reviewed_callable_classifications": dict(sorted(review_counts.items())),
        "fixture_source_statuses": dict(sorted(statuses.items())),
        "excluded_test_modules": sum(
            row.get("kind") == "upstream_test_module" and row.get("mapping_status") == "excluded"
            for row in coverage_rows
        ),
        "test_functions_in_excluded_modules": sum(
            row.get("mapping_evidence", {}).get("test_function_count", 0)
            for row in coverage_rows
            if row.get("kind") == "upstream_test_module" and row.get("mapping_status") == "excluded"
        ),
        "test_functions_with_inherited_module_exclusion": sum(
            len(row.get("mapping_evidence", {}).get("module_excluded_test_functions", []))
            for row in coverage_rows
            if row.get("kind") == "upstream_test_module" and row.get("mapping_status") == "excluded"
        ),
        "test_functions_with_individual_exclusion": sum(
            len(row.get("mapping_evidence", {}).get("excluded_test_functions", []))
            for row in coverage_rows
            if row.get("kind") == "upstream_test_module" and row.get("mapping_status") == "excluded"
        ),
        "excluded_documentation_pages": sum(
            row.get("kind") == "documented_feature_page" and row.get("mapping_status") == "excluded"
            for row in coverage_rows
        ),
        "starlette_integration_edges": len(atlas.get("starlette_integration_edges", [])),
        "source_wave_b_function_review": source_wave_b_review,
    }
