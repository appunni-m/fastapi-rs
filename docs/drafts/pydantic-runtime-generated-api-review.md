# Pydantic runtime-generated API review

## Review result

FastAPI model classes expose Pydantic's inherited `BaseModel` API at their
`fastapi.*` paths. Treat those methods and Pydantic-generated model machinery
as part of the observable consumer surface, with ownership assigned to the
reused Pydantic public API. FastAPI owns the model classes it defines, their
fields, aliases, configuration, custom validators, and the way those models
participate in FastAPI validation and OpenAPI generation. This follows the
reviewed policy in `metadata.yaml:16-21`: reuse the Pydantic public Python
model API; treat `pydantic-core` as Pydantic's implementation detail.

The source and reflection review clarifies what the unresolved item means, but
does not establish target parity. Keep `pydantic-runtime-generated-api`
unresolved until behavior is exercised in identity-checked isolated oracle and
target processes and the reviewed contract separates the two owners.

## Concrete inherited and generated surface

Both runtime profiles record 49 symbol paths with `pydantic_model_fields` and
`pydantic_generated_inherited_members`; those paths resolve to 38 distinct
class identities. Each of the 49 rows has the same 28 inherited names. The
reflection records 283 field observations across paths, or 240 across the 38
distinct identities. The repeated observations include import aliases and
inherited fields. These are reflection counts, not counts of distinct
FastAPI-declared field definitions.

The 28 inherited names break down as follows:

| Surface | Names |
| --- | --- |
| Field/configuration attributes | `model_computed_fields`, `model_config`, `model_extra`, `model_fields`, `model_fields_set` |
| Pydantic v2 operations | `model_construct`, `model_copy`, `model_dump`, `model_dump_json`, `model_json_schema`, `model_parametrized_name`, `model_post_init`, `model_rebuild`, `model_validate`, `model_validate_json`, `model_validate_strings` |
| Deprecated compatibility methods | `construct`, `copy`, `dict`, `from_orm`, `json`, `parse_file`, `parse_obj`, `parse_raw`, `schema`, `schema_json`, `update_forward_refs`, `validate` |

The 28-name reflection list is not the whole inherited namespace. Pydantic
2.13.4 provides deprecated `__fields__` access through both an instance
property and a class-level metaclass property; `__fields_set__` is a deprecated
instance property only. These accesses warn and direct callers to `model_fields`
and `model_fields_set`, respectively. Their dunder names keep them out of the
reflected member list. Their supported-contract status needs an explicit
decision; this review does not extend the contract to the wider `__pydantic_*`
implementation namespace.

The model constructor signature is a separate reflected surface: Pydantic
generates the class `__signature__` from the collected fields, aliases,
configuration, and `__init__`. The reflection and manifest have signatures
for model classes, but the 28 inherited names are recorded as names only; they
do not carry each method's callable signature.

The field/schema portion is externally visible in several ways:

- `model_fields` exposes the model's `FieldInfo` records, including
  annotations, defaults, aliases, requiredness, and field metadata. The
  runtime reflection records field names, annotations, aliases, required
  flags, and defaults. FastAPI classes with inheritance make this larger than
  the set of fields declared on one source class. Pydantic documents access to
  `model_fields` and `model_computed_fields` through an instance as deprecated;
  the class-level access is the supported form.
- `model_config` is an inherited class attribute. FastAPI's
  `BaseModelWithConfig` sets `extra="allow"`; descendants use it when accepting
  and retaining extension values.
- `model_json_schema()` returns a generated JSON Schema and accepts alias,
  reference template, generator, mode (`validation` or `serialization`), and
  union-format options. The deprecated `schema()` and `schema_json()` wrappers
  remain observable and emit Pydantic deprecation warnings.
- Pydantic also sets `__pydantic_core_schema__`,
  `__pydantic_validator__`, `__pydantic_serializer__`, and related double
  underscore attributes. These are introspection-visible implementation
  structures; the current policy identifies `pydantic-core` as an internal
  implementation detail, so do not make their internal shape a compatibility
  promise without a separate explicit decision.

The reflection selection is not a complete census of every Pydantic subclass.
`fastapi.openapi.models.BaseModelWithConfig` is a public class candidate and
defines the configuration inherited by the OpenAPI models, but its empty
`model_fields` means it has no `pydantic_model_fields` or inherited-member
record in the runtime reflection. It is separately present as a class in the
manifest. The OpenAPI `Example` type is a `TypedDict`, not a `BaseModel`, and
does not inherit this method set.

