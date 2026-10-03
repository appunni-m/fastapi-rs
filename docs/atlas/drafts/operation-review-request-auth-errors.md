# Operation review draft: request parameters, security, and public errors

Status: source-backed draft only. No active metadata, input recipe, fixture, generated artifact, implementation, or parity result was changed or created.

## Scope and pinned identities

This review covers the following 50 operation IDs in `tests/fixtures/manifest.yaml`'s `api_surface_contract.symbols`:

- **Request parameter constructors / IncEx (17):** the eight `fastapi.param_functions` factories `Body`, `Cookie`, `Depends`, `File`, `Form`, `Header`, `Path`, and `Query`; the seven `fastapi.params` `__init__` operations for `Body`, `Cookie`, `File`, `Form`, `Header`, `Path`, and `Query`; `fastapi.encoders.jsonable_encoder`; and `fastapi.types.IncEx`.
- **Security (23):** exactly the security symbols whose manifest `operation_scope.status` is `scope-review-pending`, listed individually below. The `fastapi.Security` root alias and `fastapi.param_functions.Security` have `slice-described` scope and are not part of this group.
- **Errors (10):** `fastapi.HTTPException`, `fastapi.WebSocketException`, `fastapi.exception_handlers.http_exception_handler`, `fastapi.exception_handlers.request_validation_exception_handler`, `fastapi.exceptions.HTTPException`, `fastapi.exceptions.HTTPException.__init__`, `fastapi.exceptions.ValidationException.errors`, `fastapi.exceptions.WebSocketException`, `fastapi.exceptions.WebSocketException.__init__`, and `fastapi.exceptions.WebSocketRequestValidationError`.

Pinned contract identities:

- FastAPI 0.141.1, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Python requirement `>=3.10`; oracle profile CPython 3.12.13.
- Pydantic 2.13.4 and pydantic-core 2.46.4.
- Starlette 1.6.0 is the selected Starlette oracle.
- Starlette-RS contract revision: commit `37c6615e5b54d820d70b9d910d2e06fda8ae4cfe`, descendant of the `dd2c1ac66982218f749f0510758f64f5e61c735b` WebSocket scope-mapping commit. The clean detached checkout used for this review is `/private/tmp/fastapi-rs-starlette-rs-37c6615` at `37c6615`.

The source paths and line numbers below refer to FastAPI 0.141.1 at the pinned commit. The local oracle environment reflected CPython 3.12.13, FastAPI 0.141.1, Pydantic 2.13.4, and Starlette 1.6.0. Starlette-RS `5c80d4e` added an input-only `StaticFiles` HEAD mapping after the WebSocket scope mapping at `dd2c1ac`. Latest commit `37c6615` changes only benchmark and compatibility-inventory documentation. These changes do not affect the request, security, or error contracts reviewed here. The `WebSocket` scope-mapping input and selectors from `dd2c1ac` remain in the latest manifest; they do not change FastAPI's parameter factories, security dependencies, exception constructors, handler registration, or close-code contract. The FastAPI WebSocket error path calls `WebSocket.close`; it does not rely on WebSocket's mapping interface.

## Status applied to every candidate

All 50 selected IDs are classified `supported` in the compatibility atlas as upstream source candidates. In the manifest, every selected ID has `operation_scope.status: scope-review-pending` and `target_binding.status: full-contract-not-established`. Those fields do not establish FastAPI-RS support. Current route and response observations below are input coverage only; no result is claimed.

The grouping counts by manifest visibility are:

| Group | IDs | `public` | `public_protocol` | `public_candidate` |
|---|---:|---:|---:|---:|
| Request parameter constructors / IncEx | 17 | 9 | 7 | 1 |
| Security | 23 | 11 | 7 | 5 |
| Errors | 10 | 6 | 2 | 2 |

## Request parameter constructors and IncEx

### Exact operation IDs, signatures, and declarations

`default_factory`, `alias_priority`, `strict`, `multiple_of`, `allow_inf_nan`, `max_digits`, and `decimal_places` use the `_Unset` source default, a FastAPI `DefaultPlaceholder` whose value is `None` (`fastapi/datastructures.py:153-186`); the reflected signature renders it as `Default(None)`. These defaults are intentionally distinct from an explicit `None`. The shared compact signature below lists common fields in source order and omits each `Annotated[..., Doc(...)]` wrapper. Family-specific insertion points are stated below and in each candidate row; the source spans contain the complete parameter order, annotations, and documentation metadata.

For the `Param`-derived markers and their eight selected factory/class operations (`Path`, `Query`, `Header`, `Cookie`), shared keyword parameters are:

```text
default_factory: Callable[[], Any] \| None = _Unset
alias: str | None = None
alias_priority: int | None = _Unset
validation_alias: str | AliasPath | AliasChoices | None = None
serialization_alias: str | None = None
title: str | None = None
description: str | None = None
gt/ge/lt/le: float | None = None
min_length/max_length: int | None = None
pattern: str | None = None
regex: str | None = None [deprecated]
discriminator: str | None = None
strict: bool | None = _Unset
multiple_of: float | None = _Unset
allow_inf_nan: bool | None = _Unset
max_digits: int | None = _Unset
decimal_places: int | None = _Unset
examples: list[Any] | None = None
example: Any | None = _Unset [deprecated]
openapi_examples: dict[str, Example] | None = None
deprecated: typing_extensions.deprecated | str | bool | None = None
include_in_schema: bool = True
json_schema_extra: dict[str, Any] | None = None
**extra: Any
```

