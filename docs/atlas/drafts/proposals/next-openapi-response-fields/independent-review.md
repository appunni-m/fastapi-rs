# Independent review: next OpenAPI response-field inputs

2026-10-05. Read-only source/input review of the inactive three-case proposal. **No remaining source-reachability, input-independence, or selector blocker was found after the outer-field coverage correction.** This is static review clearance for a prospective source-first admission gate, not a live oracle result or target-compatibility claim.

## Reviewed freeze and counts

| File / future materialization | SHA-256 |
| --- | --- |
| `next_openapi_response_fields.py` | `d1c2824c616533127910a459075af4b020e6e97a8d9f260dd838d3b0ef7733bf` |
| `next-openapi-response-fields.yaml` | `e1243762e877e182bffadeb4eed6668d852bfb4d1bc31f8c98a7cceb9f8ce132` |
| `review-plan.md` | `98582838fbde27dbf649a9cae9b49caac7d97c8b22bacb05aee9bab26a8ced3b` |
| Canonical future input bytes, not written/admitted | `558a3d9cde89de0fd8342fe9a04deaef08a3caac836f5afd3a1b16d0c6829767` |

The original recipe `5e55ea92…`, canonical input `82f9fa38…`, and plan `2ae0e2c5…` are superseded. The author changed the first case ID and the scope/source-reference prose; the workload, all stimuli/actions/selectors, and errors/warnings/send journals remain unchanged.

Current IDs:

- `fastapi.next-openapi-response-fields.annotated-metadata-outer-titles-retained-hooks` — five actions.
- `fastapi.next-openapi-response-fields.shared-primitive-definition` — five actions.
- `fastapi.next-openapi-response-fields.late-json-hook-error-public-retry-cache` — nine actions.

All three are ordinary parity cases with independent app/journal construction. Counts are three explicit construction observations and 19 HTTP actions: 11 `/state`, six `/openapi.json`, two `/document`. There are 64 planned indexed action observations (19 HTTP, 19 send-type, 19 application-error, seven full-document OpenAPI), plus three construction observations. The failing document action retains its exact HTTP/error/send projections without requiring a successful OpenAPI parse.

I independently called only canonical `scripts.build_parity_inputs.read_recipe`: duplicate-key loader plus workflow-9 schema passes; YAML uses only whole-value aliases and no merge keys. AST parsing for Python 3.10 succeeds, IDs/action IDs are unique in their respective scopes, every evidence path exists in the pinned FastAPI checkout, and canonical materialization matches the listed hash. No workload/factory/app was imported. Full manifest/index/metadata admission remains pending because the intended active workload path is not yet installed.

## Source correction resolved before freeze

The first draft incorrectly described primitive `Annotated[int, Field(...), SchemaProbe]` metadata as setting the **outer FastAPI response ModelField** title/aliases. Pinned FastAPI `utils.py:71` uses `FieldInfo(annotation=type_, default=default, alias=alias)`; these route callers supply no alias/title. Pydantic `fields.py:239,254–259` stores the nested annotation unchanged and takes outer aliases/title from constructor kwargs only. FastAPI `_compat/v2.py:155–166` retains that same outer FieldInfo while building its adapter; it does not replace the owner with `FieldInfo.from_annotation`.

Consequently `_compat/v2.py:268–281` uses the generated outer response-field name and overwrites every non-reference schema title here. Nested Field title/alias/serialization-alias variants remain valid public inputs to Pydantic annotation processing, but they do not exercise nondefault or empty **outer** alias/title branches. The renamed first case and revised plan now state that boundary correctly. This required a claim/ID correction, not an executable stimulus change or private field mutation.

Exact source references also corrected in the plan: serialization alias is `_compat/v2.py:133–135`; cache publication `applications.py:1084–1103`; docs dispatch `1108–1120`, public call at 1110; component sorting `openapi/utils.py:668–669` and final model validation/encoding at 679. No further correction is requested for the reviewed freeze.

## Independently derived source behavior

The inspected source revisions are FastAPI `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` (0.141.1), Pydantic `cf67d4b3193c3fe43ede18612ed62785eee11382` (2.13.4 / core 2.46.4), and sole Starlette `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` (1.6.0), with CPython 3.12.13. Source hashes in the refrozen plan agree with inspected files.

