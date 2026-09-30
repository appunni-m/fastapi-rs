# FastAPI public API scope

## Authority and inventory method

This inventory is grounded in the FastAPI `0.141.1` release tag, commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, from a local source checkout. The
FastAPI-RS compatibility environment uses
Starlette `1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` as its sole
Starlette contract, plus Pydantic `2.13.4` and HTTPX `0.28.1`. FastAPI declares
`starlette>=0.46.0`, which admits 1.6.0. The source lock is used for dependency
inventory only; all compatibility and parity runs use Starlette 1.6.0.

Method: read the pinned package's root imports and Python sources; collect every
`fastapi.*` `mkdocstrings` target in `docs/en/docs`; cross-check reference
pages, tutorials/how-to docs, release notes, and imports in tests; then inspect
the inheritance/reexport edges to Starlette. The pinned package has 48 Python
source files, 24 reference Markdown pages, 61 unique reference autodoc targets,
and 492 `test_*.py` modules. These are inventory inputs, **not** the number of
manifest operations. Many targets expand into classes with multiple methods,
many public names are aliases, and the `status`/OpenAPI-model targets expand to
large value/model sets. The active manifest indexes 452 required public
symbols with source-inventory and runtime-reflection pointers. This is the
reviewed API denominator, not an implementation-support count. It records 222
runtime-reflected signatures, one unavailable constructor signature for
`Example` (`TypedDict(total=False)`), one module object with no call signature,
and 228 non-callable values/fields. The source inventory records its
`total=False` class option; runtime reflection records its required and optional
keys. Broader operation-level behavior and full implementation coverage remain
pending.

The API authority is the versioned source plus its English reference and
user-facing docs. The migration-parity manifest should preserve fully qualified
spelling, exact Python parameter names/kinds/defaults/annotations, aliases,
deprecation metadata, and observable results. Treat each overload/member as a
separate manifest operation when callers can invoke or inspect it separately.
Use an explicit target mapping for native Rust APIs rather than treating a
Python alias or Rust convenience name as the same public symbol. This document
is an audit aid; it is not a second manifest or an execution result.

Runtime namespace reflection complements the AST inventory in
[`runtime-api-surface-core.json`](../tests/fixtures/runtime-api-surface-core.json)
and [`runtime-api-surface-standard.json`](../tests/fixtures/runtime-api-surface-standard.json).
The artifacts cover all 1,593 source symbol IDs: the core profile reflects
1,590, with `templating` and `testclient` unavailable because their optional
packages are absent; the standard plus `docs-tests` profile reflects 1,592.
Both deliberately skip `fastapi.__main__`, whose import invokes the CLI.
Reflection records importable module names, callable signatures, exact object
identity aliases, deprecation metadata, and 49 Pydantic-generated OpenAPI model
classes with their fields and inherited Pydantic members. These profiles are
CPython 3.12.13 runtime evidence, not behavioral parity or cross-version proof.
Regenerate them with `make parity-prepare-oracle parity-prepare-oracle-standard`
followed by `make parity-api-runtime`.

## Root import surface

`fastapi/__init__.py` has no `__all__`. It defines `__version__` and makes 20
explicit reexports. The reexported object identity is part of import
compatibility; aliases in the table use `as` intentionally in the source.

| Import spelling | Source object / source location | Notes |
| --- | --- | --- |
| `fastapi.__version__` | constant `"0.141.1"`, `fastapi/__init__.py:3` | Package version value. |
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

### Current target facade availability

The root facade currently exposes 14 of the 21 source bindings:
`__version__`, `APIRouter`, `Body`, `Cookie`, `Depends`, `FastAPI`, `File`,
`Form`, `Header`, `Path`, `Query`, `Response`, `UploadFile`, and `status`.
The missing exports are `BackgroundTasks`, `HTTPException`,
`WebSocketException`, `Security`, `Request`, `WebSocket`, and
`WebSocketDisconnect`. Availability here means import-level presence; it does
not prove source object identity, full signatures, or behavior. The generated
manifest's `target_binding.public_python_path` records the required spelling,
and target status remains `full-contract-not-established` until live interface
and behavior parity are recorded.

