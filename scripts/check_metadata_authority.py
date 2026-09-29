#!/usr/bin/env python3
"""Check the human-maintained API source authority against its generated records."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "metadata.yaml"
STARLETTE_RS_ROOT_OVERRIDE: Path | None = None


class MetadataError(ValueError):
    """Raised when authority metadata and its referenced records disagree."""


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise MetadataError(f"cannot read YAML {relative(path)}: {exc}") from exc
    if not isinstance(value, dict):
        raise MetadataError(f"expected a YAML mapping in {relative(path)}")
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MetadataError(f"cannot read JSON {relative(path)}: {exc}") from exc
    if not isinstance(value, dict):
        raise MetadataError(f"expected a JSON object in {relative(path)}")
    return value


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def pointer(document: Any, location: str, label: str) -> Any:
    if location == "":
        return document
    if not location.startswith("/"):
        raise MetadataError(f"{label}: JSON Pointer must start with '/': {location!r}")
    value = document
    for raw_token in location[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(value, list):
                value = value[int(token)]
            elif isinstance(value, dict):
                value = value[token]
            else:
                raise KeyError(token)
        except (IndexError, KeyError, ValueError) as exc:
            raise MetadataError(f"{label}: JSON Pointer {location!r} does not resolve") from exc
    return value


def artifact_path(path_text: str) -> Path:
    relative_path = Path(path_text)
    if STARLETTE_RS_ROOT_OVERRIDE is not None and relative_path.parts[:2] == ("..", "starlette-rs"):
        path = STARLETTE_RS_ROOT_OVERRIDE.joinpath(*relative_path.parts[2:]).resolve()
    else:
        path = (ROOT / relative_path).resolve()
    if not path.is_file():
        raise MetadataError(f"referenced artifact is missing: {path_text}")
    return path


def require_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise MetadataError(f"{label}: expected {expected!r}, found {actual!r}")


def validate_digest(path: Path, manifest_entry: dict[str, Any], label: str) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    require_equal(f"{label} manifest SHA-256", manifest_entry.get("sha256"), digest)


def validate_generator(
    inventory_meta: dict[str, Any], source: dict[str, Any], inventory: dict[str, Any]
) -> None:
    generator_path = artifact_path(inventory_meta["generator"])
    tree = ast.parse(
        generator_path.read_text(encoding="utf-8"), filename=inventory_meta["generator"]
    )
    constants: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    constants[target.id] = node.value.value
    for name, expected in (
        ("EXPECTED_VERSION", source["version"]),
        ("EXPECTED_TAG", source["tag"]),
        ("EXPECTED_COMMIT", source["commit"]),
        ("SCHEMA", inventory_meta["schema"]),
    ):
        require_equal(f"{inventory_meta['generator']}:{name}", constants.get(name), expected)
    require_equal(
        "inventory generator output schema", inventory.get("schema"), inventory_meta["schema"]
    )


def validate_count_pointers(
    metadata: dict[str, Any], artifact: dict[str, Any], manifest: dict[str, Any], label: str
) -> dict[str, int]:
    values: dict[str, int] = {}
    for name, refs in metadata.items():
        artifact_value = pointer(artifact, refs["artifact"], f"{label}.{name}.artifact")
        manifest_value = pointer(manifest, refs["manifest"], f"{label}.{name}.manifest")
        if not isinstance(artifact_value, int) or isinstance(artifact_value, bool):
            raise MetadataError(f"{label}.{name}: artifact count is not an integer")
        require_equal(f"{label}.{name} count", artifact_value, manifest_value)
        values[name] = artifact_value
    return values


def canonical_repository(value: str) -> str:
    value = value.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    elif value.startswith("ssh://git@github.com/"):
        value = "https://github.com/" + value.removeprefix("ssh://git@github.com/")
    elif "//" not in value and value.count("/") == 1:
        value = "https://github.com/" + value
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/")


def git_value(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *arguments], text=True, stderr=subprocess.PIPE
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise MetadataError(f"cannot inspect pinned source checkout {root}: {detail}") from exc


def validate_pinned_source_checkout(label: str, root: Path, expected: dict[str, str]) -> None:
    require_equal(
        f"{label} checkout commit",
        git_value(root, "rev-parse", "HEAD"),
        expected["commit"],
    )
    remote = git_value(root, "remote", "get-url", "origin")
    require_equal(
        f"{label} checkout repository",
        canonical_repository(remote),
        canonical_repository(expected["repository"]),
    )


def validate_ci_source_checkouts(metadata: dict[str, Any]) -> None:
    workflow_path = ROOT / ".github/workflows/ci.yml"
    workflow = load_yaml(workflow_path)
    steps = workflow["jobs"]["verify"]["steps"]
    checkouts: dict[str, dict[str, Any]] = {}
    for step in steps:
        settings = step.get("with", {})
        path = settings.get("path")
        if path:
            checkouts[path] = settings

    authority = metadata["authority"]
    fastapi = authority["source"] if "source" in authority else authority
    expected = {
        "fastapi": {
            "repository": fastapi["repository"],
            "commit": fastapi["commit"],
        },
        "starlette": {
            "repository": authority["starlette"]["repository"],
            "commit": authority["starlette"]["commit"],
        },
        "starlette-rs": {
            "repository": metadata["starlette_rs"]["repository"],
            "commit": metadata["starlette_rs"]["commit"],
        },
    }
    for path, identity in expected.items():
        settings = checkouts.get(path)
        if settings is None:
            raise MetadataError(f"CI must checkout {path} for pinned source validation")
        require_equal(
            f"CI {path} repository",
            canonical_repository(settings.get("repository", "")),
            canonical_repository(identity["repository"]),
        )
        require_equal(f"CI {path} revision", settings.get("ref"), identity["commit"])
    if checkouts.get("fastapi-rs", {}).get("path") != "fastapi-rs":
        raise MetadataError("CI must checkout the project under fastapi-rs beside its sources")


def validate() -> None:
    metadata = load_yaml(METADATA_PATH)
    require_equal("metadata schema", metadata.get("schema"), "fastapi-rs/api-source-authority@1")

    manifest_meta = metadata["manifest"]
    manifest_path = artifact_path(manifest_meta["path"])
    manifest = load_yaml(manifest_path)
    authority = metadata["authority"]
    fastapi = authority["source"] if "source" in authority else authority
    starlette = authority["starlette"]
    starlette_rs = metadata["starlette_rs"]
    validate_ci_source_checkouts(metadata)
    validate_pinned_source_checkout("FastAPI", (ROOT / fastapi["checkout"]).resolve(), fastapi)
    validate_pinned_source_checkout(
        "Starlette", (ROOT / starlette["checkout"]).resolve(), starlette
    )
    starlette_rs_root = STARLETTE_RS_ROOT_OVERRIDE or (ROOT / starlette_rs["owner"]).resolve()
    validate_pinned_source_checkout("Starlette-RS", starlette_rs_root, starlette_rs)

    selected_fastapi = pointer(
        manifest, manifest_meta["fastapi_identity_pointer"], "manifest FastAPI identity"
    )
    for field in ("repository", "version", "tag", "commit"):
        require_equal(f"FastAPI identity {field}", fastapi[field], selected_fastapi[field])
    selected_starlette = pointer(
        manifest, manifest_meta["starlette_identity_pointer"], "manifest Starlette identity"
    )
    for field in ("repository", "version", "commit"):
        require_equal(f"Starlette identity {field}", starlette[field], selected_starlette[field])
    require_equal(
        "selected Starlette contract role",
        selected_starlette["role"],
        "sole-selected-starlette-contract",
    )
    pydantic = authority["pydantic"]
    selected_pydantic = pointer(
        manifest, manifest_meta["pydantic_identity_pointer"], "manifest Pydantic identity"
    )
    for field, manifest_field in (
        ("version", "version"),
        ("pydantic_core_version", "pydantic_core_version"),
        ("source_lock_version", "source_lock_version"),
    ):
        require_equal(
            f"Pydantic identity {field}", pydantic[field], selected_pydantic[manifest_field]
        )

    python_contract = manifest["selected_contracts"]["python"]
    require_equal(
        "Python floor", authority["python"]["requires"], python_contract["package_requirement"]
    )
    require_equal(
        "oracle Python profile",
        authority["python"]["oracle"],
        manifest["oracle_profile"]["python"],
    )
    oracle_packages = manifest["oracle_profile"]["packages"]
    for package, expected in (
        ("fastapi", fastapi["version"]),
        ("starlette", starlette["version"]),
        ("pydantic", pydantic["version"]),
        ("pydantic-core", pydantic["pydantic_core_version"]),
    ):
        require_equal(f"oracle package {package}", oracle_packages[package], expected)

    inventory_meta = metadata["api_inventory"]
    inventory_path = artifact_path(inventory_meta["artifact"])
    inventory = load_json(inventory_path)
    manifest_inventory = manifest["source_artifacts"]["api_inventory"]
    expected_command = (
        f"python {inventory_meta['generator']} {authority['checkout']} "
        f"--output {inventory_meta['artifact']}"
    )
    require_equal("inventory generator command", inventory_meta["command"], expected_command)
    require_equal("inventory artifact path", inventory_meta["artifact"], manifest_inventory["path"])
    require_equal("inventory schema", inventory_meta["schema"], manifest_inventory["schema"])
    require_equal("inventory schema", inventory.get("schema"), inventory_meta["schema"])
    validate_digest(inventory_path, manifest_inventory, "API inventory")
    source_lock = authority["upstream_source_lock"]
    expected_source_identity = {
        "repository": fastapi["repository"],
        "tag": fastapi["tag"],
        "commit": fastapi["commit"],
        "package_version": fastapi["version"],
        "python_requirement": authority["python"]["requires"],
        "lockfile": source_lock["file"],
        "locked_components": source_lock["components"],
    }
    require_equal(
        "inventory source identity",
        pointer(inventory, inventory_meta["source_identity_pointer"], "inventory identity"),
        expected_source_identity,
    )
    source_identity = inventory["source_identity"]
    require_equal(
        "FastAPI upstream-lock Pydantic version",
        pointer(source_identity, "/locked_components/pydantic", "inventory Pydantic lock"),
        pydantic["source_lock_version"],
    )
    require_equal(
        "FastAPI upstream-lock provenance",
        manifest["source_provenance"]["fastapi_upstream_lock"]["starlette_version"],
        source_lock["components"]["starlette"],
    )
    validate_generator(inventory_meta, fastapi, inventory)
    inventory_counts = validate_count_pointers(
        inventory_meta["count_pointers"], inventory, manifest, "API inventory"
    )
    derived_inventory_counts = {
        "root_exports": len(
            pointer(inventory, inventory_meta["source_pointers"]["root_exports"], "root exports")
        ),
        "documented_targets": len(
            pointer(
                inventory,
                inventory_meta["source_pointers"]["documented_targets"],
                "documented targets",
            )
        ),
        "python_source_modules": len(
            pointer(
                inventory,
                inventory_meta["source_pointers"]["modules_and_definitions"],
                "inventory modules",
            )
        ),
        "import_bindings": len(
            pointer(
                inventory,
                inventory_meta["source_pointers"]["import_bindings_and_aliases"],
                "inventory imports",
            )
        ),
        "source_deprecations": len(
            pointer(
                inventory,
                inventory_meta["source_pointers"]["source_deprecations"],
                "inventory deprecations",
            )
        ),
    }
    for name, expected in derived_inventory_counts.items():
        require_equal(f"API inventory derived {name}", inventory_counts[name], expected)

    atlas_meta = metadata["classification_atlas"]
    atlas_path = artifact_path(atlas_meta["artifact"])
    atlas = load_json(atlas_path)
    manifest_atlas = manifest["source_artifacts"]["compatibility_atlas"]
    require_equal("atlas artifact path", atlas_meta["artifact"], manifest_atlas["path"])
    require_equal("atlas schema", atlas_meta["schema"], manifest_atlas["schema"])
    require_equal("atlas schema", atlas.get("schema"), atlas_meta["schema"])
    validate_digest(atlas_path, manifest_atlas, "classification atlas")

    import_binding_meta = metadata["import_binding_classification_review"]
    import_binding_path = artifact_path(import_binding_meta["artifact"])
    import_binding_review = load_json(import_binding_path)
    manifest_import_binding = manifest["source_artifacts"][
        "api_import_binding_classification_review"
    ]
    require_equal(
        "import-binding review artifact path",
        import_binding_meta["artifact"],
        manifest_import_binding["path"],
    )
    require_equal(
        "import-binding review schema",
        import_binding_meta["schema"],
        manifest_import_binding["schema"],
    )
    require_equal(
        "import-binding review schema",
        import_binding_review.get("schema"),
        import_binding_meta["schema"],
    )
    validate_digest(import_binding_path, manifest_import_binding, "import-binding review")
    expected_import_binding_identity = {
        "package": "FastAPI",
        "version": fastapi["version"],
        "source_commit": fastapi["commit"],
        "selected_starlette_profile": starlette["version"],
        "starlette_source_commit": starlette["commit"],
        "starlette_rs_contract_commit": metadata["starlette_rs"]["commit"],
    }
    require_equal(
        "import-binding review source identity",
        import_binding_review.get("source_identity"),
        expected_import_binding_identity,
    )
    require_equal(
        "metadata import-binding review source identity",
        import_binding_meta["source_identity"],
        expected_import_binding_identity,
    )
    require_equal(
        "manifest import-binding review source identity",
        manifest_import_binding["source_identity"],
        expected_import_binding_identity,
    )
    import_binding_scope = import_binding_review.get("scope", {})
    import_binding_recommendations = import_binding_scope.get("recommendation_counts", {})
    expected_import_binding_counts = {
        "candidates": import_binding_scope.get("candidate_count"),
        "supported": import_binding_recommendations.get("supported"),
        "private_or_internal": import_binding_recommendations.get("private/internal"),
        "uncertain": import_binding_recommendations.get("uncertain"),
        "starlette_rs_reviewed_candidates": import_binding_scope.get(
            "starlette_rs_reviewed_candidate_count"
        ),
        "starlette_rs_unreviewed_unique_targets": import_binding_scope.get(
            "starlette_rs_unreviewed_unique_target_count"
        ),
    }
    require_equal(
        "metadata import-binding review counts",
        import_binding_meta["counts"],
        expected_import_binding_counts,
    )
    require_equal(
        "manifest import-binding review counts",
        manifest_import_binding["counts"],
        expected_import_binding_counts,
    )
    require_equal(
        "metadata import-binding candidate ID digest",
        import_binding_meta["candidate_ids_sha256"],
        import_binding_scope.get("candidate_ids_sha256"),
    )
    require_equal(
        "manifest import-binding candidate ID digest",
        manifest_import_binding["candidate_ids_sha256"],
        import_binding_scope.get("candidate_ids_sha256"),
    )
    pinned_starlette_rs_sources = import_binding_review.get("pinned_starlette_rs_sources", {})
    require_equal(
        "metadata Starlette-RS contract id",
        import_binding_meta["starlette_rs_contract_id"],
        pinned_starlette_rs_sources.get("contract_id"),
    )
    require_equal(
        "manifest Starlette-RS contract id",
        manifest_import_binding["starlette_rs_contract_id"],
        pinned_starlette_rs_sources.get("contract_id"),
    )
    expected_pinned_source_digests = {
        f"{name}_sha256": pinned_starlette_rs_sources.get("files", {}).get(name, {}).get("sha256")
        for name in ("metadata", "manifest", "api_catalog", "api_review")
    }
    require_equal(
        "metadata pinned Starlette-RS evidence digests",
        import_binding_meta["pinned_starlette_rs_sources"],
        expected_pinned_source_digests,
    )
    require_equal(
        "manifest pinned Starlette-RS evidence digests",
        manifest_import_binding["pinned_starlette_rs_sources"],
        expected_pinned_source_digests,
    )

    atlas_fastapi = pointer(atlas, "/authorities/fastapi", "atlas FastAPI authority")
    for field in ("repository", "version", "commit"):
        require_equal(f"atlas FastAPI identity {field}", atlas_fastapi[field], fastapi[field])
    require_equal(
        "atlas inventory path", atlas_fastapi["inventory_path"], inventory_meta["artifact"]
    )
    candidates = pointer(atlas, atlas_meta["candidates_pointer"], "atlas API candidates")
    if not isinstance(candidates, list):
        raise MetadataError("atlas candidate pointer must resolve to a list")
    import_binding_link = atlas.get("api_import_binding_classification_review")
    for atlas_key, review_key in (("path", "path"), ("schema", "schema"), ("sha256", "sha256")):
        require_equal(
            f"atlas import-binding review {atlas_key}",
            import_binding_link.get(atlas_key) if isinstance(import_binding_link, dict) else None,
            manifest_import_binding[review_key],
        )
    require_equal(
        "atlas import-binding review source identity",
        import_binding_link.get("source_identity")
        if isinstance(import_binding_link, dict)
        else None,
        expected_import_binding_identity,
    )
    require_equal(
        "atlas import-binding review scope",
        import_binding_link.get("scope") if isinstance(import_binding_link, dict) else None,
        import_binding_scope,
    )
    require_equal(
        "atlas pinned Starlette-RS source evidence",
        import_binding_link.get("pinned_starlette_rs_sources")
        if isinstance(import_binding_link, dict)
        else None,
        pinned_starlette_rs_sources,
    )
    candidates_by_id = {candidate.get("id"): candidate for candidate in candidates}
    import_binding_rows = import_binding_review.get("rows", [])
    reviewed_import_binding_ids = {row.get("id") for row in import_binding_rows}
    if len(reviewed_import_binding_ids) != len(import_binding_rows):
        raise MetadataError("import-binding review candidate IDs are not unique")
    for row in import_binding_rows:
        candidate = candidates_by_id.get(row.get("id"))
        if candidate is None:
            raise MetadataError("import-binding review candidate is absent from the atlas")
        require_equal(
            f"atlas import-binding classification {row['id']}",
            candidate.get("classification"),
            row.get("recommendation"),
        )
        require_equal(
            f"atlas import-binding binding identity {row['id']}",
            {
                "module": candidate.get("imported_module"),
                "name": candidate.get("imported_name"),
                "target": candidate.get("target_path"),
            },
            row.get("binding"),
        )
    reviewed_starlette_import_ids = {
        candidate.get("id")
        for candidate in candidates
        if candidate.get("kind") == "import_binding"
        and (candidate.get("imported_module") or "").startswith("starlette")
        and candidate.get("id") in reviewed_import_binding_ids
    }
    require_equal(
        "Starlette import-binding review exact denominator",
        reviewed_starlette_import_ids,
        reviewed_import_binding_ids,
    )

    callable_review_artifact = manifest["source_artifacts"]["api_classification_review"]
    callable_review = load_json(artifact_path(callable_review_artifact["path"]))
    callable_review_rows = callable_review.get("rows", [])
    callable_uncertain_ids = {
        row.get("id") for row in callable_review_rows if row.get("recommendation") == "uncertain"
    }
    require_equal("retained uncertain callable denominator", len(callable_uncertain_ids), 18)
    for row in callable_review_rows:
        candidate = candidates_by_id.get(row.get("id"))
        if candidate is None:
            raise MetadataError("callable review candidate is absent from the atlas")
        require_equal(
            f"atlas callable classification {row['id']}",
            candidate.get("classification"),
            row.get("recommendation"),
        )

    classification_policy = pointer(
        atlas, atlas_meta["policy_pointer"], "atlas classification policy"
    )
    if classification_policy.get("source_inventory_is_not_runtime_reflection") is not True:
        raise MetadataError("atlas must distinguish its source inventory from runtime reflection")
    classifications = Counter(
        pointer(candidate, atlas_meta["classification_pointer"], "candidate classification")
        for candidate in candidates
    )
    expected_classes = set(atlas_meta["classifications"])
    actual_classes = set(classifications)
    require_equal("classification labels", actual_classes, expected_classes)
    require_equal(
        "classification policy labels",
        set(classification_policy),
        expected_classes | {"source_inventory_is_not_runtime_reflection"},
    )
    atlas_counts = validate_count_pointers(
        atlas_meta["count_pointers"], atlas, manifest, "classification atlas"
    )
    require_equal("atlas candidate count", atlas_counts["api_candidates"], len(candidates))
    for name, expected in classifications.items():
        count_name = "private_or_internal" if name == "private/internal" else name
        require_equal(f"atlas {name} candidate count", atlas_counts[count_name], expected)
    for name, location in atlas_meta["section_pointers"].items():
        section = pointer(atlas, location, f"atlas section {name}")
        if not isinstance(section, list):
            raise MetadataError(f"atlas section {name} must resolve to a list")

    pydantic_authority = pointer(atlas, "/authorities/pydantic", "atlas Pydantic authority")
    require_equal(
        "atlas Pydantic version", pydantic_authority["selected_version"], pydantic["version"]
    )
    require_equal(
        "atlas Pydantic source-lock version",
        pydantic_authority["source_lock_version"],
        pydantic["source_lock_version"],
    )
    starlette_authority = pointer(atlas, "/authorities/starlette", "atlas Starlette authority")
    for field in ("version", "commit"):
        require_equal(
            f"atlas Starlette identity {field}", starlette_authority[field], starlette[field]
        )

    sibling = metadata["starlette_rs"]
    require_equal(
        "Starlette-RS distribution version",
        manifest["target"]["starlette_rs_distribution"]["version"],
        sibling["distribution_version"],
    )
    require_equal(
        "Starlette-RS pinned source commit",
        manifest["target"]["starlette_rs_distribution"]["commit"],
        sibling["commit"],
    )
    sibling_manifest = load_yaml(artifact_path(sibling["manifest"]))
    sibling_metadata = load_yaml(artifact_path(sibling["metadata"]))
    sibling_atlas_authority = pointer(
        atlas, "/authorities/starlette_rs", "atlas Starlette-RS authority"
    )
    require_equal(
        "atlas Starlette-RS project revision",
        sibling_atlas_authority["implementation_revision"],
        sibling["commit"],
    )
    sibling_digest_fields = {
        "manifest": "manifest_sha256",
        "api_catalog": "api_surface_catalog_sha256",
        "api_review": "api_review_sha256",
        "coverage_matrix": "coverage_matrix_sha256",
    }
    for name, digest_field in sibling_digest_fields.items():
        sibling_artifact = artifact_path(sibling[name])
        require_equal(
            f"atlas Starlette-RS {name} digest",
            sibling_atlas_authority[digest_field],
            hashlib.sha256(sibling_artifact.read_bytes()).hexdigest(),
        )
    require_equal(
        "Starlette-RS contract id",
        pointer(sibling_manifest, sibling["manifest_contract_pointer"], "sibling contract id"),
        sibling["contract_id"],
    )
    require_equal(
        "Starlette-RS contract source revision",
        pointer(
            sibling_manifest, sibling["manifest_revision_pointer"], "sibling manifest revision"
        ),
        starlette["commit"],
    )
    require_equal(
        "Starlette-RS metadata source revision",
        pointer(
            sibling_metadata, sibling["metadata_revision_pointer"], "sibling metadata revision"
        ),
        starlette["commit"],
    )
    require_equal(
        "Starlette-RS manifest source revision",
        sibling_manifest["scope"]["inventory"]["revision"],
        sibling_metadata["authority"]["revision"],
    )

    api_contract_check = subprocess.run(
        [sys.executable, "-m", "scripts.build_api_surface_contract", "--check"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if api_contract_check.returncode:
        details = "\n".join(
            part
            for part in (
                api_contract_check.stdout.strip(),
                api_contract_check.stderr.strip(),
            )
            if part
        )
        raise MetadataError(
            "manifest API contract, including reviewed metadata overlays, is stale or invalid"
            + (f":\n{details}" if details else "")
        )

    print(
        "metadata authority valid: "
        f"FastAPI {fastapi['version']} ({len(candidates)} classified candidates), "
        f"Starlette {starlette['version']} sole contract, "
        f"{inventory_counts['root_exports']} root exports"
    )


def main() -> int:
    global STARLETTE_RS_ROOT_OVERRIDE
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--starlette-rs-source",
        type=Path,
        help="use a clean Starlette-RS checkout, such as the contract-pinned source clone",
    )
    args = parser.parse_args()
    if args.starlette_rs_source is not None:
        STARLETTE_RS_ROOT_OVERRIDE = args.starlette_rs_source.resolve()
    try:
        validate()
    except (KeyError, TypeError, MetadataError) as exc:
        raise SystemExit(f"metadata authority check failed: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
