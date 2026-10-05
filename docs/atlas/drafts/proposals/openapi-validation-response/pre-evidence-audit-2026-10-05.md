# Closed automatic validation-response pre-change audit

Independent receipt/data audit, 2026-10-05. The parent closed the helper with
exit 1 after an ordinary four-case comparison: 0 pass, 4 fail, 0 case-level
not_run, 0 fault cases. Both canonical execution commands completed with exit 0;
there were no infrastructure errors. This note reports retained live observations,
not prescribed outputs or a post-repair claim.

## Binding and inventory

The workflow/result/comparison schema-9 documents and materialized index-v5
document pass independent Draft202012 schema validation. Exact four-case order,
six-action order per case, observation-kind/index inventories for reached
actions, and all construction selectors agree with the materialized input.
The six partial source mappings each retain all four cases; their required
source references agree with the actual documentation/test evidence, whose
pinned files were separately hashed. The index does not claim full source API
or branch coverage.

| Retained artifact | Run ID / SHA256 |
|---|---|
| Oracle | `e83b394b-ffce-47eb-a0ce-b8c10c2718ac` / `a437c49971e532e1580213e3531a55ec4f985341fc610a70f71de85101c5af54` |
| Target | `7c0f7e04-6853-4a78-8857-b2c8ef0df903` / `c971c90cab62f481f97f6a5213adbd8152161d8e46e6d015d7214addfa461954` |
| Comparison | `6049170b-f3a8-4de8-997f-819e58a5de29` / `a3302f3a93fb99b6a6b05bf51ece35ed490886ea70c022758c7520f65ca63b37` |
| Materialized input | `0ef0311b4fc9930eb2faeb442bc28742f0f3d3bd0a0f6bae753dd684ed7b2dc9` |
| Workload | `9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130` |
| Recipe | `4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334` |
| Manifest | `919fa17dfa66c4a32c57fe7230e214f2c05861e4100ff69a768a72747400bfc2` |
| Materialized index | `0490d2e3366bad2ffa941e5994da07f2a0ea4a8f8c7f0d6c919044e0caf20f68` |

Comparison result references match actual source/target bytes and run IDs. Both
result input/workload/manifest bindings match the current admitted files and
index; the initial/final snapshot bytes are identical, SHA256
`dcc26554dfe170677823af2e92ae00d9592fe5949e69dc0a31d1bfd20177ea5c`.
The recorded root tree is `3a55c21e8007298b4a55bc439b41945906844fbf40d06e8c0ec8a1c7d2f8423a`,
sibling tree `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`,
combined `5b27047c175a4ea9e631fadc0419e112ccef9667155fb5a26701f21f6e5506c4`.
Target identity binds that combined tree and admission revision
`a34714f47749b6f96d5d7829dc16b0d444efaa5e`.

The recorded normal core is `d934ba09884e6c8a657300c4800a92e76577285f2bf5833e73418d21912b6140`,
sibling `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`,
pair `e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0`.
The target pair matches both snapshots, and its fault flag is false. Oracle
fault applicability is null; identity reports CPython 3.12.13, FastAPI 0.141.1,
Starlette 1.6.0, Pydantic 2.13.4/core 2.46.4 and the pinned source revisions.
The oracle finished before target started. Commands record the isolated oracle
and target interpreters and target sibling pin. Module-path verification is a
canonical worker invariant; these result identities do not contain separate
native module-path fields. This audit did not read/import native binaries.

## Actual execution and warning bounds

| Lane | Constructors | Completed actions | Unrun actions | Selected action observations actually present |
|---|---|---:|---:|---:|
| Source | 4 ok | 24 | 0 | 80 |
| Target | 2 ok, 2 ordinary errors | 12 | 12 | 40 |

Every case is marked completed because schema 9 records constructor outcomes
without turning ordinary user-input errors into infrastructure failures. The
comparison's case-level not_run count of zero does not count the 12 unrun target
actions as execution. They contain no observations. There are 28 declared
warning-capture phases: source reached all 28; target reached four constructor
phases and 12 action phases. All reached warning lists are empty. Empty sidecars
on the 12 unrun target actions are placeholders, not emitted-warning evidence.

## Earliest selected divergences

Case suffixes below are under `fastapi.openapi-validation-response.`. Both
document actions show the same per-case differences; the later state response
retains their raw sends and public document-order journal.

| Case | First divergence and observed consequence |
|---|---|
| `automatic-after-declared-responses` | First docs body differs at byte 416. Source response order is `200,409,202,422`; target is `200,422,409,202`. Both bodies are 1256 bytes; status/ordered headers match, parsed JSON values and both validation definitions match. The structural OpenAPI selector therefore agrees while exact body bytes fail. |
| `declared-422-suppresses-automatic` | First docs body differs at byte 416. Source is 611 bytes with `200,409,422,202`; target is 1280 bytes with `200,422,409,202`. Source declared 422 has description only and no components; target retains automatic `content` and `HTTPValidationError`/`ValidationError` definitions. Content-length headers and the structural document also differ. |
| `declared-4xx-suppresses-automatic` | Target constructor raises `builtins.NotImplementedError`, exact message `route-level responses currently support integer status keys only`. All six target actions are unrun. Source reaches all six actions; document response order is `200,409,4XX,202`, with no validation components. No target HTTP/cache/recovery behavior is established for this case. |
| `declared-default-suppresses-automatic` | Same exact target constructor error and six unrun actions. Source reaches all six actions; document order is `200,409,default,202`, with no validation components. No target HTTP/cache/recovery behavior is established for this case. |

For both integer cases, valid, missing and malformed required-query responses
agree exactly in status, ordered headers and raw body: 200, 422, 422 respectively.
The endpoint journal contains only the valid query call, with reading 27, in
both lanes. All reached ASGI message-type and application-error observations
agree. Final state trace phase order also agrees; its value/byte differences
come from the retained document bodies, associated response headers where their
length changed, and public document status/component-order journal. Source and
target prior raw send records agree for all three query requests; document send
bodies differ (and document starts differ in the declared-422 case).

These actual differences agree with source `openapi/utils.py:474-538`: declared
responses merge before the automatic guard, which inspects merged keys, and
validation definitions are added only in that branch. The raw-key constructor
rejection is separate from source `routing.py:1038-1054`, where description-only
records skip truthy-model status/body checks. Request validation remains
independent of documentation suppression.

## Reproduction and limits

The frozen helper is `60fa02332e94224d35de2b013493c0eb945d6a42545b005cfff5dddba7e3c39a`.
Read-only data checker `/private/tmp/fastapi-rs-openapi-validation-response-pre-audit.py`
validates schemas and retained bindings without loading workloads/products.
Its derived audit `/private/tmp/fastapi-rs-openapi-validation-response-pre-audit.json`
is SHA256 `6eb0cb31a37ea1cf881485d144e63edbb52590cdbd228451ee7deef5047bfcf6`.
This supplements the immutable canonical artifacts; it does not replace them.

No new expected outputs, normalizers, selector reductions or fault hooks were
introduced. This evidence does not cover truthy extra models, generic status
protocols, full response metadata/deep merging, alias/include contexts,
body-only/optional flattening, schema-name collisions or mutable cache histories.
The parent separately authorized a prospective TMP-only repair after this proof;
active code and fresh source/target gates remain subsequent work.
