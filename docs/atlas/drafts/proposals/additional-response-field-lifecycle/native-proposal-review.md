# Additional response fields: prospective Rust patch review

2026-10-05. Unapplied, uncompiled Rust proposal under /private/tmp only, based on
unchanged runtime at 90556f4d714f24e2c389675e48f038b98a2becad. Active Rust files
are byte-identical to the saved bases. No active tracked source/facade edit,
build, install, app/factory/native import, parity execution, unit test or formatter
run occurred. Parent owns pre-gate closure, active application and all later checks.

Design: `/private/tmp/fastapi-rs-additional-response-field-native-design-2026-10-05.md`,
SHA256 `830fdc322053a08131bd1b85a2e53eaab49c4de8de588a51bfd93c330b340efb`.
Both independent peers cleared the selected source/input design boundary; the new
Rust delta itself remains subject to their independent read-only review.

## Proposed files and actual scope

Patch modifies only application_runtime.rs, response_field.rs documentation and
openapi.rs's extra-field title attachment (381 insertions / 148 deletions).
No dependencies, Python runtime code, public exports, injection points, unsafe or
new lint suppressions are added. It addresses the independently authored lifecycle
three-case / 15-action gate plus retained extra-schema generation for existing
OpenAPI selected-output regressions. It is not a new positive OpenAPI hook gate.

- PyOperationDecorator captures raw responses without parsing/truthiness/schema
  work at declaration. Attachment makes a shallow outer dictionary and retains
  nested response/model references, preserving source-order iteration.
- Metadata/name/path/unique ID and extra fields are prepared before CallablePlan
  and the primary field. Empty explicit operation ID uses source's generated-ID
  fallback. Extra names are Response_{status}_{effective_unique_id}.
- Ready RouteResponseFields has separate primary and ordered extra owners.
  AdditionalResponseField retains status, raw nested metadata and its own optional
  ResponseField. Identical annotations at different statuses build distinct fields.
  Description-only/falsy entries retain metadata without a field.
- Integer status keys retain the existing integer-not-bool policy; body assertions
  use Python int and comparison rather than a new u16 narrowing. Truthy models
  reject values below 200 and 204/205/304 with exact source assertion text. Source
  false models skip this assertion. The current explicit nonempty description and
  description/model-only subset is retained, with parsing deferred to attachment.
- Included routes clone raw declarations, not fields or generated schemas. Each
  visited context constructs fresh extras before its primary. Whole own-branch
  bundle preparation succeeds before any publication; failed preparation drops
  locals outside app borrows and retries the branch. Parent/child branch readiness
  remains separate. Retired bundles are dropped after the mutable app borrow.
- Public openapi() uses owned slf; the ASGI docs entry calls that same service with
  no surrounding app borrow. Cache misses materialize included bundles, then clone
  complete existing document/operation inputs (metadata, CallablePlan references,
  response options, extra fields) under a short borrow. Attribute reads, raw record
  parsing, schema generation and assembly run against owned snapshots outside it.
- Cache publication records the version captured before generation, replaces the
  old schema nonfallibly, then drops it after cache lock/app borrow release. Failed
  generation leaves prior cache untouched. Cache hits skip field/JSON construction.
- Extra JSON generation consumes its retained adapter.core_schema through the
  existing native one-field GenerateJsonSchema path. Other schema callers still
  construct raw adapters exactly through the old path. Existing full document
  assembly is retained, not replaced by selected pointers or reduced schemas.
- Every non-$ref extra schema receives retained FieldInfo.title or its
  serialization_alias/alias/name transformed by Python title().replace('_',' ').
  The assembler no longer replaces that value with a newly derived operation
  name. $ref and definitions remain available to existing component assembly.
  Legacy TeaError tests only the $ref branch; flat Annotated title behavior needs
  a separate positive input gate before any support claim.
  Pinned v2.py121-124 uses `alias is not None`, retaining an empty alias;
  serialization_alias130-133 and explicit title278 use truthiness. The current
  Rust `alias.is_none()` fallback is intentional. Replacing it with is_truthy()
  would lose the source's empty-alias title behavior. Root and the independent
  native reviewer reread and confirmed this distinction; executable patch is
  unchanged. Exact pinned v2.py SHA256:
  `b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9`.

## Source ordering and safety review

