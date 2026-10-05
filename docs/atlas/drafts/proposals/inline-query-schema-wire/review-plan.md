# Inactive inline query schema wire proposal

2026-10-05. Independent source-only proposal following the tracked legacy-inline
schema diagnosis. No original/target app, workload or native module was imported
or executed; no active input/code/docs/metadata, comparator, sibling or binary
was edited. No build/install/parity/unit framework. This is not proof that a
new gate passes or fails. Current parent stages at d508878 stay separate.

## Inputs and observations

Two factories/cases choose ordinary public placement, direct or dependency.
IDs are fastapi.openapi-inline-query-schema-wire.direct-defaults and
fastapi.openapi-inline-query-schema-wire.dependency-defaults. Every signature
uses independent names offset_mark, batch_width, term, spare_number, spare_word.
Ordinary defaults are two nonzero ints, an empty str and nullable int/str None
controls. The dependency is an async ordinary function passed to public Depends;
its marker is retained in a local before the endpoint signature. Both endpoints
are async, return public JSONResponse and set response_model=None. No Query,
Field/Annotated metadata, model hooks, serializer or additional status work is
introduced.

Exactly two parity constructors and eight GET actions (four per case): initial
/openapi.json, /observe with omitted queries, /openapi.json again, /observe with
explicit valid queries. All actions select exact status/ordered headers/body,
ordered ASGI message types and exact application exception. Both docs actions
also select the whole structural OpenAPI document, supplementing raw bytes.
Construction plus every action captures ordered runner warnings: ten phases.
Action observation counts are 28 (16 on four docs actions, 12 on four endpoint
actions); there are two construction observations and no faults or expected
outputs.

Endpoint bodies contain actual injected values, the public app.openapi()
document and the live journal. Types are journaled by stable module.qualname,
not pointer-bearing repr. The second endpoint response exposes all prior
request/send/exit records and current endpoint/public document records. Public
document identity is compared only against the previously returned object,
not private cache internals. The wrapper records every prior send key and exact
bytes/container shapes with no omission or normalization. The final response's
own send/exit cannot appear recursively inside its body; its status/headers/raw
body and message types remain directly selected. This bounded eight-action
shape deliberately has no extra state request claiming a later complete trace.

The public-placement input is a reusable shape, not a fixture-ID/backend
condition. No live key order or document is prescribed; no old workload was
copied or edited. The legacy structural selectors remain intact. Its historical
11 key-order differences motivate this stronger independent gate but are not
results of these unexecuted inputs.

## Source contract and evidence

FastAPI 0.141.1 is the oracle; Starlette1.6.0, pinned Python3.12.13/Pydantic2.13.4
and immutable sibling remain unchanged. Pinned source byte bindings:

- `dependencies/utils.py`: `13693375ab95e32424e5434c21f928463634af5ee1261cf3e04031381bdf47d9`
- `_compat/v2.py`: `b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9`
- `openapi/utils.py`: `81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527`
- `encoders.py`: `4cc09230eca6435892f6bc25a2185e214dbedfe994d5103feb63ad269137caad`
- `openapi/models.py`: `b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`

Dependencies utils.py:381-549 infers Query for scalar/nonpath declarations,
carries ordinary defaults and builds the field with that FieldInfo/default;
550-565 keeps declaration append order. Direct and Depends-owned parameters
both enter the flattened dependency field list (openapi/utils.py:548-583).
_compat/v2.py:141-167 reconstructs Field attributes/default before TypeAdapter,
285-336 passes core schemas to shared GenerateJsonSchema, and 254-282 retains
mapped inline schemas and assigns nonref fallback title after lookup.
Openapi/utils.py:160-235 embeds that schema in the parameter dict. The actual
OpenAPI model/jsonable_encoder at utils.py:679 and its PathItem|Any declaration
at models.py:425-427 determine final bytes; no global key-reordering assumption
or expected default/None encoding is embedded in these inputs. The tracked
legacy diagnosis gives the Pydantic default-before-title stage as source
context, not an implementation prescription or complete model/default claim.

Reviewed recipe evidence uses existing query parameters/dependencies/custom
response docs. Source tests are not copied; private _compat/model adapters and
GenerateJsonSchema are neither imported nor observed. Positive scope is plain
primitive default-bearing validation fields, None controls, dependency
flattening and public cached document behavior. Arbitrary default serializers,
nonserializable defaults, custom aliases/titles/metadata, body/header/cookie/
path fields, refs/shared input hook batches, namespaces and mutable adapter
lifetimes remain separate gates. No native patch is offered.

## Prospective API links and admission

Both cases exercise FastAPI root/canonical constructor aliases,
FastAPI.__call__, FastAPI.get, FastAPI.openapi and JSONResponse. Only the
dependency case additionally exercises root Depends and canonical
param_functions.Depends. These are candidate mapping recommendations (14
case-operation links across eight existing IDs), not active metadata edits;
constructor identity aliases should retain current reviewed policy. Factory
helpers, typing/stdlib operations, JSONResponse output inspection and private
solver implementation do not create new FastAPI candidate links.

Planned active paths are tests/fixtures/workloads/inline_query_schema_wire.py
and tests/fixtures/input-recipes/parity/inline-query-schema-wire.yaml. These
paths do not exist through this authoring step; the TMP recipe only declares
them for later admission. Whole-value YAML aliases are used without merge keys.
Canonical read_recipe/schema and AST-only admission closed successfully, as did
repository-config Ruff lint and format checks. The only formatting change was
within this TMP workload; no workload/backend import was used. Counts and
selectors were rechecked through the canonical loaded recipe. Before any claim,
require source two successful constructions/eight completed actions and
preserve unchanged-target results before designing any native correction.
Ordinary product errors stay parity outcomes. No comparator weakening,
normalizer, fault hook, API promotion or live target fallback is authorized.
