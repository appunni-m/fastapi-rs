# Next OpenAPI wire-order feasibility — 2026-10-05

Read-only design for the root agent. No patch, application/native import, build,
parity run, unit test or tracked edit was made. This file under `/private/tmp` is
its sole output. The next three input cases are admitted but await fresh source
and unchanged-target pre receipts; their outcomes are not assumed here.

## Decision and scope

A generic Rust finalization boundary is feasible: assemble the owned native
OpenAPI document, finalize it by semantic OpenAPI node type, then run the existing
Rust jsonable encoder and ordinary JSON renderer. Insert this boundary once in
`openapi::openapi_document` after all root options are assembled, so public
`app.openapi()`, ASGI docs, and the existing public get_openapi subset share it.
The public callable's current late edits must be moved before that final boundary
as described below. It is independent of the retained-adapter batch: it consumes the batch's completed schema dictionaries and never invokes
user core/JSON-schema hooks itself.

There are two distinct implementation scopes:

1. **Bounded wire-order pass:** a Rust-owned table of model fields and child
   contexts reconstructs fresh dictionaries in the pinned model order for valid
   dictionaries emitted by the current native builder. This is the smallest
   generic addition for the immutable primitive fields in next3. It preserves
   existing dictionary values/JSON encoding and does not claim the missing final
   model validator. It must be described as partial order support.
2. **Complete final-model boundary:** Rust constructs a private Pydantic model
   graph matching the pinned OpenAPI model declarations, calls its OpenAPI
   constructor on the assembled dictionary, then calls the existing Rust
   jsonable encoder on that instance. This also delegates model validation,
   unions, aliases, defaults, URLs and model serialization to pinned Pydantic.
   It is a larger separately reviewed slice. No original FastAPI model import,
   Python source execution/helper, facade logic or new public export is needed.

Use the first scope only with the precise validation/union gaps below. Use the
second scope when promising source-equivalent final model behavior. Neither
scope establishes all OpenAPI assembly semantics or all schema generation.
The three new cases and prior203 remain unchanged live gates for either choice.

## Source facts that determine wire bytes

Pinned FastAPI 0.141.1 `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, sole Starlette
1.6.0 oracle `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, CPython 3.12.13,
Pydantic 2.13.4/core 2.46.4. Sibling stays immutable b4c8a65.

- `openapi/utils.py602-678` assembles input dictionaries in execution order,
  including sorted component definition names at668-669. Line679 then returns
  `jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)`.
  Execution-time insertion order is therefore not always final model order.
- `encoders.py243-258` calls `model_dump(mode="json", by_alias=True,
  exclude_none=True, exclude_unset=False, exclude_defaults=False)` for that model,
  then recursively encodes its returned dictionary. The dictionary branch at
  281-317 preserves iteration order, removes None-valued entries when requested
  and filters string keys beginning `_sa`. Lists retain item order, including
  null items. It does not alphabetically sort dictionaries.
- Pydantic core `validators/model_fields.rs334-386` validates fields in its
  ordered field vector and builds their model dictionary in that order; unknown
  fields are separately gathered in input order at410 onward. The model
  serializer `serializers/fields.rs158-230` preserves the main dictionary's
  iteration order and then the extras iteration order. Thus declared order is
  the result for these freshly validated ordinary dictionaries. Reordered or
  mutated preexisting model-instance storage is a separate unselected case.
- `openapi/models.py57-58` has `extra="allow"` on most models. `Reference` and
  `Discriminator` use plain BaseModel instead (95-101); their unknown-key policy
  is not the same. `Example` is an optional TypedDict with extra allow (212-218),
  not a BaseModel.
- Starlette JSONResponse `responses.py194-201` uses json.dumps with
  ensure_ascii=False, allow_nan=False, indent=None and separators=(",", ":"),
  followed by UTF-8. Its normal sends at166-167 retain their exact fields. A
  finalizer must return an ordinary dictionary, not a reordered text template or
  encoded JSON string, so public method results and normal response handling
  keep their meaning.

## Pinned field order and child roles

These orders were read from the pinned declarations, including aliases and
inherited fields; they are source descriptors, not fixture-specific templates.
A field absent or omitted by source exclusion contributes no output slot.