`fastapi.status` is a Starlette module reexport in the oracle. The current
target builds a smaller status module in FastAPI-RS, so module presence alone
does not establish the required object identity or full constant set. Treat
that as a target gap until it reexports the Starlette-RS-owned namespace and
passes identity-checked comparison.

## Documented reference targets

The following are all 61 distinct `fastapi.*` autodoc targets discovered under
`docs/en/docs` (the “reference” pages contain all of them). Page paths are
relative to `docs/en/docs/reference/`.

| Reference page | Fully qualified targets |
| --- | --- |
| `fastapi.md` | `fastapi.FastAPI` |
| `apirouter.md` | `fastapi.APIRouter` |
| `parameters.md` | `fastapi.Query`, `fastapi.Path`, `fastapi.Body`, `fastapi.Cookie`, `fastapi.Header`, `fastapi.Form`, `fastapi.File` |
| `dependencies.md` | `fastapi.Depends`, `fastapi.Security` |
| `exceptions.md` | `fastapi.HTTPException`, `fastapi.WebSocketException` |
| `background.md` | `fastapi.BackgroundTasks` |
| `uploadfile.md` | `fastapi.UploadFile` |
| `request.md`, `httpconnection.md` | `fastapi.Request`, `fastapi.requests.HTTPConnection` |
| `websockets.md` | `fastapi.WebSocket`, `fastapi.websockets.WebSocketDisconnect`, `fastapi.websockets.WebSocketState` |
| `response.md`, `responses.md` | `fastapi.Response`; `fastapi.responses.UJSONResponse`, `ORJSONResponse`, `FileResponse`, `HTMLResponse`, `JSONResponse`, `PlainTextResponse`, `RedirectResponse`, `Response`, `StreamingResponse` |
| `encoders.md` | `fastapi.encoders.jsonable_encoder` |
| `security/index.md` | `fastapi.security.APIKeyCookie`, `APIKeyHeader`, `APIKeyQuery`, `HTTPBasic`, `HTTPBearer`, `HTTPDigest`, `HTTPAuthorizationCredentials`, `HTTPBasicCredentials`, `OAuth2`, `OAuth2AuthorizationCodeBearer`, `OAuth2PasswordBearer`, `OAuth2PasswordRequestForm`, `OAuth2PasswordRequestFormStrict`, `SecurityScopes`, `OpenIdConnect` |
| `middleware.md` | `fastapi.middleware.cors.CORSMiddleware`, `fastapi.middleware.gzip.GZipMiddleware`, `fastapi.middleware.httpsredirect.HTTPSRedirectMiddleware`, `fastapi.middleware.trustedhost.TrustedHostMiddleware` |
| `staticfiles.md`, `templating.md`, `testclient.md` | `fastapi.staticfiles.StaticFiles`, `fastapi.templating.Jinja2Templates`, `fastapi.testclient.TestClient` |
| `sse.md` | `fastapi.sse.EventSourceResponse`, `fastapi.sse.ServerSentEvent` |
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

Source locations below refer to the pinned FastAPI tree. The full callable
signature—including `Annotated` metadata and deprecation annotations—is the
definition in that tree; shorthand signatures here omit verbose `Doc(...)`
metadata only. The inventory generator should retain that metadata in the
manifest or indexed machine-readable inventory.

### `FastAPI` and `APIRouter`

