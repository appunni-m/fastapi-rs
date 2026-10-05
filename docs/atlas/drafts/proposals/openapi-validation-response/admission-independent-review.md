# Independent inactive 422 admission review

Date: 2026-10-05. Reviewer: runtime peer. Bounded static clearance; no concrete admission blocker found.

This review uses lightweight YAML/AST/hash/patch reads and selected pinned source lines while the benchmark is live. It does not import or execute the workload, run products/builds/parity/canonical regeneration, inspect live benchmark results, or change active files. Parent must rerun the canonical loader, metadata/API/index/atlas/facade and Ruff admission checks after measurement closure. Reading clearance is not target support or live parity evidence.

## Bound identities and exact delta

Base revision: `62dacc5283a0cee282258e268f7545765679e974`.

- Patch: `8ec244372a58fce35a39405170614bc5408bb4100bf45847290057c2dc28a7b9`.
- Admission plan: `080bbc569e09743e2a77aabacc60d15d26c485d40be37cef9e8bf9a3b5d8ebf2`.
- Base metadata: `24e916145a0174644a48295b6065d28569325267e1db3fc44495e4fbe1989ef1`.
- Proposed metadata: `89e0abe3c85d041d3dde66fdd6c56da6c698fc90f3f5f2031121ad8b6edaef65`.
- Recipe: `4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334`.
- Workload: `9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130`.

All frozen hashes read back correctly. Recipe/workload bytes equal the archived inactive proposal. The patch touches exactly metadata plus the two future active input/workload files. Removing the 24 new fixture refs and the new minimal root alias row reproduces the base metadata structurally in full. Existing binding, target-state, feature, scope, identity, classification, alias and normalization values remain unchanged.

Exactly four refs are added to each of these six actually exercised public candidate IDs:

| ID | Public stimulus |
| --- | --- |
| `fastapi.FastAPI` | Root import and constructor call |
| `fastapi.applications.FastAPI` | Canonical class reached by that root alias |
| `fastapi.applications.FastAPI.__call__` | Wrapper explicitly awaits the app, including its `/state` branch |
| `fastapi.applications.FastAPI.get` | State/document/reading registration and saved decorator attachment |
| `fastapi.applications.FastAPI.openapi` | Public `/document` call and built-in documentation route |
| `fastapi.responses.JSONResponse` | Public endpoint/document/state response constructors |

The root alias already exists in the classified public surface; the new operations row has only `source_evidence` and `fixture_refs`. It neither supplies a native binding/full support state nor promotes private APIs. Canonical class provenance is the same constructor call; the input adds no class-identity assertion. `__init__`, handlers, `get_openapi`, internal models/defaults and unrelated operations remain unchanged. Source classification and fixture linkage do not establish full target support. Predicted generated counts in the author's plan remain predictions until parent regeneration.

## Input and source boundary

Static counts are exactly **4 ordinary parity cases / 4 construction observations / 24 GET actions / 80 action observations / 28 warning capture phases / no faults**. Each case retains the six actions in order: built-in docs, valid/missing/malformed required query, public document, state journal. IDs are unique within each case. All construction and action warning captures are enabled.

Every HTTP action selects exact status, ordered headers and raw body. Both docs actions also select the entire document with the empty JSON pointer; the full raw body preserves wire order even where structural OpenAPI selectors ignore map key order. The wrapper records every prior ASGI send field, byte value, header/container order and optional-key presence. The state route avoids recording its own response recursively while still dispatching through public `__call__`. No warning filtering, expected-result storage, backend/module predicate, private peek, upstream copied response, or comparator normalization is introduced. The factory accepts its two positional inputs and uses ordinary public decorators and response constructors.

Pinned `openapi/utils.py:474-538` confirms merged additional responses precede automatic 422 insertion; integer/status-range/default keys are canonicalized, then existing 422/4XX/default keys suppress the automatic response. These inputs use description-only extras and an ordinary required query. The default request-validation handler continues to determine live request error responses; documentation declarations install no custom handler. `applications.py:1070-1103,1110,1160-1164` confirms the public schema/cache/docs and ASGI paths. Existing documentation/test evidence paths exist, with no copied test outcomes.

A target refusal of description-only 4XX/default during construction is an ordinary captured constructor mismatch, with its actual class/message/warnings retained and its planned actions blocked by that outcome. It must not be relabeled as an injected fault, skipped case or successful HTTP execution. Require fresh source completion of all four constructions and 24 actions, then retain the unchanged-target diagnosis before implementing a fix.

The selected inputs do not prove raw custom-key protocols, modeled extras, content/header/link/extensions merging, shared-definition collisions, includes, custom handlers, body-only/optional/empty-model validation or mutable cache history. They do not extend the earlier 210 evidence to these new inputs. The recipe remains prospective until explicit parent activation.

## Reproducible static receipt

`/private/tmp/fastapi-rs-openapi-validation-response-admission-independent-static.json`, SHA256 `a0ed9e008045ff584456c2d960f65eb5d420db50639cef4d5548f2106ff173d9`, records exact hashes, six IDs / 24 refs, input counts, byte identity and metadata equality. Its helper only reads bounded inactive/source files and writes TMP. No canonical check or live result is claimed by this receipt.
