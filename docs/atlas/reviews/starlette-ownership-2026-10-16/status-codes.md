# Documented-example status-code ownership review

> Historical review against the 2026-10-16 atlas/source snapshot. Its row pointers and FastAPI 0.141.1 evidence are not active 0.157.0 source support; use the regenerated atlas and current mappings for the pinned baseline.

Date: 2026-10-16

## Scope and source snapshots

Reviewed every compatibility-atlas `documented-example:` row whose
`status-codes` mapping currently has `ownership_boundary: owner review required`.
There are 52 such rows. All are `documented_python_example_source` rows. Each
row currently points to `starlette-1.6.0-full`, has status
`out-of-current-contract-slice`, and has no operation references. Every
`source_sha256` matches the source file in the pinned FastAPI checkout.

Source revisions:

- FastAPI: tag `0.141.1`, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`
- Starlette: tag `1.6.0`, commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`
- Starlette-RS: pinned commit `4139a72449bf5751e8902fb1c7175ee7f191d338`
- Starlette-RS manifest: `tests/fixtures/manifest.yaml`, SHA-256
  `86f69fc791088794fcd59483d6a91cc08bb9b3999586665f73c2f722f9946029`

This is a source audit. The examples were not executed. No tests, builds,
parity runs, or benchmarks were run.

## Ownership findings

Status selection and status emission are separate here. FastAPI route
configuration selects statuses passed through path-operation `status_code`
and an injected `Response` value in `fastapi/routing.py:357,363,366,370,371`.
FastAPI's default HTTP exception handler preserves `exc.status_code` in a
Starlette `Response` or `JSONResponse`, and its validation handler selects
422 (`fastapi/exception_handlers.py:11,13,14,16,20,24`). FastAPI installs those
handlers in `fastapi/applications.py:1003,1005`. FastAPI's `HTTPException`
subclasses Starlette's exception and forwards the supplied status
(`fastapi/exceptions.py:17,45,83`).

The response classes imported from `fastapi.responses` are direct Starlette
re-exports (`fastapi/responses.py:6-12`). Starlette `Response` defaults to 200,
stores the supplied status, and emits it in `http.response.start`
(`starlette/responses.py:33,36,41,163,166`). Thus the explicit status values in
the examples are selected by FastAPI route settings or by application code;
Starlette owns the generic response default and emission. The two streaming
examples use `StreamingResponse`, whose default status is 200 and whose ASGI
start event sends `self.status_code` (`starlette/responses.py:225,228,237,248,249`).

No reviewed example selects a status through Starlette's generic Router miss
or slash-redirect path. No third-party component selects one of the reviewed
statuses: `TestClient` observes statuses, and the SQL examples use database
results only to choose application branches that raise FastAPI
`HTTPException`.

The security examples use FastAPI's built-in `OAuth2PasswordBearer` or
`HTTPBasic` dependency with its default `auto_error=True`. Those dependencies
select 401 for a missing/malformed authorization header
(`fastapi/security/oauth2.py:401,417-421,536,539-542`;
`fastapi/security/http.py:87-92,202-219`). The same example rows also contain
application code that raises explicit 401 or 400 exceptions, so those rows
are mixed but separable at the documented-source-row level.

## Starlette-RS contract links for generic behavior

Use these operation references as ownership links, with a scope note that they
cover only generic Starlette response behavior and do not establish FastAPI-RS
parity:

| Key | Exact contract surface and operation | Relevant requirement IDs | Current target support |
| --- | --- | --- | --- |
| `R` | `starlette.responses.Response` / `asgi-call` (`starlette.responses.Response.__call__`) | `starlette.responses.Response.asgi-call.non-empty-response`; use `starlette.responses.Response.asgi-call.empty-response` for the empty redirect body | `rust-native: supported`; `python-package: supported` |
| `S` | `starlette.responses.StreamingResponse` / `asgi-call` (`starlette.responses.StreamingResponse.__call__`) | `starlette.responses.StreamingResponse.asgi-call.unknown-size-content` | `rust-native: supported`; `python-package: supported` |