`FastAPI` is defined in `fastapi/applications.py:42`; its constructor at
`:58-1018` accepts the Starlette app settings plus FastAPI schema, dependency,
middleware, response, docs, and routing options. Parameter names in order are:
`debug`, `routes`, `title`, `summary`, `description`, `version`, `openapi_url`,
`openapi_tags`, `servers`, `dependencies`, `default_response_class`,
`redirect_slashes`, `docs_url`, `redoc_url`,
`swagger_ui_oauth2_redirect_url`, `swagger_ui_init_oauth`, `middleware`,
`exception_handlers`, `on_startup`, `on_shutdown`, `lifespan`,
`terms_of_service`, `contact`, `license_info`, `openapi_prefix`, `root_path`,
`root_path_in_servers`, `responses`, `callbacks`, `webhooks`, `deprecated`,
`include_in_schema`, `swagger_ui_parameters`, `generate_unique_id_function`,
`separate_input_output_schemas`, `openapi_external_docs`,
`strict_content_type`, and `**extra`. Defaults are part of the signature (notably
`openapi_url='/openapi.json'`, `docs_url='/docs'`, `redoc_url='/redoc'`,
`root_path=''`, `strict_content_type=True`, and `Default(...)` sentinels).
Capture the source annotations/default expressions rather than substituting
`None` for sentinels.

Direct FastAPI members and source anchors:

| Member family | Names / behavior | Source |
| --- | --- | --- |
| ASGI and initialization | `__call__(scope, receive, send)`, `setup()`, `build_middleware_stack()` | `fastapi/applications.py:1020-1163` |
| OpenAPI | `openapi()`; cached `openapi_schema`; invalidated as router routes change | `applications.py:1070-1104` |
| HTTP route registration | `add_api_route`, `api_route`, `get`, `put`, `post`, `delete`, `options`, `head`, `patch`, `trace` | `applications.py:1165-4644` |
| WebSocket route registration | `add_api_websocket_route`, `websocket`, `websocket_route` | `applications.py:1361-1375`, `4645-4661` |
| Router composition | `include_router` with prefix/tags/dependencies/responses/default response/callbacks/deprecation/schema/ID policy | `applications.py:1441-1645` |
| App hooks | `middleware`, `exception_handler`, deprecated `on_event` | `applications.py:4662-4770` |
| Frontend mounting | `frontend(path, *, directory, fallback='auto', check_dir='auto')` | `applications.py:1222-1300`; also documented in tutorial `frontend.md` |
| Public app attributes | OpenAPI metadata/settings, `webhooks`, `root_path`, `state`, `dependency_overrides`, `router`, `routes`, `exception_handlers`, `middleware_stack`, `openapi_schema` | constructor `applications.py:58-1018`; reference member allowlist in `docs/en/docs/reference/fastapi.md` |

HTTP verb decorators share the exact keyword-only signature family shown by
`FastAPI.get` (`applications.py:1646-2018`):

```text
get/put/post/delete/options/head/patch/trace(
    self, path, *, response_model=Default(None), status_code=None, tags=None,
    dependencies=None, summary=None, description=None,
    response_description='Successful Response', responses=None,
    deprecated=None, operation_id=None, response_model_include=None,
    response_model_exclude=None, response_model_by_alias=True,
    response_model_exclude_unset=False, response_model_exclude_defaults=False,
    response_model_exclude_none=False, include_in_schema=True,
    response_class=Default(JSONResponse), name=None, callbacks=None,
    openapi_extra=None,
    generate_unique_id_function=Default(generate_unique_id)
) -> decorator(endpoint) -> endpoint
```

`APIRouter` is `fastapi/routing.py:2255`. Its constructor at `:2282-2569` is
`APIRouter(*, prefix='', tags=None, dependencies=None,
default_response_class=Default(JSONResponse), responses=None, callbacks=None,
routes=None, redirect_slashes=True, default=None,
dependency_overrides_provider=None, route_class=APIRoute, on_startup=None,
on_shutdown=None, lifespan=None, deprecated=None, include_in_schema=True,
generate_unique_id_function=Default(generate_unique_id),
strict_content_type=Default(True))`. Members include `add_route`,
`add_websocket_route`, `route`, `add_api_route`, `api_route`,
`add_api_websocket_route`, `websocket`, `websocket_route`, `include_router`,
the same eight HTTP decorators, `frontend`, `on_event`, plus ASGI routing
`app`, `handle`, and `matches`. The router methods have their own source
signatures at `routing.py:2604-6453`; they are not identical in every detail to
`FastAPI` (e.g. router `add_api_route` accepts `route_class_override` and
`strict_content_type`).

