# Draft: OpenAPI document graph source review

**Status:** source review draft only. This does not change candidate classifications, promote support, or claim parity.

## Identity and evidence boundary

The reviewed upstream is FastAPI 0.141.1 at commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` (`../fastapi`), with Python 3.12.13, Pydantic 2.13.4 / pydantic-core 2.46.4, Starlette 1.6.0, and Starlette-RS contract commit `37c6615e5b54d820d70b9d910d2e06fda8ae4cfe`. The pinned FastAPI checkout and the detached Starlette-RS checkout were identity-checked for this review.

The source declarations below are FastAPI facts. Pydantic field construction, validation, generated model signatures, extra-field handling, and serialization belong to pinned Pydantic. This report does not treat either as FastAPI-RS evidence.

All 66 IDs listed below are `supported` in `tests/fixtures/compatibility-atlas.json` only in the atlas source-classification sense: the OpenAPI module is documented and its fields are documented model fields. The candidate classification is not a target-support decision.

## FastAPI call chain and ownership

- `fastapi/openapi/models.py:57-59` defines `BaseModelWithConfig(BaseModel)` with `model_config = {"extra": "allow"}`. All reviewed model classes except `Reference` inherit it. `Reference` at line 95 subclasses bare `BaseModel`.
- `fastapi/openapi/utils.py:585-601` declares `get_openapi(...)`. It builds the `info` and root dictionaries at lines 602-618, collects model definitions and traverses routes at lines 620-667, then conditionally adds `components`, `webhooks`, `tags`, and `externalDocs` at lines 668-678.
- `fastapi/openapi/utils.py:679` validates/serializes the assembled root by calling `OpenAPI(**output)` and `jsonable_encoder(..., by_alias=True, exclude_none=True)`. That is where the nested model graph is applied in this path; `get_openapi_path` returns dictionaries and does not directly instantiate `Operation` or `PathItem`.
- `fastapi/openapi/utils.py:287-308` builds operation metadata (`tags`, `summary`, optional `description`, `operationId`, and optional `deprecated`). `get_openapi_path` begins at line 311; it builds each operation, including parameters, request body, callbacks, responses, and security, and places it under the uppercase route methods converted by route processing. Its method loop is at lines 343-376; request body at 377-385; callbacks at 386-402; responses at 403-503 and later response handling.
- `fastapi/openapi/utils.py:628-647` adds route operations, schemas, and security schemes to paths/components. Lines 648-667 do the corresponding webhook traversal. The normal generator populates `components.schemas` and `components.securitySchemes`; callbacks are attached to an operation, not `components.callbacks`.
- `fastapi/applications.py:1070-1103` caches `get_openapi(...)` output and passes app title/version, routes, webhooks, tags, servers, and external docs. Lines 1105-1120 install the OpenAPI HTTP route; its handler may prepend a root-path server before returning `JSONResponse`.

Thus, the model graph describes the generated document, but a selector on generated JSON does not by itself establish direct model imports, constructor signatures, field metadata, validation failures, or standalone serialization behavior.

## Current target-manifest status

`tests/fixtures/manifest.yaml` records every listed candidate with:

- `operation_scope.status: scope-review-pending`;
- `behavior_contract_state: documentation-fixture-design-linked; operation-level review pending`;
- `target_binding.status: full-contract-not-established` and `rust_binding: null`;
- an empty `input_workflow_refs` and empty `identity_workflow_refs`.

The manifest links each candidate to documentation fixture `fastapi.docs.reference-openapi-models`, from `docs/en/docs/reference/openapi/models.md`, with mapping status `candidate` and design selectors `python.import_path`, `python.signature`, `python.attribute_value`, and `openapi.document`. This is a documentation-fixture design link, not an active input recipe or a parity result. Class records have `source_signature_state: not-recorded` and reflected runtime signatures; field records are non-callable surfaces. No model constructor/identity workflow is linked.

The manifest foundation remains `foundation-incomplete`; it reports `partial-first-request-response-slice` and `full-parity-pending`. None of the recipe links below are represented as completed comparisons here. They are input-only observations with selectors and no expected values.

## Recipe evidence index

The following are related active input recipes. They show portions of the emitted document graph, not full model contracts; their selectors are not expected outputs.

| Key | Recipe/case and selectors |
|---|---|
| `DOC` | Manifest documentation design for every candidate: `fastapi.docs.reference-openapi-models`; selectors `python.import_path`, `python.signature`, `python.attribute_value`, `openapi.document`; mapping status `candidate`, not an input workflow. |
| `ROOT` | `atlas-openapi-callback-interface-review.yaml` / `fastapi.atlas-openapi-tutorial.callback-documentation`, action `callback-openapi-document`: OpenAPI selector with JSON pointer `""` (whole document). This is an input-only callback example, not direct model construction. |
| `OPS` | `openapi-operations.yaml`: `fastapi.openapi.additional-response-extra.openapi-schema` selects `/paths/~1items~1{item_id}/get/responses`; `fastapi.openapi.additional-responses-custom-model-in-callback.openapi-schema` selects `/paths/~1callback-registration/post/callbacks` and `/components/schemas/CallbackFailure`; `fastapi.openapi.openapi-query-parameter-extension.openapi` selects `/paths/~1query-extension/get/parameters`; operation-ID case `fastapi.openapi.generate-unique-id-function.top-level-generate-unique-id` selects `/paths/~1ids~1top/post/operationId`. |
| `OPMETA` | Separate input recipes `path-operation-post-tags-isolated.yaml`, `path-operation-post-summary-isolated.yaml`, `path-operation-post-operation-id-isolated.yaml`, and `path-operation-post-deprecated-isolated.yaml` select respectively `/paths/~1items~1/post/tags`, `/paths/~1items~1/post/summary`, `/paths/~1items/post/operationId`, and `/paths/~1items-deprecated/post/deprecated`. `docs-openapi-schema.yaml` case `fastapi.docs.documentation-wave.openapi-schema.path-operation-configuration` selects `/paths/~1releases/post/summary`, `/paths/~1releases/post/tags`, and `/paths/~1releases/post/responses/201/description`. |
| `METHODS` | `path-operation-other-verbs-response-descriptions.yaml` / `fastapi.path-operation.other-verbs-response-descriptions` selects response-description leaves under GET, PUT, DELETE, PATCH, HEAD, OPTIONS, TRACE, and POST operations. These are generated path/method dictionaries, not direct `PathItem` instances. |
| `PARAMS` | `openapi-parameter-examples-source-review.yaml` selects request-body and path/query/header/cookie parameter subtrees under `/paths`; `atlas-pending-openapi-source-wave.yaml` case `fastapi.pending.openapi-source-wave.repeated-dependency-openapi` selects `/paths/~1shared-header/get/parameters`. |
| `RESP` | `openapi-operations.yaml` response cases above; `path-operation-post-response-description-isolated.yaml` selects `/paths/~1items/post/responses/200/description` and two sibling response descriptions; `path-operation-other-verbs-response-descriptions.yaml` selects response leaves for the listed methods. |
| `SEC` | `security-wave.yaml` / `fastapi.security-wave.http-basic-tutorials.openapi` selects `/components/securitySchemes/HTTPBasic` and two operation `/security` values; its `fastapi.security-wave.oauth2-scope-propagation.nested-same-scheme-openapi` case selects `/components/securitySchemes/ScopedOAuth2` and `/paths/~1security~1scoped-admin/get/security`. |
| `SCHEMA` | `docs-openapi-schema.yaml` cases select `/components/schemas/TimeWindow`, `/components/schemas/PersonPublic`, and other schema trees; `openapi-operations.yaml` callback case selects `/components/schemas/CallbackFailure`. These cover emitted schema contents, not every `Components` map. |
| `SERVERS` | `openapi-docs.yaml` / `fastapi.openapi.openapi-servers.openapi-schema` selects `/servers` and `/paths`; its cache/root-path cases also select `/servers`. `behind-proxy-tutorial003-upstream.yaml` and `behind-proxy-tutorial004-upstream.yaml` select `/servers`; `root-path-proxy.yaml` selects `/servers/0/url`. `openapi-configured-servers-reference-review.yaml` selects `/servers` and separately observes caller-owned configuration. |
| `INFO` | `metadata-summary-description-upstream.yaml` / `fastapi.metadata.summary-description.openapi-info` selects `/info/summary`, `/info/description`, `/info/termsOfService`, `/info/contact`, `/info/license`, and `/externalDocs`. |
| `WEBHOOKS` | `openapi-docs.yaml` / `fastapi.openapi.tutorial-openapi-webhooks-tutorial001.openapi-schema` selects `/webhooks`; `openapi-webhook-route-separation-source-review.yaml` / `fastapi.openapi.webhooks.event-identifier-is-not-route` selects `/paths` and `/webhooks/catalog-rebuilt`. |
| `REFS` | `dependency-tutorial-review-upstream.yaml` selects `$ref` leaves beneath generated operation response schemas; `handling-errors.yaml` selects `/paths/.../responses/422/content/application~1json/schema/$ref`. These exercise references in emitted schemas, not `Reference` constructor/alias input behavior. |

The input recipes in this index remain independent stimuli. No live FastAPI-vs-target parity is claimed by this review.

## Candidate inventory

Notation: “optional; default `None`” means the source annotation includes `| None` and an explicit `= None`. “Required” means the source declaration has no default. These are declaration facts; Pydantic 2.13.4 owns resulting model-field metadata and validation. Every row has the candidate-only `DOC` link above. Recipe keys identify emitted-document observations where present; otherwise the row states the coverage gap.

### `Components` — `fastapi/openapi/models.py:399-410`

Class declaration: `class Components(BaseModelWithConfig)` at line 399. The class inherits `extra="allow"` from `BaseModelWithConfig`. All fields below are optional and default to `None`.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.Components` | class at `fastapi/openapi/models.py:399`; no explicit source `__init__` signature | `DOC`; `SCHEMA` and `SEC` see only selected emitted component content. No direct model construct/identity/signature case. |
| `fastapi.openapi.models.Components.callbacks` | `fastapi/openapi/models.py:409` — `dict[str, dict[str, PathItem] \| Reference \| Any] \| None = None` | `OPS` observes operation callbacks; no `/components/callbacks` output or direct component-map case. |
| `fastapi.openapi.models.Components.examples` | `fastapi/openapi/models.py:403` — `dict[str, Example \| Reference] \| None = None` | Gap: no `/components/examples` observation or direct model case. Request/parameter inline examples do not cover this map. |
| `fastapi.openapi.models.Components.headers` | `fastapi/openapi/models.py:405` — `dict[str, Header \| Reference] \| None = None` | Gap: no `/components/headers` observation or direct model case. |
| `fastapi.openapi.models.Components.links` | `fastapi/openapi/models.py:407` — `dict[str, Link \| Reference] \| None = None` | Gap: no `/components/links` observation or direct model case. |
| `fastapi.openapi.models.Components.parameters` | `fastapi/openapi/models.py:402` — `dict[str, Parameter \| Reference] \| None = None` | `PARAMS` observes operation parameter values; gap for `/components/parameters` and direct component-map behavior. |
| `fastapi.openapi.models.Components.pathItems` | `fastapi/openapi/models.py:410` — `dict[str, PathItem \| Reference] \| None = None` | Gap: no `/components/pathItems` observation or direct model case. |
| `fastapi.openapi.models.Components.requestBodies` | `fastapi/openapi/models.py:404` — `dict[str, RequestBody \| Reference] \| None = None` | `PARAMS` observes inline operation request bodies; gap for `/components/requestBodies` and direct component-map behavior. |
| `fastapi.openapi.models.Components.responses` | `fastapi/openapi/models.py:401` — `dict[str, Response \| Reference] \| None = None` | `RESP` observes inline operation responses; gap for `/components/responses` and direct component-map behavior. |
| `fastapi.openapi.models.Components.schemas` | `fastapi/openapi/models.py:400` — `dict[str, Schema \| Reference] \| None = None` | `SCHEMA` observes selected emitted schema maps/entries. It does not exercise all schema values or direct `Components` construction. |
| `fastapi.openapi.models.Components.securitySchemes` | `fastapi/openapi/models.py:406` — `dict[str, SecurityScheme \| Reference] \| None = None` | `SEC` observes selected emitted security-scheme entries; no direct `Components` or map-construction case. |