In the pinned manifest, `R` takes an integer `status_code` and reports the
integer `response_status`; its Rust target is
`starlette_rs::Response::from_content(status_code, body, media_type,
ordered_headers)` with `Response::asgi_events()`. `S` covers the examples'
finite synchronous iterator with no explicit media type or content length. The
operation-level support states apply to these generic response boundaries;
they do not claim FastAPI route dispatch, dependency solving, exception
selection, or FastAPI response integration is supported.

For the one configured redirect, FastAPI sets 302 on the response class at
`docs_src/custom_response/tutorial006c_py310.py:7`. The Starlette-RS
`RedirectResponse` requirement
`starlette.responses.RedirectResponse.asgi-call.default-relative-location`
is specifically the default 307 case, so it does not describe that configured
302 example. The generic `R` response operation is the relevant status-emission
link.

The following table gives each exact source path. Its atlas row key is
`documented-example:` followed by the displayed path. `R` and `S` refer to the
contract table above. Statuses marked “default 200” are selected by the
Starlette response default and then carried through FastAPI; explicit statuses
are attributed to the code shown in the source column.

| Exact source path | Observed status behavior | Status owner and recommended boundary | Source evidence | Generic link |
| --- | --- | --- | --- | --- |
| `docs_src/additional_responses/tutorial001_py310.py` | Default 200 on the found branch; direct JSON response 404 on the missing branch | Mixed but separable: Starlette default 200; application-selected 404; Starlette response emission | `:18,20,21,22` | R |
| `docs_src/additional_responses/tutorial003_py310.py` | Default 200 on the found branch; direct JSON response 404 otherwise | Mixed but separable: Starlette default 200; application-selected 404; Starlette response emission | `:18,33,34,37` | R |
| `docs_src/additional_status_codes/tutorial001_an_py310.py` | Existing item returns with default 200; newly created item returns JSON response 201 | Mixed but separable: Starlette default 200; application-selected 201; Starlette response emission | `:18,21,25` | R |
| `docs_src/additional_status_codes/tutorial001_py310.py` | Existing item returns with default 200; newly created item returns JSON response 201 | Mixed but separable: Starlette default 200; application-selected 201; Starlette response emission | `:9,19,23` | R |
| `docs_src/app_testing/tutorial002_py310.py` | Test asserts GET `/` is 200 | Starlette response default 200 through the FastAPI route; `TestClient` observes it | `:8,21,23` | R |
| `docs_src/app_testing/tutorial003_py310.py` | Test asserts GET `/items/foo` is 200 | Starlette response default 200 through the FastAPI route; `TestClient` observes it | `:15,21,23` | R |
| `docs_src/app_testing/tutorial004_py310.py` | Test asserts GET `/items/foo` is 200 | Starlette response default 200 through the FastAPI route; `TestClient` observes it | `:21,34,35` | R |
| `docs_src/authentication_error_status_code/tutorial001_an_py310.py` | Custom `HTTPBearer403` creates status 403 for unauthenticated credentials | Application override selects 403; FastAPI handles the exception; Starlette emits the response | `:9,10,11,12` | R |
| `docs_src/bigger_applications/app_an_py310/dependencies.py` | Invalid `X-Token` or query token raises status 400 | Application dependency selects 400 with FastAPI `HTTPException`; Starlette emits the response | `:6,8,11,13` | R |
| `docs_src/bigger_applications/app_an_py310/routers/items.py` | Local missing-item status 404 and update status 403; shared `get_token_header` dependency can return 400; successful routes default to 200 | Application routes/dependency select 400/403/404; Starlette supplies default 200 and emits all responses | `:8,16,18,21,24,28,35,36`; imported dependency `docs_src/bigger_applications/app_an_py310/dependencies.py:6,8` | R |
| `docs_src/custom_request_and_route/tutorial002_an_py310.py` | Custom route handler converts request validation failure to HTTP exception 422 | Application-defined route wrapper selects 422; FastAPI handles it; Starlette emits the response | `:16,19,28` | R |
| `docs_src/custom_request_and_route/tutorial002_py310.py` | Custom route handler converts request validation failure to HTTP exception 422 | Application-defined route wrapper selects 422; FastAPI handles it; Starlette emits the response | `:15,18,27` | R |
| `docs_src/custom_response/tutorial003_py310.py` | Returns `HTMLResponse` with explicit status 200 | Application supplies 200; Starlette response class emits it | `:7,19` | R |
| `docs_src/custom_response/tutorial004_py310.py` | Returns `HTMLResponse` with explicit status 200; the path operation also declares `HTMLResponse` | Application supplies 200; FastAPI selects the response class; Starlette emits it | `:18,21` | R |
| `docs_src/custom_response/tutorial006c_py310.py` | FastAPI path operation configures `RedirectResponse` with status 302 | FastAPI route configuration selects 302; Starlette emits the configured status | `:7` | R |
| `docs_src/dependencies/tutorial006_an_py310.py` | Invalid token or key raises status 400; successful route defaults to 200 | Application dependencies select 400; Starlette supplies default 200 and emits the response | `:10,15,19` | R |
| `docs_src/dependencies/tutorial006_py310.py` | Invalid token or key raises status 400; successful route defaults to 200 | Application dependencies select 400; Starlette supplies default 200 and emits the response | `:8,13,17` | R |
| `docs_src/dependencies/tutorial008b_an_py310.py` | Yield-dependency owner error raises 400; missing item raises 404; normal return defaults to 200 | Application dependency/endpoint select 400 and 404; Starlette supplies default 200 and emits the response | `:22,25,27,28` | R |
| `docs_src/dependencies/tutorial008b_py310.py` | Yield-dependency owner error raises 400; missing item raises 404; normal return defaults to 200 | Application dependency/endpoint select 400 and 404; Starlette supplies default 200 and emits the response | `:20,23,25,26` | R |
| `docs_src/dependencies/tutorial008c_an_py310.py` | Missing non-plumbus item raises 404; successful return defaults to 200 | Application selects 404; Starlette supplies default 200 and emits the response | `:20,25,27,29` | R |
| `docs_src/dependencies/tutorial008c_py310.py` | Missing non-plumbus item raises 404; successful return defaults to 200 | Application selects 404; Starlette supplies default 200 and emits the response | `:17,23,25,27` | R |
| `docs_src/dependencies/tutorial008d_an_py310.py` | Missing non-plumbus item raises 404; successful return defaults to 200 | Application selects 404; Starlette supplies default 200 and emits the response | `:20,26,28,30` | R |
| `docs_src/dependencies/tutorial008d_py310.py` | Missing non-plumbus item raises 404; successful return defaults to 200 | Application selects 404; Starlette supplies default 200 and emits the response | `:18,24,26,28` | R |
| `docs_src/dependencies/tutorial012_an_py310.py` | Invalid token or key raises 400 on the protected routes | Application dependencies select 400; FastAPI handles the exception; Starlette emits the response | `:8,13,20,25` | R |
| `docs_src/dependencies/tutorial012_py310.py` | Invalid token or key raises 400 on the protected routes | Application dependencies select 400; FastAPI handles the exception; Starlette emits the response | `:6,11,18,23` | R |
| `docs_src/dependencies/tutorial013_an_py310.py` | Missing user raises 403; successful stream defaults to 200 | Application selects 403; Starlette `StreamingResponse` supplies 200 and emits the stream | `:27,30,31,32,36,37,38` | R + S |
| `docs_src/dependencies/tutorial014_an_py310.py` | Missing user raises 403; successful stream defaults to 200 | Application selects 403; Starlette `StreamingResponse` supplies 200 and emits the stream | `:27,31,32,37,38,39` | R + S |
| `docs_src/dependency_testing/tutorial001_an_py310.py` | Three test requests assert status 200 | Starlette response default 200 through FastAPI routes; `TestClient` observes it | `:13,18,35,44,53` | R |
| `docs_src/dependency_testing/tutorial001_py310.py` | Three test requests assert status 200 | Starlette response default 200 through FastAPI routes; `TestClient` observes it | `:11,16,33,42,51` | R |
| `docs_src/handling_errors/tutorial001_py310.py` | Missing item raises 404; found item returns with default 200 | Application selects 404; Starlette supplies default 200 and emits both responses through FastAPI | `:8,11,12` | R |
| `docs_src/handling_errors/tutorial002_py310.py` | Missing item raises 404 with a custom header; normal return defaults to 200 | Application selects 404; Starlette supplies default 200 and emits both responses through FastAPI | `:8,11,12,15` | R |
| `docs_src/handling_errors/tutorial003_py310.py` | Custom unicorn exception handler returns JSON response 418 | Application exception handler selects 418; Starlette response emits it | `:13,15,16,21` | R |
| `docs_src/handling_errors/tutorial004_py310.py` | Custom validation handler returns 400; HTTP exception handler preserves the raised 418; success defaults to 200 | Application handlers select 400 and preserve app-selected 418; Starlette supplies default 200 and emits responses | `:9,11,14,19,24,25,26` | R |
| `docs_src/handling_errors/tutorial005_py310.py` | Custom request-validation handler returns 422 | Application handler explicitly selects 422; Starlette response emits it | `:10,12,13,23` | R |
| `docs_src/handling_errors/tutorial006_py310.py` | Route raises 418; delegated FastAPI request-validation handler returns 422 for invalid input | Application selects 418; FastAPI handler selects 422; Starlette emits both responses | `:12,18,19,21,24,27` | R |
| `docs_src/path_operation_advanced_configuration/tutorial007_py310.py` | Invalid YAML and invalid model data each raise 422; valid result returns with default 200 | Application parsing/validation code selects 422; Starlette supplies default 200 and emits responses through FastAPI | `:13,27,29,31,32` | R |
| `docs_src/path_operation_configuration/tutorial001_py310.py` | Path operation declares status 201 | FastAPI route configuration selects 201; Starlette emits it | `:15,16` | R |
| `docs_src/response_change_status_code/tutorial001_py310.py` | Existing task keeps configured 200; creation sets injected `Response.status_code` to 201 | FastAPI route selects 200; application changes the response to 201; Starlette emits the selected value | `:8,9,12,13` | R |
| `docs_src/response_status_code/tutorial001_py310.py` | Path operation declares status 201 | FastAPI route configuration selects 201; Starlette emits it | `:6,7` | R |
| `docs_src/response_status_code/tutorial002_py310.py` | Path operation declares status 201 using the status enum | FastAPI route configuration selects 201; Starlette emits it | `:6,7` | R |
| `docs_src/security/tutorial003_an_py310.py` | Missing bearer header and invalid token return 401; invalid login and inactive-user paths return 400; ordinary success defaults to 200 | Mixed but separable: FastAPI `OAuth2PasswordBearer` selects missing-header 401; app code selects invalid-token/login/inactive statuses; Starlette supplies default 200 and emits responses | `:58,60-66,69-74,77-87,90-94`; FastAPI `fastapi/security/oauth2.py:401,417-421,536,539-542` | R |
| `docs_src/security/tutorial003_py310.py` | Missing bearer header and invalid token return 401; invalid login and inactive-user paths return 400; ordinary success defaults to 200 | Mixed but separable: FastAPI `OAuth2PasswordBearer` selects missing-header 401; app code selects invalid-token/login/inactive statuses; Starlette supplies default 200 and emits responses | `:56-64,67-70,73-83,86-88`; FastAPI `fastapi/security/oauth2.py:401,417-421,536,539-542` | R |
| `docs_src/security/tutorial004_an_py310.py` | Missing bearer header and invalid credentials/login return 401; inactive user returns 400; ordinary success defaults to 200 | Mixed but separable: FastAPI `OAuth2PasswordBearer` selects missing-header 401; app code selects invalid-credential/login/inactive statuses; Starlette supplies default 200 and emits responses | `:93-110,113-118,121-136,139-150`; FastAPI `fastapi/security/oauth2.py:401,417-421,536,539-542` | R |
| `docs_src/security/tutorial004_py310.py` | Missing bearer header and invalid credentials/login return 401; inactive user returns 400; ordinary success defaults to 200 | Mixed but separable: FastAPI `OAuth2PasswordBearer` selects missing-header 401; app code selects invalid-credential/login/inactive statuses; Starlette supplies default 200 and emits responses | `:92-109,112-115,118-133,136-143`; FastAPI `fastapi/security/oauth2.py:401,417-421,536,539-542` | R |
| `docs_src/security/tutorial005_an_py310.py` | Missing bearer header, invalid credentials, or missing scopes return 401; invalid login or inactive user returns 400; ordinary success defaults to 200 | Mixed but separable: FastAPI `OAuth2PasswordBearer` selects missing-header 401; app code selects credential/scope/login/inactive statuses; Starlette supplies default 200 and emits responses | `:107-140,143-148,151-163,166-177,180-182`; FastAPI `fastapi/security/oauth2.py:401,417-421,536,539-542` | R |
| `docs_src/security/tutorial005_py310.py` | Missing bearer header, invalid credentials, or missing scopes return 401; invalid login or inactive user returns 400; ordinary success defaults to 200 | Mixed but separable: FastAPI `OAuth2PasswordBearer` selects missing-header 401; app code selects credential/scope/login/inactive statuses; Starlette supplies default 200 and emits responses | `:107-140,143-148,151-163,166-179`; FastAPI `fastapi/security/oauth2.py:401,417-421,536,539-542` | R |
| `docs_src/security/tutorial007_an_py310.py` | Missing/malformed Basic authorization and invalid Basic credentials return 401; successful authentication defaults to 200 | Mixed but separable: FastAPI `HTTPBasic` selects missing/malformed-header 401; app code selects bad-credential 401; Starlette supplies default 200 and emits responses | `:25-31,34-36`; FastAPI `fastapi/security/http.py:87-92,202-219` | R |
| `docs_src/security/tutorial007_py310.py` | Missing/malformed Basic authorization and invalid Basic credentials return 401; successful authentication defaults to 200 | Mixed but separable: FastAPI `HTTPBasic` selects missing/malformed-header 401; app code selects bad-credential 401; Starlette supplies default 200 and emits responses | `:22-28,31-33`; FastAPI `fastapi/security/http.py:87-92,202-219` | R |
| `docs_src/sql_databases/tutorial001_an_py310.py` | Missing hero read/delete raises 404; ordinary success defaults to 200 | Application checks the SQLModel result and selects 404; SQLModel does not choose status; Starlette supplies default 200 and emits responses | `:58,62,66,70` | R |
| `docs_src/sql_databases/tutorial001_py310.py` | Missing hero read/delete raises 404; ordinary success defaults to 200 | Application checks the SQLModel result and selects 404; SQLModel does not choose status; Starlette supplies default 200 and emits responses | `:54,58,62,66` | R |
| `docs_src/sql_databases/tutorial002_an_py310.py` | Missing hero read/update/delete raises 404; ordinary success defaults to 200 | Application checks the SQLModel result and selects 404; SQLModel does not choose status; Starlette supplies default 200 and emits responses | `:75,79,83,87,96,100` | R |
| `docs_src/sql_databases/tutorial002_py310.py` | Missing hero read/update/delete raises 404; ordinary success defaults to 200 | Application checks the SQLModel result and selects 404; SQLModel does not choose status; Starlette supplies default 200 and emits responses | `:72,76,80,86,95,99` | R |