`APIRoute` (`routing.py:1126-1367`) is a supported customization point in the
how-to docs. Its constructor declares endpoint, response model/status,
dependencies, response filtering/aliases, response class, callbacks,
OpenAPI extras, unique-ID generation, and strict content-type policy;
`get_route_handler`, `matches`, and `handle` affect request behavior.
`APIWebSocketRoute` (`routing.py:801-870`) handles WebSocket endpoints. These
must be inventoried even though the reference page documents them through
`FastAPI`/`APIRouter` rather than a separate autodoc target. New route-tree
types (`RouteContext`, `iter_route_contexts`) appear in `routing.py`; they are
currently implementation-level structure except where exposed through route
customization and OpenAPI traversal.

`FastAPI`/`APIRouter` route operation parameters cover:

- route identity: `path`, method or method list, operation ID, name, response
  status and description;
- dependency graph: endpoint callable, `Depends`/`Security`, route/router/app
  dependencies, scopes, cache and dependency lifetime;
- request parsing: path/query/header/cookie/body/form/file fields, aliases,
  embedded bodies, media types, multipart and strict content type;
- validation: Pydantic annotations, parameter constraints, validation errors,
  and forward references;
- serialization: response model/type, response include/exclude and alias
  policy, unset/default/None filters, streaming and SSE item type;
- OpenAPI: tags, summary/description, responses, callbacks, deprecation,
  schema inclusion, examples, extra schema and unique-ID generation;
- composition: prefixes, router defaults/overrides, included routers,
  webhooks, mounted ASGI applications, frontend/static paths, and lifespan.

### Parameter and dependency declarations

The seven documented helper functions `Path`, `Query`, `Header`, `Cookie`,
`Body`, `Form`, `File` are defined separately in `fastapi/param_functions.py`
and construct `fastapi.params`/Pydantic field metadata. Shared keyword families
include `default`, `default_factory`, `alias`, `alias_priority`,
`validation_alias`, `serialization_alias`, `title`, `description`, numeric
constraints (`gt/ge/lt/le`, `multiple_of`, `allow_inf_nan`, `max_digits`,
`decimal_places`), length constraints, `pattern`, `regex`, `discriminator`,
`strict`, `examples`, `example`, `openapi_examples`, `deprecated`,
`include_in_schema`, `json_schema_extra`, and legacy `**extra`. Distinguish
per-helper defaults and constraints: `Path` requires a path default (`...`),
`Header` adds `convert_underscores=True`, `Body` adds `embed` and defaults to
`application/json`, `Form` defaults to `application/x-www-form-urlencoded`,
and `File` defaults to `multipart/form-data`. Exact definitions begin at
`fastapi/param_functions.py:13` (`Path`), `:357` (`Query`), `:701` (`Header`),
`:1018` (`Cookie`), `:1323` (`Body`), `:1653` (`Form`), and `:1968` (`File`).

`Depends(dependency=None, *, use_cache=True, scope=None)` and
`Security(dependency=None, *, scopes=None, use_cache=True)` are callables at
`param_functions.py:2283` and `:2372`. `scope` has `function` and `request`
lifetimes. Dependency signatures and generator/context-manager lifecycle are a
major public behavior family, not just these two helper constructors.

The `fastapi.params` module also defines importable `ParamTypes`, `Param`, and
`FieldInfo` subclasses `Path`, `Query`, `Header`, `Cookie`, `Body`, `Form`,
`File`, `Depends`, and `Security` (`params.py:19-753`). These class identities
are distinct from the root helper functions of the same names. The documented
root names refer to `param_functions` callables; keep both module surfaces
separate in the inventory.

### Other callable and data-object families

