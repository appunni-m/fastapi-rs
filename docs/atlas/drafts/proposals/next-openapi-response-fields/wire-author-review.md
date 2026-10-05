# Prospective OpenAPI wire assembly review

Date: 2026-10-05. Author: `/root/dependency_records_runtime` (Sol).

This is a TMP-only, unformatted, uncompiled Rust proposal. It changes
`fastapi-rs/src/openapi.rs` only and is not installed or applied to the active
tree. No builder, application, native import, parity run or unit framework was
executed. It requires the independently authored runtime/response-field patch
and independent combined review before the parent's format, strict Clippy,
static contracts, build and live parity gates. No compatibility or performance
claim follows from the static checks here.

## Frozen identities

The base is byte-identical to active `openapi.rs` and to
`827612f28226dc5c0d6e008d1a38231c03293389:fastapi-rs/src/openapi.rs`.
Documentation/admission-only HEAD at readback was
`bbac9b5e16aace4a29bfd2521ba623eb4f2b55fe`.

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `openapi-base.rs` | 43280 | `28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0` |
| `openapi.rs` | 52851 | `483e4ed5b7851f07468a328d6ec7cf0961b9af19ee969d42370aa26d21e7dfcf` |
| `openapi.patch` | 17036 | `bd4d6c53f18ec8b314431eb21f2d02179b643202e2fc1e7c03793d629b43765c` |

All files are under `/private/tmp/fastapi-rs-next-openapi-wire-native/`.
`static-review.json` records the text/source checks. This note is hashed in the
handoff after saving. Historical design:
`/private/tmp/fastapi-rs-next-openapi-wire-design.md`, SHA256
`8ff481b83db25e3ede17507a8017aa84716fcc4606f71a07d46418a777a97f60`.

Pinned source is local FastAPI 0.141.1 commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, sole Starlette 1.6.0 oracle commit
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and immutable native sibling
`/private/tmp/fastapi-rs-starlette-rs-b4c8a65`. The model descriptor source
`../fastapi/fastapi/openapi/models.py` hashes
`b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`.

## Source contract and bounded implementation

Pinned `openapi/utils.py:602-679` assembles dictionaries, sorts document
definition names at 668-669, then calls
`jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)` at 679.
That model construction does more than order keys: it validates, chooses
unions, fills defaults, converts aliases and values, and handles extras.
The proposal reproduces declaration order for valid dictionaries emitted by
the existing native assembly. It does not construct the source OpenAPI model
graph or claim that complete validation behavior.

`encoders.py:243-258` serializes models in JSON mode; 281-317 preserves the
resulting dictionary traversal order while applying the existing encoder's
exclusions; 318-334 preserves item order. The Rust finalizer runs once after
native assembly, before the existing native jsonable encoder with unchanged
options. It creates fresh model dictionaries, inserts present known fields in
the source alias/declaration order, then appends unknown fields in input order.
It does not add absent fields or mutate the generator's schema dictionaries.

Twenty-two descriptor arrays match pinned source classes including inherited
Parameter/Header fields. The source ranges are `models.py:61-114`, 123-204,
212-218, 228-319, and 399-430. Schema's external key array is moved to the single
`SCHEMA_WIRE_FIELD_ORDER` constant, reused by both existing `schema_key_rank`
and the new Schema node. The earlier Schema normalizer still owns its existing
ref rewrite, default handling, binary conversion and numeric conversion;
the finalizer does not repeat these policies.

Typed child traversal covers Info/contact/license; server variables; paths,
operations, response/header/content/link objects; components and named
definitions; media/example/encoding objects; request bodies and parameters;
Schema-valued properties and subschemas; discriminator/XML/external docs/tags.
No field-name heuristic is used outside these semantic contexts.

Named maps retain name and insertion order: paths, statuses, media types,
property names, definitions at their already assembled order, headers, links,
examples, callback expression maps, and server variables. A property named
`title`, `type` or `$ref` remains a property name; only its schema value receives
Schema ordering. Dictionary defaults, const values, enum elements, examples,
Example.value, Link.parameters/requestBody, discriminator mappings, security
requirements and unknown extension values have Any semantics and retain their
original data at this stage. The ordinary encoder still performs its existing
recursive conversions/exclusions. Security scheme unions remain with the
existing assembly/encoder; this draft does not guess their variant from keys.

There is no blanket `$ref`-to-Reference conversion. Source `Reference`
(`models.py:95-96`) ignores extras, while Schema allows extras and union choice
depends on validation. The bounded finalizer preserves `$ref` sibling keys in
mapped response schemas, including user extensions, and does not reconstruct a
singleton reference or erase those siblings. Invalid/ambiguous Reference and
model/Any union fallback remains an explicit gap.

## Shared response batch interface

The separately owned prospective files are under
`/private/tmp/fastapi-rs-next-openapi-native/`. Interfaces are coordinated with
`/root/override_reanalysis`:

- `OpenApiOperation.response_schema_title: Option<String>`; retained mapped
  primary fields supply `None` because their owner title is already applied.
  Legacy unmapped/direct subsets supply `Some(previous_title)`.
- Mapped primary and extra fields supply `response_model_name: None` so the
  actual mapped schema, including reference siblings, is consumed.
- `OpenApiInfo` adds `openapi_version: &str` and
  `tags: Option<&Py<PyAny>>`. The application supplies `"3.1.0"` and `None`,
  retaining its existing selected behavior.