## Row-keyed overlay recommendation

All 52 owners are identifiable at this exact source-row granularity. The
source files that contain several branches have explicit and separable
selection sites; they do not need to stay unresolved. Use a compound
`ownership_boundary` and `scope_note` for rows with both an app/FastAPI
selection and Starlette's default or generic emission. Use `R` for ordinary
and exception responses, and `R` plus `S` for the two dependency examples that
return a stream. Keep the scope note clear that the operation links classify
Starlette ownership only.

Preserve the row keys as `documented-example:<source_path>` in
`STARLETTE_RS_OWNERSHIP_ROW_OVERLAYS`; do not key these overlays as
`upstream-test:<source_path>`. The current `_review_rows` helper constructs
only the latter form (`scripts/atlas_starlette_ownership_review_mappings.py:22-31`),
and the atlas builder currently rejects non-test rows at
`scripts/build_fastapi_compatibility_atlas.py:10046-10052`. Applying these
recommendations later therefore needs a small row-kind extension and a helper
that accepts exact documented-example row IDs. This review did not change the
active mappings, generator, or fixtures.

## Evidence and commands

Read-only evidence commands used: `git rev-parse` and exact-tag checks for the
three source checkouts; `rg` and `nl -ba` for the source locations above; and
small Python readers for the atlas JSON, pinned manifest YAML, and source
SHA-256 comparison. The initial unprivileged Kata search could not reach its
local socket; rerunning Kata commands with the required local access succeeded.
The assigned issue inbox had no requests, and issue `b62a` was marked tracked
with `work.attention=ok` before the audit.