Representative model-specific surfaces show how FastAPI fields combine with
Pydantic generation:

- `fastapi.openapi.models.Schema` has 61 reflected model fields. Its source
  spans JSON Schema 2020-12 and OpenAPI fields; Python-safe names such as
  `schema_`, `ref`, `not_`, and `if_` carry wire aliases such as `$schema`,
  `$ref`, `not`, and `if`.
- `fastapi.openapi.models.OpenAPI` has ten fields and is the Pydantic document
  model FastAPI constructs before converting the result to a JSON-safe value.
- `Parameter` inherits the ten `ParameterBase` fields and adds `name` and
  `in_`; the latter serializes as `in`. This distinction appears in reflection
  as 12 fields on `Parameter`, while the source declarations are split across
  the two classes.
- `ServerSentEvent` contributes six fields, field validators for `event`,
  `id`, and `retry`, and a model validator requiring `data` and `raw_data` to
  be mutually exclusive. These are FastAPI-defined rules layered on Pydantic
  model validation.

The 49 reflected paths include the OpenAPI model definitions plus imported
aliases: for example, `fastapi.openapi.utils.OpenAPI` is the same class as
`fastapi.openapi.models.OpenAPI`, and the `fastapi.routing.ServerSentEvent`
binding is the same class as `fastapi.sse.ServerSentEvent`. Security modules
also bind OpenAPI models under names such as `HTTPBaseModel`, `HTTPBearerModel`,
`OAuth2Model`, and `APIKey`. The reflection shows 49 paths but 38 identities;
that is why path presence and `is` identity need separate contract observations.

## Existing reflection and contract coverage

The core and standard runtime reflections both use the pinned profile
FastAPI 0.141.1, Starlette 1.6.0, CPython 3.12.13, Pydantic 2.13.4, and
pydantic-core 2.46.4. Their manifest entries give each profile 49
`pydantic_model_classes` and say that the artifacts are CPython reflections.
For example, the `fastapi.openapi.models.APIKey` symbol contains its generated
constructor signature, Pydantic field observations, and inherited-member-name
list. The artifacts record presence and identity data; their declared purpose
does not make that data behavioral parity evidence.

The API manifest already has class candidates and source-declared field rows.
For example, `fastapi.openapi.models.APIKey` has a runtime-reflected class
signature, and its declared `in_`, `name`, and `type_` fields appear as
`pydantic_field` symbols. The model reference documentation is linked as a
candidate fixture. Those class and field rows carry selectors for import path,
signature, attribute value, and `openapi.document`, with
`documentation-fixture-design-linked; operation-level review pending` status.
The class binding's `fastapi-rs` implementation owner covers the FastAPI model
path; it does not transfer Pydantic's inherited method semantics to FastAPI.

The manifest still records `pydantic_generated_surface` as unresolved, with
the question that inherited/generated model fields, methods, and schemas need
public-surface review. Its Pydantic authority is a selected source-lock
baseline, while generated/inherited runtime behavior remains unresolved.
`metadata.yaml` states the public-layer ownership rule, but no reviewed
per-method contract enumerates the inherited methods or the results and
warnings of calling them. In particular, the runtime reflection does not
record `model_json_schema()` results, deprecated-method warning records, or
method signatures for inherited members.

## Ownership boundary

FastAPI owns these source-defined decisions:

- The OpenAPI model type graph, field names, aliases, defaults, and
  `BaseModelWithConfig` extra policy (`fastapi/openapi/models.py`).
- Security credential models and their connection to HTTP security flows
  (`fastapi/security/http.py`); OpenAPI security model bindings are FastAPI
  aliases to model definitions.
- `ServerSentEvent` fields and validators, plus its relationship to FastAPI's
  SSE response formatting (`fastapi/sse.py`).
- Which models FastAPI places in OpenAPI, how it names and separates
  validation/serialization definitions, and how it builds the final document.
  In 0.141.1, `_compat/v2.py` adapts Pydantic `GenerateJsonSchema`, builds
  definitions from Pydantic core schemas, and selects field aliases/modes;
  `openapi/utils.py` assembles the document and serializes an `OpenAPI` model
  with `by_alias=True, exclude_none=True`.

