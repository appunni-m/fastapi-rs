# FastAPI public API candidate source audit

> Draft audit of the pinned FastAPI 0.141.1 compatibility atlas on 2026-10-03. This is a source-evidence check, not a FastAPI-RS support or parity claim.

## Candidate result

All 1,593 `api_candidates` have a unique ID, one allowed classification, and one source citation with a repository path, line span, and module SHA-256:

| Classification | Candidates |
|---|---:|
| supported | 461 |
| private/internal | 1,104 |
| uncertain | 28 |
| **Total** | **1,593** |

The candidate source citations were checked against `../fastapi` at commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`. All 1,593 cited files exist; every line span is in range; every recorded module hash matches. These candidates do not need inherited Starlette-RS evidence to satisfy the source-citation criterion. All 461 supported candidates also have public-evidence references whose paths exist. All 28 uncertain candidates have reviewed reasons and evidence; there are no uncited or unclassified candidates in this set.

## Inherited exposure boundary

The atlas separately records 12 inherited API candidates: 8 supported, 3 uncertain, and 1 private/internal. Checked against the user-directed latest Starlette-RS commit `693050dce44a52a54eb319c47ec2ff15e55fa608`, six supported rows link to canonical operations whose API-review dispositions are supported and whose operation paths are present in the latest manifest. Four `APIRouter` rows cite exact API-review dispositions (`host`, `lifespan`, and `mount` uncertain; `not_found` private/internal). `FastAPI.host` and `FastAPI.mount` are documented as FastAPI exposure through Starlette inheritance, but the latest sibling manifest has no canonical registration-operation contract for either; the atlas records each under `sibling_contract_gap`. These two are not counted as Starlette-RS operation coverage.

At audit time, the generated atlas still recorded the earlier manifest hash `aa3108780be0d225f0e1e234768417446b945f0f7b16b1f013aa1a221d73ddec` and implementation revision `2f9978d4c8e28443a176b83fb9a6f2b9966d0953`, while the latest manifest hash was `a9d723785c9f76f0d41c14b770d39e55a8140a4091122ec9a7df1efa8ecf4dd9`. The latest checkout's API catalog, API review, and metadata hashes already matched. The main workstream subsequently regenerated the atlas against commit 693 and refreshed the manifest source digests.

### Pin follow-up

This audit snapshot originally used Starlette-RS `693050d`; remote `main` subsequently advanced to `4807b3a11efcb96c6ac2bf8537e806b6971aed37`. The API catalog, API review, and metadata are unchanged, so the 12 inherited API dispositions remain valid. The newer manifest adds three sibling-owned `ServerErrorMiddleware` probes and does not add FastAPI-owned API candidates. The atlas and hashes were first regenerated against `4807b3a` before the later benchmark-documentation commit.

## Validation gap and next action

At audit time, `make metadata-check` stopped on the stale 2f-to-693 pin. The subsequent `make compatibility-atlas-update STARLETTE_RS_SOURCE=/tmp/fastapi-rs-starlette-rs-693050d` and `make metadata-check STARLETTE_RS_SOURCE=/tmp/fastapi-rs-starlette-rs-693050d` completed successfully. No candidate-classification edit was indicated by this audit.


Starlette-RS then advanced to `baea19981ba3119d362be8c3a1b0913e4824313e` for a benchmark-documentation-only refresh. Manifest and API source hashes stayed unchanged; the active FastAPI pin was advanced to that commit.