- **Construction versus document order.** `routing.py:1038–1054` creates extras in response-map insertion order, before primary `1103–1114`. `openapi/utils.py:551–582` instead collects primary then extras for the eligible route. Only `/probe` contributes response fields: `/state` and `/document` declare no model and are excluded from schema. Integer status keys and explicit descriptions avoid range/default/status-conversion branches.
- **Retained core schemas and two passes.** `_compat/v2.py:285–336` builds one shared generator input sequence from retained adapter core schemas. Primitive annotations add no BaseModel/Enum flattening (`v2.py:462–483`). Pydantic `json_schema.py:384–399` makes two `generate_inner` passes. The metadata protocol is installed through `_internal/_generate_schema.py:2419–2436`; annotation JSON callbacks are invoked by `json_schema.py:574–587`. Journals record all actual calls and mode values, without prescribing a one-call rule.
- **Reference short circuit.** The shared case uses one stable public `core_schema.int_schema(ref=...)` identifier (core_schema.py:644–689, argument documented at 674) for three independent field constructions. Pydantic `json_schema.py:463–470` returns an existing definition reference for a populated CoreRef/mode; `472–484` publishes generated definitions. The fixture uses one equivalent integer schema, not different schemas sharing a ref. Whole document and callback history select deduplication/ref effects without accessing generator maps. FastAPI skips its title rewrite for `$ref` at `v2.py:276`.
- **Ordinary failure and retry.** The later-extra JSON hook is armed only after all route attachment, at workload lines 262–267. It raises the user's ValueError subclass after journaling the original hook/warning. FastAPI `applications.py:1085–1102` publishes the document and version only after generation succeeds, and `openapi/utils.py:620–627` propagates this generator failure. A later public call can construct a fresh generator; the fixture preserves earlier partial callback work in its user journal and retains later successful/cached calls. These are source-order deductions to verify live, not stored outcomes.
- **Public handled error and result identity.** Starlette `_exception_handler.py:16–20,43–63` looks up the actual exception's MRO and invokes the async handler before a response has started. Workload lines 193–205 retain full actual class/message/path and return their own JSONResponse. `/document` compares the identity of successive results from public `app.openapi()` (213–223), without reading private cache state. Cached docs route dispatch also calls the same public method (`applications.py:1110`).
- **Final document assembly.** `openapi/utils.py:473–516` merges extra field schemas/metadata after shared generation. Its final `OpenAPI(**output)` and encoder at 679, along with Pydantic sorting, remain part of the selected raw document bodies. This can expose wire-order differences beyond parsed schema equality; those differences must remain intact during later diagnostics.

## Public input independence, observations, and mapping

The factory is declarative over ordinary model/response metadata; it contains no case IDs, target lookup, backend branch, expected outputs, original FastAPI import, internal route/model-field/cache inspection, or copied generator logic. Its user hook delegates through public Pydantic handler protocols, adds a user extension, and optionally returns a documented primitive ref or raises its own error. Counter values and warning texts are generated from actual calls. No clocks, addresses, thread IDs, races, or source expected observations are used.

All 19 HTTP actions select exact status, ordered binary headers, and full body; all select ordered message types and exact application error. Seven document actions also select the whole JSON document using the valid empty JSON pointer. The independent raw body selection remains essential because parsed JSON dictionary comparison ignores key order. The observer records every send key, byte value, tuple/list distinction, header order and `more_body` presence; only `/state` avoids recursively journaling its own sends, while those state responses stay fully selected by the runner. Warnings retain category/message/stage/request and occurrence order. The user exception handler preserves actual class/message/path. Warning filenames/line numbers and traceback/frame identity are intentionally outside the projections.

| Public operation / stimulus | Positive execution scope |
| --- | --- |
| FastAPI construction, `get`, ASGI `__call__` | All three cases |
| `exception_handler` registration | All three; handler invocation only the retry case |
| JSONResponse construction and call | All three, including state responses |
| FastAPI `openapi` | All three through source-owned docs dispatch; retry case additionally makes two explicit public calls |
| Request injection and `request.url.path` | Retry case only when its handler runs; annotations in the other two cases are not invocation evidence |
| Pydantic Field and core/JSON metadata hooks | Dependency inputs; no promotion to a FastAPI export |

No APIRouter/include-router stimulus, private ModelField/DefaultPlaceholder promotion, or direct `fastapi.openapi.utils.get_openapi` call is present. Public operation mappings should retain this distinction during future admission.

## Gates and remaining boundaries

Before active admission: reviewed metadata/API mappings, canonical input/index generation and contracts, then fresh identity-checked pinned source and unchanged target runs on the exact same inputs. Constructor failures or divergent hooks/documents/errors must be retained rather than replaced/skipped; existing 203 normal cases remain separate regression evidence. No normalizations, shortened selectors, comparator changes, or target detection are justified by this review.

Unproved boundaries remain outer nondefault/empty title/alias properties, nested BaseModel/Enum flattening, mixed validation/serialization modes, request/body/stream fields, ref/name collisions or recursion, included routes, callbacks/webhooks, mutation/version refresh, namespaces, concurrent/reentrant OpenAPI, custom generators/status mappings, broader metadata merges, encoding/finalizer failures, and private cache contents. The current ordinary hook failure is not a fault-contract case. No target compatibility, implementation, coverage or benchmark claim follows from this inactive static review.

Only this independent-review file was written by this reviewer. No active/tracked file, sibling source, input artifact, helper, installed module, or existing proposal file was changed. No application import/execution, unit/parity run, build/install, or native binary read occurred.
