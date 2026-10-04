# Draft: FastAPI SSE operation review

**Scope:** `fastapi.sse.EventSourceResponse`, `fastapi.sse.ServerSentEvent`,
and its six fields. The reviewed overlays and case links live in
`metadata.yaml`; these are partial operation scopes, not full API support
claims.

## Evidence and parity

- Oracle pins: FastAPI `0.141.1` (`95f8322`), Starlette `1.6.0`
  (`4f250d6`), and Starlette-RS `80c0a26`.
- Input recipe: `tests/fixtures/input-recipes/parity/sse.yaml`, with 30
  cases from `tests/test_sse.py` and the SSE reference docs. It covers selected
  field encoding, raw vs JSON data, constructor validation errors, sync and
  async streams, POST, router/default response classes, and OpenAPI responses.
  Fixtures contain inputs only.
- FastAPI-RS binding: `fastapi-rs/src/sse.rs::register` and
  `fastapi-rs/src/application_runtime.rs::encode_sse_stream_item`.
- Current-manifest isolated parity at FastAPI-RS `2ca5e70`: 30/30 cases
  passed; no product or construction errors outside the expected invalid-input
  observations. Oracle artifact `2dcf68b4-cdc7-4eae-8878-9ab765eebe84`, target
  artifact `d1ebc80d-4b9f-4f25-8ac2-5b56ec930aa7`, comparison
  `cec576fe-8ff2-4715-9162-15c6c63c29b5`. Target runtime-boundary check passed.

## Limits

The streaming cases use immediately available items; they do not establish idle
keepalive timing, cancellation, disconnect, or every response constructor
option. The model cases do not establish general Pydantic configuration or
unobserved field combinations. The alternate `fastapi.responses.EventSourceResponse`
path remains source-classified uncertain, and `format_sse_event` remains an
internal helper; this review does not change either classification. No unit
tests or benchmarks were run for this review.
