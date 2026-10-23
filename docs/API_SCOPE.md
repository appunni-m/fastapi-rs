# FastAPI public API scope

## Authority and inventory method

This inventory is grounded in the FastAPI `0.157.0` release tag, commit
`386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`, from a local source checkout. The
FastAPI-RS compatibility environment uses
Starlette `1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` as its sole
Starlette oracle contract, plus Pydantic `2.13.5`, pydantic-core `2.46.5`,
and HTTPX `0.28.1`. FastAPI declares `starlette>=0.46.0`, which admits 1.6.0.
FastAPI 0.157.0's source `uv.lock` resolves Starlette 1.7.0; that lock is used
for dependency inventory only. Starlette-RS is a separate implementation
contract pinned in `metadata.yaml`. All compatibility and parity runs use
Starlette 1.6.0 as the oracle.

Method: read the pinned package's root imports and Python sources; collect every
`fastapi.*` `mkdocstrings` target in `docs/en/docs`; cross-check reference
pages, tutorials/how-to docs, release notes, and imports in tests; then inspect
the inheritance/reexport edges to Starlette. The pinned package has 52 Python
source files, 24 reference Markdown pages, 73 documented target names, and 527
`test_*.py` modules. These are inventory inputs, **not** the number of manifest
operations. Many targets expand into classes with multiple methods, many public
names are aliases, and the `status`/OpenAPI-model targets expand to large
value/model sets.

The source inventory is discovery only. Reviewed atlas classifications,
manifest operations, and runtime reflection have separate evidence identities;
counts from the prior 0.141.1 review are not current 0.157.0 support or parity
claims. Broader operation-level behavior and full implementation coverage
remain pending.

The API authority is the versioned source plus its English reference and
user-facing docs. The migration-parity manifest should preserve fully qualified
spelling, exact Python parameter names/kinds/defaults/annotations, aliases,
deprecation metadata, and observable results. Treat each overload/member as a
separate manifest operation when callers can invoke or inspect it separately.
FastAPI-RS has one target profile: the Python consumer surface imported as
`fastapi`. The `fastapi-rs` crate owns its behavior; `fastapi-rs-py` packages
the thin PyO3 boundary. Rust implementation details are not a second FastAPI
target or additional Python API surface. The same `fastapi-rs` crate also
exposes an additive Rust service API under `fastapi_rs::native`; that API is
outside the FastAPI Python manifest and makes no claim of full Python FastAPI
parity. This document is an audit aid; it is not a second manifest or an
execution result.

Runtime namespace reflection complements the AST inventory in
[`runtime-api-surface-core.json`](../tests/fixtures/runtime-api-surface-core.json)
and [`runtime-api-surface-standard.json`](../tests/fixtures/runtime-api-surface-standard.json).
The checked-in profiles bind FastAPI 0.157.0 at
`386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`, Starlette 1.6.0,
Pydantic 2.13.5, pydantic-core 2.46.5, and CPython 3.12.13. The core profile
imports 49 of 52 source modules; two optional-feature modules cannot import
without their extras. The standard profile imports 51 modules with no import
errors. Across both profiles, reflection records 1,828 and 1,830 source symbols,
respectively. These are runtime observations, not behavioral parity or support
claims. Runtime presence does not by itself establish a stable public API;
reviewed source classifications belong in `metadata.yaml` and the generated
compatibility atlas.

## Root import surface

`fastapi/__init__.py` has no `__all__`. It defines `__version__` and makes 20
explicit reexports. The reexported object identity is part of import
compatibility; aliases in the table use `as` intentionally in the source.