- `openapi_document` takes a final
  `shared_definitions: Option<&Py<PyDict>>`. The application passes
  `Some(&response_schemas.definitions)` from one document-local retained-field
  generator batch; the public direct subset passes `None`.

Shared definitions explicitly seed the existing sorted schema map. They are
not inferred solely from each field schema's `$defs`. Existing request/body,
parameter and stream collection is retained; its merge-by-name and normalization
semantics are not promoted to complete source-wide shared-generation support.
Mixed modes, request/response name collisions, nested model/Enum flattening,
custom maps and unselected shared-definition phases require separate gates.

This file does not build adapters or generators, reanalyze response fields,
interpret fixture identities, or change endpoint invocation. Root's combined
review must bind the separately frozen runtime/helper identities.

Peer handoff identities at this review freeze:

| Peer file | SHA256 |
| --- | --- |
| `application_runtime.rs` | `3e64ac2c566682ead3dd9172ca30df51195358efc142f61dd52c1a9cd3df437b` |
| `response_field.rs` | `562136969b3192427a497c5e8a61283bbcd41b01e96e9aa05d515ea796a734aa` |
| `next-openapi-native.patch` | `7f744b2ab2649a8fa14747f15e39796e1ea0a73734f150ad0948148852963807` |
| Peer author review | `a4613bebb9a4329fcb1f372a136380fb1af2018452602b798f0eda8790ef37d6` |

## Public entry points and cache boundaries

Public `get_openapi` moves its requested OpenAPI version and tags into common
assembly before finalization, so these valid values receive the same encoder
and field ordering as application-generated output. It retains the current
empty-route/one-simple-native-GET subset and webhook rejection. Other existing
options already enter `OpenApiInfo`; no public signature is expanded.

The existing direct subset's post-output externalDocs URL validation using
`TypeAdapter(AnyUrl).validate_python` is retained. This does not reproduce full
source `ExternalDocumentation` validation or its precise timing; contact,
license/server/tag invalid-value errors, URLs, EmailStr, constraints and all
OpenAPI model alias/exclusion semantics remain separate uncertainties.

Application-owned snapshot collection, batch generation and finalization occur
outside app/cache borrows. The finalizer has no application handle, lock or
borrow. Its fresh dictionaries/lists hold ordinary owned Python references;
errors propagate through `PyResult` and temporaries drop outside app/cache
guards. Existing successful-only OpenAPI cache publication and later retired
reference drop remain caller responsibilities. Cache hits do not regenerate
or refinalize the cached document.

Root-path docs behavior remains a later overlay: source
`applications.py:1108-1118` and native docs handling may insert/update servers
after the cached base document was generated. This proposal does not reorder
that overlay or claim mutable cache/reentrant/concurrent history parity.
Custom dictionary/list subclasses, key hashing hooks and unusual cycles can
observe extra copying/traversal; those behavior paths remain unexercised.

## Evidence and required gates

Parent's fixed input digest `558a3d9c...` covers three constructor outcomes and
nineteen actions, with full raw schema bytes, ordered sends, warning/error/hook
journals and public cache identity/retry observations. The closed source versus
unchanged-target pre-run had three failures, no skip and all planned actions
completed. Its initial state matched all three. Source and target each made
six JSON-hook calls in the shared-ref shape; this is not one-call hook dedup
evidence. The target's extra primary core construction, pass-order differences,
field-title/name differences, schema wire order and lost reference siblings are
addressed by the combined prospective patches, subject to fresh live results.

Required after combined independent review: format and strict Clippy; existing
API/metadata/facade/dependency/static contracts; fresh same-input source+target
new-three comparison with exact raw bytes and full journals; all 203 previously
selected normal cases including both legacy additional-response OpenAPI
controls; appropriate coverage/fault receipts; recorded binary/source identity
and normal restoration. No fixture, comparator or expected-output substitute
is part of this proposal.

Automatic 422 placement is a separate existing gap. Source
`utils.py:473-529` merges extras first and then inserts 422 only if 422, 4XX and
default are absent. Current native assembly inserts its automatic 422 before
extras. This patch preserves that construction; the next-three routes have no
request fields selecting it. A distinct public parity gate is required before
an ordering/suppression compatibility claim for that branch.

Further bounds: complete OpenAPI validation/coercion/constraints; true
Reference and smart-union choices; arbitrary Any fallback under response/path/
callback unions; nondefault outer response-field aliases/title/modes; source
model flattening and mixed request/shared fields; custom mapping/iterable/error
hooks; unsupported direct get_openapi/WebSocket/webhook branches; mutable route
or cache snapshots, callback reentry/concurrency. Preserving Any extension data
does not establish these contracts. Source classification is not target support.

## Static checks actually completed

- Base equality against active source and saved implementation commit.
- AST-only comparison of all 22 descriptor arrays with pinned source aliases
  and inheritance; no duplicate descriptor keys.
- One Schema order constant and rank function reuse confirmed by source read.
- Shared definitions argument and peer call sites read back consistently.
- `git apply --check openapi.patch` succeeded against the active base.
- No unsafe, new lint suppression, original FastAPI runtime import or fixture
  dispatch introduced.

These checks are text/source admission only. Rust formatting, compilation,
Clippy and live outputs have not been verified by this author.
