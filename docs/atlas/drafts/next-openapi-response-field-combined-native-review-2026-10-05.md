# Independent prospective OpenAPI native review

2026-10-05. Reviewer: `/root/dependency_records_native` (Sol).

## Status and review boundary

The final version-2 combined proposal has bounded independent static clearance.
No concrete remaining blocker was found in the selected three-case shape or
coordinated Rust interfaces. The review was completed without application,
compilation, formatting, native imports, application execution, parity runs or
unit frameworks. One source-order correction requested during initial review
was fixed and independently reviewed before clearance.

Runtime and wire findings bind their unchanged frozen files; helper findings
also bind the independently reviewed narrow version-2 delta. Static review is
not a target compatibility claim. The parent owns compilation, strict contracts
and all fresh live gates.

## Frozen identities and applicability

Reviewed implementation base: `827612f28226dc5c0d6e008d1a38231c03293389`.
Admission-only HEAD at review: `bbac9b5e16aace4a29bfd2521ba623eb4f2b55fe`.
Every saved base equalled both that Git implementation and active Rust source
bytes at the independent check; no installed/native binary was read.

| File | Base SHA256 | Initial prospective SHA256 |
| --- | --- | --- |
| application_runtime.rs | `14c6f7cf93865b8cc719055587d895ae517937212d14f105a7b5e2f6e7a5dfef` | `3e64ac2c566682ead3dd9172ca30df51195358efc142f61dd52c1a9cd3df437b` |
| response_field.rs | `952bc9fb4510c58b2d1f173859baad8eebd31ee608a9ad22d64b25bc5fe91732` | `562136969b3192427a497c5e8a61283bbcd41b01e96e9aa05d515ea796a734aa` |
| openapi.rs | `28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0` | `483e4ed5b7851f07468a328d6ec7cf0961b9af19ee969d42370aa26d21e7dfcf` |

The initial combined patch
`/private/tmp/fastapi-rs-next-openapi-combined.patch` has SHA256
`1f5695be5783debd7b93899f099eb9c89e67e2eb0634093ab2bffd2a7e98a07d`.
An independent unified-diff application entirely in memory checked every old
context line and hunk count, then reproduced the three prospective files
byte-for-byte: 13 runtime hunks, 3 helper hunks and 10 wire hunks. This performed
no filesystem patch application.

Initial shared patch: `7f744b2ab2649a8fa14747f15e39796e1ea0a73734f150ad0948148852963807`.
Initial shared author note: `a4613bebb9a4329fcb1f372a136380fb1af2018452602b798f0eda8790ef37d6`.
Wire patch: `bd4d6c53f18ec8b314431eb21f2d02179b643202e2fc1e7c03793d629b43765c`.
Wire author note: `2291258de20d6a7494ea69e50011dfc55831ba28e1dd96a76c0e698ecae18475`.
Wire static receipt: `43027e18d32898894787a08b0314a163017782ced5bd3bf418603834ee41596a`.

### Alias-order version 2

The author preserved all complete initial shared proposal files under `v1/`.
The revised response helper has SHA256
`3ef5dd24768f2ab096aec349ed6d17895a7844531e8dd1840e69f5412482c467`.
Revised shared patch:
`fbb3fceb06a5fee9c72b3e7eed429c822c570dd751bcddef88c00f8dff302344`.
Revised shared author note:
`c8356efab4c04d6a2ed3263a1cdd145e7e339ee4e4be2f4b64d14e66a526d863`.
Runtime, wire and both shared bases remain byte-identical to the initial
review. An independent v1/v2 diff confines this revision to alias resolution,
passing its owned result into title handling, and the mapping lookup ordering.