Pinned source routing.py1038-1054 builds extras in insertion order, then
1056-1074 builds dependency/body state and 1103-1114 builds primary. Effective
contexts1430-1478 rebuild fields; own vector1601-1624 commits only on success.
ResponseField uses the existing reviewed utils58-80/v2 constructor decomposition,
serialization mode, warning filter and narrow schema-error translation. New user
core/JSON hook errors propagate through existing public route/handler paths.

New app/cache borrowing regions only clone Rust/Py references, inspect readiness
and publish fully owned values. Field construction, truthiness, formatting,
metadata/model-name attribute reads, JSON schema hooks, encoding and last-reference
retirement remain outside those regions. Snapshot clone failure can only discard
extra references still owned by the app; it does not drop newly constructed fields
under the borrow. The preexisting included CallablePlan/route-metadata callbacks
at include time remain a separate source-order/borrow gap; this patch does not
move those callbacks or claim full effective-context population parity.

No new async control path is added. Endpoint/dependency dispatch, response bypass,
primary validation and serialization, generator cleanup and request-local caches
retain their existing implementation. Additional fields never validate based on
a response's actual status.

## Static checks actually performed

- `git apply --check /private/tmp/fastapi-rs-additional-response-field-native.patch`
  passed against active unchanged Rust bytes (no application performed).
- `git diff --no-index --check` between /tmp base/prospective directories emitted
  no whitespace diagnostics; exit1 reports the existing differences.
- Independent structural read verifies both route constructors retain raw input,
  both readiness publication sites publish a whole bundle, old eager parser/schema
  cloning functions are gone, both OpenAPI entry points use the owned service, and
  unsafe/allow-attribute counts are unchanged from base.
- All active Rust base bytes were reread and agree with the saved base hashes.
  No build, rustfmt/Clippy, runtime execution or unit test is claimed by these checks.

## Required gates and limitations

Root will first close source/unchanged-target lifecycle3 on the admitted same
inputs. Existing additional-response-model-openapi pointer and
path-operation-other-verbs-responses description controls have already closed
unchanged-target pre receipts under
`parity-results/additional-response-field-wave/pre-openapi-controls/`.
After active application is explicitly authorized: fmt/strict Clippy and static
contracts, fresh same-input lifecycle3 plus all 198 prior cases, the two exact
OpenAPI selected-output regressions, fixed-source instrumented evidence/faults
and restoration as root selects. Retain failures and constructor/action/raw-send
boundaries. No expected output or comparator normalization is introduced.

The lifecycle3 does not request OpenAPI. Primitive traced fields expose premature
JSON-hook presence, not positive generation order/mode/schema mappings. Separate
inputs are needed for flat Field title/aliases, false models/body-forbidden status,
JSON-hook cache failures/recovery, shared modes/definitions/collisions and broader
schemas before claims extend.

Old primary/request/body/stream raw-adapter generation, shared generation and
flattened model construction remain unchanged gaps. Source OpenAPI can create
flattened-model fields; universal absence of core hooks there is not promised.
Source locking/reentry/concurrency/version refresh, raw route proxies, arbitrary
mutable dictionaries/annotations/defaults, custom status/dict hash/format methods,
custom unique-ID functions, multi-method groups, callbacks/webhooks and broader
status/response metadata signatures remain separate boundaries. Explicit
openapi_schema setter's preexisting replacement under its mutex is untouched;
this patch's own publication drops retired schemas outside locks. Complete
worker18 still depends on the unresolved pinned sibling BackgroundTasks boundary.

## Frozen hashes

| Artifact | SHA256 |
| --- | --- |
| Patch | `fa23af094f51bfaa768be42171b341e6b185719ef6e6ee0413723e6976064cc1` |
| Base application_runtime.rs | `9608a3aacce77d8583617eed6a840dd48910fee3a0f256cb1463cd16b2dfeaad` |
| Prospective application_runtime.rs | `f93d808770555d206443514050530b2d30d487f7c19eff12f18c7bcef26a2f67` |
| Base response_field.rs | `aa943aa0caa352ba579b58f9a1b3c0ee4f660c3f9400366d023b954e97aba825` |
| Prospective response_field.rs | `952bc9fb4510c58b2d1f173859baad8eebd31ee608a9ad22d64b25bc5fe91732` |
| Base openapi.rs | `7b5f2109c53620a9ae7ed8c02e7ac6df31db5c1f944bd9a794568e036ec893dc` |
| Prospective openapi.rs | `28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0` |

These are source-proposal hashes, not live build, binary or coverage identities.
The proposal and this review are frozen pending independent review/authorization.
