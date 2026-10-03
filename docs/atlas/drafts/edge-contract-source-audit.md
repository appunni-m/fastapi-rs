# Error, alias, deprecation, and profile audit

Draft source audit for the FastAPI 0.141.1 contract. The source identity is
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f` remains the sole generic Starlette
oracle (`metadata.yaml:authority`). This report does not promote a candidate
to supported status.

## Source evidence and reviewed mapping

- The generated atlas has 42 error candidates, 69 import-alias records, 21
  deprecation records, and the three published extras `standard`,
  `standard-no-fastapi-cloud-cli`, and `all`. Every error row has at least one
  pinned-source path/line/hash and observation selectors; all aliases have a
  source path/line; all deprecation records have a source reference. These
  facts establish inventory provenance, not full behavior coverage.
- FastAPI source declares `requires-python = ">=3.10"`
  (`../fastapi/pyproject.toml:12`). The selected oracle is CPython 3.12.13
  (`metadata.yaml:authority.python`); this audit found no identity-checked
  parity matrix for the other supported interpreter versions. FastAPI lists
  Python 3.10–3.14 classifiers (`../fastapi/pyproject.toml:35-40`); that is
  not parity evidence for those interpreter versions.
- The extras are source-backed by `../fastapi/pyproject.toml:59-117`. They are
  installation profiles, not proof that all optional code paths are covered.
  The `standard` and `standard-no-fastapi-cloud-cli` extras include
  `python-multipart` and `email-validator`; the `all` extra adds
  `itsdangerous` and `pyyaml`; its direct list omits `fastar`.
- Alias entries keep declaration evidence separate from executable evidence.
  `tests/fixtures/input-recipes/parity/root-alias-identity.yaml` exercises a
  selected set of root/module/Starlette identity relations in HTTP JSON and a
  WebSocket message (`http.body.bytes` projects identity booleans;
  `websocket.messages` carries WebSocket relations).
  `metadata.yaml:source_api_classification_review.selection` identifies the
  case, relation, selector, and boolean projection. The recipe is a sample,
  not an identity proof for every alias row.
- Error selector rules in `metadata.yaml:error_selector_rules` distinguish
  HTTP exceptions, request validation, WebSocket exceptions, WebSocket request
  validation, and response validation. Concrete recipe links are:

  | Recipe | Selected observations |
  |---|---|
  | `tests/fixtures/input-recipes/parity/exception-overrides.yaml` | HTTP `status`, `headers`, `body`; one OpenAPI response-schema projection. |
  | `tests/fixtures/input-recipes/parity/request-validation-exception-handler.yaml` | Construction outcome/class/message and HTTP `status`, `headers`, `body` for path/body/malformed-JSON/form/default-handler cases. |
  | `tests/fixtures/input-recipes/parity/response-validation-error-focused.yaml` | Construction outcome/class/message; application-error class, exception, validation details, and `body` public attribute. |
  | `tests/fixtures/input-recipes/parity/response-validation-multi-error-exact-review.yaml` | Construction outcome/class/message; application-error class/details and `body` public attribute. |
  | `tests/fixtures/input-recipes/parity/validation-error-context-exact-review.yaml` | Construction outcome/class/message plus application-error class across HTTP, WebSocket, and mounted endpoints. |

  These are partial slices: no one recipe establishes every selector on every
  error candidate.
- Deprecation source records preserve decorator/warning call evidence and
  messages. `tests/fixtures/input-recipes/parity/direct-api-warnings.yaml`
  selects `python.call_outcome` and the `python.warnings` sidecar (category,
  message, file, and line); it samples parameter examples/regex and operation
  ID helpers. `tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml`
  selects `warnings.category_message` for legacy event registration. Keep
  `typing_extensions.deprecated` metadata distinct from emitted runtime
  warnings; these selected warning captures do not assert every marker,
  deprecated signature, parameter, alias, or constructor.

## Ownership crosswalk

- In pinned FastAPI source, `HTTPException` subclasses Starlette's exception
  and forwards `status_code`, `detail`, and `headers`
  (`../fastapi/fastapi/exceptions.py:6,17-83`). `WebSocketException` likewise
  subclasses and forwards to Starlette (`../fastapi/fastapi/exceptions.py:7,86-154`).
  `WebSocketDisconnect` is a direct Starlette re-export
  (`../fastapi/fastapi/websockets.py:2`). The atlas records these as
  `subclass_edge` or `direct_reexport` edges against Starlette 1.6.0 source.
- Read-only latest-target review used clean Starlette-RS commit
  `693050dce44a52a54eb319c47ec2ff15e55fa608` in
  `/tmp/fastapi-rs-starlette-rs-693050d`; its metadata still names the same
  Starlette 1.6.0 source revision. That manifest has a
  `starlette.exceptions/value-formatting` operation with exact construction,
  mutation, `str`, and `repr` requirements for both exception classes
  (`tests/fixtures/manifest.yaml:7124-7285). Its Python-package profile is marked
  supported for those values; its Rust-native profile is explicitly
  unimplemented for Python exception-class construction/representation. The
  application contract separately lists HTTP 406/default detail, 204/304,
  custom headers, WebSocket exception/denial handlers, and server-error paths
  (`tests/fixtures/manifest.yaml:758,1203-1402`). Python-package application
  support is partial; the Rust-native profile lists the generic server-error
  and several HTTP-exception paths as missing. These are Starlette-owned
  requirements; their presence in a manifest is not evidence that FastAPI-RS
  has passed them.
