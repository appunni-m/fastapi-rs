"""Validate the pinned-source API atlas and input-only fixture backlog."""

from __future__ import annotations

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


def _fail(message: str) -> None:
    raise ContractError(f"compatibility atlas: {message}")


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


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
    fastapi_source: Path,
    starlette_source: Path,
) -> dict[str, Any]:
    """Check source evidence, complete module/page links, and input-only designs."""
    _require(atlas.get("schema") == "fastapi-rs/compatibility-atlas@2", "unsupported atlas schema")
    _require(
        backlog.get("schema") == "fastapi-rs/fixture-backlog@1",
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

    fixture_rows = backlog.get("fixture_designs")
    _require(isinstance(fixture_rows, list) and bool(fixture_rows), "fixture designs are missing")
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
        else:
            sections = fixture.get("documented_sections")
            _require(isinstance(sections, list), f"documented page {fixture_id} has no section map")
            for section in sections:
                _require(
                    bool(section.get("feature_ids")),
                    f"documented section in {fixture_id} has no feature mapping",
                )
                _require(
                    bool(section.get("observation_selectors")),
                    f"documented section in {fixture_id} has no selectors",
                )
                register_selectors(
                    section["observation_selectors"], f"documented section in {fixture_id}"
                )
                _reject_output_values(section, f"documented section in {fixture_id}")

    for row in coverage_rows:
        if row.get("kind") in FIXTURE_KINDS and row.get("mapping_status") != "excluded":
            _require(
                row.get("id") in fixture_by_source,
                f"mapped source {row.get('id')} has no fixture design",
            )

    unused_definitions = selector_ids - used_selectors
    _require(
        not unused_definitions,
        f"selector catalog contains unused definitions: {sorted(unused_definitions)}",
    )

    for edge in atlas.get("starlette_integration_edges", []):
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

    kinds = Counter(row.get("kind") for row in coverage_rows)
    statuses = Counter(
        row.get("mapping_status") for row in coverage_rows if row.get("kind") in FIXTURE_KINDS
    )
    return {
        "starlette_contract": "1.6.0",
        "api_candidates": len(api_rows),
        "api_classifications": dict(sorted(classifications.items())),
        "upstream_test_modules": kinds["upstream_test_module"],
        "documented_feature_pages": kinds["documented_feature_page"],
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
        "excluded_documentation_pages": sum(
            row.get("kind") == "documented_feature_page" and row.get("mapping_status") == "excluded"
            for row in coverage_rows
        ),
        "starlette_integration_edges": len(atlas.get("starlette_integration_edges", [])),
    }