### `ExternalDocumentation` — `fastapi/openapi/models.py:112-114`

Class declaration: `class ExternalDocumentation(BaseModelWithConfig)` at line 112; extra fields are allowed by its base model.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.ExternalDocumentation` | class at `fastapi/openapi/models.py:112`; no explicit source `__init__` signature | `DOC`; `INFO` observes one top-level emitted external-doc object, not direct construction or validation. |
| `fastapi.openapi.models.ExternalDocumentation.description` | `fastapi/openapi/models.py:113` — `str \| None = None`; optional, default `None` | `INFO` selects `/externalDocs` as an object; it does not isolate description validation or null/omission behavior. |
| `fastapi.openapi.models.ExternalDocumentation.url` | `fastapi/openapi/models.py:114` — `AnyUrl`; required, no default | `INFO` selects `/externalDocs` as an object. Pydantic URL validation/canonicalization and error behavior remain unreviewed. |

### `OpenAPI` — `fastapi/openapi/models.py:419-430`

Class declaration: `class OpenAPI(BaseModelWithConfig)` at line 419; extra fields are allowed by its base model. `get_openapi` constructs this model at `utils.py:679`.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.OpenAPI` | class at `fastapi/openapi/models.py:419`; no explicit source `__init__` signature | `DOC`; `ROOT` observes a whole generated document; this is not direct class construction or identity parity. |
| `fastapi.openapi.models.OpenAPI.components` | `fastapi/openapi/models.py:427` — `Components \| None = None`; optional, default `None` | `SCHEMA`, `SEC`; no coverage of the full component graph or absent/null distinction. |
| `fastapi.openapi.models.OpenAPI.externalDocs` | `fastapi/openapi/models.py:430` — `ExternalDocumentation \| None = None`; optional, default `None` | `INFO` selects `/externalDocs`; generated assignment occurs only for truthy `external_docs` at `utils.py:677-678`. |
| `fastapi.openapi.models.OpenAPI.info` | `fastapi/openapi/models.py:421` — `Info`; required, no default | `INFO` selects fields below `/info`; `ROOT` observes it as part of a whole document. Nested `Info` validation is outside this candidate group. |
| `fastapi.openapi.models.OpenAPI.jsonSchemaDialect` | `fastapi/openapi/models.py:422` — `str \| None = None`; optional, default `None` | Gap: generator does not assign this field; no explicit `/jsonSchemaDialect` selector or configured-value case. |
| `fastapi.openapi.models.OpenAPI.openapi` | `fastapi/openapi/models.py:420` — `str`; required, no default | `ROOT` includes the root field in a whole-document selector. No explicit root-field pointer or direct model case. |
| `fastapi.openapi.models.OpenAPI.paths` | `fastapi/openapi/models.py:425` — `dict[str, PathItem \| Any] \| None = None`; optional, default `None` | `ROOT`, `OPS`, `METHODS`, `PARAMS`, `RESP`, and `WEBHOOKS` observe selected path trees. Full route/method/extra-value graph is not established. |
| `fastapi.openapi.models.OpenAPI.security` | `fastapi/openapi/models.py:428` — `list[dict[str, list[str]]] \| None = None`; optional, default `None` | Gap: `SEC` observes operation-level `/paths/.../security`, not root `/security`; `get_openapi` does not assign a root security field. |
| `fastapi.openapi.models.OpenAPI.servers` | `fastapi/openapi/models.py:423` — `list[Server] \| None = None`; optional, default `None` | `SERVERS` observes selected server lists. Variable-bearing server values and direct model behavior remain gaps. |
| `fastapi.openapi.models.OpenAPI.tags` | `fastapi/openapi/models.py:429` — `list[Tag] \| None = None`; optional, default `None` | Gap: current tag recipes observe operation `tags: list[str]`, not root `/tags` `Tag` objects. `get_openapi` copies app tags only when truthy at lines 675-676. |
| `fastapi.openapi.models.OpenAPI.webhooks` | `fastapi/openapi/models.py:426` — `dict[str, PathItem \| Reference] \| None = None`; optional, default `None` | `WEBHOOKS` observes selected webhook trees; no direct model construction or complete webhook graph case. |

