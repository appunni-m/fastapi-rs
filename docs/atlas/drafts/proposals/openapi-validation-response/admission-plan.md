# Prospective automatic validation-response admission

Date: 2026-10-05. Author: `override_reanalysis` (Sol).
TMP-only preparation against clean source revision
`62dacc5283a0cee282258e268f7545765679e974`. No active source, metadata, input, generated file,
sibling or native binary was changed. No app import, source/target execution,
parity, build, install or unit framework was run. Root owns activation and all
live gates after closing the current coverage/fault/benchmark stages.

## Frozen files and patch

The reviewed inactive proposal remains in
`docs/atlas/drafts/proposals/openapi-validation-response/`. Active-path copies
under this TMP tree are byte-identical; its inactive comment is preserved too.
The patch creates only the following two files and edits `metadata.yaml`:

| Future active path | SHA256 |
| --- | --- |
| tests/fixtures/input-recipes/parity/openapi-validation-response.yaml | 4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334 |
| tests/fixtures/workloads/openapi_validation_response.py | 9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130 |

| Proposal boundary | SHA256 |
| --- | --- |
| metadata-base.yaml | 24e916145a0174644a48295b6065d28569325267e1db3fc44495e4fbe1989ef1 |
| prospective metadata.yaml | 89e0abe3c85d041d3dde66fdd6c56da6c698fc90f3f5f2031121ad8b6edaef65 |
| admission.patch | 8ec244372a58fce35a39405170614bc5408bb4100bf45847290057c2dc28a7b9 |

Archived review-plan/independent-review/native-design hashes remain respectively
`1f859e84f347cb97878b9c618931ca63996a1ba503a012f477911e49f3914f77`,
`40d02bdd88c96d8ab0e2fa6a3d54eea4084c49134579040a56cc292b640a882e`,
and `4769c1dad88b6d5e6aa073b9c4c26ef793f1cd609fcaa5ea619c0e8fa028127a`.
They are history/design, not new product-execution evidence.

## Exact reviewed fixture links

Four case IDs, under `fastapi.openapi-validation-response.`:

- `automatic-after-declared-responses`
- `declared-422-suppresses-automatic`
- `declared-4xx-suppresses-automatic`
- `declared-default-suppresses-automatic`

Each case is linked to exactly these six supported public candidate IDs:

| Candidate operation | Actual public call / evidence | Links |
| --- | --- | ---: |
| fastapi.FastAPI | Imported root constructor; pinned `fastapi/__init__.py:7` aliases canonical FastAPI. Construction outcome/class/message and warnings remain live observations. | 4 |
| fastapi.applications.FastAPI | Same canonical constructor reached through root alias; `applications.py:42,58-1018`. No separate identity comparison is added. | 4 |
| fastapi.applications.FastAPI.__call__ | Wrapper explicitly awaits the app for all six requests; `applications.py:1160-1164`. Status, ordered headers, body, send types, errors and complete prior-send journal are selected. | 4 |
| fastapi.applications.FastAPI.get | Public decorators register state/document/reading routes, including saved decorator attachment; `applications.py:1646` delegates route registration. Required query and declared response records are ordinary public inputs. | 4 |
| fastapi.applications.FastAPI.openapi | Public `/document` helper calls it directly; built-in docs also generate through it; `applications.py:1070-1103`. Both document requests select the full document and exact raw body. | 4 |
| fastapi.responses.JSONResponse | Returned endpoint/helper response constructors through the pinned public reexport in `fastapi/responses.py`. All HTTP/sends remain live; generic behavior stays sibling-owned. | 4 |
| **Total** | **Six candidate IDs, four shared case provenances each** | **24** |

The root candidate was already supported in the manifest, but lacked an
`operations` overlay. Its new minimal row contains only pinned root/canonical
source evidence and fixture refs. Its existing identity refs, null Rust binding,
full-contract-not-established status and scope-review-pending state are preserved.
The canonical class already has an operation row; it receives refs only. The
other four existing rows likewise receive refs only. `FastAPI.__init__` remains
unchanged; adding it would be a seventh, redundant constructor-method mapping.

