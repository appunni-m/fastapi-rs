"""Build and verify the per-symbol source contract embedded in the manifest."""

from __future__ import annotations

import ast
import json
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

    def add_definition(row: dict[str, Any], pointer: str) -> None:
        pointers[row["id"]].append(pointer)
        for index, member in enumerate(row.get("members", [])):
            add_definition(member, f"{pointer}/members/{index}")

    for module_index, module in enumerate(inventory["modules"]):
        for definition_index, definition in enumerate(module["definitions"]):
            add_definition(
                definition,
                _pointer("modules", module_index, "definitions", definition_index),
            )
    for binding_index, binding in enumerate(inventory["import_bindings"]):
        pointers[binding["id"]].append(_pointer("import_bindings", binding_index))
    return dict(pointers)


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
    error_selector_rules = overlay.get("error_selector_rules", [])
    if not isinstance(error_selector_rules, list) or any(
        not isinstance(rule, dict) for rule in error_selector_rules
    ):
        raise ContractError("reviewed API error selector rules must be a list of mappings")
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
                    "rust_binding": None,
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
            "signature_contract_states": dict(sorted(signature_statuses.items())),
            "implementation_owner_plans": dict(sorted(owner_counts.items())),
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
    }


def validate_api_workflow_public_surface(
    workflow: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    """Require every direct API probe to call a source-supported public symbol."""
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise ContractError("direct Python API workflow requires the generated public API contract")
    supported = {
        symbol.get("id")
        for symbol in contract.get("symbols", [])
        if isinstance(symbol, dict) and isinstance(symbol.get("id"), str)
    }
    selected: set[str] = set()
    for case in workflow.get("cases", []):
        for probe in case.get("probes", []):
            public_callable = probe.get("public_callable", {})
            module = public_callable.get("module")
            attribute = public_callable.get("attribute")
            symbol_id = f"{module}.{attribute}"
            if symbol_id not in supported:
                raise ContractError(
                    "direct Python API workflow references a symbol outside the supported "
                    f"source API contract: {symbol_id}"
                )
            selected.add(symbol_id)
    if not selected:
        raise ContractError("direct Python API workflow contains no public callable probes")
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
