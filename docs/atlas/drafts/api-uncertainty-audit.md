# FastAPI 0.141.1 API uncertainty audit

> **Historical snapshot (superseded 2026-10-03).** The 205 unresolved source-import rows identified here are now reviewed in `tests/fixtures/api-source-classification-review.json` schema `@2`. Current authoritative counts are in the generated compatibility atlas.


## Scope and result

Read-only audit of `tests/fixtures/compatibility-atlas.json` and its four referenced classification review artifacts, using the pinned identities recorded in those local files. The atlas pins FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; the import-binding overlay also pins Starlette 1.6.0 and Starlette-RS contract commit `0ca02a3b9dc5ae8984b5bd4d0a650a8df0cf9f76`. No test, parity, or atlas generation command was run.

All 1,593 `api_candidates` rows have one of the three allowed classifications and a non-empty `source_evidence` record containing a source path, line, and module hash. All 461 `supported` rows have `public_evidence`; empty public evidence on private/internal or uncertain rows is consistent with the policy. The gap is narrower: **205 uncertain rows have source evidence but no candidate-specific review reason or review evidence.**

| Atlas classification | Rows |
| --- | ---: |
| supported | 461 |
| private/internal | 899 |
| uncertain | 233 |

The atlas references these review artifacts; each recorded SHA-256 matches the current local file, the source identities agree with the FastAPI pin, and the four candidate ID sets are disjoint.

| Review artifact | Rows | supported | private/internal | uncertain |
| --- | ---: | ---: | ---: | ---: |
| `api-classification-review.json` (callables) | 137 | 47 | 72 | 18 |
| `api-source-classification-review.json` | 187 | 6 | 179 | 2 |
| `api-public-candidate-classification-review.json` | 137 | 9 | 125 | 3 |
| `api-import-binding-classification-review.json` | 97 | 7 | 85 | 5 |
| **Total reviewed IDs** | **558** | **137** | **461** | **28** |

All 28 uncertain candidates covered by those artifacts also carry a non-empty `classification_review.reason` and `classification_review.evidence` in the atlas. The remaining 205 do not.

## Evidence-backed unresolved points

The 28 reviewed uncertainties are legitimate open contract questions, rather than missing review records. Their artifacts record candidate-specific reasons and source/document/test references. The reasons consistently distinguish source importability or exercised behavior from a documented consumer-facing contract:

- **18 callable candidates** in `api-classification-review.json` have source/test or related-document evidence, but the reviewed evidence does not establish the exact member contract. Examples include `FastAPI.api_route`, `FastAPI.websocket_route`, and `RouteContext` accessors.
- **2 source API candidates** in `api-source-classification-review.json` remain uncertain: `fastapi.responses.EventSourceResponse` (alternate import path exposure) and `fastapi.sse.EventSourceResponse.media_type` (member exposure).
- **3 public-looking candidates** in `api-public-candidate-classification-review.json` remain uncertain: `FastAPIDeprecationWarning`, `RequestErrorModel`, and `WebSocketErrorModel`. The source/release-note evidence does not resolve the exact public member contract.
- **5 Starlette import bindings** in `api-import-binding-classification-review.json` have explicit FastAPI binding and canonical Starlette/Starlette-RS evidence, but no evidence establishing the FastAPI-side path as public: `iterate_in_threadpool`, `run_in_threadpool`, `run_until_first_complete`, `fastapi.middleware.Middleware`, and `fastapi.routing.Mount`.

These 28 should stay `uncertain` until pinned documentation or an explicit reviewed contract resolves the path/member question. In particular, a supported Starlette-RS target does not by itself establish a separate FastAPI import path.

## Unreviewed uncertain rows

The other 205 uncertain candidates are all `kind: import_binding` with `visibility: imported_name`. Each has a source path/line/hash, but has no `classification_review` object and is absent from all four review artifacts. Their atlas `classification_evidence_rule` is only the generic policy, “Importability from this module is not by itself public API evidence”; `public_evidence` is empty. That policy explains why importability is insufficient, but it does not document a per-candidate decision.

The IDs below are `module.local_name` pairs. They are the complete set of uncertain rows missing a candidate-specific review reason/evidence:

