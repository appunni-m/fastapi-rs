# Retained response OpenAPI batch: prospective native patch

2026-10-05. Unapplied TMP-only proposal for application_runtime.rs and response_field.rs. Root owns the merged three-file review, formatting, compilation, live gates and eventual application. No active source, Python facade, metadata, input, comparator, sibling or dependency was changed. No unsafe/lint suppression/unit framework/fault hook was added. No application, builder, parity or test process was executed.

## Frozen bases and prospective files

Bases are byte-identical copies of active native source at admitted clean bbac9b5 (native implementation `827612f`):

| File | Base SHA256 | Prospective SHA256 |
| --- | --- | --- |
| application_runtime.rs | 14c6f7cf93865b8cc719055587d895ae517937212d14f105a7b5e2f6e7a5dfef | 3e64ac2c566682ead3dd9172ca30df51195358efc142f61dd52c1a9cd3df437b |
| response_field.rs | 952bc9fb4510c58b2d1f173859baad8eebd31ee608a9ad22d64b25bc5fe91732 | 562136969b3192427a497c5e8a61283bbcd41b01e96e9aa05d515ea796a734aa |

`next-openapi-native.patch` SHA256 `7f744b2ab2649a8fa14747f15e39796e1ea0a73734f150ad0948148852963807`: two paths, 185 insertions and 87 deletions. Git apply --check passes against unchanged active native files. No compiler or formatter ran; root must close type/style/static contracts after merge with the peer openapi.rs proposal.

## Exact coordinated interface

Peer `/root/dependency_records_runtime` owns TMP openapi.rs under `/private/tmp/fastapi-rs-next-openapi-wire-native/` and confirmed:

- `openapi_document(py, app_info, operations, root_path, shared_definitions: Option<&Py<PyDict>>)`: the app path passes `Some(&response_schemas.definitions)`; existing public direct subset passes None.
- `OpenApiInfo.openapi_version: &str` and `tags: Option<&Py<PyAny>>`: this app path supplies the previous literal `3.1.0` and None, without expanding constructor behavior.
- `OpenApiOperation.response_schema_title: Option<String>`: mapped primary None (already titled by owner); legacy/direct paths Some(previous title).
- Mapped primary/extras pass `response_model_name=None` and the complete mapping schema, preserving actual references and sibling extension keys. Shared definitions are owned by the batch until assembly completes.

The coordinated peer patch is required; this two-file proposal is not independently compilable against old openapi.rs signatures.

## Source evidence and changes

The frozen pre 3 source/target constructions and all 19 actions complete; all 3 comparisons fail with no skip. Initial state bytes agree. Source visits primary→ordered extras on each whole JSON pass; old target rebuilds primary core and generates per-field pairs. The shared-ref source and target BOTH observe six JSON-hook calls; the observable differences include retained $ref siblings, not an assumed one-call count. Source refusal409 class/message/body/headers already agree; partial-pass/retry journals differ. No expected outcome or count is embedded in production code.

- OpenApiRouteSnapshot retains its primary ResponseField and existing registered route.name alongside extras. This avoids primary TypeAdapter reconstruction and endpoint-name summary loss. Source summary uses `route.name.replace('_',' ').title()` (utils.py281–286); Python string operations preserve source Unicode/spacing. Fallback IDs also use registered name, while explicit nonempty operation IDs retain precedence.
- One document-local ResponseFieldSchemaBatch receives all eligible retained primary/extras in route/insertion order, with distinct ordinal+mode keys. It calls the existing native Pydantic generator once. Pydantic handles both passes, ref sharing and remapping (json_schema.py352–399); no callback counts, class names, fixture IDs or backend predicates influence behavior.
- Mapping lookup preserves every generated key, including siblings beside $ref. Nonref title comes from retained outer FieldInfo/name (v2.py254–282), including the registered unique ID. Inner Annotated Field metadata does not become outer title/alias metadata. Definitions stay separate, with source form-feed description truncation (v2.py337–341).
- Existing raw request/body/stream helpers remain explicit prior paths; the raw primary path remains only when no primary owner exists, e.g. current stream representation. It is not a retry after a batch/hook failure. Complete all-field modes/flattening/shared-generation remains unproved, including source's construction of flattened model owners before deduplication.

## Callback, borrow, failure and drop boundaries

Included field materialization remains before snapshot creation. The app borrow only clones strings/native plans/Py references. Retained core attribute reads, generator construction/input iteration, JSON callbacks, description processing, owner-title reads, summary formatting and final operation assembly run after that borrow ends. Snapshot owners survive both JSON passes and every lookup. No batch callback occurs inside the OpenAPI cache mutex.

Any generator/hook/mapping/title error propagates through PyResult without translation or alternate generation. Earlier user journal/warning effects persist; local batch state is discarded outside app/cache guards. Existing public openapi cache code is untouched: it snapshots cache/version, checks truthiness outside guards, generates completely, replaces only on success, records the captured version and drops retired schema after release. A failed attempt leaves prior cache/version unchanged; later calls create a fresh generator. Cache hits do not construct a batch. General reentry/concurrency, explicit cache setter and finalizer protocols remain separate prior gaps.

No endpoint dispatch, worker validation/response serialization, yielded cleanup, streaming scheduling or ASGI fault logic was modified. Existing pure-public simple native get_openapi route subset retains its existing operation construction except the agreed title Option/signature interface. Peer assembly must preserve complete refs, exact model-derived wire ordering and raw sends; parsed-schema equality alone is insufficient.

## Required closure and limits

Root combines both peer proposals, obtains independent full three-file source/diff review, applies only the reviewed patch, then owns fmt/clippy/static contracts, next 3 fixed-source parity and the unchanged prior 203 regression corpus. No positive compatibility claim follows from this static proposal. Broader request/body/stream owners, mixed modes, separate-input-output behavior, BaseModel/Enum flattening, collisions/recursive refs, final OpenAPI model validation/coercion, mutable/version history, custom metadata/statuses and generic callback error protocols remain unselected. The immutable sibling BackgroundTasks worker-crossing blocker is unchanged. No new fault hook is required for a public JSON-hook refusal.