| Public surface | Member/signature inventory | Authority |
| --- | --- | --- |
| `jsonable_encoder` | `jsonable_encoder(obj, include=None, exclude=None, by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False, custom_encoder=None, sqlalchemy_safe=True)`; encodes Pydantic models, dataclasses, enums, paths, date/time, decimal, UUID and custom types to JSON-compatible Python data. | `fastapi/encoders.py:129-...`; tutorial encoder + reference `encoders.md` |
| `get_openapi` | keyword-only `title`, `version`, `openapi_version='3.1.0'`, `summary`, `description`, required `routes`, optional `webhooks`, `tags`, `servers`, `terms_of_service`, `contact`, `license_info`, `separate_input_output_schemas=True`, `external_docs`; returns schema dict. | `fastapi/openapi/utils.py:585-...`; documented by `how-to/extending-openapi.md` |
| Swagger/ReDoc HTML | `get_swagger_ui_html(*, openapi_url, title, swagger_js_url, swagger_css_url, swagger_favicon_url, oauth2_redirect_url, init_oauth, swagger_ui_parameters)`; `get_redoc_html(*, openapi_url, title, redoc_js_url, redoc_favicon_url, with_google_fonts=True)`; zero-arg `get_swagger_ui_oauth2_redirect_html()`; module constant `swagger_ui_default_parameters`. | `fastapi/openapi/docs.py:22-...`; reference `openapi/docs.md` |
| `BackgroundTasks` | `add_task(func, *args, **kwargs)`; accepts sync or async callable and delegates run-after-response behavior to Starlette. | `fastapi/background.py:11-...` |
| `UploadFile` | attributes `file`, `filename`, `size`, `headers`, `content_type`; async `write(data)`, `read(size=-1)`, `seek(offset)`, `close()`; Pydantic schema adapter. | `fastapi/datastructures.py:21-152` |
| `HTTPException` | constructor `(status_code, detail=None, headers=None)`; inherits Starlette attributes/HTTP response handling. | `fastapi/exceptions.py:17-84` |
| `WebSocketException` | constructor `(code, reason=None)`; inherits Starlette disconnect behavior. | `fastapi/exceptions.py:86-155` |
| Validation/operational exceptions | `FastAPIError`; `DependencyScopeError`; `RequestValidationError(errors, *, body=None, endpoint_ctx=None)`; `WebSocketRequestValidationError(errors, *, endpoint_ctx=None)`; `ResponseValidationError(errors, *, body=None, endpoint_ctx=None)`; common `ValidationException.errors()`, endpoint context and formatting; `FastAPIDeprecationWarning`; `PydanticV1NotSupportedError`. | `fastapi/exceptions.py:157-...`; errors tutorial and tests |
| SSE | `ServerSentEvent` fields `data`, `raw_data`, `event`, `id`, `retry`, `comment`; exclusive `data`/`raw_data`, line and NUL validation, nonnegative retry. `format_sse_event(*, data_str=None, event=None, id=None, retry=None, comment=None) -> bytes`. `EventSourceResponse` subclasses Starlette `StreamingResponse` and sets `text/event-stream`; routing adds JSON item serialization and ping behavior. | `fastapi/sse.py:20-237`, `fastapi/routing.py` SSE handling, reference `sse.md` |
| Security callables | Constructor parameter names: `APIKeyQuery/Header/Cookie(*, name, scheme_name=None, description=None, auto_error=True)`; `HTTPBasic(*, scheme_name=None, realm=None, description=None, auto_error=True)`; `HTTPBearer(*, bearerFormat=None, scheme_name=None, description=None, auto_error=True)`; `HTTPDigest(*, scheme_name=None, description=None, auto_error=True)`; `OAuth2(*, flows=OAuthFlowsModel(), scheme_name=None, description=None, auto_error=True)`; `OAuth2PasswordBearer(tokenUrl, scheme_name=None, scopes=None, description=None, auto_error=True, refreshUrl=None)`; `OAuth2AuthorizationCodeBearer(authorizationUrl, tokenUrl, refreshUrl=None, scheme_name=None, scopes=None, description=None, auto_error=True)`; `OpenIdConnect(*, openIdConnectUrl, scheme_name=None, description=None, auto_error=True)`. These implement async `__call__(request)` dependencies; optional auth (`auto_error=False`), credential shape, HTTP 401 headers/body, and generated OpenAPI security schemes are observable. | `fastapi/security/api_key.py:55-318`, `http.py:16-418`, `oauth2.py:14-653`, `open_id_connect_url.py:11-...`; `reference/security/index.md` |
| OAuth form/credential models | `HTTPBasicCredentials(username,password)`, `HTTPAuthorizationCredentials(scheme,credentials)`, `OAuth2PasswordRequestForm(*, grant_type=None, username, password, scope='', client_id=None, client_secret=None)`, strict form variant with required `grant_type`, and `SecurityScopes(scopes=None)`. The form classes are callable dependency records, not independent HTTP endpoints. | `fastapi/security/http.py:16-...`, `oauth2.py:14-...`; reference/security page |

