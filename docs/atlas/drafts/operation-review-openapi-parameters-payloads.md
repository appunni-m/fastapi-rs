# Operation review draft: OpenAPI parameters and payload models

Status: source-backed review draft; no metadata, recipe, fixture, atlas, or target-code changes made.

## Scope and pinned identities

This review covers the 59 candidate IDs in `tests/fixtures/compatibility-atlas.json` under `fastapi.openapi.models`: `Header`, `Parameter`, `ParameterBase`, `ParameterInType`, `RequestBody`, `Response`, `MediaType`, `Encoding`, `Example`, `Link`, and `XML`, plus the listed fields/members on those types.

Pinned identities from `metadata.yaml` and the checked-out source identities:

- FastAPI 0.141.1, source commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Python source contract requires `>=3.10`; oracle profile is CPython 3.12.13.
- Pydantic 2.13.4 (`pydantic-core` 2.46.4).
- Starlette-RS commit `37c6615e5b54d820d70b9d910d2e06fda8ae4cfe` is the sibling target contract. These OpenAPI model declarations are FastAPI-owned; no Starlette-RS inheritance is asserted for them.

The pinned FastAPI source says `fastapi.openapi.models` contains “OpenAPI Pydantic models used to generate and validate the generated OpenAPI” (`docs/en/docs/reference/openapi/models.md:1-5`). The declaration facts below come from `fastapi/openapi/models.py` at the pinned commit. Pydantic-dependent behavior is not inferred from annotations alone.

## Status applied to all 59 rows

The atlas currently classifies all 59 IDs as `classification: supported`; 58 have `visibility: public`, and `fastapi.openapi.models.Example.__pydantic_config__` has `visibility: public_protocol`. This is source evidence: the module is documented and its Pydantic fields/config member are documented. It is an upstream API classification only. The active `metadata.yaml` atlas policy says “source candidates require operation review”; there are no exact target contract overlay entries for these 59 IDs, no FastAPI-RS binding/feature mapping for them, and no `fixture_refs` or `observation_selectors` attached to them. Their exact FastAPI-RS status is therefore **pending operation review / no target support claim**. Route-level OpenAPI observations listed below are partial projections and do not establish direct type identity, importability, constructor signatures, validation, alias handling, or serialization parity.

All selected candidate rows below carry the same atlas classification and target-manifest status. “Required” is source-level shorthand for a non-optional field annotation without a default on a `BaseModel` subclass; it still needs identity-checked parity before it can be claimed as target behavior. `Example` is a `TypedDict`, not a `BaseModel` subclass.

## Candidate register

All source references in this table are relative to the pinned FastAPI repository, in `fastapi/openapi/models.py`.

