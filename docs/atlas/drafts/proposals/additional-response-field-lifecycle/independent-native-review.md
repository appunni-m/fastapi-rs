# Additional response fields: independent prospective Rust review

2026-10-05. Read-only source/ownership review of the unapplied temporary proposal.
No active edit, formatter, compiler/Clippy, build, installation, application,
native import, parity or unit test was executed. Only this independent note was
written. Input authorship, static implementation review and subsequent live
receipt evidence remain separate.

## Exact reviewed identities and applicability

- Patch: `/private/tmp/fastapi-rs-additional-response-field-native.patch`, SHA256
  `fa23af094f51bfaa768be42171b341e6b185719ef6e6ee0413723e6976064cc1`.
- Author note: `/private/tmp/fastapi-rs-additional-response-field-native-patch-review.md`,
  current/refrozen SHA256
  `1cbda85a7185e5091990b2cadea9be64f38737814850456aaeabcfedab9eea10`.
  The initial `7f1d356f...` note identity was superseded only by its alias-source
  precision paragraph; the executable patch and Rust copies stayed unchanged.
- Base/prospective copies:
  `/private/tmp/fastapi-rs-additional-response-field-native/{base,prospective}/`.
- Base repository revision in the proposal:
  `90556f4d714f24e2c389675e48f038b98a2becad`.

| Core file | Base SHA256 | Prospective SHA256 |
| --- | --- | --- |
| application_runtime.rs | `9608a3aacce77d8583617eed6a840dd48910fee3a0f256cb1463cd16b2dfeaad` | `f93d808770555d206443514050530b2d30d487f7c19eff12f18c7bcef26a2f67` |
| response_field.rs | `aa943aa0caa352ba579b58f9a1b3c0ee4f660c3f9400366d023b954e97aba825` | `952bc9fb4510c58b2d1f173859baad8eebd31ee608a9ad22d64b25bc5fe91732` |
| openapi.rs | `7b5f2109c53620a9ae7ed8c02e7ac6df31db5c1f944bd9a794568e036ec893dc` | `28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0` |

Each of the three active Rust files was reread and is byte-identical to its saved
base. The patch addresses exactly those three paths, with 381 additions/148
deletions; response_field.rs changes documentation only. Unsafe, allow-attribute
and panic/placeholder macro occurrence counts are unchanged. No facade, public
export, dependency, sibling, input, manifest or generated file is touched. This
review did not run git apply, a formatter or a compiler; applicability here means
the exact active source bytes agree with the reviewed saved base.

## Bounded static clearance

No concrete compile/type/ownership or selected lifecycle3 logic blocker was found
by reading. This is static clearance for the immutable 3-case/15-action proposal
and preservation of existing OpenAPI algorithms, subject to parent-controlled
compilation and live gates. It is not a build result, source reachability result,
passing parity result or a broad OpenAPI/response-dictionary support claim.

### Empty declarations and direct attachment

`PyOperationDecorator.responses` captures the raw optional Python value. The
declaration function no longer traverses it, truth-tests it or generates a schema.
At attachment, `route_response_declarations` constructs a shallow outer PyDict,
preserving insertion order and references to nested records/annotations. None or
an ordinary empty mapping produces an empty vector without adapter or JSON work.
Ready fields still contain the independently constructed optional primary owner.
The direct-OpenAPI compatibility check reads that outer dictionary's emptiness.

Name/path/scope/unique-ID setup precedes extra construction. All extra fields then
complete before endpoint callable validation, CallablePlan/dependency processing
and the primary field. This matches the relevant source ordering in FastAPI
`routing.py:1000-1074,1103-1114`; saved decorator processing is deferred to the
source attachment stage (`2973-3038`). The native sibling Route metadata setup
and preexisting endpoint/name/classification callbacks are not asserted to reproduce
all source callback ordering outside the selected ordinary async endpoints.

Direct app borrows used before field work only clone metadata/default references.
Field construction is outside them. Publication occurs after successful field
preparation. At fallible registration exits, the later-declared app guard drops
before outer newly prepared owners. Existing operation-table partial publication
on a later registration failure remains an acknowledged earlier boundary.

### Model truthiness, status policy, errors and warnings

Every entry is visited in input order. Its selected model receives one truth test;
missing/falsy models build no field and skip the body assertion. A truth-test
exception propagates as its original PyErr. Truthy models use Python int plus
comparisons: integer statuses at least 200 except 204, 205 and 304 allow a body. There is
no added u16 narrowing for extra statuses. The assertion and field names use
Python format and retain source wording for the accepted integer subset. A
non-dict nested entry receives the source assertion text.

The existing integer-not-bool, explicit nonempty-description and description/model
key subset is still restricted. Policy checks occur before model work; that is
not the general source mapping protocol. Dict subclasses, custom status/hash/
format callbacks, false-model giant-int formatting and mutable record histories
are not proved by the selected ordinary inputs. In particular, the native status
string conversion also occurs for a falsy entry at construction, whereas the
source retains its raw key until later schema processing; no broad callback
timing claim is made for those excluded forms.

