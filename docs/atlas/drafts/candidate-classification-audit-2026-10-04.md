# FastAPI public API candidate classification audit

**Date:** 2026-10-04
**Status:** source-evidence draft; no active metadata or classifications changed.
**Authority:** FastAPI 0.141.1, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` (`metadata.yaml:6-14`; checked against `../fastapi`). Starlette 1.6.0 remains the generic oracle; this audit classifies FastAPI-owned source paths only.

## Denominators and checks

| Scope | Count | Dispositions |
|---|---:|---|
| Generated FastAPI source API candidates in `tests/fixtures/compatibility-atlas.json` | 1,593 | 461 supported; 1,104 private/internal; 28 uncertain |
| Reviewed public-looking class/field/value/import-binding subset | 137 | 9 supported; 125 private/internal; 3 uncertain |
| Separately reviewed inherited API candidates | 13 | 9 supported; 1 private/internal; 3 uncertain |

The generated discovery inventory reports 48 Python modules, 21 root exports, 61 documented targets, 651 import bindings, 315 module definitions, 350 source-defined callables, and 21 symbols with source deprecation evidence (`tests/fixtures/api-inventory.json:counts`). The 13 inherited candidates are a separate atlas section and are excluded from the 1,593 FastAPI-owned rows.

All 1,593 atlas IDs are unique and have one allowed classification. Every row has a source citation whose pinned FastAPI file, line span, and recorded module SHA-256 matched the checkout. All 461 supported rows have existing, in-range public-evidence references. The 392-row source-classification review and 137-row public-candidate review also have existing, in-range source/evidence citations. No missing IDs, broken source spans, or stale source hashes were found. This verifies citation integrity and disposition coverage; it does not establish FastAPI-RS parity.

## Finding

**Review one weak supported disposition before treating the public-candidate slice as settled:** `fastapi.types.IncEx` is classified `supported` in `tests/fixtures/api-public-candidate-classification-review.json:3404-3408`. The pinned source confirms a direct Pydantic binding at `../fastapi/fastapi/types.py:7`, and the release note says “Re-export IncEx type from Pydantic” at `../fastapi/docs/en/docs/release-notes.md:976`. However, that release note does not name the consumer import path `fastapi.types.IncEx`; the pinned root package exports at `../fastapi/fastapi/__init__.py:5-25` also do not export `IncEx`. Thus the evidence establishes the alias and its origin, but leaves its module-level public contract ambiguous.

The review schema accepts a `supported` row when it has a `documented` basis plus any reference under `docs/en/docs/` (`scripts/public_candidate_review_schema.py:181-190`); it does not require that the cited passage identify the candidate's import path. For this row, retain `uncertain` unless a pinned-source consumer-facing contract for `fastapi.types.IncEx` is established, or add evidence that closes that path-specific gap. This is an evidence-quality concern, not a confirmed runtime defect.

## Prioritized next action

Resolve `fastapi.types.IncEx` first: either document the exact module-path contract in the reviewed source evidence or change its reviewed disposition to `uncertain`, then regenerate/reconcile the atlas metadata and run `make metadata-check`. No other confirmed classification reversal or missing source citation was identified in this pass; keep target behavior and Starlette-owned generic contracts out of this source-classification decision.

## Disposition recorded

The root review changed `fastapi.types.IncEx` to `uncertain`: the release note
confirms a Pydantic re-export but does not establish the `fastapi.types` import
path as a consumer-facing contract. The reviewed candidate artifact and pinned
metadata were updated, and `make compatibility-atlas-update` regenerated the
atlas and API contract. The generated 1,593-candidate disposition is now 460
supported, 1,104 private/internal, and 29 uncertain; the 137-row public-looking
subset is 8 supported, 125 private/internal, and 4 uncertain. The final
metadata and contract checks are being run against this generated state.