Pydantic owns the inherited BaseModel method signatures and semantics:
validation, trusted construction, copying, dumping, model field/config
properties, schema generation, model rebuilds, and v1 compatibility warnings.
Pydantic's source documents that `model_dump` and `model_dump_json` delegate to
the model serializer; `model_validate*` delegate to the model validator; and
`model_json_schema` delegates to Pydantic's JSON Schema generator. Pydantic
also creates the class field map, core schema, validator, serializer, and
constructor signature during model construction. The Pydantic behavior remains
observable through a FastAPI model class even though FastAPI does not define
those inherited methods.

The OpenAPI generation boundary is mixed. Pydantic's generator provides the
field/model JSON Schema rules. FastAPI subclasses that generator for its bytes
schema behavior and controls the input/output schema selection, OpenAPI
references, titles, route inclusion, document shape, aliases, and omission of
`None` values. A direct `Model.model_json_schema()` result and
`app.openapi()` therefore need separate observations; they exercise different
call paths.

## Remaining uncertainty

- Runtime inventory records constructor signatures, but the inherited methods'
  own signatures are absent from the manifest. The reviewed contract needs to
  decide whether it records all 28 method names with signatures or uses
  Pydantic 2.13.4 as the versioned contract source for that dependency-owned
  group.
- The reflection captures `model_fields` data but not JSON Schema results or
  the full values of generated/private Pydantic schemas, serializers, and
  validators. Keep private implementation structures outside the support
  claim unless the public contract intentionally adds them.
- The inherited-name list omits dunder-named `__fields__` and
  `__fields_set__`, even though Pydantic 2.13.4 retains them as deprecated
  compatibility properties. Decide whether to include those two specific
  warnings/values before describing the 28-member list as exhaustive.
- The current API call outcome selector returns the exception class and
  message; full Pydantic error records are represented by
  `validation.error_details` for ASGI dispatch. The available contract does
  not yet establish a full `ValidationError.errors()` projection for direct
  `Model.model_validate()` calls.
- `python.import_path` and `python.object_identity` selectors are cataloged as
  planned. Runtime reflection has alias identities, but isolated fixture
  coverage for import paths and `is` relations needs workflow support before
  it can serve as parity evidence.
- Current API reflection is for CPython 3.12.13. It does not establish the
  target Python runtime identity or behavior across the package's declared
  Python versions.

## Fixture and selector recommendations

Add input-only YAML recipes under `tests/fixtures/input-recipes/` after the
reviewed contract is updated. Keep all outcomes in the isolated oracle/target
comparison, with no expected outputs in recipe files.

1. **Model field, signature, and alias surface.** Import `APIKey`, `Schema`,
   `OpenAPI`, `Parameter`, and `BaseModelWithConfig`; inspect class signatures,
   selected `model_fields`/`model_config` values, and model instances built
   with Python field names and wire aliases. Use `python.signature` and
   `python.attribute_value`; document a JSON-safe projection for `FieldInfo`
   if direct attribute selection cannot encode its instances.
2. **Pydantic operations and deprecations.** Exercise a representative model
   through `model_validate`, `model_dump(by_alias=True)`,
   `model_dump_json(by_alias=True)`, and `model_json_schema()` in both schema
   modes where fields differ. Add calls to representative deprecated wrappers
   (`dict`, `schema`, and a class validation wrapper) with
   `python.warnings`; compare ordered category, message, and stable source
   location. Also capture instance access to `model_fields` and
   `model_computed_fields`; capture both class and instance access to
   `__fields__`, and instance access to `__fields_set__`, with their warning
   records. Expand to every deprecated member only if the final public contract
   includes the complete inherited compatibility set.
3. **FastAPI OpenAPI assembly.** Build an app whose request and response
   models exercise aliases, optional/default fields, nested models, extra
   values, and a security scheme. Compare `openapi.document` and selected
   `openapi.request_schema` pointers. Include a direct model schema call in a
   separate operation so Pydantic output is not conflated with FastAPI's
   adapted OpenAPI output.
4. **FastAPI-specific model validation.** Select valid and invalid
   `ServerSentEvent` inputs for event/id line restrictions, negative retry,
   and simultaneous `data` plus `raw_data`; capture direct call outcomes and
   exercise SSE response encoding through ASGI with `http.body.bytes`. Pair
   this with `validation.error_details` for FastAPI request validation cases.