Each of the seven selected `params.*.__init__` constructors also takes `annotation: Any | None = None`, which is absent from its corresponding factory signature. The body-family factories insert `embed`/`media_type` after `default_factory` and before common fields; their class constructors insert `annotation` after `default_factory`, then `embed`/`media_type`, then common fields. `Body` has `embed: bool \| None = None` and `media_type` `application/json`; `Form` and `File` have media types `application/x-www-form-urlencoded` and `multipart/form-data`, respectively. In both the `Header` factory and constructor, `convert_underscores: bool = True` is inserted after `alias` and before `alias_priority`.

On each `param_functions` factory, `**extra` is marked deprecated in the annotation metadata and its documentation says to use `json_schema_extra` instead (`fastapi/param_functions.py:289-301`, repeated in the factory declarations). The corresponding `params.*.__init__` declarations use plain `**extra: Any` and forward extra schema fields; that constructor parameter is not itself annotated as deprecated (`fastapi/params.py:29-72`).

| Manifest candidate ID | Pinned declaration and signature delta |
|---|---|
| `fastapi.param_functions.Body` | `fastapi/param_functions.py:1323-1650`, `def Body(default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, embed: bool \| None = None, media_type: str = "application/json", <common Param options>) -> Any`; factory default is reflected as `PydanticUndefined`. |
| `fastapi.param_functions.Cookie` | `fastapi/param_functions.py:1018-1320`, `def Cookie(default: Any = Undefined, *, <Param options>) -> Any`; omission uses the undefined sentinel. |
| `fastapi.param_functions.Depends` | `fastapi/param_functions.py:2283-2369`, `def Depends(dependency: Callable[..., Any] \| None = None, *, use_cache: bool = True, scope: Literal["function", "request"] \| None = None) -> Any`; `dependency` is optional at declaration time so FastAPI can infer it from an annotated dependency type. |
| `fastapi.param_functions.File` | `fastapi/param_functions.py:1968-2280`, `def File(default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, media_type: str = "multipart/form-data", <common Param options>) -> Any`. |
| `fastapi.param_functions.Form` | `fastapi/param_functions.py:1653-1965`, `def Form(default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, media_type: str = "application/x-www-form-urlencoded", <common Param options>) -> Any`. |
| `fastapi.param_functions.Header` | `fastapi/param_functions.py:701-1015`, `def Header(default: Any = Undefined, *, <common options with `convert_underscores: bool = True` inserted after `alias`>) -> Any`; the option controls the derived header alias. |
| `fastapi.param_functions.Path` | `fastapi/param_functions.py:13-354`, `def Path(default: Any = ..., *, <Param options>) -> Any`; path parameters remain required and the implementation rejects a different default. |
| `fastapi.param_functions.Query` | `fastapi/param_functions.py:357-698`, `def Query(default: Any = Undefined, *, <Param options>) -> Any`; omission uses the undefined sentinel. |
| `fastapi.params.Body.__init__` | `fastapi/params.py:470-575`, `Body.__init__(self, default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, embed: bool \| None = None, media_type: str = "application/json", <shared field options>, **extra: Any)`; no explicit return annotation. |
| `fastapi.params.Cookie.__init__` | `fastapi/params.py:390-466`, `Cookie.__init__(self, default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, <shared Param options>, **extra: Any)`; no explicit return annotation. |
| `fastapi.params.File.__init__` | `fastapi/params.py:664-742`, `File.__init__(self, default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, media_type: str = "multipart/form-data", <shared field options>, **extra: Any)`; no explicit return annotation. |
| `fastapi.params.Form.__init__` | `fastapi/params.py:582-660`, `Form.__init__(self, default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, media_type: str = "application/x-www-form-urlencoded", <shared field options>, **extra: Any)`; no explicit return annotation. |
| `fastapi.params.Header.__init__` | `fastapi/params.py:306-384`, `Header.__init__(self, default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, alias: str \| None = None, convert_underscores: bool = True, alias_priority: int \| None = _Unset, validation_alias: str \| AliasPath \| AliasChoices \| None = None, serialization_alias: str \| None = None, <remaining common Param options>, **extra: Any)`; no explicit return annotation. |
| `fastapi.params.Path.__init__` | `fastapi/params.py:140-218`, `Path.__init__(self, default: Any = ..., *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, <shared Param options>, **extra: Any)`; no explicit return annotation; it asserts `default is ...`. |
| `fastapi.params.Query.__init__` | `fastapi/params.py:224-300`, `Query.__init__(self, default: Any = Undefined, *, default_factory: Callable[[], Any] \| None = _Unset, annotation: Any \| None = None, <shared Param options>, **extra: Any)`; no explicit return annotation. |
| `fastapi.encoders.jsonable_encoder` | `fastapi/encoders.py:129-366`, `jsonable_encoder(obj: Any, include: IncEx \| None = None, exclude: IncEx \| None = None, by_alias: bool = True, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, custom_encoder: dict[type[Any], Callable[[Any], Any]] \| None = None, sqlalchemy_safe: bool = True) -> Any`. |
| `fastapi.types.IncEx` | `fastapi/types.py:7`, `from pydantic.main import IncEx as IncEx`; this is a re-exported type alias, not a FastAPI constructor. Pydantic 2.13.4 defines the recursive alias in `pydantic/main.py:77` as a union of integer/string sets and integer/string mappings to `IncEx \| bool`. |

