# FastAPI error-contract review

Reviewed against FastAPI 0.141.1 (`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`)
and Starlette 1.6.0 (`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`). The source
checkouts report those exact package versions.

## Candidate inventory and selectors

The compatibility atlas lists 42 error/warning candidates: 8 supported error
records, 29 private/internal error records, 4 private/internal warning import
records, and 1 uncertain warning class (`fastapi.exceptions.FastAPIDeprecationWarning`).
The eight supported records are the root/module identities for
`HTTPException`, `WebSocketException`, and `WebSocketDisconnect`, plus
`fastapi.exceptions.RequestValidationError` and
`fastapi.exceptions.WebSocketRequestValidationError`. The other error records
include internal `HTTPException` imports in applications, handlers, routing,
and security modules; validation base/response/dependency errors; and Pydantic
compatibility errors. They are inventory findings, not public API claims.

The generated manifest says `/contract_metadata/errors` is a 42-candidate
inventory “with suggested selectors; no executable cases”; its separate
symbol map has 13 error-contract references. Keep these counts distinct from
fixture evidence. The reviewed selector rules in `metadata.yaml:2186-2248`
define five families:

| Family | Suggested observations |
| --- | --- |
| HTTP exception | `error.class`, `error.args`, `error.public_attributes`, HTTP status, ordered headers, body bytes/JSON |
| Request validation | HTTP exception observations plus `validation.error_class` and `validation.error_details` |
| WebSocket exception | error class/args/public attributes plus close code and reason |
| WebSocket request validation | WebSocket observations plus validation class/details |
| Response validation | error class/args/public attributes, `asgi.application_error.exception`, validation class/details |

Warning candidates suggest `warnings.category_message`. Existing direct API
warning recipes capture warning records through `python.warnings`; that covers
emission inputs but does not establish a public import contract for the
uncertain warning class or its internal aliases.

## Current workflow coverage

- `public-errors-http-websocket-wave.yaml` has 16 cases. It covers FastAPI and
  Starlette HTTP exception dispatch, bodyless/status edge cases, constructor
  snapshots, WebSocket close behavior, and `WebSocketDisconnect` constructor
  inputs. HTTP cases compare construction outcome/class/message and exact
  response status, headers, and body; WebSocket cases compare close code,
  reason, and event order. The constructor matrices are represented inside
  exact response bodies rather than direct `error.*` selectors.
- `request-validation-exception-handler.yaml` has 7 cases spanning path, body,
  malformed JSON, form input, default/custom handlers, structured manual errors,
  and explicit endpoint context. Its wire observations are exact status,
  headers, and body. `request-validation-error-details-wave.yaml` adds a
  multi-location request and a rethrowing handler that selects validation
  class/details and public attributes (`args`, body, endpoint path/file/line).
  `validation-exception-api-contract.yaml` checks request/WebSocket validation
  class identity, signatures, and constructor returned/raised outcome.
- `websocket-validation-handler-wave.yaml` has four default/custom handler
  cases and compares close code/reason, event order, messages, and workload
  trace. `validation-error-context-exact-review.yaml` has 13 cases. Root and
  mounted WebSocket rethrow cases select only `validation_error_class`; direct
  request and WebSocket validation-error construction cases additionally
  select exception details, `args`, body, and endpoint context fields.
- Response validation has focused, multi-error, and uncovered-wave workflows.
  These observe the application error’s validation class/details; the focused
  case also selects public attributes. The 10-case uncovered wave passed
  10/10 at FastAPI-RS `2abe8842447448dc16696375cb67e110564cca85` against the
  current manifest. `ResponseValidationError` remains private/internal in the
  candidate inventory, so these are runtime error observations rather than a
  public import claim.
- The direct warning workflows contain 17 cases plus one sidecar case. Their
  `capture_warnings` inputs add `python.warnings` to the selector set in
  `scripts/parity/materialized.py:77-82`.

## Highest-impact gap and input-only boundary

The direct WebSocket constructor workflow still selects call outcome rather
than instance fields. An input-only ASGI case now exercises a route with
invalid path, query, and header-dependency values and the existing rethrowing
handler pattern. It selects the exception class/message, validation details,
`args`, `endpoint_ctx`, and derived endpoint fields. The case lives in
`tests/fixtures/input-recipes/parity/validation-error-context-exact-review.yaml`
as `fastapi.validation-error-context.exact.websocket-error-fields`; its
workload is `tests/fixtures/workloads/validation_error_context_exact_review.py`.
The existing default-close case remains separate for the 1008/reason contract.

