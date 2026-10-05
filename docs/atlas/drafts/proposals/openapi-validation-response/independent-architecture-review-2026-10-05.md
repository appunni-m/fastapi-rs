# Independent automatic validation response architecture review

2026-10-05. Read-only source/native review at HEAD
`a34714f47749b6f96d5d7829dc16b0d444efaa5e`. This is a prospective implementation
review, not a live receipt audit. The parent reports closed source-first four
constructors/24 actions and four unchanged-target mismatches; another reviewer
owns the actual receipts. No app/native import, parity/build/install, unit
framework, active edit or sibling mutation was performed by this reviewer.
FastAPI 0.141.1, Starlette 1.6.0 and the existing immutable sibling pin remain
unchanged.

## Reviewed identities

| File | SHA256 |
|---|---|
| source_routing | `7b1ef65fb6b209445dc43be070a23324b7879aef9c6b9f63e6968234b7723b55` |
| source_utils | `0d7d15ae73307d5b19c51cfc222b50e36736fbef9f0f398566479131947650ca` |
| source_openapi_utils | `81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527` |
| native_application_runtime | `d1bdcd3f66118c38df96fbb75528264d298335d27f2ca275dcc699bdc4a280a2` |
| native_openapi | `da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7` |
| historical_design | `4769c1dad88b6d5e6aa073b9c4c26ef793f1cd609fcaa5ea619c0e8fa028127a` |
| active_recipe | `4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334` |
| active_workload | `9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130` |

## Source stages and minimum owned data

The historical design above remains accurate on these seams. Pinned
`routing.py:1015-1054` retains original additional status keys. Each record is
asserted to be a dict; its model is read and truth-tested. Only a truthy model
invokes body eligibility, raw-status field-name formatting and a serialization
field. Description-only or false-model records have no status conversion at
attachment. Primary status normalization is a distinct path.

A minimal native owner is `AdditionalResponseField.status: Py<PyAny>` alongside
the existing `Py<PyDict>` record and optional retained `ResponseField`. Literal
Python None must remain an owned value, not an absent Rust Option. Its
`clone_ref(py)` implementation, `RouteResponseFields::additional_fields`,
included-context preparation and `OpenApiRouteSnapshot` should clone that raw
owner without str/int/truthiness/hash work. No new cache or borrowed retained
Python lifetime is required. The current Vec preserves input order, while
source's separate response_fields dict lookup/hash histories remain unproved.

For the OpenAPI-facing additional response, retaining the raw `Py<PyAny>` until
per-operation assembly is the closest small ownership seam. A separate owned
canonical Python key can then be produced for document lookup/insertion. A
String projection should not be claimed to preserve arbitrary upper-return
objects or str-subclass/callback behavior. The four inputs use plain integer
and literal string keys, so they do not distinguish such projections.

## Attachment eligibility and errors

`fastapi/utils.py:26-40` requires, in order:

1. Raw None returns true.
2. Raw, case-sensitive membership in default/1XX/2XX/3XX/4XX/5XX returns true.
3. Otherwise `int(raw_status)`, then allow >=200 except 204/205/304.

The native integer-only/bool rejection and eager `.str()` at
`build_additional_response_fields:5426-5474` should be removed. A native helper
may use ordinary Python set membership and public int/comparison APIs with
`PyResult`; callbacks and exceptions must propagate without skipping records.
Matching an exotic collision's exact CPython frozenset probe history is not a
claim of this selected slice. There is no u16 upper bound in this helper.

Run this helper only after model truthiness. A disallowed body raises the
source assertion using the original formatted status; an allowed body formats
`Response_{status}_{unique_id}` from that original owner and constructs the
serialization field. Case-normalizing first would incorrectly accept a truthy
model under DEFAULT/lowercase 4xx. None/range keys and false/raising model
protocols have no positive input gate here, but the implementation should not
introduce a contradictory conversion order.

The existing explicit description/model-only, nonempty-description policy is
an older restricted metadata boundary. It is not FastAPI's general record
validation/deepcopy/deep-merge contract; keep that limitation visible rather
than claiming it repaired by raw key ownership.

