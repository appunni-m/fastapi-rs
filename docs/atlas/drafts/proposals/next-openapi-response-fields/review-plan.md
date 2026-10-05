# Next OpenAPI response-field gate: inactive input proposal

2026-10-05. Three independent ordinary parity cases / 19 HTTP actions / three
construction observations. These are candidate user inputs only. No application,
endpoint factory, native extension, builder, parity process or unit test was run.
Only this directory under /private/tmp was written. Nothing was admitted to active
inputs or mapped in metadata, and no expected outputs or comparator changes exist.
Parent's passing additional-field 203 cases remain separate prior evidence; they
do not establish the new hook/title/shared-generation observations here.

## Candidate files and static identity

- `next_openapi_response_fields.py`, intended future workload path
  `tests/fixtures/workloads/next_openapi_response_fields.py`, SHA256
  `d1c2824c616533127910a459075af4b020e6e97a8d9f260dd838d3b0ef7733bf`.
- `next-openapi-response-fields.yaml`, intended future recipe path
  `tests/fixtures/input-recipes/parity/next-openapi-response-fields.yaml`, SHA256
  `e1243762e877e182bffadeb4eed6668d852bfb4d1bc31f8c98a7cceb9f8ce132`.
- Canonical input bytes under the existing materializer's JSON serialization
  (`json.dumps(..., indent=2, ensure_ascii=False) + newline`) have SHA256
  `558a3d9cde89de0fd8342fe9a04deaef08a3caac836f5afd3a1b16d0c6829767`.
  No materialized active workflow or receipt was created.

Static checks passed: the repository's read_recipe function only (no builder
entry point), its duplicate-key loader and workflow@9 schema; Python 3.10 AST;
unique case IDs and action IDs within each case; all upstream evidence paths;
root-config Ruff lint and format check after Ruff formatting this temporary
workload. Initial E501/layout diagnostics were corrected by that formatting.
Full load_workflow/index/metadata admission is unperformed: the future active
workload path intentionally does not exist yet. Source constructor/signature
reachability and target behavior for the combined Field metadata, stable user
ref and hook-error forms await fresh live receipts. Every planned call remains
selected; unsupported construction or binding is a retained outcome, never a
backend-dependent skip or replacement path.

## Selected observations and cases

All HTTP actions select exact status, ordered headers and complete body, ordered
ASGI message types and exact application error. Successful document actions also
select the full OpenAPI document using the empty JSON pointer. The public /state
response returns complete hook order/counts, warning category/message records,
handled exception class/message/path, original propagated exceptions if any,
public document-result identity relations and lossless prior send messages. No
warning category or occurrence is filtered by the fixture.

The ASGI wrapper encodes every message key, all bytes as hex, header order and
list/tuple distinction. It omits only recording /state into the journal returned
by /state itself; each state response is still selected normally by the runner.
It does not omit or normalize more_body presence, schema key order, content-length,
body bytes or failure sends. The normal JSON comparator's mapping semantics do
not erase the independently retained body-byte trace. Warning filenames/line
numbers and tracebacks are not projected; class/category/message and occurrence
order are preserved. There are no clocks, addresses, thread IDs or race outcomes.

| Case ID suffix | Actions | Public stimulus and diagnostic boundary |
| --- | --- | --- |
| annotated-metadata-outer-titles-retained-hooks | 5 | State; docs first; state; docs cached; state. One primitive primary and four ordered extras use distinct public metadata hooks. Extras carry ordinary inner Field title/alias/serialization_alias variants, including empty strings. Actual schema/hook/warning journals expose annotation processing and the generated OUTER response-field title overwrite; these inputs do not set outer title or aliases. |
| shared-primitive-definition | 5 | Same action order. One annotation with a stable user-defined primitive core-schema ref is used as primary and at statuses 409 then 202. The document and callback journal expose shared definitions/ref mapping and repeated-field generation without nested-model field discovery. |
| late-json-hook-error-public-retry-cache | 9 | State; docs refusal; state; public app.openapi retry via /document; state; public cached call; state; cached docs; state. A later extra hook rejects once after setup. Prior-hook work, all warnings, original error handler outcome, whole-document retry and cached public-object identity are retained. |

