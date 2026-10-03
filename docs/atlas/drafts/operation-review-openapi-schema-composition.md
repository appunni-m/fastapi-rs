# OpenAPI schema-composition candidate review (draft)

Scope: the 67 FastAPI API candidates for `Discriminator`, `Schema`, `SchemaOrBool`, and `SchemaType`. This is a source-backed review draft; it changes no active contract, fixture, recipe, generated artifact, or implementation.

## Pinned identities and evidence boundary

- FastAPI 0.141.1 source: commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; source file `../fastapi/fastapi/openapi/models.py`. The atlas records SHA-256 `b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d` for that module.
- Pydantic: `2.13.4`; Pydantic Core: `2.46.4`. The repository pins these in `metadata.yaml` and the runtime lock. FastAPI source imports Pydantic `BaseModel`, `Field`, and `GetJsonSchemaHandler` in `models.py:7-12`.
- Python: project floor `>=3.10`; oracle profile CPython `3.12.13` (`metadata.yaml`). The reviewed declarations use PEP 604 unions and built-in generic types.
- Starlette oracle: `1.6.0`, source commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. Starlette-RS contract pin recorded for this review: `37c6615e5b54d820d70b9d910d2e06fda8ae4cfe`.

The definitions below are FastAPI/Pydantic source facts. Pydantic's runtime validation, accepted aliases, serialization, warnings, and error details are not inferred from annotations alone. Target statements are limited to the checked FastAPI-RS manifest and the visible Python facade; no parity execution was performed for this review.

## Candidate and target contract status

The source atlas contains **67** candidates in this group. Their atlas classification is `supported` because the inventory sees documented OpenAPI model declarations/fields (`docs/en/docs/reference/openapi/models.md:3-5`); project policy says inventory classification is not implementation evidence. The four names are absent from the reviewed overlays in `metadata.yaml`.

For **each of the 67 manifest entries**:

- `operation_scope.status`: `scope-review-pending`.
- `behavior_contract_state`: `documentation-fixture-design-linked; operation-level review pending`.
- `target_binding.implementation_owner`: `fastapi-rs`.
- `target_binding.status`: `full-contract-not-established`; `target_binding.rust_binding`: `null`.
- `identity_workflow_refs`: empty. Source signatures are not recorded in `source_signature_state`; class reflection being available is not target parity evidence.

All 67 have the documentation fixture design `fastapi.docs.reference-openapi-models` with `mapping_status: candidate` and selectors `python.import_path`, `python.signature`, `python.attribute_value`, and `openapi.document`. This is a candidate design link, not an executable parity result. `Schema` additionally has a direct API signature workflow; `SchemaType` has a separate partial upstream test mapping described below. Other OpenAPI workflows that observe generated `openapi.document` output are feature-level evidence unless explicitly mapped to these symbols/fields; they do not establish field-by-field parity.

The checked target facade `fastapi-rs-py/python/fastapi/openapi/models.py:1-7` currently re-exports `APIKey`, `APIKeyIn`, `BaseModelWithConfig`, `SecuritySchemeType`, and `SecurityBase`; it does not expose this review's four names. The manifest likewise records no Rust binding for them. This reports the current visible binding state only; it is not a decision that the surface is out of scope.

## Existing fixture and recipe links

- **Documentation candidate:** `fastapi.docs.reference-openapi-models` → `docs/en/docs/reference/openapi/models.md`; selectors `python.import_path`, `python.signature`, `python.attribute_value`, `openapi.document`; mapping status `candidate` (not an active probe).
- **Direct `Schema` API candidate:** recipe `tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml`, case `fastapi.direct-api-reference-wave.openapi-schema-signature`, observation selector `python.signature`. It reflects only the generated class signature; it does not construct a matrix of fields, aliases, defaults, or errors. The manifest records no identity workflow for this symbol.
- **`SchemaType` / `Schema.type` upstream test sample:** atlas maps `tests/test_openapi_schema_type.py` to fixture `fastapi.test.test-openapi-schema-type` and recipe `tests/fixtures/input-recipes/parity/public-model-edge-cases-upstream.yaml`. Four case IDs cover `"array"`, `["string", "null"]`, `null`, and boolean `true`; the atlas mapping is partial and observes `http.body.bytes`. In the pinned upstream test (`../fastapi/tests/test_openapi_schema_type.py:5-24`), the accepted cases instantiate `Schema(type=...)`; `Schema(type=True)` is expected to raise `ValueError`. This is indirect evidence for the `Schema.type` annotation/validation path, not an identity or standalone `SchemaType` probe.
- **Missing candidate-specific coverage:** no active input/identity workflow is attached to `Discriminator`, `SchemaOrBool`, or any `Schema` field; the documented field design does not establish behavior for nested composition, aliases, model dumps, validation boundaries, or deprecations. Existing broader OpenAPI document recipes may incidentally contain generated schemas, but this atlas group has no reviewed field-to-case mapping to attribute those observations here.