`Param` and `Body` implement the shared option semantics. The implicit `validation_alias` and `serialization_alias` fall back to a string `alias`; an explicit alias is also used by FastAPI to build the request field. `Header` converts underscores to hyphens when it must derive the alias from a Python parameter name and `convert_underscores` remains true. `Path` always has a required route value even though its signature accepts `default` and `default_factory` for compatibility. Other parameter requiredness is determined from the undefined/default value when FastAPI constructs the Pydantic field; the function signature alone does not imply a particular field is required.

`regex` is marked deprecated and warns when non-`None`; `example` is marked deprecated and warns if explicitly supplied, including an explicit `None`. Both warnings are raised by FastAPI's `Param` / `Body` initialization (`fastapi/params.py:48-67,74-79,104-109,491-510,519-524,549-554`), not by Starlette or Pydantic. The deprecated `**extra` annotation applies to the factory declarations; the class initializers retain a plain `**extra: Any`. No selected factory or constructor itself is decorated as deprecated. The source uses `Annotated`, PEP 604 unions, and builtin generic syntax, hence Python 3.10+; `AliasPath` and `AliasChoices` types are Pydantic APIs.

### FastAPI / Starlette / Pydantic ownership and call chain

FastAPI's `get_dependant()` inspects endpoint signatures and recursively builds dependencies (`fastapi/dependencies/utils.py:271-347`). `analyze_param()` identifies `Depends`, `FieldInfo`, and the parameter classes; it chooses inferred `Path`, `File`, `Body`, or `Query` when an endpoint parameter has no explicit marker (`utils.py:381-547`). `add_param_to_fields()` routes path/query/header/cookie fields (`utils.py:550-565`), then `request_params_to_args()` and `request_body_to_args()` extract data and invoke field validation (`utils.py:780-879,951-1024`). FastAPI owns this declaration analysis, alias derivation, dependency graph, and error aggregation. Pydantic owns `FieldInfo`, `AliasPath`, `AliasChoices`, and core validation; FastAPI adapts those models and validation calls. Starlette owns the incoming ASGI request and generic request/header/query/cookie/form data interfaces; its 1.6.0 contract is the only generic oracle selected here.

`Depends` creates a frozen `params.Depends` record consumed by `get_dependant()`. `use_cache` controls dependency-result reuse, while `scope` is passed into the dependency graph. The separate `Security` marker carries scopes and is handled by the same graph; its two public helper IDs are explicitly outside this pending group because the manifest already describes a slice.

`jsonable_encoder` is FastAPI-owned conversion behavior. It uses the imported Pydantic `IncEx` type in `include` and `exclude`; Pydantic handles model serialization and its include/exclude form, while FastAPI handles recursive conversion for dataclasses, enums, paths, special types, and custom encoders. FastAPI response serialization passes `response_model_include` and `response_model_exclude` through `fastapi/routing.py:301-342,366-461`; the default request-validation handler also calls `jsonable_encoder` for `exc.errors()` (`fastapi/exception_handlers.py:20-26`). The `IncEx` alias identity/type shape remains Pydantic-owned.

### Existing input recipes and limits

Existing inputs include endpoint-level request cases and direct `jsonable_encoder` call probes. The latter bind directly to that selected callable; route cases do not independently import, signature-check, or construct each selected factory/class:

