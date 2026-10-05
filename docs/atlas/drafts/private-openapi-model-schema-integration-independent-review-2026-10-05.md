# Independent Schema/email/integration review

2026-10-05. Read-only review of frozen peer-authored Rust. No active source
edits, formatter/compiler, native imports, apps, parity or unit framework.
The reviewer's own `openapi_models.rs` is explicitly outside independent scope;
its agreed interfaces are checked only at these peer call boundaries.

## Frozen identities

| File | SHA256 |
|---|---|
| openapi_model_schema.rs | 61fce7d296203569b5e4f85b1a41f78dd9ca489030a7a95da3e5527fd1b398db |
| openapi_model_email.rs | bc1e793e253722163924e32e6daf73785bfdd3f6639a13b234c7e9150a1ddcd0 |
| integration/openapi.rs | da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7 |
| integration/lib.rs | 1f46ec965e3646c03a2da56ad6548dd8735f2a21b77ee5a02e7c49a2e1698be4 |
| integration patch | 8e97b13ca103952f5c20dc01b669cf244a88fb618300e36773ce83e19bff2cba |
| integration author note | 03c73f448cb72cc4f501a29791b9c035dc6fe308262d9cb7fbae2a771196bd39 |

Companions are in `/private/tmp/fastapi-rs-openapi-final-model-native/`;
integration files are in `/private/tmp/fastapi-rs-openapi-final-model-integration/`.
Pinned source `fastapi/openapi/models.py` hashes
`b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`.

## Findings

No concrete compile/logic/ownership blocker found by reading these four Rust
files. This is bounded static clearance, pending root compilation and live gates.

1. An independent source AST/table comparison matches all 61 ordered Schema
   declarations, 12 aliases, 8 `ge=0` constraints, 1 `gt=0` constraint, None
   defaults and the exact deprecated-example message/metadata. Direct
   SchemaOrBool fields retain source `Optional`; remaining nullable forms use
   source PEP 604 union order. Recursive and companion type-name ForwardRefs
   agree with the main builder's namespace contract. Field aliases remain
   metadata and do not replace the Python attribute names.
2. Email selects Pydantic EmailStr only after the optional import and source
   assert. Its try includes both import and EmailStr lookup; only ImportError
   takes the fallback. Logging is captured before the try as source imports
   the logger before its optional branch. The fallback str heap type has the
   source module/name, native classmethod callbacks, warning-before-stringify,
   with-info plain validation and exact string/email JSON-schema result.
   Callback arguments and owned logger references are consistent with PyO3
   and Pydantic's pinned calling conventions by reading.
3. Integration deletes the role-order traversal and all its private shapes,
   calls the agreed final root model exactly once, then uses the unchanged
   Rust encoder options (`by_alias=true`, `exclude_none=true`, JSON-mode model
   dumping through the existing encoder). Pinned `openapi/utils.py:679` makes
   these same two calls. No dictionary-shape union-selection heuristic or
   alternate fallback output remains at the finalization boundary.
4. The direct public API delegates to the same finalizer. It removes the second
   late TypeAdapter(AnyUrl) rewrite. `models.py:112–114` puts URL validation on
   ExternalDocumentation inside OpenAPI construction; errors now propagate
   from that root before encoding, preserving its model title/location rather
   than substituting a later standalone URL-adapter error. This is source
   control-flow evidence; no new live invalid-URL result was produced here.
5. Each collected operation's security model is encoded before global scheme
   insertion/dedup. `utils.py:140–146` encodes selected scheme models before
   definition insertion. This supplies ordinary dictionaries to the canonical
   graph instead of accepting unrelated same-named native BaseModel instances.
   Per-operation repeated definitions are encoded separately; earlier
   snapshot collection still controls which dependencies/name are available.
6. Private module declarations and main registration precede application and
   OpenAPI registration. Companion native callbacks require no public module
   exports. Registration errors propagate before user factories. No facade,
   sibling, dependency or public model binding changes appear in this patch.

## Ownership, retained pipeline and cache

The integration does not change application/response-field code. The retained
shared definitions parameter, normalizers, schema rank table, public annotation
installation and collection helpers are byte-preserved by static comparison.
Primary/extra field batching and its selected hook order remain upstream of
this finalization boundary.

The unchanged application path releases its snapshot borrow before response
batch generation, operation assembly and final model/encoder callbacks. Its
cache getter releases app/mutex guards before truthiness. A failed finalizer or
encoder returns before cache publication. Successful cache replacement retires
the old reference after both guards leave scope (`application_runtime.rs:
3233–3262,4047–4097`). New code adds no app/cache guard. Local document, schema,
definition, model and callback references retire outside those guards; normal
owned PyO3 references support error propagation. The direct API's native
callable is stateless and holds only an immutable receiver borrow.

## Static receipts and applicability

- `openapi-final-model-native/cross-review-schema-static.json` records the
  independent source AST/table audit without executing source or models.
- `openapi-final-model-cross-review/integration-static-receipt.json` binds the
  integration hashes, finalization/security order, preserved helpers and
  private registration.
- The integration patch passes `git apply --check` against detached TMP copies
  of its exact saved bases. The first check against the workspace found the
  patch already applied: workspace openapi.rs/lib.rs hashes equaled the frozen
  prospective versions. That was not an applicability defect; the detached
  check isolates applicability without altering the active tree.

## Limits and required closure

The private graph's source classification is not public model API support.
Email fallback legacy `__get_validators__` returns a native iter/next object,
not a Python generator; send/throw/close, callable names/reprs, introspection,
mutable history and generator-specific behavior are outside current evidence.
Both optional dependency profiles still need identity-bound inputs before
broader fallback claims.

Security snapshot collection already deduplicates within an operation and
captures scheme names before these callbacks. This patch restores the source
encoding boundary for the supplied operations; it does not establish arbitrary
same-request callback mutations or all collection timing. Existing schema
normalization and request/stream/mixed-mode flattening remain separate from
the source root model, as do public API signature subsets and mutable cache
history/concurrency. The inactive 422/default/4XX gate remains separate.

The previous whole 206 result remains failed evidence (205 pass / 1 fail /
0 not-run), not support closure. Root must compile and run fresh full 206,
the three raw-schema/hook/cache cases, existing security and four direct public
OpenAPI API controls, then selected same-build coverage/fault and normal
restoration. This note makes no parity, performance or completed-build claim.