| Import spelling | Source object / source location | Notes |
| --- | --- | --- |
| `fastapi.__version__` | constant `"0.157.0"`, `fastapi/__init__.py:3` | Package version value. |
| `fastapi.status` | `starlette.status`, `fastapi/__init__.py:5` | Whole status namespace; delegated to Starlette. |
| `fastapi.FastAPI` | `fastapi.applications.FastAPI`, `__init__.py:7` | Main ASGI app. |
| `fastapi.BackgroundTasks` | `fastapi.background.BackgroundTasks`, `__init__.py:8` | FastAPI subclass of Starlette's task collection. |
| `fastapi.UploadFile` | `fastapi.datastructures.UploadFile`, `__init__.py:9` | FastAPI subclass/schema adapter over Starlette upload file. |
| `fastapi.HTTPException` | `fastapi.exceptions.HTTPException`, `__init__.py:10` | FastAPI subclass of Starlette exception. |
| `fastapi.WebSocketException` | `fastapi.exceptions.WebSocketException`, `__init__.py:11` | FastAPI subclass of Starlette exception. |
| `fastapi.Body`, `Cookie`, `Depends`, `File`, `Form`, `Header`, `Path`, `Query`, `Security` | functions in `fastapi.param_functions`, `__init__.py:12-20` | These are helper callables, distinct from similarly named `FieldInfo` subclasses in `fastapi.params`. |
| `fastapi.Request` | `fastapi.requests.Request`, `__init__.py:21` | Same Starlette `Request` class object. |
| `fastapi.Response` | `fastapi.responses.Response`, `__init__.py:22` | Same Starlette `Response` class object. |
| `fastapi.APIRouter` | `fastapi.routing.APIRouter`, `__init__.py:23` | FastAPI router, subclassing Starlette `Router`. |
| `fastapi.WebSocket` | `fastapi.websockets.WebSocket`, `__init__.py:24` | Same Starlette `WebSocket` class object. |
| `fastapi.WebSocketDisconnect` | `fastapi.websockets.WebSocketDisconnect`, `__init__.py:25` | Same Starlette disconnect exception. |

The root reexports do **not** include `HTTPConnection`, `WebSocketState`,
`TestClient`, response subclasses, security classes, exception-validation
types, `APIRoute`, `get_openapi`, or `jsonable_encoder`; their module paths
remain significant.

FastAPI 0.157.0 also adds a source-defined `fastapi.telemetry` module that
reexports `TelemetryConfig`, `TelemetryData`, and `get_telemetry_data`;
`FastAPI` accepts a `telemetry` constructor option. The source candidate atlas
records the module and three names as uncertain: the pinned source explicitly
reexports them, but the user guide does not name those import paths. Existing
constructor cases compare the parameter signature and selected configuration
acceptance only. Request-local data, active traces/metrics/logs, provider and
exporter ownership, and telemetry-aware lifespan behavior remain unresolved;
the target has no telemetry runtime implementation. Do not treat the
constructor cases or import bindings as telemetry parity evidence.

### Current target facade availability

The root facade currently exposes all 21 source bindings:
`APIRouter`, `BackgroundTasks`, `Body`, `Cookie`, `Depends`, `FastAPI`, `File`,
`Form`, `Header`, `HTTPException`, `Path`, `Query`, `Request`, `Response`,
`Security`, `UploadFile`, `WebSocket`, `WebSocketDisconnect`,
`WebSocketException`, `__version__`, and `status`. Pinned-source reflection
identifies `BackgroundTasks` as `fastapi.background.BackgroundTasks` and
`Security` as `fastapi.param_functions.Security`; the root-alias identity
workflow observes both root-to-module alias relations. Request injection has a
partial identity-checked ASGI workflow; generic Request API parity remains
owned by Starlette-RS and is not established by that FastAPI integration case.
Root import and alias identity do not prove full signatures or behavior. The
generated manifest's `target_binding.public_python_path` records the required
spelling, and both target bindings remain `full-contract-not-established` until
full interface and behavior parity are recorded.

`fastapi.status` is a Starlette module reexport in the oracle. FastAPI-RS now
binds the exact `starlette.status` module object. The focused identity-checked
workflow compares that identity, the declared `__all__` order, and all
exported values. Deprecated aliases, warnings, `dir`, and missing-attribute
behavior remain delegated to the pinned Starlette-RS contract and are not
observed by this FastAPI workflow.