| Recipe | Relevant selectors and limit |
|---|---|
| `tests/fixtures/input-recipes/parity/request-validation-parameters.yaml` | Its `fastapi.request-parameters.path.*`, `.query.*`, `.header.*`, and `.cookie.*` cases observe HTTP `status` and `body`; cases cover missing/invalid values, aliases, repeated values, and header underscore conversion. They do not check factory/class identity, all constructor options, or Pydantic field metadata directly. |
| `tests/fixtures/input-recipes/parity/request-parameter-matrix.yaml` | `fastapi.request-param-matrix.{query,header,path,body}.*` cases observe `status` and `body`; covers selected optional/missing/present values and path alias combinations. No direct constructor or signature probe. |
| `tests/fixtures/input-recipes/parity/request-forms.yaml` | `fastapi.request-forms.*` cases observe `status` and `body`; covers URL-encoded form values, form sequences/models, invalid/missing values and selected extra fields. |
| `tests/fixtures/input-recipes/parity/request-multipart.yaml` | `fastapi.request-multipart.{form,file,mixed}.*` cases observe `status` and `body`; covers required/optional/repeated form/file fields, `bytes` and upload values, mixed form+file, and selected validation aliases. Starlette's multipart parser/upload objects and the installed multipart dependency are outside the FastAPI constructor contract. |
| `tests/fixtures/input-recipes/parity/request-coercion.yaml` | Four cases observe `status` and `body` for JSON typing, GET body, content-type rejection, and model aliases; these are route-level coercion cases. |
| `tests/fixtures/input-recipes/parity/param-class-query-wave.yaml` | Two `fastapi.param-class.query-*` cases observe `status` and `body` for a Query default absent/present; not an exhaustive `Query.__init__` contract. |
| `tests/fixtures/input-recipes/parity/dependency-wave.yaml` | `fastapi.dependency-wave.*` cases observe `status` and `body` for regular `Depends` construction/use and override flows; not direct `Depends` signature or identity. |
| `tests/fixtures/input-recipes/parity/jsonable-encoder-atlas-wave.yaml` | Directly calls `fastapi.encoders.jsonable_encoder`; probes in `output-matrix` observe Python `value` for include/exclude sets, lists and generators, model/nested filters, encoders and special values. The unsupported-value and Pydantic-v1 rejection probes observe `outcome`. Manifest selectors are `python.attribute_value` and `python.call_outcome` (the source workflow selectors are `python_return_value.value` and `python_call_outcome.outcome`). This is the strongest direct input for `jsonable_encoder`, but does not independently import or compare `fastapi.types.IncEx` identity or test every recursive alias form. |
| `tests/fixtures/input-recipes/parity/encoding.yaml` | Nine direct-call cases: `fastapi.jsonable-encoder.tutorial.datetime-model`, `.mapping.{include,exclude}`, `.model.{alias,defaults,exclude-unset,exclude-defaults}`, and `.custom-encoder.{exact-type,base-type}`. Each selects callable return `value` and signature; manifest selectors are `python.attribute_value` and `python.signature`. |
| `tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml` | `fastapi.direct-api-reference-wave.encoder-reference-dataclass` directly observes `value` and `signature` for `jsonable_encoder`; its input is a dataclass case, not the full encoder signature contract. |
| `tests/fixtures/input-recipes/parity/pydantic-core-encoder-compatibility.yaml` | `fastapi.jsonable-encoder.pydantic-undefined` (`undefined-sentinel`) and `fastapi.jsonable-encoder.pydantic-core-urls` (`raw-core-url`, `public-any-url`) directly select callable return `value`; manifest selector is `python.attribute_value`. |
| `tests/fixtures/input-recipes/parity/response-model-include-exclude-source-review.yaml` and `response-model-data-filter-exclude-unset-none-review.yaml` | HTTP `status`/`body` selectors show route response filtering by include/exclude and exclude-unset/none. They test a response-model path, not standalone `IncEx` import/type behavior. |

Sixteen of the 17 selected IDs have no candidate-specific `input_workflow_refs`. `fastapi.encoders.jsonable_encoder` has 76 refs spanning the four direct-call recipes above. These include direct output and signature probes, but there is still no import/type identity probe for `fastapi.types.IncEx` or isolated direct signature/identity/constructor/error probe for each parameter factory and `params.*.__init__`. Empty include/exclude behavior, nested `IncEx` mappings with both integer and string keys and `True` sentinels, alias generators/priorities, deprecated-argument warnings, `Path` rejected defaults, and the complete field-option surface remain unverified by these recipes.

## Security APIs

### Exact pending IDs, signatures, and declarations

The five `fastapi.security.*` import bindings below are the pending public package re-exports. Their constructor signature is the signature of the class at the destination path. All re-export declarations are direct imports; no deprecation is attached to these names.