| Module | Count | Local names |
| --- | ---: | --- |
| `fastapi.__main__` | 1 | `main` |
| `fastapi.applications` | 22 | `AsyncExitStackMiddleware`, `DecoratedCallable`, `Default`, `DefaultPlaceholder`, `Depends`, `Doc`, `Enum`, `IncEx`, `RequestValidationError`, `WebSocketRequestValidationError`, `deprecated`, `generate_unique_id`, `get_openapi`, `get_redoc_html`, `get_swagger_ui_html`, `get_swagger_ui_oauth2_redirect_html`, `http_exception_handler`, `logger`, `os`, `request_validation_exception_handler`, `routing`, `websocket_request_validation_exception_handler` |
| `fastapi.background` | 2 | `Doc`, `ParamSpec` |
| `fastapi.concurrency` | 3 | `AbstractContextManager`, `CapacityLimiter`, `anyio` |
| `fastapi.datastructures` | 2 | `Doc`, `GetJsonSchemaHandler` |
| `fastapi.dependencies.models` | 2 | `inspect`, `sys` |
| `fastapi.dependencies.utils` | 4 | `dataclass`, `dataclasses`, `inspect`, `sys` |
| `fastapi.encoders` | 26 | `AnyUrl`, `BaseModel`, `Decimal`, `Doc`, `Enum`, `GeneratorType`, `IPv4Address`, `IPv4Interface`, `IPv4Network`, `IPv6Address`, `IPv6Interface`, `IPv6Network`, `IncEx`, `NameEmail`, `Path`, `Pattern`, `PurePath`, `PydanticUndefinedType`, `PydanticV1NotSupportedError`, `SecretBytes`, `SecretStr`, `UUID`, `dataclasses`, `datetime`, `defaultdict`, `deque` |
| `fastapi.exceptions` | 3 | `BaseModel`, `Doc`, `create_model` |
| `fastapi.logger` | 1 | `logging` |
| `fastapi.middleware.asyncexitstack` | 1 | `AsyncExitStack` |
| `fastapi.openapi.docs` | 3 | `Doc`, `json`, `jsonable_encoder` |
| `fastapi.openapi.models` | 8 | `AnyUrl`, `BaseModel`, `Enum`, `Field`, `GetJsonSchemaHandler`, `TypedDict`, `logger`, `typing_deprecated` |
| `fastapi.openapi.utils` | 25 | `BaseModel`, `Body`, `DefaultPlaceholder`, `Dependant`, `DependencyCacheKey`, `FastAPIDeprecationWarning`, `METHODS_WITH_BODY`, `ModelNameMap`, `OpenAPI`, `ParamTypes`, `REF_PREFIX`, `Response`, `copy`, `dataclass`, `deep_dict_update`, `field`, `generate_operation_id_for_path`, `get_flat_params`, `get_validation_alias`, `http`, `inspect`, `is_body_allowed_for_status_code`, `jsonable_encoder`, `routing`, `warnings` |
| `fastapi.param_functions` | 6 | `AliasChoices`, `AliasPath`, `Doc`, `Example`, `deprecated`, `params` |
| `fastapi.params` | 9 | `AliasChoices`, `AliasPath`, `Enum`, `Example`, `FastAPIDeprecationWarning`, `FieldInfo`, `dataclass`, `deprecated`, `warnings` |
| `fastapi.responses` | 1 | `importlib` |
| `fastapi.routing` | 51 | `AbstractAsyncContextManager`, `AbstractContextManager`, `AsyncExitStack`, `ContextVar`, `DecoratedCallable`, `Default`, `DefaultPlaceholder`, `Dependant`, `Doc`, `EndpointContext`, `Enum`, `EventSourceResponse`, `FastAPIError`, `IncEx`, `IntEnum`, `KEEPALIVE_COMMENT`, `ObjectReceiveStream`, `RequestValidationError`, `ResponseValidationError`, `ServerSentEvent`, `SolvedDependency`, `WebSocketRequestValidationError`, `anyio`, `asynccontextmanager`, `contextlib`, `copy`, `create_model_field`, `dataclass`, `deprecated`, `email`, `errno`, `field`, `format_sse_event`, `functools`, `generate_unique_id`, `get_dependant`, `get_parameterless_sub_dependant`, `get_stream_item_type`, `get_typed_return_annotation`, `get_value_or_default`, `inspect`, `is_body_allowed_for_status_code`, `json`, `jsonable_encoder`, `os`, `params`, `solve_dependencies`, `stat`, `threading`, `types`, `warnings` |
| `fastapi.security.api_key` | 4 | `APIKey`, `APIKeyIn`, `Doc`, `SecurityBase` |
| `fastapi.security.base` | 1 | `SecurityBaseModel` |
| `fastapi.security.http` | 9 | `BaseModel`, `Doc`, `HTTPBaseModel`, `HTTPBearerModel`, `HTTPException`, `SecurityBase`, `b64decode`, `binascii`, `get_authorization_scheme_param` |
| `fastapi.security.oauth2` | 7 | `Doc`, `Form`, `HTTPException`, `OAuth2Model`, `OAuthFlowsModel`, `SecurityBase`, `get_authorization_scheme_param` |
| `fastapi.security.open_id_connect_url` | 3 | `Doc`, `OpenIdConnectModel`, `SecurityBase` |
| `fastapi.types` | 3 | `BaseModel`, `Enum`, `types` |
| `fastapi.utils` | 8 | `DefaultPlaceholder`, `DefaultType`, `FastAPIDeprecationWarning`, `FieldInfo`, `PydanticV1NotSupportedError`, `fastapi`, `re`, `warnings` |
| **Total** | **205** | |

Within this gap, **170** rows have a non-null `imported_module`; **35** are plain/import-form bindings with `imported_module: null`. The current `source-api-classification-review@1` schema and loader require every reviewed import binding to provide non-empty string values for `binding.module`, `binding.name`, and `binding.target`. It therefore cannot faithfully represent those 35 rows as-is. This is a review-schema limitation in addition to the missing per-candidate decisions.

## Recommended active changes

1. Extend the general source API review at `tests/fixtures/api-source-classification-review.json` to review the 205 listed import-binding candidates. Record each candidate's actual source binding, source location, evidence basis, concrete evidence, reason, and recommendation. Use `supported` only where the pinned source/docs establish the exact FastAPI path; use `private/internal` where implementation-only evidence meets the policy; leave any genuinely unresolved entry `uncertain` with its own reason/evidence.
2. Update the source-review selection and summary in `metadata.yaml` to cover that exact candidate set without colliding with the callable, public-candidate, or Starlette-specific import-binding overlays. Extend the source-review schema/loader to represent the 35 `imported_module: null` import forms accurately, or add an equivalent explicit import-statement representation before recording those rows.
3. Recompute the source-review candidate counts, ID digest, artifact hash, and atlas references; regenerate `tests/fixtures/compatibility-atlas.json` with the repository's compatibility-atlas update workflow. Acceptance should require every remaining `uncertain` candidate to retain a non-empty source reference and a candidate-specific review reason/evidence.

This audit changes no active metadata, atlas, or fixture input.