## Documented reference targets

The following are all 73 distinct `fastapi.*` documented target names recorded
for the pinned source under `docs/en/docs`; the inventory includes documented
module targets as well as named objects. Page paths are relative to
`docs/en/docs/reference/`.

| Reference page | Fully qualified targets |
| --- | --- |
| `fastapi.md` | `fastapi.FastAPI` |
| `apirouter.md` | `fastapi.APIRouter` |
| `parameters.md` | `fastapi.Query`, `fastapi.Path`, `fastapi.Body`, `fastapi.Cookie`, `fastapi.Header`, `fastapi.Form`, `fastapi.File` |
| `dependencies.md` | `fastapi.Depends`, `fastapi.Security` |
| `exceptions.md` | `fastapi.HTTPException`, `fastapi.WebSocketException` |
| `background.md` | `fastapi.BackgroundTasks` |
| `uploadfile.md` | `fastapi.UploadFile` |
| `request.md`, `httpconnection.md` | `fastapi.Request`, `fastapi.requests`, `fastapi.requests.HTTPConnection` |
| `websockets.md` | `fastapi.WebSocket`, `fastapi.websockets`, `fastapi.websockets.WebSocketDisconnect`, `fastapi.websockets.WebSocketState` |
| `response.md`, `responses.md` | `fastapi.Response`; `fastapi.responses`, `fastapi.responses.UJSONResponse`, `ORJSONResponse`, `FileResponse`, `HTMLResponse`, `JSONResponse`, `PlainTextResponse`, `RedirectResponse`, `Response`, `StreamingResponse` |
| `encoders.md` | `fastapi.encoders.jsonable_encoder` |
| `security/index.md` | `fastapi.security`, `fastapi.security.APIKeyCookie`, `APIKeyHeader`, `APIKeyQuery`, `HTTPBasic`, `HTTPBearer`, `HTTPDigest`, `HTTPAuthorizationCredentials`, `HTTPBasicCredentials`, `OAuth2`, `OAuth2AuthorizationCodeBearer`, `OAuth2PasswordBearer`, `OAuth2PasswordRequestForm`, `OAuth2PasswordRequestFormStrict`, `SecurityScopes`, `OpenIdConnect` |
| `middleware.md` | `fastapi.middleware.cors`, `fastapi.middleware.cors.CORSMiddleware`, `fastapi.middleware.gzip`, `fastapi.middleware.gzip.GZipMiddleware`, `fastapi.middleware.httpsredirect`, `fastapi.middleware.httpsredirect.HTTPSRedirectMiddleware`, `fastapi.middleware.trustedhost`, `fastapi.middleware.trustedhost.TrustedHostMiddleware` |
| `staticfiles.md`, `templating.md`, `testclient.md` | `fastapi.staticfiles`, `fastapi.staticfiles.StaticFiles`, `fastapi.templating`, `fastapi.templating.Jinja2Templates`, `fastapi.testclient`, `fastapi.testclient.TestClient` |
| `sse.md` | `fastapi.sse`, `fastapi.sse.EventSourceResponse`, `fastapi.sse.ServerSentEvent` |
| `status.md` | `fastapi.status` (Starlette module reexport) |
| `openapi/docs.md` | `fastapi.openapi.docs.get_swagger_ui_html`, `get_redoc_html`, `get_swagger_ui_oauth2_redirect_html`, `swagger_ui_default_parameters` |
| `openapi/models.md` | `fastapi.openapi.models` (43 declared public model/type names; enumerated below) |

Reference autodoc member allowlists are also authoritative: `FastAPI` lists
`openapi_version`, `webhooks`, `state`, `dependency_overrides`, `openapi`,
`websocket`, `include_router`, `frontend`, all eight HTTP verb decorators,
`on_event`, `middleware`, and `exception_handler`; `APIRouter` lists
`websocket`, `include_router`, `frontend`, the eight HTTP verb decorators,
and `on_event`. The methods below add source-visible public callables that
appear elsewhere in examples or are used as supported extension points.