| Node | Declared wire-key order | Source lines |
| --- | --- | --- |
| OpenAPI | openapi, info, jsonSchemaDialect, servers, paths, webhooks, components, security, tags, externalDocs | models419-430 |
| Info | title, summary, description, termsOfService, contact, license, version | models73-80 |
| PathItem | $ref, summary, description, get, put, post, delete, options, head, patch, trace, servers, parameters | models305-318 |
| Operation | tags, summary, description, externalDocs, operationId, parameters, requestBody, responses, callbacks, deprecated, security, servers | models289-302 |
| Response | description, headers, content, links | models282-286 |
| Reference | $ref | models95-96 |
| Components | schemas, responses, parameters, examples, requestBodies, headers, securitySchemes, links, callbacks, pathItems | models399-410 |
| MediaType | schema, example, examples, encoding | models236-240 |
| Parameter | description, required, deprecated, style, explode, allowReserved, schema, example, examples, content, name, in | models243-260; inherited base precedes child fields |
| Header | description, required, deprecated, style, explode, allowReserved, schema, example, examples, content | models243-264 |
| RequestBody | description, content, required | models267-270 |
| Contact / License | name, url, email / name, identifier, url | models61-70 |
| Server / ServerVariable | url, description, variables / enum, default, description | models83-92 |

Schema's complete declared alias-key sequence (models123-204):

```
$schema, $vocabulary, $id, $anchor, $dynamicAnchor, $ref, $dynamicRef,
$defs, $comment, allOf, anyOf, oneOf, not, if, then, else,
dependentSchemas, prefixItems, items, contains, properties,
patternProperties, additionalProperties, propertyNames, unevaluatedItems,
unevaluatedProperties, type, enum, const, multipleOf, maximum,
exclusiveMaximum, minimum, exclusiveMinimum, maxLength, minLength,
pattern, maxItems, minItems, uniqueItems, maxContains, minContains,
maxProperties, minProperties, required, dependentRequired, format,
contentEncoding, contentMediaType, contentSchema, title, description,
default, deprecated, readOnly, writeOnly, examples, discriminator, xml,
externalDocs, example
```

**Context, not a key name alone, determines recursion.**

- paths/webhooks: named map; preserve path insertion order, finalize each typed
  PathItem/Reference member. PathItem's methods follow declared method order.
- responses, headers, content, links, component sections: named maps; preserve
  status/header/media/name insertion order, finalize members using the declared
  value types. Do not sort response status strings or user component maps. Only
  upstream-generated component schemas have the explicit source name sort.
- Schema properties/patternProperties/dependentSchemas/$defs: preserve property
  or definition name order; each value is SchemaOrBool. A user property literally
  named "type", "title" or "$ref" is a name and must stay in that map's slot.
- allOf/anyOf/oneOf/prefixItems: ordered lists of SchemaOrBool. items, contains,
  not, if, then, else, additionalProperties, propertyNames, unevaluatedItems,
  unevaluatedProperties and contentSchema have typed SchemaOrBool values. Boolean
  schemas stay booleans. Their false value must not be omitted as if None.
- enum/const/default/example/examples element data and unknown extensions have
  Any payload roles as declared. Preserve arbitrary dictionary key order and
  values there, with only the source model/encoder conversions and exclusions.
  A dictionary under x-user-data is not automatically a Schema because it
  contains a familiar key. Typed examples/encoding/discriminator/XML/externalDocs
  use their own model roles when reached through their declared fields.
- Security requirement map names/scopes and discriminator mapping names are
  named data. Their keys are not model field names. A full graph also retains
  the inherited field order and enum behavior of each security-scheme model.

## Smallest bounded Rust implementation shape

Use a closed `WireNodeKind` plus immutable descriptors containing ordered external
keys and child shapes: object, named map, ordered list, scalar or Any. Keep known
model fields in descriptor order; append unknown extra-allow keys in their
original input order. Construct new PyDict/PyList objects, retain values with
owned Py references, and never mutate the generator's dictionaries or app cache
in place. Return the newly finalized ordinary PyDict to the current encoder.

Own-node provenance comes from the assembler/field context, not case IDs, route
names, particular schema refs, observed comparison artifacts or payload values.
The ordinary generated Schema branch may include $ref and sibling Schema fields;
no `contains "$ref" => Reference` shortcut is allowed. Literal aliases are wire
keys ($ref/schema/not/if/else); arbitrary unknown keys such as schema_ or ref must
not be renamed merely because they resemble a model's Python attribute name.

For valid native Response/PathItem nodes with known required fields, descriptor
order is deterministic. Where the source declares model|Any or model|Reference
unions, the order pass does not establish smart-union validation/selection. It
must retain the bounded valid-node assumption rather than silently dropping
unknown data, inventing a validation error or introducing a new unsupported
branch into previously accepted public inputs. Full union correctness requires
the model graph below. This is an explicit compatibility gap, not a claim that
source model validation can be omitted generally.