The new helper performs the raw serialization alias truth test, captures the
property's `sa or None` result, performs the outer `or` truth test and falls
back to raw alias/name with the source None-only condition. This happens before
mapping lookup. A truthy raw alias is tested twice, including possible
second-test false/error behavior. Only after successful mapping lookup does
the `$ref` guard skip title reads; a nonref reads/tests title and uses the
already captured alias when needed. Alias errors propagate before mapping
errors, with no relookup or alternate fallback. The owned alias survives
lookup/title processing and drops outside app/cache guards. This resolves the
initial source-order finding without broader mode or fixture claims.

### Final combined version 2 binding

Final patch: `/private/tmp/fastapi-rs-next-openapi-combined-v2.patch`, 34,263 bytes,
SHA256 `ec57db0d992b38325f3e2f8040843342e67c11b367ca95db3def7397d3950be1`.
It is byte-for-byte the revised shared patch concatenated with the unchanged
wire patch. Independent in-memory unified-diff application again checked each
context and count and reproduced exactly the final runtime `3e64ac2c…`, helper
`3ef5dd24…` and wire `483e4ed5…` files. Hunk counts remain 13/3/10. No active file
was patched by the reviewer. The initial combined patch remains historical.

## Source-backed findings

### Retained owners, order and field keys

Pinned `openapi/utils.py:551–582` collects each eligible route's primary response
field, insertion-ordered additional fields and stream field, alongside other
field groups. The proposal retains existing primary and additional owners in
the snapshot. Its response-only input vector collects each primary followed by
each actual extra owner. Operation reads consume exactly that same order;
fieldless extras do not increment the ordinal. Ordinal-plus-mode keys remain
distinct when fields share core references. Mapping errors propagate, rather
than falling back to rebuilding the primary adapter.

`ResponseFieldSchemaBatch` reads retained `adapter.core_schema` only after the
application snapshot borrow ends. The pinned Pydantic
`json_schema.py:352–399` accepts positional inputs, performs the two whole input
passes, returns `(key, mode)` mappings and separate definitions, and rejects
generator reuse. A new document-local generator on each miss delegates these
passes and remapping to Pydantic. No field or hook count controls native logic.
The closed pre-run observed six shared-ref JSON-hook calls in both products;
this does not support a universal one-call deduplication claim.

Source `v2.py:337–341` truncates definition descriptions at form feed; the helper
does the same after generation. Separate definitions enter the sorted native
component map explicitly. Actual mapped primary and extra schemas pass through
with `response_model_name=None`, preserving `$ref` siblings rather than
reconstructing a singleton model-name reference.

### Name and title provenance

Registration names/unique IDs already determine retained response field names
(`routing.py:1028,1103–1112`, `utils.py:58–78`). The new snapshot uses registered
route name for summary and fallback operation ID. Summary now calls the source
Python string operations `replace('_', ' ').title()` (`openapi/utils.py:281–286`).
Explicit nonempty operation IDs keep their existing precedence.

For a mapped non-reference schema, the owner supplies the outer FieldInfo title
or effective alias/name title. This is separate from inner Annotated metadata.
Setting the assembly title override to `None` prevents the legacy reconstructed
title from replacing that owner-derived value. The source does not overwrite a
schema containing `$ref`; sibling extensions survive.

The initial helper had a source-sensitive ordering difference: `v2.py:265–273`
computes `field.serialization_alias or field.alias` before dictionary lookup
and the `$ref` test, but the initial helper computed aliases only in the
non-reference/falsy-title branch. The version-2 correction retains both
source truth tests (`serialization_alias` itself is `sa or None`, then the
outer `or`), raw alias's None-only fallback (`v2.py:121–124`), and exceptions,
and is independently cleared as described above.

### Cache, callbacks and cleanup ownership

Included fields are materialized before snapshotting. New snapshot collection
clones native data and Py owners; generator construction, schema hooks,
description/title processing, wire assembly and encoding occur after release
of the app borrow. The batch, inputs and snapshots retain owners across both
passes and subsequent lookups.

