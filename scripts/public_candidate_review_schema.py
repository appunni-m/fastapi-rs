"""Strict schema for the reviewed public-looking FastAPI source candidate slice."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import PurePosixPath
from typing import Any

PUBLIC_CANDIDATE_REVIEW_SCHEMA = "fastapi-rs/public-candidate-classification-review@1"
PUBLIC_CANDIDATE_KINDS = {"class", "field", "import_binding", "value"}
PUBLIC_CANDIDATE_RECOMMENDATIONS = {"supported", "private/internal", "uncertain"}
PUBLIC_CANDIDATE_EVIDENCE_BASIS = {
    "documented",
    "implementation-only",
    "member-exposure-unresolved",
    "source-declaration",
}
PUBLIC_CANDIDATE_EVIDENCE_ROLES = {
    "fastapi-implementation-use",
    "fastapi-public-documentation",
    "fastapi-source-binding",
    "fastapi-source-declaration",
    "fastapi-source-field",
    "fastapi-source-member",
}


class PublicCandidateReviewSchemaError(ValueError):
    """Raised when a public candidate review does not match its closed schema."""


def _exact_keys(
    value: Any,
    required: set[str],
    label: str,
    *,
    optional: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PublicCandidateReviewSchemaError(f"{label} must be an object")
    missing = required - set(value)
    unknown = set(value) - required - (optional or set())
    if missing or unknown:
        details = []
        if missing:
            details.append("missing=" + ",".join(sorted(missing)))
        if unknown:
            details.append("unknown=" + ",".join(sorted(unknown)))
        raise PublicCandidateReviewSchemaError(f"{label} has invalid keys ({'; '.join(details)})")
    return value


def _relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise PublicCandidateReviewSchemaError(f"{label} must be a non-empty relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise PublicCandidateReviewSchemaError(f"{label} must be a normalized relative path")
    return value


def _line(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise PublicCandidateReviewSchemaError(f"{label} must be a positive line number")
    return value


def validate_public_candidate_review_schema(
    review: Any, *, expected_identity: dict[str, str]
) -> dict[str, Any]:
    """Validate every key, enum, identity, and summary in the review artifact."""
    review = _exact_keys(
        review,
        {"rows", "schema", "scope", "source_identity"},
        "public candidate review",
    )
    if review["schema"] != PUBLIC_CANDIDATE_REVIEW_SCHEMA:
        raise PublicCandidateReviewSchemaError("public candidate review has an unsupported schema")

    identity = _exact_keys(
        review["source_identity"],
        {"package", "source_commit", "version"},
        "public candidate source identity",
    )
    if identity != expected_identity:
        raise PublicCandidateReviewSchemaError(
            "public candidate review has the wrong source identity"
        )

    scope = _exact_keys(
        review["scope"],
        {"candidate_count", "candidate_ids_sha256", "recommendation_counts"},
        "public candidate review scope",
    )
    rows = review["rows"]
    if not isinstance(rows, list) or not rows:
        raise PublicCandidateReviewSchemaError("public candidate review has no rows")

    identifiers: list[str] = []
    counts: Counter[str] = Counter()
    for index, raw_row in enumerate(rows):
        label = f"public candidate review row {index}"
        if not isinstance(raw_row, dict):
            raise PublicCandidateReviewSchemaError(f"{label} must be an object")
        candidate_kind = raw_row.get("candidate_kind")
        if not isinstance(candidate_kind, str) or candidate_kind not in PUBLIC_CANDIDATE_KINDS:
            raise PublicCandidateReviewSchemaError(f"{label} has an unsupported candidate kind")
        required = {
            "candidate_kind",
            "evidence",
            "evidence_basis",
            "id",
            "reason",
            "recommendation",
            "source",
        }
        if candidate_kind == "import_binding":
            required.add("binding")
        row = _exact_keys(raw_row, required, label)

        identifier = row["id"]
        if not isinstance(identifier, str) or not identifier.strip():
            raise PublicCandidateReviewSchemaError(f"{label} ID must be non-empty")
        identifiers.append(identifier)

        recommendation = row["recommendation"]
        if (
            not isinstance(recommendation, str)
            or recommendation not in PUBLIC_CANDIDATE_RECOMMENDATIONS
        ):
            raise PublicCandidateReviewSchemaError(f"{label} has an unsupported recommendation")
        counts[recommendation] += 1
        reason = row["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise PublicCandidateReviewSchemaError(f"{label} reason must be non-empty")

        source = _exact_keys(row["source"], {"line", "path"}, f"{label} source")
        _relative_path(source["path"], f"{label} source path")
        _line(source["line"], f"{label} source line")

        if candidate_kind == "import_binding":
            binding = _exact_keys(row["binding"], {"module", "name", "target"}, f"{label} binding")
            if any(
                not isinstance(binding[key], str) or not binding[key].strip() for key in binding
            ):
                raise PublicCandidateReviewSchemaError(f"{label} binding values must be non-empty")

        basis = row["evidence_basis"]
        if (
            not isinstance(basis, list)
            or not basis
            or any(not isinstance(item, str) or not item.strip() for item in basis)
            or set(basis) - PUBLIC_CANDIDATE_EVIDENCE_BASIS
        ):
            raise PublicCandidateReviewSchemaError(f"{label} has an unsupported evidence basis")

        evidence = row["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise PublicCandidateReviewSchemaError(f"{label} evidence must be non-empty")
        roles: set[str] = set()
        has_public_documentation = False
        for evidence_index, raw_reference in enumerate(evidence):
            ref_label = f"{label} evidence {evidence_index}"
            reference = _exact_keys(
                raw_reference,
                {"line", "path", "role"},
                ref_label,
                optional={"end_line"},
            )
            _relative_path(reference["path"], f"{ref_label} path")
            line = _line(reference["line"], f"{ref_label} line")
            end_line = _line(reference.get("end_line", line), f"{ref_label} end line")
            if end_line < line:
                raise PublicCandidateReviewSchemaError(f"{ref_label} range ends before it starts")
            role = reference["role"]
            if not isinstance(role, str) or role not in PUBLIC_CANDIDATE_EVIDENCE_ROLES:
                raise PublicCandidateReviewSchemaError(f"{ref_label} has an unsupported role")
            roles.add(role)
            has_public_documentation |= role == "fastapi-public-documentation" and reference[
                "path"
            ].startswith("docs/en/docs/")

        if recommendation == "supported" and (
            "documented" not in basis or not has_public_documentation
        ):
            raise PublicCandidateReviewSchemaError(
                f"{label} supported disposition lacks public documentation evidence"
            )
        if recommendation == "private/internal" and (
            "implementation-only" not in basis or "fastapi-implementation-use" not in roles
        ):
            raise PublicCandidateReviewSchemaError(
                f"{label} internal disposition lacks implementation evidence"
            )

    if len(identifiers) != len(set(identifiers)):
        raise PublicCandidateReviewSchemaError("public candidate review IDs must be unique")
    if (
        not isinstance(scope["candidate_count"], int)
        or isinstance(scope["candidate_count"], bool)
        or scope["candidate_count"] != len(rows)
    ):
        raise PublicCandidateReviewSchemaError("public candidate review count does not match rows")
    digest = hashlib.sha256(("\n".join(sorted(identifiers)) + "\n").encode()).hexdigest()
    raw_digest = scope["candidate_ids_sha256"]
    if (
        not isinstance(raw_digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", raw_digest) is None
        or raw_digest != digest
    ):
        raise PublicCandidateReviewSchemaError("public candidate review ID digest is stale")
    recommendation_counts = scope["recommendation_counts"]
    if not isinstance(recommendation_counts, dict) or recommendation_counts != dict(counts):
        raise PublicCandidateReviewSchemaError(
            "public candidate review disposition counts are stale"
        )
    return review
