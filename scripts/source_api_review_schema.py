"""Strict structural validation for the reviewed FastAPI source API overlay."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import PurePosixPath
from typing import Any

SOURCE_API_REVIEW_SCHEMA = "fastapi-rs/source-api-classification-review@2"
SOURCE_API_RECOMMENDATIONS = {"supported", "private/internal", "uncertain"}
SOURCE_API_CANDIDATE_KINDS = {"field", "import_binding", "value"}
SOURCE_API_EVIDENCE_BASIS = {
    "documented",
    "implementation-only",
    "member-exposure-unresolved",
    "source-declaration",
}
SOURCE_API_EVIDENCE_ROLES = {
    "fastapi-implementation-use",
    "fastapi-public-documentation",
    "fastapi-source-binding",
    "fastapi-source-class-documentation",
    "fastapi-source-declaration",
    "fastapi-source-field",
    "fastapi-source-member",
}
SOURCE_API_SELECTION_KEYS = {
    "uncertain_candidate_ids",
    "uncertain_candidate_id_prefixes",
    "uncertain_imported_modules",
}


class SourceApiReviewSchemaError(ValueError):
    """Raised when a source API review does not match its closed schema."""


def _require_exact_keys(
    value: Any,
    required: set[str],
    label: str,
    *,
    optional: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SourceApiReviewSchemaError(f"{label} must be an object")
    allowed = required | (optional or set())
    actual = set(value)
    missing = required - actual
    unknown = actual - allowed
    if missing or unknown:
        details = []
        if missing:
            details.append("missing=" + ",".join(sorted(missing)))
        if unknown:
            details.append("unknown=" + ",".join(sorted(unknown)))
        raise SourceApiReviewSchemaError(f"{label} has invalid keys ({'; '.join(details)})")
    return value


def _require_strings(value: Any, label: str, *, nonempty: bool = True) -> list[str]:
    if not isinstance(value, list) or not value:
        raise SourceApiReviewSchemaError(f"{label} must be a non-empty array")
    if any(not isinstance(item, str) or (nonempty and not item.strip()) for item in value):
        raise SourceApiReviewSchemaError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise SourceApiReviewSchemaError(f"{label} must not contain duplicates")
    return value


def _require_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SourceApiReviewSchemaError(f"{label} must be a non-empty relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise SourceApiReviewSchemaError(f"{label} must remain within the pinned source tree")
    return value


def _require_line(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise SourceApiReviewSchemaError(f"{label} must be a positive integer")
    return value


def validate_source_api_selection(selection: Any) -> dict[str, list[str]]:
    """Validate the selection policy stored in metadata.yaml."""
    selected = _require_exact_keys(selection, SOURCE_API_SELECTION_KEYS, "source API selection")
    return {
        "uncertain_candidate_ids": _require_strings(
            selected["uncertain_candidate_ids"],
            "source API selected candidate IDs",
        ),
        "uncertain_imported_modules": _require_strings(
            selected["uncertain_imported_modules"],
            "source API selected imported modules",
        ),
        "uncertain_candidate_id_prefixes": _require_strings(
            selected["uncertain_candidate_id_prefixes"],
            "source API selected candidate prefixes",
        ),
    }


def validate_source_api_review_schema(
    review: Any,
    *,
    expected_identity: dict[str, str],
    expected_selection: dict[str, list[str]],
) -> dict[str, Any]:
    """Validate every key, enum, and summary in a source API review artifact."""
    review = _require_exact_keys(
        review,
        {"rows", "schema", "scope", "source_identity"},
        "source API review",
    )
    if review["schema"] != SOURCE_API_REVIEW_SCHEMA:
        raise SourceApiReviewSchemaError("source API review has an unsupported schema")
    identity = _require_exact_keys(
        review["source_identity"],
        {"package", "source_commit", "version"},
        "source API review identity",
    )
    if identity != expected_identity:
        raise SourceApiReviewSchemaError("source API review has the wrong FastAPI identity")

    scope = _require_exact_keys(
        review["scope"],
        {"candidate_count", "candidate_ids_sha256", "recommendation_counts", "selection"},
        "source API review scope",
    )
    selection = validate_source_api_selection(scope["selection"])
    if selection != expected_selection:
        raise SourceApiReviewSchemaError("source API review selection differs from metadata.yaml")
    count = scope["candidate_count"]
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise SourceApiReviewSchemaError("source API review candidate count must be positive")
    ids_digest = scope["candidate_ids_sha256"]
    if not isinstance(ids_digest, str) or re.fullmatch(r"[0-9a-f]{64}", ids_digest) is None:
        raise SourceApiReviewSchemaError("source API review candidate ID digest is malformed")

    rows = review["rows"]
    if not isinstance(rows, list) or not rows:
        raise SourceApiReviewSchemaError("source API review has no rows")
    identifiers: list[str] = []
    counts: Counter[str] = Counter()
    for index, raw_row in enumerate(rows):
        label = f"source API review row {index}"
        if not isinstance(raw_row, dict):
            raise SourceApiReviewSchemaError(f"{label} must be an object")
        candidate_kind = raw_row.get("candidate_kind")
        if not isinstance(candidate_kind, str) or candidate_kind not in SOURCE_API_CANDIDATE_KINDS:
            raise SourceApiReviewSchemaError(f"{label} has an unsupported candidate kind")
        row_keys = {
            "candidate_kind",
            "evidence",
            "evidence_basis",
            "id",
            "reason",
            "recommendation",
            "source",
        }
        if candidate_kind == "import_binding":
            row_keys.add("binding")
        row = _require_exact_keys(raw_row, row_keys, label)
        identifier = row["id"]
        if not isinstance(identifier, str) or not identifier.strip():
            raise SourceApiReviewSchemaError(f"{label} ID must be a non-empty string")
        identifiers.append(identifier)
        recommendation = row["recommendation"]
        if not isinstance(recommendation, str) or recommendation not in SOURCE_API_RECOMMENDATIONS:
            raise SourceApiReviewSchemaError(f"{label} has an unsupported recommendation")
        counts[recommendation] += 1

        reason = row["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise SourceApiReviewSchemaError(f"{label} reason must be a non-empty string")
        source = _require_exact_keys(row["source"], {"line", "path"}, f"{label} source")
        _require_relative_path(source["path"], f"{label} source path")
        _require_line(source["line"], f"{label} source line")

        if candidate_kind == "import_binding":
            raw_binding = row["binding"]
            if not isinstance(raw_binding, dict):
                raise SourceApiReviewSchemaError(f"{label} binding must be an object")
            if "form" not in raw_binding:
                # Keep the original compact representation for ImportFrom aliases.
                binding = _require_exact_keys(
                    raw_binding,
                    {"module", "name", "target"},
                    f"{label} from-import binding",
                )
                if any(
                    not isinstance(binding[key], str) or not binding[key].strip()
                    for key in ("module", "name", "target")
                ):
                    raise SourceApiReviewSchemaError(
                        f"{label} from-import binding values must be non-empty strings"
                    )
            else:
                binding = _require_exact_keys(
                    raw_binding,
                    {"as_name", "form", "level", "local_name", "module", "name", "target"},
                    f"{label} import binding",
                )
                if binding["form"] != "import":
                    raise SourceApiReviewSchemaError(
                        f"{label} binding has an unsupported import form"
                    )
                if not isinstance(binding["module"], str) or not binding["module"].strip():
                    raise SourceApiReviewSchemaError(
                        f"{label} import module must be a non-empty string"
                    )
                if binding["name"] is not None:
                    raise SourceApiReviewSchemaError(f"{label} plain import name must be null")
                if binding["as_name"] is not None and (
                    not isinstance(binding["as_name"], str) or not binding["as_name"].strip()
                ):
                    raise SourceApiReviewSchemaError(
                        f"{label} plain import alias must be a non-empty string or null"
                    )
                if (
                    not isinstance(binding["level"], int)
                    or isinstance(binding["level"], bool)
                    or binding["level"] != 0
                ):
                    raise SourceApiReviewSchemaError(f"{label} plain import level must be zero")
                for key in ("local_name", "target"):
                    if not isinstance(binding[key], str) or not binding[key].strip():
                        raise SourceApiReviewSchemaError(
                            f"{label} import binding {key} must be a non-empty string"
                        )

        basis = _require_strings(row["evidence_basis"], f"{label} evidence basis")
        if set(basis) - SOURCE_API_EVIDENCE_BASIS:
            raise SourceApiReviewSchemaError(f"{label} has an unsupported evidence basis")
        evidence = row["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise SourceApiReviewSchemaError(f"{label} evidence must be a non-empty array")
        evidence_roles: set[str] = set()
        has_public_documentation = False
        for evidence_index, raw_reference in enumerate(evidence):
            ref_label = f"{label} evidence {evidence_index}"
            reference = _require_exact_keys(
                raw_reference,
                {"line", "path", "role"},
                ref_label,
                optional={"end_line"},
            )
            path = _require_relative_path(reference["path"], f"{ref_label} path")
            line = _require_line(reference["line"], f"{ref_label} line")
            end_line = (
                _require_line(reference["end_line"], f"{ref_label} end_line")
                if "end_line" in reference
                else line
            )
            if end_line < line:
                raise SourceApiReviewSchemaError(f"{ref_label} range ends before it starts")
            role = reference["role"]
            if not isinstance(role, str) or role not in SOURCE_API_EVIDENCE_ROLES:
                raise SourceApiReviewSchemaError(f"{ref_label} has an unsupported evidence role")
            evidence_roles.add(role)
            has_public_documentation |= role == "fastapi-public-documentation" and path.startswith(
                "docs/en/docs/"
            )

        if recommendation == "supported" and (
            "documented" not in basis or not has_public_documentation
        ):
            raise SourceApiReviewSchemaError(
                f"{label} supported disposition lacks public documentation evidence"
            )
        if recommendation == "private/internal" and (
            "implementation-only" not in basis or "fastapi-implementation-use" not in evidence_roles
        ):
            raise SourceApiReviewSchemaError(
                f"{label} internal disposition lacks implementation evidence"
            )

    if len(identifiers) != len(set(identifiers)):
        raise SourceApiReviewSchemaError("source API review IDs must be unique")
    if count != len(rows):
        raise SourceApiReviewSchemaError(
            "source API review candidate count does not match its rows"
        )
    observed_ids_digest = hashlib.sha256(
        ("\n".join(sorted(identifiers)) + "\n").encode()
    ).hexdigest()
    if observed_ids_digest != ids_digest:
        raise SourceApiReviewSchemaError(
            "source API review candidate ID digest does not match its rows"
        )

    recommendation_counts = _require_exact_keys(
        scope["recommendation_counts"],
        set(counts),
        "source API review recommendation counts",
    )
    for label, value in recommendation_counts.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SourceApiReviewSchemaError(f"source API review count for {label} is invalid")
    if recommendation_counts != dict(counts):
        raise SourceApiReviewSchemaError("source API review recommendation counts are stale")
    return review