| Candidate ID | Pinned source declaration |
|---|---|
| `fastapi.openapi.models.XML` | `:104` — `class XML(BaseModelWithConfig)` |
| `fastapi.openapi.models.XML.name` | `:105` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.XML.namespace` | `:106` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.XML.prefix` | `:107` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.XML.attribute` | `:108` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.XML.wrapped` | `:109` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Example` | `:212` — `class Example(TypedDict, total=False)`; all listed keys are optional |
| `fastapi.openapi.models.Example.summary` | `:213` — `str \| None`; optional key and nullable value |
| `fastapi.openapi.models.Example.description` | `:214` — `str \| None`; optional key and nullable value |
| `fastapi.openapi.models.Example.value` | `:215` — `Any \| None`; optional key and nullable value |
| `fastapi.openapi.models.Example.externalValue` | `:216` — `AnyUrl \| None`; optional key and nullable value |
| `fastapi.openapi.models.Example.__pydantic_config__` | `:218` — `{"extra": "allow"}`; TypedDict Pydantic config, not a data key |
| `fastapi.openapi.models.ParameterInType` | `:221` — `class ParameterInType(Enum)` |
| `fastapi.openapi.models.ParameterInType.query` | `:222` — enum member value `"query"` |
| `fastapi.openapi.models.ParameterInType.header` | `:223` — enum member value `"header"` |
| `fastapi.openapi.models.ParameterInType.path` | `:224` — enum member value `"path"` |
| `fastapi.openapi.models.ParameterInType.cookie` | `:225` — enum member value `"cookie"` |
| `fastapi.openapi.models.Encoding` | `:228` — `class Encoding(BaseModelWithConfig)` |
| `fastapi.openapi.models.Encoding.contentType` | `:229` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Encoding.headers` | `:230` — `dict[str, Union["Header", Reference]] \| None = None`; optional, default `None`; forward reference to `Header` |
| `fastapi.openapi.models.Encoding.style` | `:231` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Encoding.explode` | `:232` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Encoding.allowReserved` | `:233` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.MediaType` | `:236` — `class MediaType(BaseModelWithConfig)` |
| `fastapi.openapi.models.MediaType.schema_` | `:237` — `Schema \| Reference \| None`, default `None`, alias `"schema"` |
| `fastapi.openapi.models.MediaType.example` | `:238` — `Any \| None = None`; optional, default `None` |
| `fastapi.openapi.models.MediaType.examples` | `:239` — `dict[str, Example \| Reference] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.MediaType.encoding` | `:240` — `dict[str, Encoding] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase` | `:243` — `class ParameterBase(BaseModelWithConfig)` |
| `fastapi.openapi.models.ParameterBase.description` | `:244` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.required` | `:245` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.deprecated` | `:246` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.style` | `:248` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.explode` | `:249` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.allowReserved` | `:250` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.schema_` | `:251` — `Schema \| Reference \| None`, default `None`, alias `"schema"` |
| `fastapi.openapi.models.ParameterBase.example` | `:252` — `Any \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.examples` | `:253` — `dict[str, Example \| Reference] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.ParameterBase.content` | `:255` — `dict[str, MediaType] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Parameter` | `:258` — `class Parameter(ParameterBase)` |
| `fastapi.openapi.models.Parameter.name` | `:259` — `str`; no default, required field |
| `fastapi.openapi.models.Parameter.in_` | `:260` — `ParameterInType = Field(alias="in")`; no default, required field; Python name `in_`, serialized/input alias `in` |
| `fastapi.openapi.models.Header` | `:263-264` — `class Header(ParameterBase): pass`; adds no declared fields and inherits `ParameterBase` fields |
| `fastapi.openapi.models.RequestBody` | `:267` — `class RequestBody(BaseModelWithConfig)` |
| `fastapi.openapi.models.RequestBody.description` | `:268` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.RequestBody.content` | `:269` — `dict[str, MediaType]`; no default, required field |
| `fastapi.openapi.models.RequestBody.required` | `:270` — `bool \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Link` | `:273` — `class Link(BaseModelWithConfig)` |
| `fastapi.openapi.models.Link.operationRef` | `:274` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Link.operationId` | `:275` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Link.parameters` | `:276` — `dict[str, Any \| str] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Link.requestBody` | `:277` — `Any \| str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Link.description` | `:278` — `str \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Link.server` | `:279` — `Server \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Response` | `:282` — `class Response(BaseModelWithConfig)` |
| `fastapi.openapi.models.Response.description` | `:283` — `str`; no default, required field |
| `fastapi.openapi.models.Response.headers` | `:284` — `dict[str, Header \| Reference] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Response.content` | `:285` — `dict[str, MediaType] \| None = None`; optional, default `None` |
| `fastapi.openapi.models.Response.links` | `:286` — `dict[str, Link \| Reference] \| None = None`; optional, default `None` |

There are no source deprecation decorators on these 59 declarations. The neighboring `Schema.example` field is separately marked deprecated in source (`models.py:198-204`) but is outside this candidate group. Aliases relevant here are `MediaType.schema_` → `schema`, `ParameterBase.schema_` → `schema`, and `Parameter.in_` → `in`. `Encoding.model_rebuild()` at `models.py:435` resolves its forward reference. `BaseModelWithConfig` sets `model_config = {"extra": "allow"}` at `models.py:57-58`; `ParameterBase`, its `Parameter` and `Header` children, `Encoding`, `MediaType`, `RequestBody`, `Link`, `Response`, and `XML` inherit that configuration. The source declares no explicit `__init__` for these models; any constructor signature is Pydantic-generated under the pinned Pydantic version. The source uses Python 3.10 union syntax; `Example` uses `typing_extensions.TypedDict`.