5. **Public aliases.** Compare bindings for the reflected aliases, including
   `fastapi.openapi.utils.OpenAPI` / `fastapi.openapi.models.OpenAPI`,
   `fastapi.routing.ServerSentEvent` / `fastapi.sse.ServerSentEvent`, and
   security model aliases. Use `python.import_path` and `python.object_identity`
   when workflow support is available; the runtime reflection alias groups
   are useful discovery inputs.

The selector catalog already supports `python.signature`,
`python.attribute_value`, `python.call_outcome`, `python.warnings`,
`openapi.document`, `openapi.request_schema`, `validation.error_details`, and
HTTP body bytes. Source-backed fixtures should keep those projections narrow:
preserve aliases, requiredness/defaults, warning text/category/location,
schema modes, validation errors, and output bytes; normalize only documented
differences.

## Pinned source references

The checked-out FastAPI source is selected by `metadata.yaml:6-12` at commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; the installed Pydantic source is
selected as 2.13.4 in `metadata.yaml:16-21` and the oracle profile. The Pydantic
API text below is available as docstrings in that pinned local source tree.

| Source path and line span | Supports |
| --- | --- |
| `metadata.yaml:16-21` | Pydantic 2.13.4 / pydantic-core 2.46.4 and public-layer ownership policy. |
| `tests/fixtures/manifest.yaml:42-47,217-234,272-289` | Pinned Pydantic identity, 49 reflection counts per profile, and unresolved generated-surface item. |
| `tests/fixtures/manifest.yaml:5049-5099,5101-5141` | Example class/signature/field contract rows and their pending review status. |
| `tests/fixtures/runtime-api-surface-core.json` and `tests/fixtures/runtime-api-surface-standard.json`, `/symbols` rows with `pydantic_model_fields` | Identity-checked fields and the exact 28-name inherited inventory in both profiles. |
| `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/main.py:119-152,253-314` | BaseModel's generated structures, initializer, and public field/config properties. |
| `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/main.py:316-425,427-598,601-740,742-822` | Construction/copy, serialization/schema generation, rebuild, and validation operations. |
| `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/main.py:1299-1318,1322-1641`, `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:326-336`, and `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/_internal/_utils.py:410-446` | Deprecated dunder compatibility properties, deprecated v1 methods, instance-access deprecation warnings, and Pydantic warning behavior. |
| `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/_internal/_model_construction.py:566-714` and `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/_internal/_signature.py:30-45,165-189` | Field collection, generated core schema/validator/serializer, and generated constructor signature. |
| `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/fields.py:106-149` | Public `FieldInfo` attributes and field metadata. |
| `/Users/lazytrot/work/fastapi-rs/.venv-oracle/lib/python3.12/site-packages/pydantic/json_schema.py:225-265,2518-2563` | Pydantic JSON Schema generator and model schema entry point. |
| `/Users/lazytrot/work/fastapi/fastapi/openapi/models.py:57-114,123-204,228-435` | FastAPI OpenAPI model config, fields/aliases, model inheritance, and forward-reference rebuild calls. |
| `/Users/lazytrot/work/fastapi/docs/en/docs/reference/openapi/models.md:1-5` | Consumer-facing OpenAPI Pydantic model description. |
| `/Users/lazytrot/work/fastapi/fastapi/_compat/v2.py:57-70,254-346` | FastAPI's `GenerateJsonSchema` extension and definition generation from Pydantic field core schemas. |
| `/Users/lazytrot/work/fastapi/fastapi/openapi/utils.py:620-679` | FastAPI route/schema assembly and final `OpenAPI` model encoding. |
| `/Users/lazytrot/work/fastapi/fastapi/security/http.py:16-67,69-102`, `/Users/lazytrot/work/fastapi/fastapi/security/api_key.py:11-29` | FastAPI credential models and its construction of OpenAPI security model values. |
| `/Users/lazytrot/work/fastapi/fastapi/sse.py:52-156` | FastAPI's SSE model fields, validators, and cross-field validation rule. |
| `tests/fixtures/observation-selectors.json`, `python.signature`, `python.attribute_value`, `python.warnings`, `python.import_path`, `python.object_identity`, `openapi.document`, `openapi.request_schema`, `validation.error_details` | Current selector definitions and support states for recommended observations. |