### `Operation` — `fastapi/openapi/models.py:289-302`

Class declaration: `class Operation(BaseModelWithConfig)` at line 289; extra fields are allowed by its base model. Every field below is optional and defaults to `None`.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.Operation` | class at `fastapi/openapi/models.py:289`; no explicit source `__init__` signature | `DOC`; `ROOT`/`OPS` observe generated operations only. |
| `fastapi.openapi.models.Operation.callbacks` | `fastapi/openapi/models.py:299` — `dict[str, dict[str, "PathItem"] \| Reference] \| None = None` | `OPS` observes `/paths/.../callbacks`; `atlas-pending-callbacks-source-wave.yaml` observes a callback field. No direct callback model/Reference behavior. |
| `fastapi.openapi.models.Operation.deprecated` | `fastapi/openapi/models.py:300` — `bool \| None = None` | `OPMETA` selects `/paths/~1items-deprecated/post/deprecated`; no direct field validation case. |
| `fastapi.openapi.models.Operation.description` | `fastapi/openapi/models.py:292` — `str \| None = None` | No dedicated description pointer in the listed recipes. `get_openapi_operation_metadata` emits a truthy route description; current recipe link is only `ROOT`/other whole-document scope. |
| `fastapi.openapi.models.Operation.externalDocs` | `fastapi/openapi/models.py:293` — `ExternalDocumentation \| None = None` | Gap: no operation-level `/paths/.../externalDocs` selector or source assignment from route metadata. Top-level `INFO` does not cover this field. |
| `fastapi.openapi.models.Operation.operationId` | `fastapi/openapi/models.py:294` — `str \| None = None` | `OPMETA` and `OPS` select operationId leaves for explicit and generated IDs. Warning/error and direct model semantics remain separate. |
| `fastapi.openapi.models.Operation.parameters` | `fastapi/openapi/models.py:295` — `list[Parameter \| Reference] \| None = None` | `PARAMS` observes selected operation parameter lists; source aggregation/deduplication is not a complete model contract. |
| `fastapi.openapi.models.Operation.requestBody` | `fastapi/openapi/models.py:296` — `RequestBody \| Reference \| None = None` | `PARAMS` and `atlas-pending-openapi-source-wave.yaml` observe selected inline request-body trees; no direct `RequestBody`/`Reference` case. |
| `fastapi.openapi.models.Operation.responses` | `fastapi/openapi/models.py:298` — `dict[str, Response \| Any] \| None = None` | `RESP` observes selected response maps/descriptions. The `Any` arm and arbitrary extension handling are not exhaustively exercised. |
| `fastapi.openapi.models.Operation.security` | `fastapi/openapi/models.py:301` — `list[dict[str, list[str]]] \| None = None` | `SEC` observes selected operation security lists and schemes. No direct `Operation` construction or empty/null variation. |
| `fastapi.openapi.models.Operation.servers` | `fastapi/openapi/models.py:302` — `list[Server] \| None = None` | Gap: no operation-level `/paths/.../servers` selector or source population path. Top-level `SERVERS` does not cover this field. |
| `fastapi.openapi.models.Operation.summary` | `fastapi/openapi/models.py:291` — `str \| None = None` | `OPMETA` selects a summary leaf; `docs-openapi-schema.yaml` also selects `/paths/~1releases/post/summary`. |
| `fastapi.openapi.models.Operation.tags` | `fastapi/openapi/models.py:290` — `list[str] \| None = None` | `OPMETA` selects operation tags. This is distinct from `OpenAPI.tags` and `Tag` model objects. |

### `PathItem` — `fastapi/openapi/models.py:305-318`

Class declaration: `class PathItem(BaseModelWithConfig)` at line 305; extra fields are allowed by its base model. All fields are optional with default `None`. Each HTTP method field is `Operation | None`.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.PathItem` | class at `fastapi/openapi/models.py:305`; no explicit source `__init__` signature | `DOC`; `ROOT`, `OPS`, and `METHODS` observe generated path items, not direct model construction. |
| `fastapi.openapi.models.PathItem.delete` | `fastapi/openapi/models.py:312` — `Operation \| None = None` | `METHODS` selects a DELETE operation response subtree; no standalone field construction. |
| `fastapi.openapi.models.PathItem.description` | `fastapi/openapi/models.py:308` — `str \| None = None` | Gap: no path-item-level `/paths/.../description` selector or source assignment. Operation descriptions are separate. |
| `fastapi.openapi.models.PathItem.get` | `fastapi/openapi/models.py:309` — `Operation \| None = None` | `METHODS` and `OPS` observe generated GET operation subtrees; no direct field constructor case. |
| `fastapi.openapi.models.PathItem.head` | `fastapi/openapi/models.py:314` — `Operation \| None = None` | `METHODS` selects a HEAD operation response subtree; no standalone field case. |
| `fastapi.openapi.models.PathItem.options` | `fastapi/openapi/models.py:313` — `Operation \| None = None` | `METHODS` selects an OPTIONS operation response subtree; no standalone field case. |
| `fastapi.openapi.models.PathItem.parameters` | `fastapi/openapi/models.py:318` — `list[Parameter \| Reference] \| None = None` | Gap: recipes observe operation `/parameters`; FastAPI generator places parameters on each operation and does not assign path-item-level parameters. |
| `fastapi.openapi.models.PathItem.patch` | `fastapi/openapi/models.py:315` — `Operation \| None = None` | `METHODS` selects a PATCH operation response subtree; no standalone field case. |
| `fastapi.openapi.models.PathItem.post` | `fastapi/openapi/models.py:311` — `Operation \| None = None` | `OPS`, `OPMETA`, and `METHODS` observe generated POST operation subtrees; no direct field constructor case. |
| `fastapi.openapi.models.PathItem.put` | `fastapi/openapi/models.py:310` — `Operation \| None = None` | `METHODS` selects a PUT operation response subtree; no standalone field case. |
| `fastapi.openapi.models.PathItem.ref` | `fastapi/openapi/models.py:306` — `str \| None = Field(default=None, alias="$ref")`; Python name `ref`, wire alias `$ref`; optional, default `None` | `REFS` observes schema `$ref` leaves, not path-item `$ref` input/serialization. No path-item reference case. |
| `fastapi.openapi.models.PathItem.servers` | `fastapi/openapi/models.py:317` — `list[Server] \| None = None` | Gap: no `/paths/.../servers` observation or FastAPI source population path. |
| `fastapi.openapi.models.PathItem.summary` | `fastapi/openapi/models.py:307` — `str \| None = None` | Gap: no path-item-level `/paths/.../summary` selector or source assignment. Operation summary is separate. |
| `fastapi.openapi.models.PathItem.trace` | `fastapi/openapi/models.py:316` — `Operation \| None = None` | `METHODS` selects a TRACE operation response subtree; no standalone field constructor case. |