### OpenAPI model namespace

`fastapi.openapi.models` contains these 43 public class/type names in
`fastapi/openapi/models.py:57-431`: `BaseModelWithConfig`, `Contact`,
`License`, `Info`, `ServerVariable`, `Server`, `Reference`, `Discriminator`,
`XML`, `ExternalDocumentation`, `SchemaType`, `Schema`, `SchemaOrBool`,
`Example`, `ParameterInType`, `Encoding`, `MediaType`, `ParameterBase`,
`Parameter`, `Header`, `RequestBody`, `Link`, `Response`, `Operation`,
`PathItem`, `SecuritySchemeType`, `SecurityBase`, `APIKeyIn`, `APIKey`,
`HTTPBase`, `HTTPBearer`, `OAuthFlow`, `OAuthFlowImplicit`,
`OAuthFlowPassword`, `OAuthFlowClientCredentials`,
`OAuthFlowAuthorizationCode`, `OAuthFlows`, `OAuth2`, `OpenIdConnect`,
`SecurityScheme`, `Components`, `Tag`, and `OpenAPI`.

Most names in this namespace are Pydantic models or enums that define
serialized OpenAPI input/output shapes. `Example` is instead a
`TypedDict(total=False)` with optional `summary`, `description`, `value`, and
`externalValue` keys and Pydantic's `extra="allow"` configuration. Preserve
field aliases, optional/default semantics, enum values, extra-field behavior,
schema serialization, and round-trip validation. The `SecurityScheme` and
`SchemaOrBool` names are type aliases in source, not classes. Pydantic model
fields are generated behavior; capture their field names, aliases and
validation/serialization rules from the pinned source at manifest-generation
time.

## Callable and class-member families

The complete discovered surface is in
[`api-inventory.json`](../tests/fixtures/api-inventory.json); reviewed support,
private/internal, and uncertain classifications and operation requirements are
in [`metadata.yaml`](../metadata.yaml). The 0.157.0 source inventory contains 758
import bindings, 360 module-level definitions, 388 source-defined callables,
277 public or protocol callables, 102 public classes, 51 instance-assignment
candidates, 39 Pydantic model classes, 9 Pydantic integration classes, 32
Starlette re-export bindings, 101 Starlette import dependencies, 15 subclass
edges, and 21 source-deprecation candidates. These counts are discovery inputs,
not a count of supported target operations.

The public operation families include constructors and signatures; HTTP and
WebSocket route registration; router composition; dependency declarations and
lifetimes; path/query/header/cookie/body/form/file validation; request and
response conversion; OpenAPI generation; security schemes and credentials;
exception types and handlers; background tasks; Server-Sent Events; TestClient;
static files and templates; middleware; lifespan hooks; and the CLI boundary.
The exact source signatures, aliases, deprecations, required inputs, optional
profiles, and observations are maintained per operation in the manifest and
parity index. Class APIs are split into observable constructors, methods,
properties, protocols, aliases, and failures instead of being represented by
class names alone.

FastAPI 0.157.0 adds `telemetry` as the first keyword-only `FastAPI` constructor
parameter. The current constructor parameters, in source order, are `telemetry`,
`debug`, `routes`, `title`, `summary`, `description`, `version`, `openapi_url`,
`openapi_tags`, `servers`, `dependencies`, `default_response_class`,
`redirect_slashes`, `docs_url`, `redoc_url`,
`swagger_ui_oauth2_redirect_url`, `swagger_ui_init_oauth`, `middleware`,
`exception_handlers`, `on_startup`, `on_shutdown`, `lifespan`,
`terms_of_service`, `contact`, `license_info`, `root_path`,
`root_path_in_servers`, `responses`, `callbacks`, `webhooks`, `deprecated`,
`include_in_schema`, `swagger_ui_parameters`, `generate_unique_id_function`,
`separate_input_output_schemas`, `openapi_external_docs`, and
`strict_content_type`. The `openapi_prefix` parameter and `**extra` catchall
were removed upstream before this pin and are not part of the 0.157.0 contract.
`routes` and `root_path` retain deprecation metadata. The callable signature,
annotations, `Doc` strings, defaults, and deprecation markers are reflected from
the pinned source in the API and signature artifacts.