Exact totals: 11 /state, six /openapi.json and two /document actions; all 19 are
HTTP, all three cases are parity, with no fault point or target-only contract.
Every case creates an independent app and journal. The user refusal is ordinary
JSON-schema metadata behavior, armed only after all successful route attachment.
It is neither an internal injection nor a constructor expected-output fixture.

The /state and /document helpers use response_model=None and
include_in_schema=False. Only /probe contributes fields. /document invokes the
public app.openapi() method and returns the actual document in JSONResponse;
it compares only the identity of two public results, never reads a private cache.
No /probe request is required: endpoint dispatch/value validation is already a
separate gate. All helper endpoints are async, avoiding the known sibling
BackgroundTasks ownership gap.

## Exact pinned source basis

FastAPI 0.141.1 commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`;
Starlette 1.6.0 commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` is the sole
oracle. Pydantic 2.13.4 / pydantic-core 2.46.4 source commit
`cf67d4b3193c3fe43ede18612ed62785eee11382`; CPython 3.12.13.
The immutable sibling remains b4c8a65; no sibling/cache source was changed.

1. routing.py1038-1054 creates truthy extra serialization fields in response
   insertion order before dependency/body1056-1074 and primary1103-1114. This is
   registration-time core construction, not JSON generation. The prototype
   lifecycle3 already observes that order; these new cases retain it in state.
2. openapi/utils.py551-580 collects primary before extras for each eligible route,
   then stream fields; it concatenates body/response/request groups. It is a
   different order from field construction. All fields in this gate are response
   fields of one direct eligible route, so that sequence is deterministic.
3. v2.py285-345 creates one GenerateJsonSchema for the collected field sequence,
   consuming each retained adapter.core_schema. It can separately construct
   flattened model fields. These primitive annotations produce no BaseModel/Enum
   flattening, so no claim of zero core callbacks for general OpenAPI is implied.
4. Pydantic json_schema.py352-399 makes two passes over input schemas through
   generate_inner. Nonref annotation JSON hooks can run again in the second pass;
   the gate records all occurrences instead of fixing a one-call assumption.
   generate_inner450-482 short-circuits an already generated CoreRef/mode, sharing
   its definition. The same user primitive ref across three independent fields
   exercises that normal batch-level behavior. core_schema.py644-698 documents
   int_schema(ref=...) as a public unique reference identifier. The fixture does
   not inspect ModelField, TypeAdapter internals or generator maps.
5. utils.py71 creates an OUTER FieldInfo(annotation=type_, default=default,
   alias=alias), where these response-field callers supply no alias or title.
   Pydantic fields.py239/254-259 takes those outer kwargs; an Annotated Field
   nested inside type_ does not populate the outer response field's attributes.
   v2.py155-166 retains that outer object while constructing its adapter. Thus
   these inputs select generated outer name titles and the interaction with
   inner annotation metadata, not the explicit outer-title/alias branches.
   get_schema_from_model_field254-282 overwrites every non-$ref schema title from
   outer metadata/name after shared generation. Its raw alias121-124 is None-only;
   serialization_alias133-135 and explicit title use truthiness. Those non-None,
   truthy and empty OUTER aliases/titles remain unproved and are unreachable via
   this ordinary response_model/responses.model shape. They are not made reachable
   by private ModelField/FieldInfo access or mutation in this fixture.
6. applications.py1084-1103 assigns the document/cache version only after a
   successful get_openapi call. Its docs route1108-1120 uses that public method (the call is at line 1110).
   A user JSON-hook error must preserve unsuccessful generation work and permit
   a later normal request to generate again. Success then reuses the public result.
   The handler registered through exception_handler receives the actual user
   subclass; it returns its own ordinary 409 JSONResponse and header. Handler
   class/message/path and raw send details remain exact.
7. openapi/utils.py476-516 merges additional response schema and metadata after
   shared generation; 594-669 generates the document and sorts component names
   at lines 668-669; line 679 performs final model validation/encoding.
   Whole documents are retained, including all paths/components/ref targets.
   A matching schema pointer alone cannot establish the callback contract.

