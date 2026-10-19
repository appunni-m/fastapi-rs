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

- `public-errors-http-websocket-wave.yaml` has 14 cases. It covers FastAPI and
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
  trace. `validation-error-context-exact-review.yaml` has root and mounted
  WebSocket rethrow cases, but selects only `validation_error_class`.
- Response validation has focused, multi-error, and uncovered-wave workflows.
  These observe the application error’s validation class/details; the focused
  case also selects public attributes. `ResponseValidationError` remains
  private/internal in the candidate inventory, so these are runtime error
  observations rather than a public import claim.
- The direct warning workflows contain 17 cases plus one sidecar case. Their
  `capture_warnings` inputs add `python.warnings` to the selector set in
  `scripts/parity/materialized.py:77-82`.

## Highest-impact gap and next input-only boundary

Prioritize a WebSocket request-validation object-observation case. The
existing close workflow checks the serialized close result, while the root and
mounted rethrow cases select only the exception class. The direct constructor
workflow selects call outcome, not the constructed exception’s fields. As a
result, the candidate’s `error.args`, `error.public_attributes`, and
`validation.error_details` selectors are not joined on a WebSocket
`WebSocketRequestValidationError` instance in an input case.

Add one independently authored ASGI case to the existing WebSocket validation
workflow: send a WebSocket connect to a route with multiple invalid
path/query/dependency values, use the existing rethrow-handler pattern, and
select `application_error.exception`, `validation_error_class`,
`validation_error_details`, and `error_public_attributes` for `args`,
`endpoint_ctx`, and the derived endpoint fields. Keep the current default-close
case for the separate 1008/reason contract. The input recipe should contain
only the request and route stimulus, with no expected outputs.

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

This review establishes source and input coverage only. It makes no
FastAPI-RS parity or support claim.