The existing `normalize_schema` in openapi.rs796-977 already has the full Schema
key rank list and stable unknown-key order. It also does separate transformations:
$defs extraction/removal, ref-prefix rewriting, selected default removal and
binary format/number conversion. Separate those existing generation/compatibility
steps from the new final ordering layer. Do not repeat them during finalization
or treat them as source final-model validation. Their independent semantic gaps
must not be hidden by a wire-order pass. In particular the existing recursive
normalizer omits the typed unevaluatedItems traversal and currently changes
exclusiveMinimum numerics only; Pydantic Schema has several float/constraint
fields. No complete numeric/model validation claim follows from that helper.

Concrete general ordering changes a final pass would cover in current output:
PathItem methods in registration order, Operation.deprecated inserted before
parameters, Parameter.name/in before inherited fields, RequestBody.required
before content in one branch, and root externalDocs before components. These are
model-order differences, even where old map selectors happen to pass.

A separate assembly-order gap remains: source utils476-516 merges declared extra
responses before appending its automatic422 response at517-529, while native
openapi.rs346-357 appends422 before extras. A named-map finalizer must preserve,
not sort away, this difference. Generic construction must use the source phase
and source presence check for "422", "4XX" and "default". The new3 probe has no
query/body parameters and therefore does not gate this case. Root should keep it
as an existing unselected assembly gap or pair a source-backed correction with
its own public input/parity gate before claiming compatibility. Routine fixture
and design work needs no new human approval; the boundary is evidence and the
current source freeze. No case-specific ordering is justified.

## Full model validation option, authored and controlled by Rust

Rust may build an internal immutable model graph with pinned public
pydantic.create_model, Field, typing/typing_extensions and constraint annotations.
All field names, aliases, type relationships, defaults, extra policies,
inheritance and union order are Rust descriptors. Existing security.rs2371-2426
already constructs Pydantic model types from Rust and establishes this technique.

Build the complete recursive graph before publication, resolve Schema/Operation/
Encoding recursion using an explicit internal types namespace, and keep the
classes private. Use actual annotation objects and controlled internal forward
refs only; do not evaluate copied FastAPI Python source. Child models use the
configured base and correct inherited field order. Reference/Discriminator use
their distinct plain BaseModel policy. Example remains a TypedDict with its own
extra policy. Every alias, literal enum, AnyUrl/str union, Schema constraint and
required/default distinction needs source review. A subset graph marking
responses/Schema/paths as Any is a partial graph and does not prove those models.

At finalization, call the private class named OpenAPI with keyword contents of
the assembled owned output, matching source constructor use. Call the existing
Rust jsonable_encoder with by_alias=true, exclude_none=true, all other source
defaults. Its BaseModel path already performs model_dump(mode="json") and recursive
encoding (encoding.rs162-183). Do not model_construct, dump_json, alphabetically
sort, or manually swallow validation/serialization exceptions. Pydantic must
select smart unions in declared order; operation responses and root paths allow
Any fallback, but typed components do not have universal Any fallback.

Preserve original PyErr/class/message/location/warnings. Name the class OpenAPI
and retain appropriate internal module/name metadata so error titles do not
become a synthetic compatibility class name. The pinned optional-email fallback,
URL coercion/normalization, TypedDict output order and serialization-warning
behavior need their own parity stimuli before claiming that broader graph.
Private model graphs need no promotion of internal source API classifications
and no Python facade changes or original FastAPI runtime dependency.

Pydantic model creation may run its own annotation/plugin code. Model graph
construction and use therefore must happen outside app/cache/native-container
borrows. Prefer an owned per-extension/interpreter graph created during native
registration or an independently owned private holder; do not hold an
initialization/cache lock while building/calling it. Publish the whole graph
only after success, and retire/drop replaced Python references after releasing
borrow/lock guards. Reentrant initialization and multiple-interpreter identity
need review rather than an unqualified process-global Python-object cache.

## Cache, docs, ownership and exact rendering

The current OpenApiAppSnapshot already owns route/app inputs before Python
schema work (runtime4045-4075). The new finalization works on those owned results,
with no Rust app borrow or OpenAPI-cache mutex held across validation, model_dump,
recursive encoding, warning/exception hooks or retired-reference destruction.
Both ordering failures and final-model errors must leave cache/version publication
untouched; current public openapi3231-3260 publishes only after construction and
drops retired cache references after releasing guards. JSON-hook failure/retry
semantics remain the shared-batch owner's boundary.

Finalize the base app document once, before caching it. Public cache hits return
that same completed PyDict without re-finalization or re-running generators.
Source applications1084-1103 has this success-only cache assignment.

The docs root-path overlay happens **after** base finalization/cache lookup in
source applications1108-1118. If servers is newly inserted by dict-copy overlay,
its new position is dictated by that later operation; do not re-run model-order
finalization on the overlay. If a servers key already exists, replacement keeps
its position. Native docs runtime10421-10431 already calls the root-path overlay
after public openapi; preserve that flow. Empty root_path in new3 leaves this
broader branch unselected. Public get_openapi's accepted route/webhook subset
must not be enlarged as part of this wire change.