- FastAPI owns its validation exception classes, default handlers, and the
  mapping from validation failures to HTTP/WebSocket outcomes. Starlette-RS
  owns generic ASGI dispatch, exception middleware, protocol state, and generic
  HTTP/WebSocket behavior. Keep the crosswalk limited to the exact inherited,
  re-exported, and integration surfaces; do not import Starlette's full API
  inventory into the FastAPI contract. At audit time, the atlas's existing
  `complete-starlette-consumption-crosswalk` backlog was tied to the older
  Starlette-RS revision. The main workstream subsequently pinned 693050d and
  regenerated the crosswalk against its manifest. Keep this item open for
  operation-level behavior review; revision reconciliation alone does not
  prove FastAPI-RS parity.

## Unresolved contract gaps

1. Atlas error and alias records hold pinned source evidence and selector
   vocabulary, but exact recipe references live in the coverage matrix and
   reviewed metadata links rather than on each record. Reviewers must follow
   those joins before treating an entry as exercised.
2. `FastAPIDeprecationWarning` remains `uncertain` as a consumer-facing import
   contract: the class is defined at `../fastapi/fastapi/exceptions.py:252-256`
   and is used by warnings and upstream tests, but source/release-note evidence
   does not by itself establish a documented import path. Runtime warning
   category/message capture does not settle import-path support.
3. The atlas already records unresolved optional boundaries for the FastAPI
   CLI and `fastapi.testclient.TestClient` (`fastapi-cli-compatibility-boundary`,
   `fastapi-testclient-public-alias`). The extras table alone cannot establish
   subprocess semantics, TestClient alias identity/signature, or the matching
   optional install profile.
4. The prioritized backlog's
   `complete-alias-deprecation-error-and-extra-matrix` remains backlog: exact
   alias identity, warning/deprecation, all 42 error candidates, each optional
   profile, and Python 3.10–3.14 still need explicit, identity-checked
   dispositions. Starlette-owned cases must be covered through the pinned
   Starlette-RS crosswalk rather than duplicated as FastAPI behavior.

No active atlas or exclusion mapping was changed by this audit. Afterward the
main workstream regenerated the active atlas on Starlette-RS 693050d and
`make metadata-check` plus identity-bound parity completed successfully for
the currently implemented slices. The remaining join/coverage decisions
above are still open; a refreshed source pin does not promote partial behavior
to full support.

Follow-up: remote Starlette-RS `main` advanced to `4807b3a11efcb96c6ac2bf8537e806b6971aed37`. Its three new `ServerErrorMiddleware` debug/error-path requirements exercise the sibling middleware directly and remain sibling-owned. The pin, source hashes, atlas, and index are now refreshed to that revision; the FastAPI alias, deprecation, error, optional-profile, and Python-version gaps above remain open.


Starlette-RS later advanced to `baea19981ba3119d362be8c3a1b0913e4824313e` with a benchmark-documentation-only change. The active FastAPI pin now uses that exact remote head; runtime contract and source hashes are unchanged.
