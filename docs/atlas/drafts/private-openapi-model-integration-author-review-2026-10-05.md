# Prospective final OpenAPI model integration

Author freeze, 2026-10-05. These two prospective Rust files and their patch are
under `/private/tmp/fastapi-rs-openapi-final-model-integration/`. No tracked
source, metadata, recipe, comparator, sibling or binary was modified. No
formatter, compiler, build, application, parity or unit framework was run.
This is an uncompiled source-backed implementation proposal, pending the
combined independent review and parent-owned live closure.

## Changes and source boundaries

1. `openapi_document` constructs the complete ordinary document, calls the
   private `OpenAPI(**document)` graph, and passes that model to the existing
   Rust `jsonable_encoder` with `by_alias=true` and `exclude_none=true`.
   Pinned `fastapi/openapi/utils.py:679` performs those exact two operations;
   `fastapi/encoders.py:243-258` supplies JSON-mode model dumping. The generic
   role-based wire-order tree is removed. The actual graph and Pydantic engine
   choose typed model versus `Any` branches and the resulting key order.
2. Each operation's security scheme model is encoded before
   `register_security_scheme`, using the same Rust encoder options. Source
   `openapi/utils.py:132-146` performs model encoding before definition-dict
   insertion; `get_openapi_path` invokes that for each operation. Components
   receive those ordinary dictionaries. Encoding only the global deduplicated
   vector was an earlier unpublished draft; its patch bytes remain in
   `draft-history/initial-global-security-encoding.patch`.
3. Public `get_openapi` returns `openapi_document` directly. The second, late
   `TypeAdapter(AnyUrl)` externalDocs rewrite is removed: source
   `openapi/models.py:112-114` retains `ExternalDocumentation.url: AnyUrl`, so
   the real final graph validates/normalizes the URL before model dumping.
   This also preserves source error timing instead of validating again after
   output encoding. The existing public subset and signature are unchanged.
4. `lib.rs` declares three private modules and registers the main graph once
   during native core registration, before application API registration and
   user factories. There is no facade export, original FastAPI runtime import,
   evaluated Python source, unsafe code or new lint allowance.

`SCHEMA_WIRE_FIELD_ORDER`, `schema_key_rank`, schema normalization, response
batch definitions, field mapping/title/ref behavior, assembly metadata types
and all application/response-field interfaces remain byte-preserved here.
The model finalization boundary is not a replacement for schema normalization.

## Coordination and ownership

Main graph API agreed with the runtime peer:

```rust
pub(crate) fn register(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()>;
pub(crate) fn finalize_document<'py>(
    py: Python<'py>, document: &Bound<'py, PyDict>
) -> PyResult<Bound<'py, PyAny>>;
```

The private core handle is `_FastApiOpenApiModel`. The main builder creates and
rebuilds all descriptor models before publishing that handle. Companion APIs
are `schema_fields(py) -> PyResult<Py<PyDict>>` and
`email_type(py) -> PyResult<Py<PyAny>>`; those callback classes need no separate
public module registration. Main and companion content remain peer-owned.

Document assembly, per-operation security encoding, final graph construction
and model encoding run on owned operation/schema snapshots outside any app or
response-field cache borrow. Existing application cache code is untouched:
errors propagate from the graph or encoder, and successful output alone is
published. Failed temporary model/document values unwind without adding a
fallback document, alternate ordering path or exception special case.

## Review limits and closure gates

- The application snapshot currently deduplicates schemes within one operation
  before this function sees them. This diff restores per-operation encoding
  before global deduplication; arbitrary repeated same-name security dependency
  callback counts within one operation remain a prior collection limitation.
- Graph descriptor fidelity, email fallback and schema validators are reviewed
  separately in the peer-owned modules. No build or behavior result follows
  from these two files alone.
- Existing request/body/stream schema construction and broader mixed-mode
  flattening remain outside this change. The retained primary/extra shared
  batch and its source-ordered JSON hooks remain intact.
- The preserved normal run is failed evidence: 44 whole workflows, 206 selected,
  205 passed, 1 failed, 0 not-run. Its exact raw OpenAPI mismatch and frozen source,
  input, binary and artifact bindings are in `failed-206-evidence-audit.md`.
  No coverage, fault, restoration or equivalent-benchmark closure is claimed.
- Parent-owned fresh gates must include the full 206 regression and the four
  existing public API cases in `openapi-get-openapi-public-api` and
  `openapi-get-openapi-single-route`; those two API workflows are not members
  of the 44-workflow normal ledger. The older two ASGI OpenAPI output controls
  do not replace these direct public API controls.
- The immutable Starlette-RS pin and its documented BackgroundTasks worker
  crossing blocker remain unchanged. Historical benchmark artifacts retain
  their old manifest bindings; any fresh benchmark gate must be measured and
  recorded separately by the parent.

## Frozen author files

| File | SHA256 |
|---|---|
| openapi-base.rs | ce1258b83ef4728aca7ad86fc038bac740022ea687b0a3b795eff629d8a1838f |
| lib-base.rs | b1cc63880964645182f5ede6c65d399e44fe3f8bcbdd034d371eb4d772904e3c |
| openapi.rs | da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7 |
| lib.rs | 1f46ec965e3646c03a2da56ad6548dd8735f2a21b77ee5a02e7c49a2e1698be4 |
| openapi-final-model-integration.patch | 8e97b13ca103952f5c20dc01b669cf244a88fb618300e36773ce83e19bff2cba |
| failed-206-evidence-audit.md | b004195da7c0538625fe1d4472f2ccc623334c920f4ae4fb92c01a9c635afda6 |

## Frozen peer composition

| File | SHA256 |
|---|---|
| openapi_models.rs | c3df23ba6819364fb8e39c1a07fd628fb1edb229ecf67b93a0234b48d5771b1d |
| openapi_model_schema.rs | 61fce7d296203569b5e4f85b1a41f78dd9ca489030a7a95da3e5527fd1b398db |
| openapi_model_email.rs | bc1e793e253722163924e32e6daf73785bfdd3f6639a13b234c7e9150a1ddcd0 |