Every ref has only recipe_path, case_id and workload_path. The current direct
operation resolver (`scripts/parity/api_contract.py:978-1078`) derives complete
selected-case provenance from the materialized index; it does not make an
individual operation own every selected observation. The 14 derived selector
IDs, including docs aliases plus construction/action warnings, are recorded in
`static-admission.json`. This preserves all existing aggregate selectors,
features, bindings, target states, scope statements, aliases, normalizers,
classifications and identities. No private/default/handler/get_openapi/APIRouter/
Request/Pydantic operation is added. Root/canonical fixture provenance does not
add an object-identity assertion.

## Source evidence and selected boundary

Pinned FastAPI0.141.1 / Starlette1.6.0 / Python3.12.13 /
Pydantic2.13.4-core2.46.4 remain authoritative. Starlette-RS b4c8a65 is unchanged.

- `routing.py:1015-1054` retains ordered raw responses and constructs an extra
  field only for a truthy model. These declarations contain descriptions only.
- `openapi/utils.py:332-343` collects the required ordinary query parameter;
  `416-473` inserts the primary response; `474-516` merges extras in declaration
  order and canonicalizes status keys. `517-538` then tests merged keys
  422/4XX/default before adding automatic validation response/definitions.
- `openapi/utils.py:667-679` sorts component names and finalizes through the
  actual model/encoder. No fixture sort or output visitor removes key order.
- `routing.py:481-491,751-755` validates before endpoint invocation and
  `exception_handlers.py:20-26` supplies the default request-validation JSON
  response. Documentation declarations do not install a handler.
- Existing recipe evidence is unchanged: additional-responses, query-params and
  handling-errors documentation; default-validationerror, custom-validationerror
  and additional-responses-router test paths. Their test bodies/expected data
  are not copied. No extra documentation path is required by the ordinary
  direct-operation fixture resolver; inherited-operation matching is separate.

Description-only wildcard/default attachment failures, if observed in the
unchanged target, remain normal parity outcomes with exact constructor class/
message and actions not_run. They are neither injected faults nor successful
HTTP executions. Source must first complete all four constructions and all
24 planned actions. No new fault hook/build is necessary for these public inputs.

The source/native design's broader raw-key protocols, response models/content/
headers/links/extensions, recursive merges, user definition collisions,
body-only/optional/empty-model validation, includes, custom handlers and mutable
history stay unselected. Current206/public4 evidence belongs to different inputs.

## Static checks and parent sequence

Canonical `read_recipe` plus schema9 passes on the unchanged TMP copy. The
workload positional factory is AST-checked; action IDs/methods/counts, evidence
paths and warnings flags were verified without importing the workload. YAML
uses whole-value aliases and no merge keys. Existing independent Ruff/static
receipts apply to the byte-identical workload/recipe; no formatter was run here.
`git apply --check` succeeds against the current base. Structural comparison
proves exactly 24 added refs and one minimal source-evidence root row, with
all existing operation attributes and everything outside operations equal.

Counts: **4 parity / 4 construction / 24 GET / 80 action observations /
28 ordered-warning phases / no faults**. Each case has docs, valid query,
missing query, malformed query, public document and state actions. Lossless
prior ASGI sends include every key, optional more_body, bytes, header order and
container kind. Whole documents and exact status/headers/body protect values
and wire order. No expected outputs, target detection or normalization is added.

The current index has 554 workflows/2300 cases; manifest operation refs are
1345 across 152 symbols. Prospective deltas are **+1 workflow/+4 cases/
+24 operation refs/+2 symbols with refs**, giving 555/2304/1369/
154 after successful parent regeneration. These are predictions, not a
post-regeneration receipt. Supported/private/uncertain candidate classification
counts remain 460/1102/31; metadata classification data is untouched.

After measurement closure, root reviews/applies the patch, then owns canonical
`make parity-inputs parity-index-update parity-validate`, atlas update,
metadata/facade/API checks, manifest/index/hash audit and a committed/frozen
source-first four-case gate. Require four source constructions and 24 actual
source actions before preserving unchanged-target diagnosis. Do not weaken
selectors, skip constructor mismatches, relabel them as faults or overwrite the
existing206/coverage/fault/benchmark evidence. No runtime implementation is part
of this admission patch.