## FastAPI source usage and call chain

These are upstream FastAPI facts, not target findings:

1. `FastAPI.openapi()` calls `fastapi.openapi.utils.get_openapi(...)` when the cached schema is absent or routes change (`fastapi/applications.py:1070-1103`). The `/openapi.json` route calls `self.openapi()` and returns the resulting document (`applications.py:1105-1118`).
2. `get_openapi_path()` gathers route parameters, then `_get_openapi_operation_parameters()` projects each route field to a dictionary with `name`, `in`, `required`, and `schema`, optionally adding `description`, `examples`/`example`, and `deprecated` (`fastapi/openapi/utils.py:159-228`). `ParamTypes` supplies path/query/header/cookie values. The `Parameter` and `ParameterInType` classes describe and validate the resulting OpenAPI structure; normal route processing builds dictionaries rather than exposing these model instances.
3. `get_openapi_operation_request_body()` projects a request `Body` field to `required` and a `content` map containing media type, schema, and optional examples/example (`openapi/utils.py:231-263`). `get_openapi_path()` attaches that value to `requestBody`; it builds operation response dictionaries, applies additional-response dictionaries, and may merge `route.openapi_extra` (`openapi/utils.py:311-525`).
4. `OpenAPI`, `Operation`, `Components`, `Schema`, and the candidate models are connected by source annotations: `Operation.parameters`/`requestBody`/`responses` at `models.py:289-300`; response and reusable-component links at `models.py:399-410`; `Schema.xml` at `models.py:193-204`. `Encoding.model_rebuild()` is explicit at `models.py:435`.
5. At the end of `get_openapi()`, FastAPI validates the assembled dictionary with `OpenAPI(**output)`, then serializes using `jsonable_encoder(..., by_alias=True, exclude_none=True)` (`openapi/utils.py:679`). This is the principal FastAPI call chain that touches nested `Parameter`, `RequestBody`, `Response`, `MediaType`, `Example`, `Link`, `Encoding`, and `XML` schema definitions. It does not establish standalone import or constructor parity for each candidate.
6. `Example` is also imported as a type by `fastapi/params.py:8` and `fastapi/param_functions.py:8` for `openapi_examples` annotations; it is encoded into OpenAPI dictionaries by the two operation projection helpers above. `Header` as an OpenAPI model is a nested field type in `Encoding.headers`, `Response.headers`, and reusable `Components.headers`; this is distinct from the user-facing `fastapi.Header` parameter factory.

## Existing recipe observations and coverage gaps

These are active input recipes and selectors already present in the worktree. They are **partial route/document observations**, not evidence that the standalone model candidates are supported by FastAPI-RS. None of these recipes is mapped to the 59 candidate IDs in the current metadata overlay.