Extra construction calls the unchanged reviewed ResponseField constructor,
including FieldInfo decomposition, serialization adapter, narrow warning filter
and schema-error translation. Arbitrary user hook errors and UserWarnings remain
preserved. There is no blanket new catch, coercion or warning suppression.
Included matching-time failure continues through the existing public exception
handler/response path before endpoint or yielded-resource entry.

### Independent owners and included branch publication

Each status invokes ResponseField::new separately, even with the same annotation.
The ordered extra owners are distinct from the primary. Including a router clones
raw declaration references and marks its bundle deferred; it never clones the
original router's ready adapters into a context. Each reached prefix creates new
extra owners, then its primary. Schema snapshot clone_ref copies those already
owned references without accidentally rebuilding an adapter.

The existing IncludedFieldBranch visit/index schedule is retained. A visited
branch snapshots all own raw inputs under a short borrow, builds every complete
bundle locally outside it, and only then validates all destination indexes and
the exact descendant branch marker. The commit replaces whole Ready bundles and
marks readiness with no fallible Python calls. Retired bundles drop after the
mutable app guard is released. On an earlier preparation/validation error, outer
prepared owners drop after any inner app guard. A second-extra refusal therefore
publishes none of that branch; retry rebuilds earlier successful local extras.
An already published parent remains independent from a later failed child, as in
source `routing.py:1430-1478,1599-1625`.

The new code adds no callback/destructor while holding app/router/cache guards.
Snapshot failure discards only additional references still owned by unchanged app
routes, so those borrowed snapshot operations cannot trigger last-reference
retirement. Existing include-time CallablePlan/route-metadata work under borrows
is unchanged and remains outside this bounded field repair.

### Public and ASGI OpenAPI service

Owned `slf: Py<Self>` for public openapi and its Rust ASGI call remove the former
outer app borrow across generation. Cached schema/version references are cloned
under a short app/cache guard; schema truthiness runs after both are released.
A current truthy cache returns without materialization or JSON work. A miss
materializes included bundles, clones complete existing metadata/operation/plan/
extra-field inputs, and performs schema/attribute/encoding work outside guards.
Snapshot operations add references without executing user hooks.

Successful cache publication uses replacement under a brief guard, records the
version captured before generation and drops the retired schema afterward.
Generation errors leave the prior cache/version untouched. Root-path response
adjustment and JSON encoding now also occur outside the app borrow. New schema
ownership does not validate an endpoint result through its returned extra status;
the primary runtime field and returned-Response bypass are untouched.

The preexisting cache condition remains version-first, unlike source
`applications.py:1084-1104`'s schema-truthiness-first condition. Ordinary PyDict
cache hits/misses are unaffected; observable custom truthiness/version mutation,
reentry/concurrent publication and the existing explicit setter's replacement
under its mutex remain excluded. The review does not assert those are fixed.

### Retained adapter schema and exact alias fallback

Extra JSON generation reads the retained field adapter's core_schema and uses the
factored generation half of the existing native one-field generator. Other schema
callers still construct their old raw adapters and use the same generation half;
parameter/body/primary/stream assembly is not replaced. Included OpenAPI misses
can newly materialize primary fields alongside extras, as source context
traversal does; prior hook timing therefore still needs actual regression gates.

For a non-$ref schema the helper overwrites title, using a truthy FieldInfo.title
or serialization alias/alias/name plus Python title().replace('_',' '). The old
assembler overwrite with a freshly derived operation name is removed. A $ref
keeps its schema/definitions behavior, preserving the existing TeaError regression
shape; description-only entries generate no model schema.

Pinned `_compat/v2.py:121-124` returns raw alias whenever it is **not None**,
including empty string. `130-133` uses truthiness for serialization_alias, and
`267-279` selects serialization_alias or field.alias and title. The patch's raw
alias `is_none()` fallback is therefore correct; changing it to `is_truthy()`
would turn alias='' into the field name and differ from source. Title and
serialization-alias truth tests are appropriate. Scalar string/None metadata
matches this rule. The source computes field_alias before reading/applying title,
while the helper skips alias reads on a truthy explicit title; descriptor/custom
attribute side effects are a wider unselected ordering gap.

No selected new case requests OpenAPI or positively validates mode/title/alias/
definition mapping. The existing two regression controls select their documented
outputs only; a flat Annotated/Field OpenAPI gate remains necessary before a
positive non-$ref title claim. Shared field mapping, flattened models, mode
collisions, callbacks and mutable schemas remain explicit older gaps.

## Required parent gates

Close fixed-source/fixed-input source then unchanged-target lifecycle3 first;
retain ordinary construction and handled-error observations. After explicit
application, parent runs formatting, strict Clippy and static contracts, then
fresh lifecycle3, the previous 198 cases and existingOpenAPI2 (203 total) with unchanged exact
selectors. Fresh normal coverage86 and separate fault55+6 need their own native
identities, completed receipts/provider evidence and restoration proof. This note
adds no expected values, exception normalization, comparison shortcut or test.