The public `GetOpenApiCallable` currently edits openapi_version and tags after
openapi_document has encoded its output, then separately validates externalDocs
URL (openapi.rs574-611). A common finalizer inside that earlier function alone
would leave tags after externalDocs and would omit full model validation of the
late values. Carry these root options as owned assembly input and apply them
before the one final boundary, or split raw assembly from finalization and call
the shared finalizer only after each caller completes its options. Keep the
supported empty/one-simple-route subset unchanged. The complete model option
must consume externalDocs before validation rather than validate/encode it twice.
The bounded order option retains existing URL behavior as an explicit distinct
semantic boundary, with public-method controls required for any timing change.

Use the existing ordinary JSON renderer after obtaining the ordered dictionary:
no direct TypeAdapter/Pydantic dump_json bytes, sort_keys, custom text renderer,
float formatting or schema-map normalization. Source JSONResponse's allow_nan
failure and native json_bytes9222-9224 must remain observable. Raw schema bodies,
content length, ordered headers, all ASGI message fields, warnings and error
journals in next3 remain exact. No output selector or comparator changes.

## Review and implementation gates

1. Close fresh pinned source and unchanged827 target pre runs for the identical
   admitted next3 digest. Preserve constructor/action failures and raw journals.
2. Review descriptors against pinned models.py, including inherited Parameter
   order, extra policies, wire aliases, typed-map/list edges and generic Any data.
   A source-file AST/read-only inventory can check completeness, but it supplies
   no target-support evidence. No unit tests/source-generated expectations.
3. Independently review Rust ownership/drop paths and any private model graph
   for absence of callbacks under app/cache/init borrows, error suppression,
   fixture dispatch and original FastAPI imports.
4. After the pre-run source freeze closes, coordinate fmt/strict Clippy/static
   facade/metadata/Rust contracts and fresh same-input source/target next3. Require all19 HTTP actions,
   three construction observations, full schema bytes, full lossless raw sends,
   public object identity/cache relations, hook occurrence/mode order, unfiltered
   warning/error journals and retry behavior. Shared-adapter and wire-order work
   are separate required causes of equivalence; this order design cannot cure
   generator callback/ref-mapping errors.
5. Retain all prior203 cases, including existing pointer/description OpenAPI
   controls, on the same fixed native pair and source snapshot. Existing map-only
   selectors do not prove schema byte order. Do not weaken them or next3.

Broader final-model validation/union fallback, metadata extension placement,
invalid/nullable numeric constraints, multiple methods, parameter/request-body
order, root-path servers overlay, Reference extras, Example TypedDict, nested
models, callbacks/webhooks/security, mutable/reentrant/concurrent caches and
user model-instance history need additional independent public cases. Passing
next3 alone establishes only its selected immutable primitive schema documents,
hooks/cache outcomes and raw wire data; complete OpenAPI compatibility remains
unclaimed.

## Readback identities

The three relevant native files remain byte-identical to their 827612f source
versions despite later metadata/documentation admission edits. No fresh full
source/binary equality claim is made for that later tree.

| File | SHA256 |
| --- | --- |
| fastapi-rs/src/openapi.rs | 28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0 |
| fastapi-rs/src/encoding.rs | f0da7038906d300ce3342079598e7278b0466244d75ea2a0721d6617311b5d4f |
| fastapi-rs/src/application_runtime.rs | 14c6f7cf93865b8cc719055587d895ae517937212d14f105a7b5e2f6e7a5dfef |
| pinned FastAPI openapi/models.py | b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d |
| pinned FastAPI openapi/utils.py | 81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527 |
| pinned FastAPI encoders.py | 4cc09230eca6435892f6bc25a2185e214dbedfe994d5103feb63ad269137caad |
| pinned FastAPI applications.py | 38dccb19b2a0b0b984c8d7541263842954a37c087cf96b4463aea17873c6183c |
| pinned Starlette responses.py | 10a5f318bb014296e57d9a3f6ffa51d478e21b07d5bf978597dba2ec9dc21e4a |
| pinned Pydantic main.py | 35b842cfe92ef300e060b40c062ef93afee1cb075cf0b7b0037a1434867c2554 |
| pinned core validators/model_fields.rs | 5e17769d664de1a3a2f631fb70a4117ad41c79cddddaf5b665c2bd4738ef86f3 |
| pinned core serializers/fields.rs | a48a461d9632e4f6664428726cb3e79fca82ca0cb181391d55c4dfb101de53c2 |