## Upstream FastAPI/Pydantic source facts

`BaseModelWithConfig` is a `pydantic.BaseModel` subclass with `model_config = {"extra": "allow"}` (`models.py:57-58`). `Schema` derives from this configured model (`:123`). `Discriminator` derives directly from `BaseModel` (`:99`). `Schema.model_rebuild()` is called at `:433` after the recursive alias declaration, so forward-reference rebuilding belongs to the source contract.

`Discriminator` declares required `propertyName: str` (`:100`) and optional `mapping: dict[str, str] | None = None` (`:101`). The class declaration does not spell out a Python `__init__` signature; Pydantic supplies the model runtime signature.

`SchemaType` is `Literal["array", "boolean", "integer", "null", "number", "object", "string"]` (`:118-120`). `SchemaOrBool` is `Schema | bool` (`:207-209`), i.e. recursive schema-bearing fields can hold either a schema model or a boolean according to the declared type. This does not by itself specify target acceptance/coercion behavior.

`Schema` (`:123-204`) declares 61 fields. Every field has a `None` default, so none is required by its Python class declaration. The exact public candidate inventory is listed below with field type, source line, aliases, constraints, and the one deprecation annotation. `Field(alias=...)` values are Pydantic field aliases in FastAPI source; the atlas/manifest `alias_refs` for these candidates are empty. `Schema.example` carries `typing_extensions.deprecated` metadata (source lines `:198-204`): it remains declared, and the message directs callers to `examples`. This is distinct from the JSON Schema field `Schema.deprecated: bool | None` (`:189`), which is itself a schema annotation. The manifest `deprecation_refs` are empty for the group, so the `example` deprecation has not been linked into the reviewed manifest.

## Candidate-by-candidate source record

Each identifier below is one of the 67 atlas candidates. The source path is relative to the pinned FastAPI checkout. Fixture notes name the best current mapping for that candidate; the shared documentation mapping and uniform target status above apply to every row.

### `Discriminator`