| Manifest candidate ID | Pinned declaration and signature |
|---|---|
| `fastapi.security.OAuth2AuthorizationCodeBearer` | Re-export `fastapi/security/__init__.py:10`; constructor at `fastapi/security/oauth2.py:553-640`: `(authorizationUrl: str, tokenUrl: str, refreshUrl: str \| None = None, scheme_name: str \| None = None, scopes: dict[str, str] \| None = None, description: str \| None = None, auto_error: bool = True)`. First two arguments are required positional-or-keyword parameters. |
| `fastapi.security.OAuth2PasswordRequestForm` | Re-export `security/__init__.py:12`; constructor at `security/oauth2.py:59-153` is keyword-only: `grant_type: str \| None = None`, required `username: str` and `password: str`, `scope: str = ""`, `client_id: str \| None = None`, `client_secret: str \| None = None`. The form metadata requires `grant_type` to match `^password$` when supplied. |
| `fastapi.security.OAuth2PasswordRequestFormStrict` | Re-export `security/__init__.py:13`; constructor at `security/oauth2.py:226-327` is positional-or-keyword: required `grant_type: str`, `username: str`, and `password: str`; `scope: str = ""`; `client_id: str \| None = None`; `client_secret: str \| None = None`. Its required `grant_type` has form pattern `^password$`. |
| `fastapi.security.OpenIdConnect` | Re-export `security/__init__.py:15`; keyword-only constructor at `security/open_id_connect_url.py:22-73`: required `openIdConnectUrl: str`, then `scheme_name: str \| None = None`, `description: str \| None = None`, `auto_error: bool = True`. The camel-case spelling is the declared keyword. |
| `fastapi.security.SecurityScopes` | Re-export `security/__init__.py:14`; constructor at `security/oauth2.py:666-693`: `scopes: list[str] \| None = None`; positional-or-keyword and optional. It stores `scopes or []` and joins them into `scope_str`. |
| `fastapi.security.http.HTTPAuthorizationCredentials.scheme` | `security/http.py:51-58`, required Pydantic field `scheme: Annotated[str, Doc(...)]`; no default, alias, or deprecation. The `credentials` sibling is not one of this pending ID set. |
| `fastapi.security.http.HTTPBase.make_not_authenticated_error` | `security/http.py:87-92`, `make_not_authenticated_error(self) -> fastapi.exceptions.HTTPException`; no arguments beyond `self`. It builds a 401 error with `detail="Not authenticated"` and an HTTP authenticate challenge derived from the scheme. |
| `fastapi.security.http.HTTPBasicCredentials.password` | `security/http.py:26`, required Pydantic field `password: Annotated[str, Doc(...)]`; no default, alias, or deprecation. |
| `fastapi.security.http.HTTPBasicCredentials.username` | `security/http.py:25`, required Pydantic field `username: Annotated[str, Doc(...)]`; no default, alias, or deprecation. |
| `fastapi.security.oauth2.OAuth2.make_not_authenticated_error` | `security/oauth2.py:401-421`, `make_not_authenticated_error(self) -> fastapi.exceptions.HTTPException`; no arguments beyond `self`. It creates status 401, detail `"Not authenticated"`, and `WWW-Authenticate: Bearer`. |
| `fastapi.security.oauth2.OAuth2AuthorizationCodeBearer` | Class at `security/oauth2.py:547-650`, subclass of `OAuth2`; exact initializer parameters are given for the package re-export above. No class-level alias or deprecation. |
| `fastapi.security.oauth2.OAuth2AuthorizationCodeBearer.__call__` | `security/oauth2.py:642-650`, `async __call__(self, request: starlette.requests.Request) -> str \| None`; request is required. It returns the bearer parameter or raises/returns `None` according to `auto_error`. |
| `fastapi.security.oauth2.OAuth2AuthorizationCodeBearer.__init__` | `security/oauth2.py:553-640`; same signature and requiredness as the package re-export above; positional-or-keyword, no `*`. |
| `fastapi.security.oauth2.OAuth2PasswordRequestForm` | Class at `security/oauth2.py:14-159`; its signature is the re-export signature above. It receives its fields through `Form` annotations and turns the whitespace-separated `scope` string into a list. |
| `fastapi.security.oauth2.OAuth2PasswordRequestForm.__init__` | `security/oauth2.py:59-159`; same keyword-only signature and requiredness as the package re-export above. The username/password form field names are fixed; optional `grant_type`, client credentials, and scope carry the stated defaults. |
| `fastapi.security.oauth2.OAuth2PasswordRequestFormStrict` | Class at `security/oauth2.py:162-327`; signature is the strict re-export signature above. It requires `grant_type`. |
| `fastapi.security.oauth2.OAuth2PasswordRequestFormStrict.__init__` | `security/oauth2.py:226-327`; same positional-or-keyword signature as the strict re-export above; there is no leading `*`, so positional arguments are accepted by the declaration. |
| `fastapi.security.oauth2.SecurityScopes` | Class at `security/oauth2.py:653-693`; signature is the package re-export signature above. It is a FastAPI dependency-injection value, not a Pydantic model. |
| `fastapi.security.oauth2.SecurityScopes.__init__` | `security/oauth2.py:666-693`; `__init__(self, scopes: list[str] \| None = None)`; positional-or-keyword, optional; no explicit return annotation, alias, or deprecation. |
| `fastapi.security.open_id_connect_url.OpenIdConnect` | Class at `security/open_id_connect_url.py:11-94`; signature is the package re-export signature above. Source documentation explicitly describes this implementation as a stub rather than a complete OIDC protocol implementation. |
| `fastapi.security.open_id_connect_url.OpenIdConnect.__call__` | `security/open_id_connect_url.py:87-94`, `async __call__(self, request: starlette.requests.Request) -> str \| None`; it returns the raw Authorization header when present. |
| `fastapi.security.open_id_connect_url.OpenIdConnect.__init__` | `security/open_id_connect_url.py:22-78`; same keyword-only signature and required camel-case `openIdConnectUrl` as the package re-export above. |
| `fastapi.security.open_id_connect_url.OpenIdConnect.make_not_authenticated_error` | `security/open_id_connect_url.py:80-85`, `make_not_authenticated_error(self) -> starlette.exceptions.HTTPException`; no arguments beyond `self`. Unlike `HTTPBase` and `OAuth2`, this source imports and constructs Starlette's base HTTP exception. |

These declarations use PEP 604 unions, builtin generic types, and `Annotated`/`Doc`, so the source requires Python 3.10+. The selected declarations are not marked deprecated. Form fields rely on the FastAPI `Form` marker and Pydantic validation; the exact form parsing layer also depends on Starlette's request/form interface and multipart support.

### FastAPI and Starlette ownership / route call chain

Security scheme objects carry FastAPI-owned `model`, `scheme_name`, and `auto_error` state. Endpoint and dependency signatures are parsed by `get_dependant()` (`fastapi/dependencies/utils.py:271-347`); the solver recognizes `SecurityScopes` for injection (`utils.py:350-371,721-724`) and passes scopes from `params.Security` through nested dependencies (`utils.py:290-330`). When FastAPI constructs OpenAPI, it walks dependencies, accumulates OAuth scopes, and projects security models and scope requirements into the document (`fastapi/openapi/utils.py:99-150`). That is a FastAPI dependency/OpenAPI integration contract.

The scheme callables read Starlette `Request` headers/cookies/query parameters. API-key and HTTP-auth classes return credential values or raise FastAPI/Starlette HTTP exceptions; FastAPI's dependency solver invokes the callable. `HTTPBasicCredentials` and `HTTPAuthorizationCredentials` are Pydantic models/fields. Pydantic owns their field validation, while FastAPI constructs them from the parsed header credentials. Starlette owns request-header/query/cookie/form access and its generic ASGI behavior. The exception response conversion and HTTP response transport also cross the separately pinned Starlette exception/response boundary.