The complete directly declared source methods for a documented class must be
enumerated individually during manifest generation. Important per-class
families include Pydantic model fields/validation/serialization, async
security dependency `__call__`, inherited response constructors/properties,
upload file I/O, WebSocket send/receive/iteration/state, Request body/form
methods, and TestClient's full client methods. Do not replace these with
class-name-only inventory entries.

## Module-level import-compatible aliases and optional surfaces

Some behavior is a FastAPI import facade over the selected Starlette package.
These names are intentionally reexported in source, even if they are not root
exports:

| FastAPI module path | Reexported API |
| --- | --- |
| `fastapi.requests` | `HTTPConnection`, `Request` |
| `fastapi.datastructures` | `URL`, `Address`, `FormData`, `Headers`, `QueryParams`, `State`; plus FastAPI's `UploadFile` subclass |
| `fastapi.responses` | Starlette `FileResponse`, `HTMLResponse`, `JSONResponse`, `PlainTextResponse`, `RedirectResponse`, `Response`, `StreamingResponse`; FastAPI `EventSourceResponse`, deprecated `UJSONResponse` and `ORJSONResponse` |
| `fastapi.websockets` | `WebSocket`, `WebSocketDisconnect`, `WebSocketState` |
| `fastapi.testclient` | Starlette `TestClient` |
| `fastapi.staticfiles`, `fastapi.templating` | Starlette `StaticFiles`, `Jinja2Templates` |
| `fastapi.middleware` | Starlette `Middleware`; submodules reexport `CORSMiddleware`, `GZipMiddleware`, `HTTPSRedirectMiddleware`, `TrustedHostMiddleware`; deprecated `fastapi.middleware.wsgi.WSGIMiddleware` remains importable at this tag |
| `fastapi.routing` | FastAPI `APIRouter`, `APIRoute`, `APIWebSocketRoute`; Starlette `Mount`; additional router tree structures |
| `fastapi.concurrency` | Starlette `iterate_in_threadpool`, `run_in_threadpool`, `run_until_first_complete`; FastAPI `contextmanager_in_threadpool` |

`pyproject.toml` defines the `fastapi` console script as
`fastapi.cli:main`. CLI support is an optional extra (`fastapi-cli`); `dev` and
`run` are separate command behavior and require an independently pinned CLI
identity if the replacement claims that extra. The CLI should not silently be
counted as a core library operation.

## Deprecations and compatibility aliases

These are still in the `0.141.1` source surface and must remain visible in the
contract; deprecation does not mean “omit from inventory.” Preserve warnings,
logging, accepted arguments, and emitted schema where observable.