- **`fastapi.openapi.models.Discriminator`** — `fastapi/openapi/models.py:99` — class Discriminator(BaseModel); Pydantic constructs the runtime class signature. Source line 99. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Discriminator.propertyName`** — `fastapi/openapi/models.py:100` — `str`; no default; required. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Discriminator.mapping`** — `fastapi/openapi/models.py:101` — `dict[str, str] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.

### `Schema`

- **`fastapi.openapi.models.Schema`** — `fastapi/openapi/models.py:123` — class Schema(BaseModelWithConfig); Pydantic constructs the runtime class signature. Source line 123. Inherits BaseModelWithConfig (models.py:57-58; extra="allow"); forward references are resolved by Schema.model_rebuild() at models.py:433. Direct recipe: `direct-api-reference-wave`, case `fastapi.direct-api-reference-wave.openapi-schema-signature`, selector `python.signature` (class signature only).
- **`fastapi.openapi.models.Schema.schema_`** — `fastapi/openapi/models.py:126` — `str | None`; default `None`; optional; alias `$schema`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.vocabulary`** — `fastapi/openapi/models.py:127` — `str | None`; default `None`; optional; alias `$vocabulary`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.id`** — `fastapi/openapi/models.py:128` — `str | None`; default `None`; optional; alias `$id`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.anchor`** — `fastapi/openapi/models.py:129` — `str | None`; default `None`; optional; alias `$anchor`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.dynamicAnchor`** — `fastapi/openapi/models.py:130` — `str | None`; default `None`; optional; alias `$dynamicAnchor`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.ref`** — `fastapi/openapi/models.py:131` — `str | None`; default `None`; optional; alias `$ref`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.dynamicRef`** — `fastapi/openapi/models.py:132` — `str | None`; default `None`; optional; alias `$dynamicRef`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.defs`** — `fastapi/openapi/models.py:133` — `dict[str, 'SchemaOrBool'] | None`; default `None`; optional; alias `$defs`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.comment`** — `fastapi/openapi/models.py:134` — `str | None`; default `None`; optional; alias `$comment`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.allOf`** — `fastapi/openapi/models.py:137` — `list['SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.anyOf`** — `fastapi/openapi/models.py:138` — `list['SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.oneOf`** — `fastapi/openapi/models.py:139` — `list['SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.not_`** — `fastapi/openapi/models.py:140` — `Optional['SchemaOrBool']`; default `None`; optional; alias `not`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.if_`** — `fastapi/openapi/models.py:141` — `Optional['SchemaOrBool']`; default `None`; optional; alias `if`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.then`** — `fastapi/openapi/models.py:142` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.else_`** — `fastapi/openapi/models.py:143` — `Optional['SchemaOrBool']`; default `None`; optional; alias `else`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.dependentSchemas`** — `fastapi/openapi/models.py:144` — `dict[str, 'SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.prefixItems`** — `fastapi/openapi/models.py:145` — `list['SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.items`** — `fastapi/openapi/models.py:146` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.contains`** — `fastapi/openapi/models.py:147` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.properties`** — `fastapi/openapi/models.py:148` — `dict[str, 'SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.patternProperties`** — `fastapi/openapi/models.py:149` — `dict[str, 'SchemaOrBool'] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.additionalProperties`** — `fastapi/openapi/models.py:150` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.propertyNames`** — `fastapi/openapi/models.py:151` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.unevaluatedItems`** — `fastapi/openapi/models.py:152` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.unevaluatedProperties`** — `fastapi/openapi/models.py:153` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.type`** — `fastapi/openapi/models.py:156` — `SchemaType | list[SchemaType] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.enum`** — `fastapi/openapi/models.py:157` — `list[Any] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.const`** — `fastapi/openapi/models.py:158` — `Any | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.multipleOf`** — `fastapi/openapi/models.py:159` — `float | None`; default `None`; optional; constraint(s) `gt=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.maximum`** — `fastapi/openapi/models.py:160` — `float | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.exclusiveMaximum`** — `fastapi/openapi/models.py:161` — `float | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.minimum`** — `fastapi/openapi/models.py:162` — `float | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.exclusiveMinimum`** — `fastapi/openapi/models.py:163` — `float | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.maxLength`** — `fastapi/openapi/models.py:164` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.minLength`** — `fastapi/openapi/models.py:165` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.pattern`** — `fastapi/openapi/models.py:166` — `str | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.maxItems`** — `fastapi/openapi/models.py:167` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.minItems`** — `fastapi/openapi/models.py:168` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.uniqueItems`** — `fastapi/openapi/models.py:169` — `bool | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.maxContains`** — `fastapi/openapi/models.py:170` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.minContains`** — `fastapi/openapi/models.py:171` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.maxProperties`** — `fastapi/openapi/models.py:172` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.minProperties`** — `fastapi/openapi/models.py:173` — `int | None`; default `None`; optional; constraint(s) `ge=0`. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.required`** — `fastapi/openapi/models.py:174` — `list[str] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.dependentRequired`** — `fastapi/openapi/models.py:175` — `dict[str, set[str]] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.format`** — `fastapi/openapi/models.py:178` — `str | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.contentEncoding`** — `fastapi/openapi/models.py:181` — `str | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.contentMediaType`** — `fastapi/openapi/models.py:182` — `str | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.contentSchema`** — `fastapi/openapi/models.py:183` — `Optional['SchemaOrBool']`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.title`** — `fastapi/openapi/models.py:186` — `str | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.description`** — `fastapi/openapi/models.py:187` — `str | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.default`** — `fastapi/openapi/models.py:188` — `Any | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.deprecated`** — `fastapi/openapi/models.py:189` — `bool | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.readOnly`** — `fastapi/openapi/models.py:190` — `bool | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.writeOnly`** — `fastapi/openapi/models.py:191` — `bool | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.examples`** — `fastapi/openapi/models.py:192` — `list[Any] | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.discriminator`** — `fastapi/openapi/models.py:195` — `Discriminator | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.xml`** — `fastapi/openapi/models.py:196` — `XML | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.externalDocs`** — `fastapi/openapi/models.py:197` — `ExternalDocumentation | None`; default `None`; optional. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.
- **`fastapi.openapi.models.Schema.example`** — `fastapi/openapi/models.py:198` — `Any | None with `typing_deprecated(...)` metadata`; default `None`; optional; deprecation message: “Deprecated in OpenAPI 3.1.0 / JSON Schema 2020-12; still supported; use `examples` instead.”. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.

### `SchemaOrBool`

- **`fastapi.openapi.models.SchemaOrBool`** — `fastapi/openapi/models.py:209` — `SchemaOrBool = Schema | bool`; public type alias/value, not a callable constructor. No candidate-specific executable input/identity workflow; only the shared documentation-fixture candidate described above.

### `SchemaType`

- **`fastapi.openapi.models.SchemaType`** — `fastapi/openapi/models.py:118` — `SchemaType = Literal['array', 'boolean', 'integer', 'null', 'number', 'object', 'string']`; public type alias/value, not a callable constructor. Partial source-test mapping: `public-model-edge-cases-upstream`, cases `fastapi.openapi-schema-type.accepted-string`, `.accepted-string-union`, `.accepted-null`, `.invalid-boolean`; atlas selector `http.body.bytes`.

## Unresolved behavior for parity review

The source definitions are not a complete target operation contract. Before a support claim, the review still needs identity-checked comparisons for model/type identity and signatures where applicable, and input/serialization/error observations for:

- all `Schema` keyword fields and aliases, including `$schema`, `$vocabulary`, `$id`, `$anchor`, `$dynamicAnchor`, `$ref`, `$dynamicRef`, `$defs`, `not`, `if`, and `else`;
- recursive `SchemaOrBool` values nested through `defs`, `allOf`, `anyOf`, `oneOf`, `not`, `if`/`then`/`else`, `dependentSchemas`, tuple/prefix items, `items`, `contains`, `properties`, `patternProperties`, additional/property schemas, unevaluated schemas, and `contentSchema`;
- `Discriminator.propertyName` requiredness, optional mappings, unknown extras, and interaction with `Schema.discriminator`;
- `SchemaType` valid/invalid values beyond the four partial cases, including each literal, list element validation, and coercion behavior;
- `Field(gt=0)` and `Field(ge=0)` boundaries; optional-null/default/omission behavior; unknown keys; Python-name versus alias input; alias serialization; model schema generation; field-set behavior; and exact Pydantic validation exception class/message/location/order;
- deprecation metadata/warnings or introspection for `Schema.example`, and the distinction from ordinary `Schema.deprecated` data.

These are open parity questions, not assertions that the pinned upstream lacks the behavior or that the target intentionally excludes it. No tests or benchmarks were run. The only file produced by this review is this draft.


Historical sibling-pin audit: Starlette-RS dd2c1ac66982218f749f0510758f64f5e61c735b added an input-only WebSocket scope-mapping adapter/workflow and updated parity metadata/manifest; it changed no production runtime implementation or dependency declaration. That input remains in the selected 37c6615 contract. The latest Starlette-RS revision 37c6615e5b54d820d70b9d910d2e06fda8ae4cfe changes only benchmark and compatibility-inventory documentation. It does not change runtime source, dependency declarations, API catalog/review, manifest, or parity inputs; the selected sibling contract and the behavior reviewed here are unchanged. This is outside the reviewed OpenAPI model group. Generic WebSocket scope behavior remains sibling-owned; no FastAPI-RS support or parity is inferred.