## Documentation normalization and automatic 422

Pinned `openapi/utils.py:416-516` inserts the primary response first, then
processes extras in declaration order. Each key is obtained by
`str(raw_status).upper()`; DEFAULT alone becomes lowercase default. Existing
keys are updated in place, preserving their original insertion position.
Source deep-copies the extra record, removes model, calls setdefault, then
looks up the original-key response field and mapped schema.

There is a second distinct `str(raw_status).upper()` at the status-text stage,
followed by `int(raw_status)` for unknown ranges. This stage is evaluated even
when an explicit description is nonempty. Thus an unknown description-only
key can construct successfully and fail later at OpenAPI. Avoid moving this
conversion into route attachment or silently accepting it through a generic
string conversion. Keeping the existing restricted description subset does
not prove all deepcopy/recursive merge or unknown-key behavior.

`additional_response_openapi:5476-5497` currently maps the schema before wire
assembly; mapped field alias/title callbacks therefore are not a generally
exact interleave with primary/key/deepcopy operations. Either status
normalization seam must identify that retained callback-history boundary. The
selected four contain no models, custom key protocols or extra-field mapping
callbacks, so this does not block their bounded correction. Shared field batch
construction remains before operation merging, and no failed batch fallback
should be added.

At `openapi/utils.py:517-538`, automatic 422 is evaluated **after every extra**:
flattened parameter fields or a body field must be present, and the actual
merged response dict must contain none of 422, 4XX, default. In current
`openapi.rs:376-435`, move the automatic branch below the additional loop and
replace `operation.status != Some(422)` with ordered short-circuit PyDict
membership for those three literal keys. This also covers a primary response
class supplying 422; do not consult only the explicit Rust status flag.

The automatic response is appended after extras and its canonical definition
group is added only on that branch. Declared responses affect documentation,
not the existing RequestValidationError handler or endpoint validation. Retain
the actual private OpenAPI model/encoder finalization, shared definitions,
response refs/titles and sorted final schema assembly; no ordering visitor,
normalizer or case predicate is needed.

## Borrow, failure and publication bounds

Direct saved-decorator attachment builds extras before CallablePlan/dependency
and primary field construction and before publishing a route. Included branches
prepare each complete field bundle outside the app borrow, then publish the
whole branch atomically. Raw owners must be cloned under short borrows and
status/model/format/schema callbacks must execute outside app/cache borrows.
Failed preparation leaves the branch Deferred; partial and retired owners are
dropped after borrowed sections, preserving retry and reentry boundaries.

OpenAPI includes are materialized first; the retained schema batch and
operation wire work then run from owned snapshots outside the app borrow.
`PyFastApi.openapi:3233-3270` tests cache truthiness outside its Mutex/app borrow,
computes the complete new document outside them, and publishes only success.
Any new str/upper/int/hash/equality/dict/model callback error should abort that
attempt and leave the old cache untouched. Snapshot/key/schema owners dropped
on failure must not be held behind a long app/cache lock. No unsafe conversion,
original FastAPI runtime import or Python control-flow helper is necessary.

## Bounded conclusion and remaining source gaps

The selected four independent inputs are model-free required-int query routes.
They cover declared response order, canonical literal 4XX/default admission,
automatic 422 placement/suppression, complete docs/raw wire and normal valid/
invalid request behavior. No new fault hook is appropriate: all branches are
reachable through public declarations and requests. Review the author's frozen
patch before any implementation clearance; this note is not that patch review.

The validation definitions collision is a separate prior gap. Source starts
route-local definitions at utils.py:323, adds both definitions if the local
ValidationError is absent, and later globally updates at 646-647. Existing
BTreeMap entry.or_insert is not the same overwrite/group policy. These four
have no user models/definition collisions, so they cannot prove a collision
repair; do not silently expand or claim it fixed. Other retained gaps include
empty flattened parameter models/body-only eligibility, general response
metadata merge/deepcopy, mutable key/record histories, field-dict lookup
protocols and generic callback interleave. None calls for fixture identities,
backend detection, expected outputs or weakened selectors.