The seven documented parameter helpers `Path`, `Query`, `Header`, `Cookie`,
`Body`, `Form`, and `File` are distinct from their `fastapi.params` field-info
classes. `Depends` and `Security` define dependency declarations, and the
public security classes expose async dependency calls as well as constructors.
`fastapi.openapi.models` contributes 43 public model and type names; FastAPI
also exposes large exception, response, upload, request, websocket, SSE, and
security namespaces. Keep aliases and the identity of directly imported
Starlette objects explicit.

## Deprecations and compatibility aliases

Deprecation is part of the pinned contract: preserve accepted arguments,
annotations, warnings, logs, and emitted schema where observable.

| Surface | FastAPI 0.157.0 contract |
| --- | --- |
| `FastAPI(routes=...)` and `APIRouter(routes=...)` | Accepted with deprecation metadata as inherited Starlette compatibility parameters. |
| `FastAPI(root_path=...)` | Accepted with deprecation metadata; configure the server root path instead. Non-empty values also emit `FastAPIDeprecationWarning`. |
| `FastAPI.on_event(...)` and `APIRouter.on_event(...)` | Deprecated lifespan compatibility API. |
| `regex` and singular `example` parameter metadata | Deprecated alternatives retained alongside `pattern` and `examples`. |
| `UJSONResponse` and `ORJSONResponse` | Deprecated response classes; optional serializers are needed only when rendering. |
| `fastapi.middleware.wsgi.WSGIMiddleware` | Deprecated import alias; upstream recommends `a2wsgi.WSGIMiddleware`. |
| `FastAPI(openapi_prefix=...)` and `FastAPI(**extra)` | Removed before the selected release; neither belongs in the current constructor surface. |

The root and module-level aliases are listed in the API inventory and
classification artifacts. In particular, `fastapi.Response` and
`fastapi.responses.Response` are the same Starlette class object in the source
oracle; `fastapi.WebSocket` and `fastapi.websockets.WebSocket` are likewise an
identity alias. Module reexports do not automatically imply package-root
exports.

## Starlette behavior delegated through the full replacement

The selected Starlette oracle remains 1.6.0. FastAPI 0.157.0's Starlette
imports, subclass edges, and application-integration requirements are recorded
in the generated API inventory and compatibility atlas. The generic Starlette
surface remains owned by the sibling Starlette-RS contract.

FastAPI inherits `starlette.applications.Starlette` in `applications.py:26,42`
and `APIRouter` inherits `starlette.routing.Router` in `routing.py:91,2255`.
The replacement dependency is assumed to be a complete Starlette substitute;
therefore Starlette's own manifest owns its public API denominator. FastAPI's
contract must still test integration at these seams and must not duplicate
Starlette endpoints as if FastAPI implemented them independently.

FastAPI publicly exposes or inherits these major Starlette behavior families:

- ASGI invocation, request/response scope semantics, startup/shutdown/lifespan,
  mounted sub-applications, route matching, path parameters, URL generation,
  trailing-slash redirects, middleware stack order, exception handlers, and
  app state;
- `Request`, `HTTPConnection`, `Response` and built-in response constructors;
  request headers/query/cookies/body/form/upload, streaming, redirects,
  conditional/range/file responses, response headers/cookies/background tasks;
- WebSocket state transitions, accept/send/receive/close, iteration, disconnect
  codes and exceptions;
- router/route/mount types, static files, templates, test client, background
  task scheduling, concurrency helpers and middleware;
- status constants and the imported Starlette types/objects used in public
  FastAPI signatures.