### `Reference` — `fastapi/openapi/models.py:95-96`

Class declaration: `class Reference(BaseModel)` at line 95. Unlike other reviewed classes it does not inherit FastAPI's `extra="allow"` configuration.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.Reference` | class at `fastapi/openapi/models.py:95`; no explicit source `__init__` signature | `DOC`; `REFS` observes generated `$ref` document leaves, not direct import identity, construction, validation, or extra-field policy. |
| `fastapi.openapi.models.Reference.ref` | `fastapi/openapi/models.py:96` — `str = Field(alias="$ref")`; Python field `ref`, alias `$ref`; required, no default | `REFS` observes serialized `$ref` values in schema trees. Input by Python name versus alias and error details are unverified. |

### `Server` — `fastapi/openapi/models.py:89-92`

Class declaration: `class Server(BaseModelWithConfig)` at line 89; extra fields are allowed by its base model.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.Server` | class at `fastapi/openapi/models.py:89`; no explicit source `__init__` signature | `DOC`; `SERVERS` observes configured top-level server objects; no direct constructor/identity case. |
| `fastapi.openapi.models.Server.description` | `fastapi/openapi/models.py:91` — `str \| None = None`; optional, default `None` | `SERVERS` selects `/servers` with a configured description; no direct null/omission or validation case. |
| `fastapi.openapi.models.Server.url` | `fastapi/openapi/models.py:90` — `AnyUrl \| str`; required, no default | `SERVERS` and root-path recipes select server values. Pydantic URL parsing/normalization versus the `str` union branch is unresolved. |
| `fastapi.openapi.models.Server.variables` | `fastapi/openapi/models.py:92` — `dict[str, ServerVariable] \| None = None`; optional, default `None` | Gap: no selected server has a `variables` map in the reviewed cases. |

### `ServerVariable` — `fastapi/openapi/models.py:83-86`

Class declaration: `class ServerVariable(BaseModelWithConfig)` at line 83; extra fields are allowed by its base model.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.ServerVariable` | class at `fastapi/openapi/models.py:83`; no explicit source `__init__` signature | `DOC`; no server-variable constructor, import-identity, or variable-map observation. |
| `fastapi.openapi.models.ServerVariable.default` | `fastapi/openapi/models.py:85` — `str`; required, no default | Gap: no server-variable instance in `SERVERS` inputs. |
| `fastapi.openapi.models.ServerVariable.description` | `fastapi/openapi/models.py:86` — `str \| None = None`; optional, default `None` | Gap: no server-variable instance or description selector. |
| `fastapi.openapi.models.ServerVariable.enum` | `fastapi/openapi/models.py:84` — `Annotated[list[str] \| None, Field(min_length=1)] = None`; optional, default `None`, non-null list has Pydantic `min_length=1` constraint | Gap: no variable enum case; validation boundary and error detail belong to Pydantic and are unverified here. |