| Pinned source file | SHA256 |
| --- | --- |
| FastAPI routing.py | 7b1ef65fb6b209445dc43be070a23324b7879aef9c6b9f63e6968234b7723b55 |
| FastAPI _compat/v2.py | b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9 |
| FastAPI openapi/utils.py | 81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527 |
| FastAPI applications.py | 38dccb19b2a0b0b984c8d7541263842954a37c087cf96b4463aea17873c6183c |
| FastAPI utils.py | 0d7d15ae73307d5b19c51cfc222b50e36736fbef9f0f398566479131947650ca |
| Pydantic fields.py | 6bc66125f23c143e934030fbf9c58c9b5657950bdad3031d4f6132e55bd57be3 |
| Pydantic json_schema.py | 75ade143dbd03cb1213ecac39d49628df4357ee0825621959d4cceac064b803b |
| Pydantic annotated_handlers.py | 59fc854aac28108157061ed3ef73f270a9682350e25f8e465a2d3e24eb024786 |
| Pydantic core_schema.py | d4f337d727ff906a66fc7ec62e734546420f01018f2fdce1eab7f64b1a215718 |

These are source contracts and candidate reachability analysis, not live oracle
outcomes. No upstream input or expectation was copied.

## Prospective admission and review gates

Map the reviewed ordinary public operations through existing overlays only:
FastAPI constructor/get with response_model/responses/operation_id and schema
exclusion; FastAPI.openapi; FastAPI.exception_handler; injected Request.url;
JSONResponse construction/call and ASGI docs dispatch. Constructor/action outcomes,
response headers/body, full document, warnings/errors and raw-send state should
remain joined to the same 19 actions. Internal ModelField/DefaultPlaceholder and
Pydantic generator internals remain internal; public Pydantic hook protocols are
fixture dependencies, not newly promoted FastAPI exports. Handler mapping requires
the included handling-errors.md evidence. Source classification is not support.

Before activation: independent source/input review, full metadata mapping and
normal admission through the existing recipe/index/atlas/facade contracts. Then
run fresh pinned oracle and unchanged-current target against the identical
materialized digest and fixed source/binary snapshots, retaining all mismatches.
Only after those pre receipts close should an implementation be considered.
All 203 existing cases and existing OpenAPI selected-output controls remain gates;
no normalizations, selectors or earlier inputs should be weakened for these cases.

A bounded later implementation should snapshot retained primary and extra owners,
use their core schemas in a shared generator batch, retain keyed field-schema
mappings, and apply source field title metadata during operation assembly. It
must preserve generator two-pass hooks/errors and app cache publication timing,
with callbacks and retired-reference destruction outside app/cache borrows.
This is a design direction, not an authored Rust patch or all-fields proposal.

## Deliberately unresolved boundaries

This three-case gate covers direct immutable primitive serialization fields,
generated outer titles despite inner annotation metadata, and one repeated scalar
ref. Nondefault OUTER FieldInfo title/serialization_alias/alias (including empty
alias) branches are not positively selected. No public response-model keyword in
this shape provides those outer attributes; the inner Field variants must not be
reported as equivalent coverage. It does not establish nested BaseModel/Enum flattening,
recursive or generic models, definition-name collisions, multiple input/output
modes or separate_input_output_schemas=False, request/body/stream fields, included
route traversal, callbacks/webhooks, custom generators, mutable annotation/map
history, route-version refresh, reentry/concurrent OpenAPI, custom mapping/status
keys or broader response metadata merge policy. Cache failure is one ordinary
user JSON hook, not schema validation/encoding/finalizer or recursive cache errors.
No broad support or performance claim follows from this unexecuted proposal.

## Independent review correction before freeze

Root/native source review corrected the first draft's outer-attribute claim using
utils.py71, fields.py239/254-259 and v2.py155-166. Only the first case ID and this
plan's scope/evidence were corrected; models, Field metadata, hooks, all 19 actions,
selectors, raw byte journals and workload bytes are unchanged. The original
recipe 5e55ea92 / canonical 82f9fa38 / plan 2ae0e2c5 identities are superseded by the
current hashes above. The remaining alias/property implementation review remains
source analysis, not positive evidence from these three user workflows.