Specific FastAPI source behavior in this group:

- `HTTPBase.__call__` (not a candidate ID in this pending set) reads `Authorization`, splits its scheme and credentials, uses `auto_error`, and calls the pending `make_not_authenticated_error` method (`security/http.py:94-102`). HTTPBasic, HTTPBearer, and HTTPDigest provide the HTTP scheme configuration (`http.py:105-...`, `222-...`, `319-...`).
- The OAuth2 base class parses no token itself: its `__call__` returns the Authorization string or uses the pending OAuth2 error method (`security/oauth2.py:401-430`). The authorization-code bearer override splits the header, requires a bearer scheme, and returns the token parameter (`oauth2.py:642-650`).
- The password-form dependency has a signature FastAPI can inspect; its `Form`-marked constructor parameters become form fields, then `__init__` stores them (`oauth2.py:59-159`). The strict subclass requires the OAuth2 grant type in the same manner (`oauth2.py:226-327`).
- `SecurityScopes` is injected by FastAPI's dependency solver with the combined scopes, and OpenAPI's dependency traversal separately propagates scope requirements. The public constructor's caller-supplied value path and the solver-filled value path are therefore distinct candidate behaviors.
- `OpenIdConnect` builds an OpenAPI scheme model but source explicitly says it is a stub. Its callable returns the header unchanged and does not parse or validate a complete OIDC flow (`open_id_connect_url.py:11-19,74-94`). Its authentication error is a Starlette `HTTPException`, not the FastAPI subclass.

### Existing input recipes and limits

The following recipes use route-level inputs for related pending candidates. They do not establish public import identity or the full direct class/method signature unless a probe explicitly says so.

| Recipe | Candidate relation, cases, selectors, and limits |
|---|---|
| `tests/fixtures/input-recipes/parity/security_credentials_upstream.yaml` | The `fastapi.security.api-key-{cookie,query,...}.*`, `http-basic-*`, `http-bearer-*`, and `http-base-*` cases observe HTTP `status`, `headers`, `body`; selected OpenAPI cases observe `status`, `headers` and JSON pointers under `/components/securitySchemes/...` and `/paths/.../security`. These route cases expose selected HTTP credential and challenge behavior, including missing/optional credentials and some OpenAPI scheme data. They do not directly construct `HTTPAuthorizationCredentials` or `HTTPBasicCredentials`, check field requiredness, or call `HTTPBase.make_not_authenticated_error` directly. |
| `tests/fixtures/input-recipes/parity/http-basic.yaml` | `fastapi.advanced.security.http-basic.*` observes `status`, `headers`, `body`; its OpenAPI case observes status/headers. It includes valid/missing/malformed Basic credentials and scheme mismatch, not direct credential model construction or the pending method's identity. |
| `tests/fixtures/input-recipes/parity/security-wave.yaml` | `fastapi.security-wave.http-base-*`, `http-digest-*`, `oauth2-base`, `oauth2-optional`, and `http-basic-*` cases observe `status`, `headers`, `body`; OpenAPI cases select status and pointers for the security scheme and operation security. The nested-scope case selects `/components/securitySchemes/ScopedOAuth2` and `/paths/~1security~1scoped-admin/get/security`. This is route behavior, not direct `OAuth2.make_not_authenticated_error` invocation. |
| `tests/fixtures/input-recipes/parity/security_oauth_openapi_upstream.yaml` | Authorization-code cases `fastapi.security.oauth2-authorization-code-bearer.*` and scope cases observe HTTP `status`, `headers`, `body`; OpenAPI cases observe pointers for authorization-code URLs/scopes and operation `security`. OpenID cases `fastapi.security.openid-connect*` similarly select status/headers/body plus scheme URL/type/description and operation security. Password-bearer and generic OAuth2 cases cover selected token/header behavior and OpenAPI. These do not inspect constructor signatures, import identity, all URL/scope options, or implement/verify full OIDC semantics. |
| `tests/fixtures/input-recipes/parity/security-oauth2-strict-required-gap-wave.yaml` | Strict form cases `fastapi.security-gap.oauth2-strict-required.*` observe HTTP `status`, `headers`, `body`; the OpenAPI case selects security scheme, `/paths/~1login/post/requestBody`, and a protected operation's `security`. Covers missing/incorrect/correct grant type and login body. |
| `tests/fixtures/input-recipes/parity/security-oauth2-strict-optional-gap-wave.yaml` | `fastapi.security-gap.oauth2-strict-optional.*` observes `status`, `headers`, `body`; the OpenAPI case selects the login `requestBody` and protected operation security. Covers selected optional strict-form routes, not direct `__init__` signature. |
| `tests/fixtures/input-recipes/parity/security-oauth2-optional-description-strict-form-gap-wave.yaml` | `fastapi.security-gap.oauth2-optional-description.test-strict-login-*` cases observe `status`, `headers`, `body` for strict login inputs; the cases do not include an OpenAPI pointer observation or constructor identity check. |
| `tests/fixtures/input-recipes/parity/security_scopes_upstream.yaml` | `fastapi.security.scopes*` cases observe `status`, `headers`, `body` for a dependency called once, scope non-propagation, and subdependency caching. They do not observe `SecurityScopes` object identity, the direct `scopes` constructor default, or `scope_str`. |
| `tests/fixtures/input-recipes/parity/security-tutorial005-auth-scopes-gap-wave.yaml` | Token/scope route cases observe `status`, `headers`, `body`; an OpenAPI case is present for selected scopes. This is route and document projection only. |
| `tests/fixtures/input-recipes/parity/security-declaration-api.yaml` | The `fastapi.security.declaration-public-surface` probes select `python_signature.signature` for `fastapi.Security` and `fastapi.param_functions.Security`, plus `python_call_outcome.outcome` for a scoped declaration. Those two helpers are already slice-described and expressly excluded from the 23 pending IDs; this input does not directly inspect any of the pending security class IDs. |