### `Tag` — `fastapi/openapi/models.py:413-416`

Class declaration: `class Tag(BaseModelWithConfig)` at line 413; extra fields are allowed by its base model.

| Candidate ID | Exact source field | Related recipe observations / gap |
|---|---|---|
| `fastapi.openapi.models.Tag` | class at `fastapi/openapi/models.py:413`; no explicit source `__init__` signature | `DOC`; no direct `Tag` import/constructor/identity case or root tag-object selector. |
| `fastapi.openapi.models.Tag.description` | `fastapi/openapi/models.py:415` — `str \| None = None`; optional, default `None` | Gap: operation tag recipes use strings and do not exercise this field. |
| `fastapi.openapi.models.Tag.externalDocs` | `fastapi/openapi/models.py:416` — `ExternalDocumentation \| None = None`; optional, default `None` | Gap: no root `Tag.externalDocs` selector or input object. Top-level `INFO` covers a different `ExternalDocumentation` location. |
| `fastapi.openapi.models.Tag.name` | `fastapi/openapi/models.py:414` — `str`; required, no default | Gap: no root `/tags/<index>/name` selector. Operation tags are `list[str]`, not `Tag` instances. |

## Aliases, deprecations, and Python-facing constraints

- For these 66 candidates, the atlas has no alias or deprecation record for the candidate itself. The only source field aliases in this set are `PathItem.ref` (`$ref`) and `Reference.ref` (`$ref`), each recorded above. Neither alias establishes input-by-name behavior; pinned Pydantic controls that behavior.
- No candidate in this group is source-deprecated. The `Schema.example` deprecation elsewhere in `models.py` is outside this review group.
- The class names and fields are under the documented `fastapi.openapi.models` module declaration in `docs/en/docs/reference/openapi/models.md:1-5`; they are not root-level `fastapi` exports established by this evidence. Under the project facade rule, Python target files remain direct native re-exports and literal `__all__` only; Rust owns FastAPI behavior. The target manifest currently records no Rust binding for these candidates.