| Recipe and case ID | Current selectors | Candidate relevance and limit |
|---|---|---|
| `tests/fixtures/input-recipes/parity/openapi-parameter-examples-source-review.yaml` — `fastapi.openapi.examples-parameter-locations.openapi` | `/paths/~1probe~1body/post/requestBody`; `/paths/~1probe~1path~1{sample_id}/get/parameters`; `/paths/~1probe~1query/get/parameters`; `/paths/~1probe~1header/get/parameters`; `/paths/~1probe~1cookie/get/parameters`; `/components/schemas/ParameterExampleRecord` | Partial generated projections for `Parameter`, `ParameterBase`, `ParameterInType`, `Header` parameter location, and `Example` data. Does not instantiate/import the model classes, exercise all fields, or establish constructor/validation/dump behavior. |
| `tests/fixtures/input-recipes/parity/request-body-media-type-upstream-v3.yaml` — `fastapi.request-body-media-type.upstream.openapi-schema` | whole OpenAPI document (`''`) | Partial generated request-body/media-type document observation for the recipe's body setup; not direct `RequestBody` or `MediaType` model parity. |
| Same recipe — `fastapi.request-body-media-type.source-derived.mixed-media-json-fallback` | `/paths/~1mixed/post/requestBody/content/application~1json` | Partial request-body content projection. No direct `MediaType` construction/validation or `Encoding` observation. |
| `tests/fixtures/input-recipes/parity/additional-responses.yaml` — `fastapi.docs.additional-responses.openapi` | `/paths/~1inventory~1{sku}/get/responses/200/content/application~1vnd.fastapi-rs.inventory+json/schema/$ref`; `/paths/~1inventory~1{sku}/get/responses/404/description`; `/paths/~1inventory~1{sku}/get/responses/404/content/application~1vnd.fastapi-rs.inventory+json/schema/$ref`; selected component schema properties | Partial generated `Response` description/content projection for an additional response. Does not cover model identity, response headers, or links. |
| `tests/fixtures/input-recipes/parity/additional-response-model-openapi.yaml` — `fastapi.openapi.additional-response-model` | `/paths/~1tea/get/responses/418`; `/components/schemas/TeaError` | Additional-response dictionary/schema projection only; no direct `Response` model behavior. |
| `tests/fixtures/input-recipes/parity/openapi-operations.yaml` — `fastapi.openapi.openapi-query-parameter-extension.openapi` | `/paths/~1query-extension/get/parameters` | Route-extension parameter projection only; no `Parameter` class identity or standalone validation. |

Coverage gaps for all 59 IDs: there is no recipe with an isolated identity-checked import/signature/construction/validation/dump probe for these exact classes, fields, or enum members. The current selectors do not establish the full Pydantic model contract, nested extra-field policy, explicit alias input behavior, omitted versus explicit `None`, `model_fields` requiredness, JSON Schema output, error type/location, or by-alias serialization for every field. There is also no selector for `MediaType.encoding`, `Encoding` members, `Response.headers`, `Response.links`, `Link` members, or `XML` members. Existing examples only show a subset of generated operation dictionaries.

## Unresolved behavior before any support claim

- Whether `fastapi.openapi.models` directly exposes the same object identities and import paths for all eleven types and all reviewed fields/members in an isolated target process.
- Exact Pydantic 2.13.4 constructor signatures and validation for required, optional, nullable, unknown, and aliased inputs; alias behavior for `in_`/`schema_`; extra values under `extra="allow"`; forward-reference behavior; and TypedDict extra/config semantics.
- Exact `model_dump`/`jsonable_encoder` output, omission of `None`, alias serialization, enum serialization, and error diagnostics for direct use of each model.
- Generated OpenAPI coverage for `encoding`, `links`, response `headers`, and schema `xml`, including the behavior when callers provide them through response metadata or `openapi_extra`.
- Whether any unsupported cases should be explicitly excluded from the eventual support contract. Current route-level selectors do not answer this.

Do not promote atlas source classification to target support. Promotion requires reviewed `metadata.yaml` mappings and identity-checked, isolated parity evidence for the actual public model interfaces; generated OpenAPI dictionary parity alone is insufficient.


Historical sibling-pin audit: Starlette-RS dd2c1ac66982218f749f0510758f64f5e61c735b added an input-only WebSocket scope-mapping adapter/workflow and updated parity metadata/manifest; it changed no production runtime implementation or dependency declaration. That input remains in the selected 37c6615 contract. The latest Starlette-RS revision 37c6615e5b54d820d70b9d910d2e06fda8ae4cfe changes only benchmark and compatibility-inventory documentation. It does not change runtime source, dependency declarations, API catalog/review, manifest, or parity inputs; the selected sibling contract and the behavior reviewed here are unchanged. This is outside the reviewed OpenAPI model group. Generic WebSocket scope behavior remains sibling-owned; no FastAPI-RS support or parity is inferred.