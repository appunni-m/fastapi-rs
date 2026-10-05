"""Strict loading and reference validation for Python/ASGI workflows."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from yaml import SafeLoader

from scripts.parity.fault_contracts import (
    HTTP_REQUEST_FORM_PARSE_CONTRACT,
    HTTP_REQUEST_JSON_DECODE_CONTRACT,
    FaultContractError,
    verification_mode,
)

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_SCHEMA = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v2.schema.json"
WORKFLOW_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v3.schema.json"
WORKFLOW_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v4.schema.json"
WORKFLOW_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v5.schema.json"
WORKFLOW_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v6.schema.json"
WORKFLOW_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v7.schema.json"
WORKFLOW_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v8.schema.json"
API_WORKFLOW_SCHEMA = ROOT / "tests/fixtures/schemas/python-api-workflow.schema.json"
API_WORKFLOW_SCHEMA_V2 = ROOT / "tests/fixtures/schemas/python-api-workflow-v2.schema.json"
API_WORKFLOW_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-api-workflow-v3.schema.json"
API_WORKFLOW_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-api-workflow-v4.schema.json"
API_RESULT_SCHEMA = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v2.schema.json"
API_RESULT_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v3.schema.json"
API_RESULT_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v4.schema.json"
API_RESULT_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v5.schema.json"
API_COMPARISON_SCHEMA = ROOT / "tests/fixtures/schemas/python-api-comparison-v1.schema.json"
API_COMPARISON_SCHEMA_V2 = ROOT / "tests/fixtures/schemas/python-api-comparison-v2.schema.json"
API_COMPARISON_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-api-comparison-v3.schema.json"
API_COMPARISON_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-api-comparison-v4.schema.json"
RESULT_SCHEMA = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v2.schema.json"
RESULT_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v3.schema.json"
RESULT_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v4.schema.json"
RESULT_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v5.schema.json"
RESULT_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v6.schema.json"
RESULT_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v7.schema.json"
RESULT_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v8.schema.json"
COMPARISON_SCHEMA = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v2.schema.json"
COMPARISON_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v3.schema.json"
COMPARISON_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v4.schema.json"
COMPARISON_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v5.schema.json"
COMPARISON_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v6.schema.json"
COMPARISON_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v7.schema.json"
COMPARISON_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v8.schema.json"
WORKFLOW_SCHEMA_ID = "fastapi-rs/python-asgi-workflow@2"
WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-asgi-workflow@3"
WORKFLOW_SCHEMA_V4_ID = "fastapi-rs/python-asgi-workflow@4"
WORKFLOW_SCHEMA_V5_ID = "fastapi-rs/python-asgi-workflow@5"
WORKFLOW_SCHEMA_V6_ID = "fastapi-rs/python-asgi-workflow@6"
WORKFLOW_SCHEMA_V7_ID = "fastapi-rs/python-asgi-workflow@7"
WORKFLOW_SCHEMA_V8_ID = "fastapi-rs/python-asgi-workflow@8"
API_WORKFLOW_SCHEMA_ID = "fastapi-rs/python-api-workflow@1"
API_WORKFLOW_SCHEMA_V2_ID = "fastapi-rs/python-api-workflow@2"
API_WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow@3"
API_WORKFLOW_SCHEMA_V4_ID = "fastapi-rs/python-api-workflow@4"
MATERIALIZED_INPUT_INDEX_SCHEMA_ID = "fastapi-rs/materialized-input-index@4"
API_RESULT_SCHEMA_ID = "fastapi-rs/python-api-workflow-result@2"
API_RESULT_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow-result@3"
API_RESULT_SCHEMA_V4_ID = "fastapi-rs/python-api-workflow-result@4"
API_RESULT_SCHEMA_V5_ID = "fastapi-rs/python-api-workflow-result@5"
API_COMPARISON_SCHEMA_ID = "fastapi-rs/python-api-comparison@1"
API_COMPARISON_SCHEMA_V2_ID = "fastapi-rs/python-api-comparison@2"
API_COMPARISON_SCHEMA_V3_ID = "fastapi-rs/python-api-comparison@3"
API_COMPARISON_SCHEMA_V4_ID = "fastapi-rs/python-api-comparison@4"
API_WORKFLOW_SCHEMA_IDS = frozenset(
    {
        API_WORKFLOW_SCHEMA_ID,
        API_WORKFLOW_SCHEMA_V2_ID,
        API_WORKFLOW_SCHEMA_V3_ID,
        API_WORKFLOW_SCHEMA_V4_ID,
    }
)
API_RESULT_SCHEMA_IDS_BY_WORKFLOW = {
    API_WORKFLOW_SCHEMA_ID: API_RESULT_SCHEMA_ID,
    API_WORKFLOW_SCHEMA_V2_ID: API_RESULT_SCHEMA_V3_ID,
    API_WORKFLOW_SCHEMA_V3_ID: API_RESULT_SCHEMA_V4_ID,
    API_WORKFLOW_SCHEMA_V4_ID: API_RESULT_SCHEMA_V5_ID,
}
API_RESULT_SCHEMAS_BY_ID = {
    API_RESULT_SCHEMA_ID: API_RESULT_SCHEMA,
    API_RESULT_SCHEMA_V3_ID: API_RESULT_SCHEMA_V3,
    API_RESULT_SCHEMA_V4_ID: API_RESULT_SCHEMA_V4,
    API_RESULT_SCHEMA_V5_ID: API_RESULT_SCHEMA_V5,
}
API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW = {
    API_WORKFLOW_SCHEMA_ID: API_COMPARISON_SCHEMA_ID,
    API_WORKFLOW_SCHEMA_V2_ID: API_COMPARISON_SCHEMA_V2_ID,
    API_WORKFLOW_SCHEMA_V3_ID: API_COMPARISON_SCHEMA_V3_ID,
    API_WORKFLOW_SCHEMA_V4_ID: API_COMPARISON_SCHEMA_V4_ID,
}
API_COMPARISON_SCHEMAS_BY_ID = {
    API_COMPARISON_SCHEMA_ID: API_COMPARISON_SCHEMA,
    API_COMPARISON_SCHEMA_V2_ID: API_COMPARISON_SCHEMA_V2,
    API_COMPARISON_SCHEMA_V3_ID: API_COMPARISON_SCHEMA_V3,
    API_COMPARISON_SCHEMA_V4_ID: API_COMPARISON_SCHEMA_V4,
}
RESULT_SCHEMA_ID = "fastapi-rs/python-asgi-workflow-result@2"
RESULT_SCHEMA_V3_ID = "fastapi-rs/python-asgi-workflow-result@3"
RESULT_SCHEMA_V4_ID = "fastapi-rs/python-asgi-workflow-result@4"
RESULT_SCHEMA_V5_ID = "fastapi-rs/python-asgi-workflow-result@5"
RESULT_SCHEMA_V6_ID = "fastapi-rs/python-asgi-workflow-result@6"
RESULT_SCHEMA_V7_ID = "fastapi-rs/python-asgi-workflow-result@7"
RESULT_SCHEMA_V8_ID = "fastapi-rs/python-asgi-workflow-result@8"
COMPARISON_SCHEMA_ID = "fastapi-rs/python-asgi-comparison@2"
COMPARISON_SCHEMA_V3_ID = "fastapi-rs/python-asgi-comparison@3"
COMPARISON_SCHEMA_V4_ID = "fastapi-rs/python-asgi-comparison@4"
COMPARISON_SCHEMA_V5_ID = "fastapi-rs/python-asgi-comparison@5"
COMPARISON_SCHEMA_V6_ID = "fastapi-rs/python-asgi-comparison@6"
COMPARISON_SCHEMA_V7_ID = "fastapi-rs/python-asgi-comparison@7"
COMPARISON_SCHEMA_V8_ID = "fastapi-rs/python-asgi-comparison@8"

WORKFLOW_SCHEMAS = {
    WORKFLOW_SCHEMA_ID: WORKFLOW_SCHEMA,
    WORKFLOW_SCHEMA_V3_ID: WORKFLOW_SCHEMA_V3,
    WORKFLOW_SCHEMA_V4_ID: WORKFLOW_SCHEMA_V4,
    WORKFLOW_SCHEMA_V5_ID: WORKFLOW_SCHEMA_V5,
    WORKFLOW_SCHEMA_V6_ID: WORKFLOW_SCHEMA_V6,
    WORKFLOW_SCHEMA_V7_ID: WORKFLOW_SCHEMA_V7,
    WORKFLOW_SCHEMA_V8_ID: WORKFLOW_SCHEMA_V8,
    API_WORKFLOW_SCHEMA_ID: API_WORKFLOW_SCHEMA,
    API_WORKFLOW_SCHEMA_V2_ID: API_WORKFLOW_SCHEMA_V2,
    API_WORKFLOW_SCHEMA_V3_ID: API_WORKFLOW_SCHEMA_V3,
    API_WORKFLOW_SCHEMA_V4_ID: API_WORKFLOW_SCHEMA_V4,
}
RESULT_SCHEMAS = {
    RESULT_SCHEMA_ID: RESULT_SCHEMA,
    RESULT_SCHEMA_V3_ID: RESULT_SCHEMA_V3,
    RESULT_SCHEMA_V4_ID: RESULT_SCHEMA_V4,
    RESULT_SCHEMA_V5_ID: RESULT_SCHEMA_V5,
    RESULT_SCHEMA_V6_ID: RESULT_SCHEMA_V6,
    RESULT_SCHEMA_V7_ID: RESULT_SCHEMA_V7,
    RESULT_SCHEMA_V8_ID: RESULT_SCHEMA_V8,
    API_RESULT_SCHEMA_ID: API_RESULT_SCHEMA,
    API_RESULT_SCHEMA_V3_ID: API_RESULT_SCHEMA_V3,
    API_RESULT_SCHEMA_V4_ID: API_RESULT_SCHEMA_V4,
    API_RESULT_SCHEMA_V5_ID: API_RESULT_SCHEMA_V5,
}
COMPARISON_SCHEMAS = {
    COMPARISON_SCHEMA_ID: COMPARISON_SCHEMA,
    COMPARISON_SCHEMA_V3_ID: COMPARISON_SCHEMA_V3,
    COMPARISON_SCHEMA_V4_ID: COMPARISON_SCHEMA_V4,
    COMPARISON_SCHEMA_V5_ID: COMPARISON_SCHEMA_V5,
    COMPARISON_SCHEMA_V6_ID: COMPARISON_SCHEMA_V6,
    COMPARISON_SCHEMA_V7_ID: COMPARISON_SCHEMA_V7,
    COMPARISON_SCHEMA_V8_ID: COMPARISON_SCHEMA_V8,
    API_COMPARISON_SCHEMA_ID: API_COMPARISON_SCHEMA,
    API_COMPARISON_SCHEMA_V2_ID: API_COMPARISON_SCHEMA_V2,
    API_COMPARISON_SCHEMA_V3_ID: API_COMPARISON_SCHEMA_V3,
    API_COMPARISON_SCHEMA_V4_ID: API_COMPARISON_SCHEMA_V4,
}
RESULT_SCHEMA_IDS_BY_WORKFLOW = {
    WORKFLOW_SCHEMA_ID: RESULT_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID: RESULT_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID: RESULT_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID: RESULT_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID: RESULT_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V7_ID: RESULT_SCHEMA_V7_ID,
    WORKFLOW_SCHEMA_V8_ID: RESULT_SCHEMA_V8_ID,
    **API_RESULT_SCHEMA_IDS_BY_WORKFLOW,
}
COMPARISON_SCHEMA_IDS_BY_WORKFLOW = {
    WORKFLOW_SCHEMA_ID: COMPARISON_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID: COMPARISON_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID: COMPARISON_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID: COMPARISON_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID: COMPARISON_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V7_ID: COMPARISON_SCHEMA_V7_ID,
    WORKFLOW_SCHEMA_V8_ID: COMPARISON_SCHEMA_V8_ID,
    **API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
}


class ContractError(ValueError):
    """A malformed workflow or stale reference in the parity contract."""


class _UniqueKeyLoader(SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ContractError(f"duplicate YAML mapping key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON number is forbidden: {value}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc


def read_manifest() -> dict[str, Any]:
    """Load the one manifest and enforce the pinned oracle profile shape."""
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    try:
        with manifest_path.open(encoding="utf-8") as stream:
            manifest = yaml.load(stream, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read manifest {manifest_path}: {exc}") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != "fastapi-rs/contract-foundation@1"
    ):
        raise ContractError("manifest schema identity is missing or unsupported")
    profile = manifest.get("oracle_profile")
    if not isinstance(profile, dict) or profile.get("id") != (
        "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13"
    ):
        raise ContractError("manifest must define the fixed FastAPI/Starlette 1.6.0 oracle profile")
    selected = manifest.get("selected_contracts")
    if not isinstance(selected, dict):
        raise ContractError("manifest selected_contracts must be a mapping")
    expected_commits = {
        "fastapi": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "starlette": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    }
    for contract_name, commit in expected_commits.items():
        contract = selected.get(contract_name)
        if not isinstance(contract, dict):
            raise ContractError(f"manifest selected contract {contract_name} must be a mapping")
        expected_version = "0.141.1" if contract_name == "fastapi" else "1.6.0"
        if contract.get("version") != expected_version or contract.get("commit") != commit:
            raise ContractError(
                f"manifest {contract_name} contract changed without updating "
                "the fixed oracle profile"
            )
    if profile.get("python") != {"implementation": "CPython", "version": "3.12.13"}:
        raise ContractError("manifest oracle runtime must remain CPython 3.12.13")
    if profile.get("source_commits") != expected_commits:
        raise ContractError("manifest oracle commits do not match the selected source contracts")
    pydantic = selected.get("pydantic")
    if not isinstance(pydantic, dict):
        raise ContractError("manifest Pydantic contract must be a mapping")
    if (pydantic.get("version"), pydantic.get("pydantic_core_version")) != (
        "2.13.4",
        "2.46.4",
    ):
        raise ContractError(
            "manifest Pydantic baseline changed without updating the oracle profile"
        )
    expected_packages = {
        "annotated-doc": "0.0.4",
        "annotated-types": "0.7.0",
        "anyio": "4.12.1",
        "fastapi": "0.141.1",
        "idna": "3.18",
        "pydantic": "2.13.4",
        "pydantic-core": "2.46.4",
        "starlette": "1.6.0",
        "typing-extensions": "4.16.0",
        "typing-inspection": "0.4.2",
    }
    if profile.get("packages") != expected_packages:
        raise ContractError("manifest oracle runtime package pins are incomplete or changed")
    expected_extensions = {
        "standard-multipart": {
            "id": "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-standard-multipart-0.0.32",
            "base_profile": profile["id"],
            "added_packages": {"python-multipart": "0.0.32"},
            "fastapi_extra": "standard",
            "prepare_target": "parity-prepare-oracle-standard",
        }
    }
    if manifest.get("oracle_profile_extensions") != expected_extensions:
        raise ContractError(
            "manifest optional oracle environment differs from the pinned multipart extension"
        )
    target = manifest.get("target")
    if not isinstance(target, dict) or target.get("version") != "0.1.0":
        raise ContractError(
            "manifest target version must remain the pinned development version 0.1.0"
        )
    try:
        project_metadata = yaml.safe_load((ROOT / "metadata.yaml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read FastAPI-RS metadata: {exc}") from exc
    starlette_rs_metadata = (
        project_metadata.get("starlette_rs") if isinstance(project_metadata, dict) else None
    )
    metadata_starlette_rs_commit = (
        starlette_rs_metadata.get("commit") if isinstance(starlette_rs_metadata, dict) else None
    )
    if (
        not isinstance(metadata_starlette_rs_commit, str)
        or len(metadata_starlette_rs_commit) != 40
        or any(character not in "0123456789abcdef" for character in metadata_starlette_rs_commit)
    ):
        raise ContractError("metadata.yaml must pin a full lowercase Starlette-RS commit")
    if target.get("starlette_rs_distribution") != {
        "name": "starlette-rs-py",
        "version": "0.1.0",
        "starlette_contract": "1.6.0",
        "commit": metadata_starlette_rs_commit,
    }:
        raise ContractError("manifest target must select Starlette-RS 0.1.0 for the 1.6.0 contract")
    source_artifacts = manifest.get("source_artifacts")
    if not isinstance(source_artifacts, dict):
        raise ContractError("manifest source_artifacts must be a mapping")
    for artifact_name in (
        "api_inventory",
        "api_classification_review",
        "api_import_binding_classification_review",
        "compatibility_atlas",
        "fixture_backlog",
        "observation_selector_catalog",
        "runtime_api_surface_core",
        "runtime_api_surface_standard",
        "materialized_input_index",
    ):
        artifact = source_artifacts.get(artifact_name)
        if not isinstance(artifact, dict):
            raise ContractError(f"manifest {artifact_name} reference is missing")
        _verify_digest_ref(artifact.get("path"), artifact.get("sha256"), artifact_name)
        if artifact_name == "materialized_input_index":
            if artifact.get("schema") != MATERIALIZED_INPUT_INDEX_SCHEMA_ID:
                raise ContractError("manifest materialized input index schema is unsupported")
            _verify_digest_ref(
                artifact.get("schema_path"),
                artifact.get("schema_sha256"),
                "materialized input index schema",
            )

    atlas_artifact = source_artifacts["compatibility_atlas"]
    atlas = read_json(_resolve_repo_file(atlas_artifact["path"], "compatibility atlas"))
    review_artifact = source_artifacts["api_classification_review"]
    review_link = atlas.get("api_classification_review") if isinstance(atlas, dict) else None
    if not isinstance(review_link, dict) or any(
        review_link.get(atlas_key) != review_artifact.get(manifest_key)
        for atlas_key, manifest_key in (
            ("path", "path"),
            ("schema", "schema"),
            ("sha256", "sha256"),
        )
    ):
        raise ContractError("manifest callable-classification review differs from atlas evidence")
    review = read_json(_resolve_repo_file(review_artifact["path"], "API classification review"))
    if (
        not isinstance(review, dict)
        or review.get("schema") != review_artifact.get("schema")
        or review.get("source_identity", {}).get("selected_starlette_profile") != "1.6.0"
    ):
        raise ContractError("API callable-classification review identity is unsupported")

    import_binding_review_artifact = source_artifacts["api_import_binding_classification_review"]
    import_binding_review_link = atlas.get("api_import_binding_classification_review")
    if not isinstance(import_binding_review_link, dict) or any(
        import_binding_review_link.get(atlas_key)
        != import_binding_review_artifact.get(manifest_key)
        for atlas_key, manifest_key in (
            ("path", "path"),
            ("schema", "schema"),
            ("sha256", "sha256"),
        )
    ):
        raise ContractError("manifest import-binding review differs from atlas evidence")
    import_binding_review = read_json(
        _resolve_repo_file(
            import_binding_review_artifact["path"], "API import-binding classification review"
        )
    )
    if not isinstance(import_binding_review, dict):
        raise ContractError("API import-binding classification review must be an object")
    scope = import_binding_review.get("scope", {})
    source_identity = import_binding_review.get("source_identity", {})
    counts = import_binding_review_artifact.get("counts", {})
    recommendations = scope.get("recommendation_counts", {})
    expected_review_counts = {
        "candidates": scope.get("candidate_count"),
        "supported": recommendations.get("supported"),
        "private_or_internal": recommendations.get("private/internal"),
        "uncertain": recommendations.get("uncertain"),
        "starlette_rs_reviewed_candidates": scope.get("starlette_rs_reviewed_candidate_count"),
        "starlette_rs_unreviewed_unique_targets": scope.get(
            "starlette_rs_unreviewed_unique_target_count"
        ),
    }
    pinned_sources = import_binding_review.get("pinned_starlette_rs_sources", {})
    pinned_files = pinned_sources.get("files", {}) if isinstance(pinned_sources, dict) else {}
    source_digests = {
        f"{name}_sha256": pinned_files.get(name, {}).get("sha256")
        for name in ("metadata", "manifest", "api_catalog", "api_review")
    }
    if (
        import_binding_review.get("schema") != import_binding_review_artifact.get("schema")
        or source_identity != import_binding_review_artifact.get("source_identity")
        or not isinstance(pinned_sources, dict)
        or pinned_sources.get("contract_id")
        != import_binding_review_artifact.get("starlette_rs_contract_id")
        or import_binding_review.get("scope", {}).get("candidate_ids_sha256")
        != import_binding_review_artifact.get("candidate_ids_sha256")
        or expected_review_counts != {key: counts.get(key) for key in expected_review_counts}
        or source_digests != import_binding_review_artifact.get("pinned_starlette_rs_sources")
    ):
        raise ContractError("API import-binding classification review metadata is unsupported")

    unresolved = manifest.get("unresolved")
    workflow_contract = (
        unresolved.get("python_asgi_workflow") if isinstance(unresolved, dict) else None
    )
    if not isinstance(workflow_contract, dict):
        raise ContractError("manifest Python/ASGI workflow contract is missing")
    schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison schema"),
        ("recipe_path", "recipe_sha256", "workflow input recipe"),
    )
    for path_key, digest_key, label in schema_refs:
        _verify_digest_ref(
            workflow_contract.get(path_key),
            workflow_contract.get(digest_key),
            label,
        )
    workflow_v3_contract = (
        unresolved.get("python_asgi_workflow_v3") if isinstance(unresolved, dict) else None
    )
    if not isinstance(workflow_v3_contract, dict):
        raise ContractError("manifest Python/ASGI v3 workflow contract is missing")
    workflow_v3_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v3 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v3 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v3 schema"),
    )
    for path_key, digest_key, label in workflow_v3_schema_refs:
        _verify_digest_ref(
            workflow_v3_contract.get(path_key),
            workflow_v3_contract.get(digest_key),
            label,
        )
    workflow_v4_contract = unresolved.get("python_asgi_workflow_v4")
    if not isinstance(workflow_v4_contract, dict):
        raise ContractError("manifest Python/ASGI v4 workflow contract is missing")
    if (
        workflow_v4_contract.get("schema_id") != WORKFLOW_SCHEMA_V4_ID
        or workflow_v4_contract.get("result_schema_id") != RESULT_SCHEMA_V4_ID
        or workflow_v4_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V4_ID
    ):
        raise ContractError("manifest Python/ASGI v4 schema identities are unsupported")
    workflow_v4_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v4 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v4 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v4 schema"),
    )
    for path_key, digest_key, label in workflow_v4_schema_refs:
        _verify_digest_ref(
            workflow_v4_contract.get(path_key),
            workflow_v4_contract.get(digest_key),
            label,
        )
    workflow_v5_contract = unresolved.get("python_asgi_workflow_v5")
    if not isinstance(workflow_v5_contract, dict):
        raise ContractError("manifest Python/ASGI v5 workflow contract is missing")
    if (
        workflow_v5_contract.get("schema_id") != WORKFLOW_SCHEMA_V5_ID
        or workflow_v5_contract.get("result_schema_id") != RESULT_SCHEMA_V5_ID
        or workflow_v5_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V5_ID
    ):
        raise ContractError("manifest Python/ASGI v5 schema identities are unsupported")
    workflow_v5_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v5 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v5 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v5 schema"),
    )
    for path_key, digest_key, label in workflow_v5_schema_refs:
        _verify_digest_ref(
            workflow_v5_contract.get(path_key),
            workflow_v5_contract.get(digest_key),
            label,
        )
    workflow_v6_contract = unresolved.get("python_asgi_workflow_v6")
    if not isinstance(workflow_v6_contract, dict):
        raise ContractError("manifest Python/ASGI v6 workflow contract is missing")
    if (
        workflow_v6_contract.get("schema_id") != WORKFLOW_SCHEMA_V6_ID
        or workflow_v6_contract.get("result_schema_id") != RESULT_SCHEMA_V6_ID
        or workflow_v6_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V6_ID
    ):
        raise ContractError("manifest Python/ASGI v6 schema identities are unsupported")
    workflow_v6_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v6 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v6 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v6 schema"),
    )
    for path_key, digest_key, label in workflow_v6_schema_refs:
        _verify_digest_ref(
            workflow_v6_contract.get(path_key),
            workflow_v6_contract.get(digest_key),
            label,
        )
    workflow_v7_contract = unresolved.get("python_asgi_workflow_v7")
    if not isinstance(workflow_v7_contract, dict):
        raise ContractError("manifest Python/ASGI v7 workflow contract is missing")
    if (
        workflow_v7_contract.get("schema_id") != WORKFLOW_SCHEMA_V7_ID
        or workflow_v7_contract.get("result_schema_id") != RESULT_SCHEMA_V7_ID
        or workflow_v7_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V7_ID
    ):
        raise ContractError("manifest Python/ASGI v7 schema identities are unsupported")
    workflow_v7_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v7 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v7 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v7 schema"),
    )
    for path_key, digest_key, label in workflow_v7_schema_refs:
        _verify_digest_ref(
            workflow_v7_contract.get(path_key),
            workflow_v7_contract.get(digest_key),
            label,
        )
    workflow_v8_contract = unresolved.get("python_asgi_workflow_v8")
    if not isinstance(workflow_v8_contract, dict):
        raise ContractError("manifest Python/ASGI v8 workflow contract is missing")
    if (
        workflow_v8_contract.get("schema_id") != WORKFLOW_SCHEMA_V8_ID
        or workflow_v8_contract.get("result_schema_id") != RESULT_SCHEMA_V8_ID
        or workflow_v8_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V8_ID
    ):
        raise ContractError("manifest Python/ASGI v8 schema identities are unsupported")
    workflow_v8_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v8 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v8 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v8 schema"),
    )
    for path_key, digest_key, label in workflow_v8_schema_refs:
        _verify_digest_ref(
            workflow_v8_contract.get(path_key),
            workflow_v8_contract.get(digest_key),
            label,
        )
    api_workflow_contract = (
        unresolved.get("python_api_workflow") if isinstance(unresolved, dict) else None
    )
    if not isinstance(api_workflow_contract, dict):
        raise ContractError("manifest direct Python API workflow contract is missing")
    api_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API comparison schema",
        ),
        ("recipe_path", "recipe_sha256", "direct Python API workflow recipe"),
    )
    for path_key, digest_key, label in api_schema_refs:
        _verify_digest_ref(
            api_workflow_contract.get(path_key),
            api_workflow_contract.get(digest_key),
            label,
        )
    api_workflow_v2_contract = unresolved.get("python_api_workflow_v2")
    if not isinstance(api_workflow_v2_contract, dict):
        raise ContractError("manifest direct Python API v2 workflow contract is missing")
    if (
        api_workflow_v2_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V2_ID
        or api_workflow_v2_contract.get("result_schema_id") != API_RESULT_SCHEMA_V3_ID
        or api_workflow_v2_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V2_ID
    ):
        raise ContractError("manifest direct Python API v2 schema identities are unsupported")
    api_v2_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v2 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v3 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v2 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v2_schema_refs:
        _verify_digest_ref(
            api_workflow_v2_contract.get(path_key),
            api_workflow_v2_contract.get(digest_key),
            label,
        )
    api_workflow_v3_contract = unresolved.get("python_api_workflow_v3")
    if not isinstance(api_workflow_v3_contract, dict):
        raise ContractError("manifest direct Python API v3 workflow contract is missing")
    if (
        api_workflow_v3_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V3_ID
        or api_workflow_v3_contract.get("result_schema_id") != API_RESULT_SCHEMA_V4_ID
        or api_workflow_v3_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V3_ID
    ):
        raise ContractError("manifest direct Python API v3 schema identities are unsupported")
    api_v3_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v3 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v4 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v3 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v3_schema_refs:
        _verify_digest_ref(
            api_workflow_v3_contract.get(path_key),
            api_workflow_v3_contract.get(digest_key),
            label,
        )
    api_workflow_v4_contract = unresolved.get("python_api_workflow_v4")
    if not isinstance(api_workflow_v4_contract, dict):
        raise ContractError("manifest direct Python API v4 workflow contract is missing")
    if (
        api_workflow_v4_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V4_ID
        or api_workflow_v4_contract.get("result_schema_id") != API_RESULT_SCHEMA_V5_ID
        or api_workflow_v4_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V4_ID
    ):
        raise ContractError("manifest direct Python API v4 schema identities are unsupported")
    api_v4_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v4 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v5 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v4 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v4_schema_refs:
        _verify_digest_ref(
            api_workflow_v4_contract.get(path_key),
            api_workflow_v4_contract.get(digest_key),
            label,
        )
    asgi_workflow_contract = (
        unresolved.get("python_asgi_workflow") if isinstance(unresolved, dict) else None
    )
    workload = (
        asgi_workflow_contract.get("first_slice_workload")
        if isinstance(asgi_workflow_contract, dict)
        else None
    )
    if not isinstance(workload, dict):
        raise ContractError("manifest first-slice workload reference is missing")
    _verify_digest_ref(workload.get("path"), workload.get("sha256"), "first-slice workload")
    return manifest


def select_oracle_profile(
    manifest: dict[str, Any], extension_id: str | None = None
) -> dict[str, Any]:
    """Resolve a pinned package overlay while retaining the sole Starlette profile."""
    base = manifest["oracle_profile"]
    if extension_id is None:
        return base
    extension = manifest["oracle_profile_extensions"].get(extension_id)
    if extension is None:
        raise ContractError(f"unknown oracle package extension: {extension_id}")
    return {
        **base,
        "id": extension["id"],
        "packages": {**base["packages"], **extension["added_packages"]},
    }


def _verify_digest_ref(path_value: Any, digest_value: Any, label: str) -> None:
    if not isinstance(path_value, str) or not isinstance(digest_value, str):
        raise ContractError(f"manifest {label} path/digest reference is malformed")
    path = _resolve_repo_file(path_value, f"manifest {label}")
    if sha256_file(path) != digest_value:
        raise ContractError(f"manifest {label} digest is stale: {path_value}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_repo_file(value: str, label: str) -> Path:
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ContractError(f"{label} resolves outside the repository: {value}") from exc
    if not candidate.is_file():
        raise ContractError(f"{label} does not exist: {value}")
    return candidate


def _validate_json_pointer(pointer: str, context: str) -> None:
    for segment in pointer.split("/")[1:]:
        index = 0
        while index < len(segment):
            if segment[index] == "~":
                if index + 1 >= len(segment) or segment[index + 1] not in "01":
                    raise ContractError(f"{context} has an invalid RFC 6901 escape: {pointer}")
                index += 2
            else:
                index += 1


def _validate_unique_ids(rows: list[dict[str, Any]], key: str, context: str) -> None:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise ContractError(f"{context} contains duplicate {key} values")


def load_workflow(
    input_path: Path,
    *,
    source_root: Path | None = None,
) -> tuple[dict[str, Any], Path, str, Path]:
    """Load an input-only workflow and verify every local/source reference."""
    workflow_path = input_path if input_path.is_absolute() else ROOT / input_path
    workflow_path = workflow_path.resolve()
    try:
        workflow_path.relative_to(ROOT)
    except ValueError as exc:
        raise ContractError("workflow inputs must live inside the repository") from exc
    if not workflow_path.is_file():
        raise ContractError(f"workflow input does not exist: {workflow_path}")

    workflow = read_json(workflow_path)
    if not isinstance(workflow, dict):
        raise ContractError("workflow input must be a JSON object")
    workflow_schema_id = workflow.get("schema")
    schema_path = WORKFLOW_SCHEMAS.get(workflow_schema_id)
    if schema_path is None:
        raise ContractError(f"unsupported workflow schema: {workflow_schema_id!r}")

    schema = read_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema exposes several schema-specific exception types.
        raise ContractError(f"workflow schema is invalid: {exc}") from exc
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(workflow),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ContractError(f"workflow input does not match its schema: {details}")
    workload_path = _resolve_repo_file(workflow["workload"]["file"], "workload file")
    try:
        workload_path.relative_to((ROOT / "tests/fixtures/workloads").resolve())
    except ValueError as exc:
        raise ContractError("workflow workload must live under tests/fixtures/workloads") from exc
    _validate_unique_ids(workflow["cases"], "case_id", "workflow cases")
    for case in workflow["cases"]:
        if workflow_schema_id in {WORKFLOW_SCHEMA_V7_ID, WORKFLOW_SCHEMA_V8_ID}:
            try:
                mode = verification_mode(case)
            except FaultContractError as exc:
                raise ContractError(
                    f"invalid fault-contract case {case['case_id']}: {exc}"
                ) from exc
            if mode == "fault-contract":
                actions = case["actions"]
                if case["fault"]["contract"] in {
                    HTTP_REQUEST_FORM_PARSE_CONTRACT,
                    HTTP_REQUEST_JSON_DECODE_CONTRACT,
                }:
                    if (
                        len(actions) != 1
                        or actions[0]["kind"] != "http_request"
                        or not any(
                            observation["kind"] == "http_response"
                            and "status" in observation["selectors"]
                            for observation in actions[0]["observations"]
                        )
                    ):
                        raise ContractError(
                            "JSON body decode fault contract requires one status-observing "
                            "HTTP request"
                        )
                elif (
                    len(actions) < 2
                    or actions[0]["kind"] != "http_request"
                    or not any(
                        observation["kind"] == "application_error"
                        and observation["selector"] == "exception"
                        for observation in actions[0]["observations"]
                    )
                    or not any(
                        action["kind"] == "http_request"
                        and any(
                            observation["kind"] == "http_response"
                            and "status" in observation["selectors"]
                            for observation in action["observations"]
                        )
                        for action in actions[1:]
                    )
                ):
                    raise ContractError(
                        "fault-contract route recovery requires an initial HTTP application-error "
                        "observation followed by a status-observing HTTP request"
                    )
        if workflow_schema_id in {
            WORKFLOW_SCHEMA_ID,
            WORKFLOW_SCHEMA_V3_ID,
            WORKFLOW_SCHEMA_V4_ID,
            WORKFLOW_SCHEMA_V5_ID,
            WORKFLOW_SCHEMA_V6_ID,
            WORKFLOW_SCHEMA_V7_ID,
            WORKFLOW_SCHEMA_V8_ID,
        }:
            _validate_unique_ids(case["actions"], "action_id", f"actions in {case['case_id']}")
            if workflow_schema_id in {
                WORKFLOW_SCHEMA_V3_ID,
                WORKFLOW_SCHEMA_V4_ID,
                WORKFLOW_SCHEMA_V5_ID,
                WORKFLOW_SCHEMA_V6_ID,
                WORKFLOW_SCHEMA_V7_ID,
                WORKFLOW_SCHEMA_V8_ID,
            }:
                lifespan_positions = [
                    index
                    for index, action in enumerate(case["actions"])
                    if action["kind"] == "lifespan"
                ]
                if len(lifespan_positions) > 1:
                    raise ContractError(
                        f"case {case['case_id']} may contain only one lifespan action"
                    )
                if lifespan_positions and lifespan_positions[0] != 0:
                    raise ContractError(f"lifespan action must be first in case {case['case_id']}")
            for action in case["actions"]:
                if action["kind"] == "lifespan":
                    continue
                if workflow_schema_id == WORKFLOW_SCHEMA_V5_ID and action["kind"] == "http_request":
                    receive_mode = action.get("receive_mode")
                    timeout_present = "cancel_after_seconds" in action
                    has_cancellation_observation = any(
                        observation["kind"] == "asgi_cancellation"
                        for observation in action["observations"]
                    )
                    if receive_mode == "wait_until_cancelled" and not timeout_present:
                        raise ContractError(
                            "wait_until_cancelled requires a finite cancel_after_seconds timeout"
                        )
                    if timeout_present:
                        timeout = action["cancel_after_seconds"]
                        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                            raise ContractError(
                                "cancel_after_seconds must be a positive finite number"
                            )
                        try:
                            finite_timeout = math.isfinite(float(timeout))
                        except (OverflowError, ValueError):
                            finite_timeout = False
                        if not finite_timeout or float(timeout) <= 0:
                            raise ContractError(
                                "cancel_after_seconds must be a positive finite number"
                            )
                    if timeout_present and receive_mode != "wait_until_cancelled":
                        raise ContractError(
                            "cancel_after_seconds is permitted only with wait_until_cancelled"
                        )
                    if has_cancellation_observation and receive_mode != "wait_until_cancelled":
                        raise ContractError(
                            "asgi_cancellation observations require wait_until_cancelled"
                        )
                if (
                    action["kind"] == "websocket_session"
                    and action["receive_events"][-1]["type"] != "websocket.disconnect"
                ):
                    raise ContractError(
                        "WebSocket receive events must end with an explicit websocket.disconnect"
                    )
                if (
                    workflow_schema_id
                    in {WORKFLOW_SCHEMA_V6_ID, WORKFLOW_SCHEMA_V7_ID, WORKFLOW_SCHEMA_V8_ID}
                    and action["kind"] == "websocket_conversation"
                ):
                    sessions = {session["session_id"] for session in action["sessions"]}
                    if len(sessions) != len(action["sessions"]):
                        raise ContractError(
                            "WebSocket conversation session IDs must be unique in "
                            f"{case['case_id']}"
                        )
                    selectors = {
                        observation["selector"]
                        for observation in action["observations"]
                        if observation["kind"] == "websocket"
                    }
                    if selectors != {"event_order", "messages"}:
                        raise ContractError(
                            "WebSocket conversations must compare both event_order and messages"
                        )
                    received_sessions = {
                        step["session_id"]
                        for step in action["steps"]
                        if step["kind"] == "receive_next"
                    }
                    if received_sessions != sessions:
                        raise ContractError(
                            "WebSocket conversations must receive an observable event from each "
                            "session"
                        )
                    states = {session_id: "new" for session_id in sessions}
                    for step in action["steps"]:
                        session_id = step["session_id"]
                        if session_id not in states:
                            raise ContractError(
                                "WebSocket conversation step references unknown session "
                                f"{session_id!r}"
                            )
                        state = states[session_id]
                        kind = step["kind"]
                        if kind == "connect":
                            if state != "new":
                                raise ContractError(
                                    f"WebSocket session {session_id!r} connects more than once "
                                    "or after activity"
                                )
                            states[session_id] = "connected"
                        elif kind == "disconnect":
                            if state != "connected":
                                raise ContractError(
                                    f"WebSocket session {session_id!r} disconnects outside "
                                    "its active interval"
                                )
                            states[session_id] = "closed"
                        elif state != "connected":
                            raise ContractError(
                                f"WebSocket session {session_id!r} has activity before "
                                "connect or after disconnect"
                            )
                    incomplete = sorted(
                        session_id for session_id, state in states.items() if state != "closed"
                    )
                    if incomplete:
                        raise ContractError(
                            "WebSocket conversation sessions must each connect and disconnect: "
                            + ", ".join(incomplete)
                        )
                for observation in action["observations"]:
                    if observation["kind"] == "openapi":
                        for pointer in observation["json_pointers"]:
                            _validate_json_pointer(
                                pointer, f"{case['case_id']}:{action['action_id']}"
                            )
        elif workflow_schema_id in API_WORKFLOW_SCHEMA_IDS:
            _validate_unique_ids(case["probes"], "probe_id", f"probes in {case['case_id']}")

        if source_root is not None:
            for evidence in case["source_evidence"]:
                source_path = (source_root / evidence["path"]).resolve()
                try:
                    source_path.relative_to(source_root.resolve())
                except ValueError as exc:
                    raise ContractError(
                        "source evidence resolves outside the pinned source tree: "
                        f"{evidence['path']}"
                    ) from exc
                if not source_path.is_file():
                    raise ContractError(f"source evidence does not exist: {evidence['path']}")
                if workflow_schema_id in API_WORKFLOW_SCHEMA_IDS:
                    if sha256_file(source_path) != evidence["sha256"]:
                        raise ContractError(
                            f"direct API source evidence digest is stale: {evidence['path']}"
                        )

    return workflow, workflow_path, sha256_file(workflow_path), workload_path