At target commit `0ed6a592e812c9d0f19a154c43ce83d8e8c84029` and the current
manifest, the indexed workflow matches 13/13 cases. The comparison includes
the constructor field observations; it does not establish full FastAPI-RS
support for these classes or for the broader error API.

## Source evidence and ownership boundary

- FastAPI exception storage and formatting: `fastapi/exceptions.py:174-231`;
  `WebSocketRequestValidationError` inherits the shared validation fields and
  has no request body field.
- WebSocket validation error construction: `fastapi/routing.py:770-798`,
  especially the error raise at 790-794.
- Default handler maps request errors to a 422 JSON response and WebSocket
  validation errors to policy close 1008 with encoded `exc.errors()`:
  `fastapi/exception_handlers.py:20-34`.
- FastAPI installs those defaults while preserving supplied handlers with
  `setdefault`: `fastapi/applications.py:1000-1012`. Its middleware-stack split
  between regular exception handlers and server-error handling is at
  `fastapi/applications.py:1020-1041`.
- Generic exception-handler MRO dispatch and ASGI response-start behavior are
  Starlette-owned: `starlette/_exception_handler.py:16-63`; handler
  registration and default HTTP/WebSocket handlers are
  `starlette/middleware/exceptions.py:27-73`.
- Existing case links and selector gaps are in
  `tests/fixtures/input-recipes/parity/websocket-validation-handler-wave.yaml`,
  `tests/fixtures/input-recipes/parity/validation-error-context-exact-review.yaml`,
  and `tests/fixtures/input-recipes/parity/validation-exception-api-contract.yaml`.

## Focused parity evidence

At FastAPI-RS `0ed6a592e812c9d0f19a154c43ce83d8e8c84029`, the current
`public-errors-http-websocket-wave` comparison passed 16/16. Comparison
`parity-results/comparisons/cc58568d-3ea2-4b13-a088-6ac455fb8e85.json`
(SHA-256 `ffe1c1f0154bee97c3491bb2d207501b8c501134d3ab7194f8b31a353712fe1c`)
binds input SHA-256
`565d64a79ccddd9351038d90adcf419c8d78eeda281997d7ae687cfbb7cbf8a5` and
manifest SHA-256
`f67678c11d87b35d56d5d5b04c78b40cf8251faeb9865e8b405cdc7aa296705b`.

The `validation-error-context-exact-review` workflow passed 13/13 at the same
target, source pins, and manifest. Comparison
`parity-results/comparisons/3588cad3-d433-4fe8-98d8-c3ab1cdf3655.json`
(SHA-256 `0c416bf32050124d70ff4b12d598bf45882782f5d0600258314cbc2c4b3ae985`)
binds input SHA-256
`cfd2e2791db3a2f6a4310087c646cb2595bbab843d03aec7dae656ec093cabc7`.

Both runs used FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at
`4139a72449bf5751e8902fb1c7175ee7f191d338`. The target source-tree SHA-256 is
`81021c0d646f53c5813380c92d11afdbce711302951f9d9b706bb3806340216b`; its
combined target-binary SHA-256 is
`94923c52126048117452d9e721b63bbe7e4ced7014550feffe52f2a38acab9b8`.
The response-validation uncovered wave also passed 10/10 at target commit
`2abe8842447448dc16696375cb67e110564cca85`. Comparison
`parity-results/comparisons/8bba6520-8674-4bb5-a3e3-6204eb90a4bb.json`
(SHA-256 `8a6e088276813cda79d9b274387026ce5bb76c4b10b5aa1304058459cfd1c180`)
binds input SHA-256
`5e8c166dc5c6507ffc9816bdc7a4c305873dad39b37beb3a2f5190d754fce161` and the
same manifest and source pins. Its target source-tree SHA-256 is
`a5ecb519676891377be174a8f2c1e87b54f71a8f608424b72f9baab123ebed63`; its
target-binary SHA-256 is
`94923c52126048117452d9e721b63bbe7e4ced7014550feffe52f2a38acab9b8`.
Generated comparison artifacts remain in the ignored `parity-results` tree.

This is bounded workflow evidence. The complete 42-candidate source-backed
error audit, remaining operation mappings, and full FastAPI-RS compatibility
remain open.