No pending security ID has an `input_workflow_ref` in the manifest for a standalone constructor/signature/import-identity probe. Existing recipes provide selected end-to-end HTTP and OpenAPI projections, but there is no direct identity/signature workflow for the five package re-exports, no direct tests for the required/optional model fields, and no direct invocation result for either pending not-authenticated method. The scope recipes do not establish all scope aggregation/caching cases. The OIDC recipes establish only the explicitly selected stub-level route/OpenAPI cases.

## Public exception types and handlers

### Exact operation IDs, declarations, and signatures

| Manifest candidate ID | Pinned declaration and signature |
|---|---|
| `fastapi.HTTPException` | `fastapi/__init__.py:10`, direct re-export `from .exceptions import HTTPException as HTTPException`; same object as `fastapi.exceptions.HTTPException`. Class and initializer follow below. |
| `fastapi.WebSocketException` | `fastapi/__init__.py:11`, direct re-export `from .exceptions import WebSocketException as WebSocketException`; same object as `fastapi.exceptions.WebSocketException`. Class and initializer follow below. |
| `fastapi.exception_handlers.http_exception_handler` | `fastapi/exception_handlers.py:11-17`, `async def http_exception_handler(request: starlette.requests.Request, exc: starlette.exceptions.HTTPException) -> starlette.responses.Response`; both parameters required. The annotated exception is Starlette's base HTTP exception, so it also accepts FastAPI's subclass. |
| `fastapi.exception_handlers.request_validation_exception_handler` | `fastapi/exception_handlers.py:20-26`, `async def request_validation_exception_handler(request: starlette.requests.Request, exc: fastapi.exceptions.RequestValidationError) -> starlette.responses.JSONResponse`; both parameters required. |
| `fastapi.exceptions.HTTPException` | `fastapi/exceptions.py:17-83`, class extending `starlette.exceptions.HTTPException`. Its initializer is the selected operation below. |
| `fastapi.exceptions.HTTPException.__init__` | `fastapi/exceptions.py:45-83`, `(self, status_code: int, detail: Any = None, headers: Mapping[str, str] \| None = None) -> None`; `status_code` is required, `detail` and `headers` optional. `headers` is a mapping; it is passed to Starlette unchanged. |
| `fastapi.exceptions.ValidationException.errors` | `fastapi/exceptions.py:174-191`, `errors(self) -> Sequence[Any]`; no parameters beyond `self`, returns the stored error sequence. The owning base type itself is not one of the ten operation IDs. |
| `fastapi.exceptions.WebSocketException` | `fastapi/exceptions.py:86-154`, class extending `starlette.exceptions.WebSocketException`; its initializer is the selected operation below. |
| `fastapi.exceptions.WebSocketException.__init__` | `fastapi/exceptions.py:128-154`, `(self, code: int, reason: str \| None = None) -> None`; `code` required; `reason` optional. It delegates both to Starlette's base exception. |
| `fastapi.exceptions.WebSocketRequestValidationError` | `fastapi/exceptions.py:224-231`, class extending `ValidationException` with no local initializer. It inherits `ValidationException.__init__(errors: Sequence[Any], *, endpoint_ctx: EndpointContext \| None = None)`: errors required; endpoint context optional keyword-only. |

FastAPI's handler annotations use PEP 604 unions, `Mapping`/`Sequence` from `collections.abc`, and `Annotated`/`Doc`; Python 3.10+ is required. Neither exception subclass is decorated as deprecated. `HTTPException` and `WebSocketException` inherit Starlette's exception types and public transport semantics; the subclass constructor/annotations are FastAPI source behavior. `RequestValidationError` and `WebSocketRequestValidationError` store FastAPI's aggregated errors and optional endpoint context. Pydantic supplies validation error records; FastAPI supplies the aggregation, context, exception type, default handler registration, and encoding path.

### FastAPI / Starlette ownership and call chain

`FastAPI.__init__` installs defaults for the Starlette HTTP exception, `RequestValidationError`, and `WebSocketRequestValidationError` (`fastapi/applications.py:1000-1012`). FastAPI passes those handler mappings into Starlette's `ExceptionMiddleware` as part of building its middleware stack (`applications.py:1022-1040`). Starlette owns generic exception dispatch, the base exception classes, `Response`/`JSONResponse`, and ASGI delivery. FastAPI owns its exception subclasses and handler functions.