| Symbol/argument | Lifecycle and behavior | Source |
| --- | --- | --- |
| `FastAPI(routes=...)` constructor argument | Marked deprecated in annotated signature; inherited Starlette compatibility path. | `applications.py:80-95` |
| `FastAPI(openapi_prefix=...)` | Marked deprecated in signature, recommends `root_path`; nonempty value also logs a deprecation warning and is used as root-path fallback. | `applications.py` constructor (`openapi_prefix` declaration near `:620`, behavior near `:920`) |
| `FastAPI.on_event(event_type)` / `APIRouter.on_event` | Deprecated; lifespan context manager is replacement. `FastAPI.on_event` is decorated with `typing_extensions.deprecated`. | `applications.py:4654-4681`; `routing.py:6423+` |
| `regex` field argument | Deprecated since FastAPI 0.100.0 / Pydantic v2; use `pattern`. Remains accepted and emits `FastAPIDeprecationWarning`. | `params.py:48-109` and corresponding helper signatures in `param_functions.py` |
| `example` field argument | Deprecated; use `examples`; remains accepted and emits `FastAPIDeprecationWarning`. | `params.py:61-78`; helpers at `param_functions.py` |
| legacy `extra` field kwargs | Deprecated in helper `Annotated` signatures; use `json_schema_extra`. Remains accepted and is merged into schema extras; the FastAPI `Param`/`Body` source does not issue a call-time warning for `extra` itself (it does for `example` and `regex`). | `param_functions.py:289-301`; `params.py:74-110, 519-569` |
| `UJSONResponse`, `ORJSONResponse` | Both decorated deprecated classes; instantiation warns. Still require optional `ujson`/`orjson` only when rendering. | `responses.py:48-105`; `tests/test_deprecated_responses.py` |
| `fastapi.middleware.wsgi.WSGIMiddleware` | Import compatibility reexport marked deprecated in release notes/docs; use `a2wsgi.WSGIMiddleware`. | `middleware/wsgi.py`; `docs/en/docs/advanced/wsgi.md` and release notes |
| `FastAPI(on_startup=..., on_shutdown=...)` | Legacy lifecycle path; use `lifespan`. These are accepted constructor options. Check the pinned Starlette runtime for warning semantics rather than inferring a warning from prose. | `applications.py:58-...` |

`Param.deprecated` / route `deprecated` fields are separate API metadata that
marks a parameter or operation deprecated in OpenAPI. They are not Python API
deprecation warnings.

## Starlette behavior delegated through the full replacement

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

The following names are importable from package modules but are either
undocumented, explicitly internal, or are source implementation structures.
Keep an inventory audit record for each and choose deliberately whether it is
inside the compatibility denominator; do not accidentally treat every
non-underscored imported dependency as FastAPI's API.

- `fastapi.exceptions`: `EndpointContext`, `ValidationException`,
  `RequestErrorModel`, `WebSocketErrorModel`, `PydanticV1NotSupportedError`,
  `DependencyScopeError`, `FastAPIError`, and `FastAPIDeprecationWarning`.
  The runtime exception classes used by handlers/tests are practically
  observable and should be included; request-model factory objects and context
  helper types need deliberate public/private classification.
- `fastapi.datastructures.Default`, `DefaultPlaceholder`, and `DefaultType`;
  source docstrings explicitly say not to use them directly, but route/default
  customization and release notes expose `DefaultPlaceholder.value` to
  advanced integrations.
- `fastapi.routing.APIRoute`, `APIWebSocketRoute`, and route-context classes;
  `APIRoute` is a documented customization point. `RouteContext` and included
  route tree nodes support current router internals and may be reachable via
  `.routes`; track behavior changes at the observable app surface.
- `fastapi.middleware.asyncexitstack.AsyncExitStackMiddleware`,
  `fastapi.middleware.wsgi.WSGIMiddleware`, `fastapi.concurrency.*`,
  `fastapi.utils.*`, `fastapi.dependencies.*`, and `fastapi._compat.*` contain
  implementation helpers/reexports. Private underscore names are not public
  API solely because tests import or monkeypatch them.
- `fastapi.cli.main` and package `fastapi.__main__` delegate to optional CLI
  installation; the console script is a separately selectable optional lane.

## Mapping to the canonical manifest

For the single `tests/fixtures/manifest.yaml`:

1. Use oracle identity FastAPI `0.141.1`, CPython version, Pydantic identity,
   and the selected Starlette 1.6.0 source identity, plus behavior-relevant
   optional extras. Keep source dependency-lock inventory separate from the
   sole selected compatibility profile.
2. Declare separate public target profiles for the Python facade and native
   Rust API if both are offered. The facade target must exercise the same
   import names shown above; a Rust-only API does not silently satisfy Python
   import operations.
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
7. Make inventory discovery check: root imports, the 61 docs targets,
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