## Unresolved behavior before any support claim

1. Direct import-path identity, runtime signature compatibility, model-field metadata, constructor acceptance, required-field errors, alias input/output behavior, nested union behavior, and `model_dump`/JSON encoder differences for every listed class.
2. Pydantic 2.13.4 behavior for `AnyUrl | str`, `enum` minimum length, `Any` arms, extra fields (allowed for `BaseModelWithConfig`, different base for `Reference`), and omission versus explicit null after `exclude_none=True`.
3. The unused-but-publicly documented optional fields: root security/tags/schema dialect; operation-level external docs/servers; path-item `$ref`/summary/description/servers/parameters; component examples/headers/links/parameters/pathItems/requestBodies/responses/callbacks; and server variables. Current generator source does not populate most of these.
4. Full nested graph behavior across ordinary paths, webhooks, callbacks, references, security schemes, schema definitions, and caller-provided OpenAPI customizations. The listed inputs sample selected subtrees and do not exhaust variants or failure boundaries.
5. Identity-checked isolated source/target observations for candidate imports and any selected behavior, with expected outputs generated only by the isolated oracle/comparator workflow. Until then, the manifest's pending statuses remain authoritative.


Historical sibling-pin audit: Starlette-RS dd2c1ac66982218f749f0510758f64f5e61c735b added an input-only WebSocket scope-mapping adapter/workflow and updated parity metadata/manifest; it changed no production runtime implementation or dependency declaration. That input remains in the selected 37c6615 contract. The latest Starlette-RS revision 37c6615e5b54d820d70b9d910d2e06fda8ae4cfe changes only benchmark and compatibility-inventory documentation. It does not change runtime source, dependency declarations, API catalog/review, manifest, or parity inputs; the selected sibling contract and the behavior reviewed here are unchanged. This is outside the reviewed OpenAPI model group. Generic WebSocket scope behavior remains sibling-owned; no FastAPI-RS support or parity is inferred.