The existing public OpenAPI method snapshots cache/version under a short guard,
checks truthiness outside it, builds the full document outside app/cache guards,
publishes only on success, and drops the retired schema after releasing guards.
A generator, hook, mapping or title error leaves cache publication untouched;
local generation state drops outside those guards and later calls create a
fresh generator. Ordered user journal/warning effects remain observable. Cache
hits bypass generation. The ASGI docs route releases its metadata borrow before
calling that public path, then retains the existing root-path overlay and send
path. No invocation, worker validation, yield cleanup or fault dispatch hunk is
introduced.

This is not a blanket reentry guarantee: the existing explicit cache setter
replaces its schema while holding the mutex. Source truthy-cache/version history,
route mutation, custom finalizers and concurrent/reentrant calls remain outside
the selected contract and unchanged by this patch.

### Wire contexts and public subset

Source final assembly is `OpenAPI(**output)` followed by the ordinary encoder
(`openapi/utils.py:638–679`). Its declaration order is observable in raw bytes.
An independent AST derivation of pinned `openapi/models.py` field declarations,
inherited fields and aliases matched all 22 native descriptor arrays exactly,
including Parameter/Header inheritance and all 61 Schema fields. The existing
schema ranker and finalizer use the same Schema order constant.

Named maps retain insertion order and names while their values receive the
appropriate context: path/status/media/property/definition/header/link/example/
callback/server-variable maps. Any positions retain their data at finalization:
defaults, consts, enum/example payloads, Link parameter/requestBody payloads,
discriminator mappings, security requirements and extension values. A property
named `type`, `title` or `$ref` stays a property name. There is no generic `$ref`
conversion into source Reference objects. The finalizer creates fresh model
dictionaries and does not mutate generator dictionaries. Subsequent ordinary
encoding retains its previous exclusions/conversions.

The public `get_openapi` simple-route/empty-route subset supplies its version and
tags before common finalization and preserves existing rejection boundaries.
All changed internal call sites/literals agree on the added shared definitions
argument, OpenApiInfo fields and optional schema title. Its existing late
externalDocs URL adapter remains after output construction; this is an explicit
timing/full-model-validation seam, not newly verified source behavior.

## Static safety and remaining gates

The 500 initial and 520 final added lines contained no unsafe block, new lint suppression,
original FastAPI import, evaluated Python helper, fixture/case identity,
backend predicate or class-name branch. Rust-owned Py references and local
Bound lifetimes presented no concrete new ownership/type issue by reading.
This does not replace Rustfmt, strict Clippy or compilation.

The response batch is not the complete source all-field generator: callback,
body, parameter and stream fields, nested BaseModel/Enum flattening, mixed modes,
separate-input/output options, component-name collisions and remapping between
the retained response batch and legacy helpers remain bounded gaps. The sorted
component merge retains existing normalization/merge policies. Full OpenAPI
validation, coercion, defaults, alias acceptance, smart unions/Reference
selection, URLs and arbitrary invalid dictionaries are not implemented by the
wire ordering table. Custom mapping/list subclasses, key/hash hooks, cycles and
mutable metadata may observe additional traversal/copying. Automatic 422
placement/suppression is an unchanged separate assembly gap.

Required parent closure after the revised independent review: apply only the
reviewed three files, format/compile/strict contracts, new-three exact fixed-input
source/target comparison plus all 203 prior normal cases, and independently
recorded coverage/fault/restoration measurements. No live pass is inferred here.

## Pinned source hashes read during review

| Source | SHA256 |
| --- | --- |
| FastAPI `_compat/v2.py` | `b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9` |
| FastAPI `openapi/utils.py` | `81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527` |
| FastAPI `openapi/models.py` | `b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d` |
| FastAPI `routing.py` | `7b1ef65fb6b209445dc43be070a23324b7879aef9c6b9f63e6968234b7723b55` |
| Pydantic `json_schema.py` | `75ade143dbd03cb1213ecac39d49628df4357ee0825621959d4cceac064b803b` |