Against the selected Starlette 1.6.0 contract, FastAPI relies on more than the
named public reexports: it imports/uses `starlette._exception_handler`'s
`wrap_app_handling_exceptions`, `starlette._utils`'s `get_route_path` and
`is_async_callable`, plus routing types/helpers (`Route`, `Router`,
`WebSocketRoute`, `Mount`, `BaseRoute`, `Match`, `compile_path`,
`request_response`, `websocket_session`, `get_name`) and threadpool helpers.
FastAPI overrides Starlette routing/app construction and relies on the exact
ASGI scope, `BaseRoute` matching, exception middleware, and task/lifespan
contracts. Mark these as required cross-project integration requirements, not
as a permission to use Starlette private APIs as FastAPI public objects. The
source-location crosswalk is in [`COMPATIBILITY_ATLAS.md`](COMPATIBILITY_ATLAS.md).

FastAPI also depends on Pydantic v2 as a user-facing type/schema boundary:
endpoint Python annotations and callable signatures drive dependency
inspection, request validation, response filtering/serialization, and OpenAPI
schema output. `fastapi.UploadFile` integrates with Pydantic core/json schema;
`fastapi.openapi.models` are Pydantic models; `fastapi._compat` adapts field,
schema and validation behavior. A Rust implementation needs a declared Python
facade/interop contract for user-defined callables, type annotations, Pydantic
models and exceptions; reimplementing only HTTP routing does not satisfy the
FastAPI API.

## Source-visible names that need an explicit policy

The generated API inventory records source-level exports, imports, definitions,
reexports, and likely public candidates. A source name is not a support claim.
For each candidate, `metadata.yaml` and the compatibility atlas record whether
the FastAPI contract is supported, private/internal, or uncertain and link the
source evidence, relevant fixture mappings, aliases, deprecations, and optional
requirements. Undocumented implementation helpers under `fastapi._compat`,
`fastapi.dependencies`, `fastapi.utils`, and similar modules are classified
individually rather than accepted because tests import or monkeypatch them.

## Mapping to the canonical manifest

For the single `tests/fixtures/manifest.yaml`:

1. Use oracle identity FastAPI `0.157.0`, CPython version, Pydantic identity,
   and the selected Starlette 1.6.0 source identity, plus behavior-relevant
   optional extras. Keep source dependency-lock inventory separate from the
   sole selected compatibility profile.
2. Use one public target profile: the Python `fastapi` consumer surface. Bind
   each Python operation to its FastAPI-RS implementation owner; the PyO3
   packaging crate is not a separate implementation or target profile.
3. Create canonical surfaces for root exports and module namespaces; record
   object aliases as aliases, not extra unrelated operations. Expand each
   class into independently observable constructor, public method, property,
   iteration/protocol and exception operations.
4. Use explicit `delegated_to: starlette-rs`-style target bindings for inherited
   Starlette contract, while retaining FastAPI integration cases for app and
   router inheritance, request parsing, middleware/lifespan, response types,
   exceptions, and TestClient.
5. Map every parameter family and deprecation in this report to the exact
   parameter-level manifest metadata; test both accepted legacy arguments and
   emitted warning/log/schema behavior.
6. Use FastAPI docs/tutorial examples and upstream tests to derive input-only
   parity actions. Each live source result and target result must be produced
   in isolated processes from the same actions; do not save expected outputs
   in inputs.
7. Make inventory discovery check: root imports, the 73 documented targets,
   documented members, module reexports, optional CLI scope, and intentional
   private exclusions. A name-only count cannot claim full parity.

Primary source anchors: `fastapi/__init__.py`; `applications.py`;
`routing.py`; `param_functions.py`; `params.py`; `exceptions.py`;
`dependencies/models.py` and `dependencies/utils.py`; `_compat/v2.py`;
`openapi/models.py` and `openapi/utils.py`; `security/*.py`; `responses.py`;
`sse.py`; `datastructures.py`; `background.py`. Primary docs anchors are the
reference pages listed above, `how-to/extending-openapi.md`,
`how-to/custom-request-and-route.md`, `tutorial/frontend.md`,
`tutorial/handling-errors.md`, `advanced/wsgi.md`, and the release notes.