- `http_exception_handler` preserves `exc.headers`; if `is_body_allowed_for_status_code()` is false it returns an empty Starlette `Response`. Otherwise it returns a Starlette `JSONResponse` containing `{"detail": exc.detail}` (`exception_handlers.py:11-17`). It does not call `jsonable_encoder` for arbitrary HTTP exception detail.
- `request_validation_exception_handler` encodes `exc.errors()` with FastAPI's `jsonable_encoder` and returns status 422 with `{"detail": ...}` (`exception_handlers.py:20-26`). Pydantic-originated error records and FastAPI's encoded 422 body have distinct owners.
- `WebSocketException` is a Starlette subclass; Starlette's exception middleware handles the raised websocket exception and the socket close semantics. There is no selected FastAPI default `websocket_exception_handler` function in this group.
- FastAPI's WebSocket request route raises `WebSocketRequestValidationError` on dependency validation failure (`fastapi/routing.py:767-793`); FastAPI registers its default websocket validation handler in `applications.py:1009-1012`, and that handler calls `websocket.close(...)` with the policy-violation code and encoded validation errors (`exception_handlers.py:29-35`).
- HTTP route request validation aggregates solver errors into `RequestValidationError` before the default handler runs (`fastapi/routing.py:444-456,744-755`). `ValidationException.errors()` simply returns the stored sequence; its public behavior is independent from how Starlette dispatches it.

The `dd2c1ac` Starlette-RS WebSocket scope-mapping input adds observations for a `WebSocket` used as a scope mapping. The FastAPI websocket validation handler above uses `.close`, and the `WebSocketException` contract is its code/reason delegation to Starlette. Those mapping selectors do not change either error constructor or handler path.

### Existing input recipes and limits

| Recipe | Exact observations and limit |
|---|---|
| `tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml` | Cases `fastapi.direct-api-reference-wave.http-exception-signature` and `...websocket-exception-signature` call root `fastapi.HTTPException` / `fastapi.WebSocketException` and select `python_signature.signature`. They compare the root-callable signatures; they do not independently probe constructor outcome, exception public attributes, headers/code/reason types, or the module-qualified import. |
| `tests/fixtures/input-recipes/parity/root-alias-identity.yaml` | `fastapi.root-alias-identity.http-reexports` selects HTTP `status`/`body`; the associated manifest identity workflow projects root-to-module re-export identity relations. This is a workload projection, not a live target result. |
| `tests/fixtures/input-recipes/parity/public-errors-http-websocket-wave.yaml` | The FastAPI HTTP detail/header and bodyless-status cases observe construction `outcome`, `exception_class`, `exception_message`, plus HTTP `status`, `headers`, `body`. The pre-accept WebSocket case observes the same construction selectors plus WebSocket `close_code`, `close_reason`, and `event_order`. It covers selected constructor-to-response behavior, not every exception attribute or direct handler signature. |
| `tests/fixtures/input-recipes/parity/request-validation-exception-handler.yaml` | Path/body/malformed-JSON/form cases and the server-error-precedence case observe construction `outcome`, `exception_class`, `exception_message`, plus HTTP `status`, `headers`, `body`. This is handler/route behavior; it does not directly call `ValidationException.errors()` or exhaust validation detail variants. |
| `tests/fixtures/input-recipes/parity/validation-error-context-upstream.yaml` | HTTP cases observe `status` and `body`; WebSocket and mounted-WebSocket cases observe `validation_error_class`. It covers selected endpoint context and error class results, not direct `endpoint_ctx` constructor/signature or all error record contents. |
| `tests/fixtures/input-recipes/parity/exception-overrides.yaml` | Override route cases observe HTTP `status`, `headers`, `body`; OpenAPI case observes status/headers. They exercise handler registration/override precedence at route level, not every handler's direct callable interface. |
| `tests/fixtures/input-recipes/parity/security-api-key-exception-boundary.yaml` | Missing API-key header case selects HTTP `status`, `headers`, `body`; relevant to the FastAPI HTTP exception handler boundary and `WWW-Authenticate` result, but not an isolated handler invocation. |

The two root aliases have a signature recipe and a root-to-module identity input, and error responses have selected end-to-end recipes. The manifest still marks all ten operation scopes pending and all target bindings `full-contract-not-established`. None of these recipe inputs is proof of parity. No recipe directly checks every FastAPI exception object's `.args`, exact public attributes, `HTTPException` header mapping edge cases, all body-allowed status classes, `ValidationException.errors()` sequence identity, or endpoint-context formatting. The WebSocket validation handler function is upstream call-chain context but is not one of the 10 selected operation IDs.

## Review conclusions

- Keep source classification separate from target support: every candidate is a public/source candidate, but all 50 manifest operations remain scope-review-pending and have no full target contract.
- FastAPI owns parameter/dependency declaration analysis, security integration, FastAPI exception subclasses, handler registration, response validation aggregation, and FastAPI's JSONable conversion. Pydantic owns `IncEx`, `FieldInfo`, aliases/core validation, and model credential fields. Starlette 1.6.0 owns generic request/form/response/exception/WebSocket behavior and is the sole Starlette oracle.
- Existing recipes establish selected route, response, and OpenAPI observation surfaces. They do not replace direct identity/signature/constructor probes for the pending IDs or prove parity by their presence alone.
- Starlette-RS `37c6615` preserves the `dd2c1ac` WebSocket scope-mapping and `5c80d4e` StaticFiles HEAD input mappings; both are unrelated to every selected parameter, security, exception, and handler declaration/call contract.
