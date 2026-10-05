# Prospective private OpenAPI final-model graph

Date: 2026-10-05. TMP-only author review; no Rust build, formatting, native import,
workload execution, parity run or active source edit.

## Purpose and source boundary

The closed first post-change whole matrix is 205 passed / 1 failed / 0 skipped.
The failing first-ASGI OpenAPI action has equal parsed documents and different raw
bytes. A field-order finalizer cannot decide the pinned Pydantic smart union:
`OpenAPI.paths` contains `PathItem | Any`, and string-to-`ParameterInType` enum
conversion can lower the path model's exactness below `Any`. That choice retains
the complete raw path object, including its nested insertion order. This proposal
delegates that decision to the pinned Pydantic graph instead of inferring it from
an input dictionary or route shape.

Pinned `fastapi/openapi/models.py` SHA256:
`b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`.
The definition data covers this complete file, including source model bases,
nullable/required defaults, aliases, union order, literals, enum members, URL
types, constraints, and the total=False Example TypedDict. `get_openapi` ends
with `jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)` at
`fastapi/openapi/utils.py:679`; this is the finalization boundary reproduced.

## Files and interfaces

The author owns only the new prospective `openapi_models.rs`. The separately
authored companions provide:

- `crate::openapi_model_schema::schema_fields(py) -> PyResult<Py<PyDict>>`, with
  the 61 ordered Schema field definitions, recursive annotations, constraints,
  aliases and deprecated metadata.
- `crate::openapi_model_email::email_type(py) -> PyResult<Py<PyAny>>`, selecting
  the pinned optional EmailStr implementation/fallback.

Main registration is
`register(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()>`.
The integration author declares all three modules privately and calls this main
registration once before application/OpenAPI registration and user factories.
Only `_FastApiOpenApiModel` is published on `fastapi_rs._core`, after all models
have rebuilt successfully. There is no new Python facade export or public model
API support claim.

Finalization is
`finalize_document<'py>(py: Python<'py>, document: &Bound<'py, PyDict>) ->
PyResult<Bound<'py, PyAny>>`. It calls the retained root model with the complete
dictionary as keyword arguments. The integration author then uses the existing
Rust encoder with the same source alias/exclusion options. The graph has no
original FastAPI runtime import, Python source evaluator, generated helper
function, case identity branch or serialization-order heuristic.

## Definition and construction audit

The source AST emits only Rust annotation data, not executable Python source or
copied source tests. `generate-model-descriptors.py` parses the source text without
importing it. `audit-model-descriptors.py` separately checks the emitted table,
source facts, descriptor order, bases, defaults, aliases, enum members, aliases,
fixed forward names and registration publication point.

The checked table contains 43 source-order graph definitions:

- 35 main-owned BaseModel classes plus the companion Schema class;
- 139 main-owned declared fields: 135 model fields and 4 Example keys;
- 61 companion Schema fields, giving all 200 source declared fields;
- 3 ordered Enum classes, 3 type aliases and 1 total=False TypedDict.

Source PEP 604 unions use public `operator.or_` with source order; the explicit
`typing.Union["Header", Reference]` uses `typing.Union`. Builtin generic aliases
use public `list`/`dict.__class_getitem__`; Literal and Annotated use their public
subscription APIs. Fixed type-name ForwardRefs carry annotation data only.
`ServerVariable.enum` retains its Annotated `Field(min_length=1)` metadata.
Required ordinary fields have annotation-only create_model arguments; required
aliases receive `Field(alias=...)` without a default. None defaults, literal
`{}` scopes defaults, bearer text and actual enum-member defaults remain distinct.

`BaseModelWithConfig` uses Pydantic's default BaseModel with `extra='allow'`.
Every other model uses its exact source base; Reference and Discriminator use
plain BaseModel. Example is a functional `typing_extensions.TypedDict` with
`total=False`, its source module label, and `__pydantic_config__={'extra':'allow'}`.
Every model and enum carries the source `fastapi.openapi.models` module label and
source class name. These labels support internal validation/error semantics;
public class identity, introspection, pickle/import bindings and mutable class
history remain separate.

Pydantic 2.13.4 `main.py:1735–1836` defines the public dynamic-model interface.
Its `model_rebuild` at 633–702 accepts `_types_namespace` and skips already
complete models by default. The Rust builder supplies the complete namespace and
rebuilds all models once before exposing the root. This accounts for dynamic
construction without a source module's Python globals; it does not force rebuild
already complete schemas on each request.

## Assembly and ownership conditions

One preexisting assembly correction is required in the integration draft:
`openapi/utils.py:140–146` encodes each security scheme model using alias and
exclude_none before inserting its definition. Native assembly currently inserts
unrelated native BaseModel instances. The integration author must apply that
existing Rust encoder at the same boundary, rather than broaden the graph's
model union or reuse incomplete unrelated same-named classes. The main graph's
canonical security types/enums remain source-shaped.

All registration dictionaries, classes, metadata, namespace entries and rebuild
results are owned Python references with normal PyO3 lifetimes. No Rust static
holds interpreter-owned values; no unsafe code, locks, RefCell guards or
application/cache borrows exist in this module. Failed construction or rebuilding
propagates its PyErr, and temporary references retire outside app/cache borrows.
Only root publication is atomic; this does not claim to undo Pydantic's internal
allocations or caches after a failed native module import.

At document finalization, the integration caller must already own the assembled
snapshot and release app/cache borrows before invoking Pydantic or the encoder.
That permits user-data validators/serializers and Python destruction without
introducing a borrowed application state callback boundary. Native module
registration completes the graph before concurrent requests can use it.

## Required review and live gates

This prospective main file is uncompiled and unexecuted. Independent review must
bind the frozen main/Schema/email/integration files and check all annotations,
constraints, union order, email fallback source behavior, namespace rebuild and
Rust lifetimes. Root owns combined applicability, formatting, strict Clippy,
native build, fresh whole 206 normal cases, raw document equality, selected
coverage/fault evidence and exact normal restoration. Keep the failed first
whole run and its source/target identities intact.

The first-ASGI raw document regression and the new three exact-schema/hook/cache
cases are required gates. Existing security workflows are required regression
gates for the encoded-definition insertion. No graph completeness inventory or
static descriptor equality substitutes for those observed outcomes.

## Remaining scope

The private graph does not establish a public `fastapi.openapi.models` export
surface. Existing route assembly, request/primary/shared-schema generation,
normalizers, cached application snapshots and direct `get_openapi` signature
subsets remain their own boundaries. The current three inputs do not establish
all enum/URL/numeric/invalid-model branches, arbitrary mappings, recursion,
mutable model history or thread/reentrancy behavior. Schema/email companions
need their own source review; the pinned environment's optional dependency branch
and fallback errors/warnings need independent fixture evidence.

Automatic 422, explicit default/4XX suppression and response-status ordering
remain a separate inactive input gate. Direct public late externalDocs validation
location/ordering is a separate source-backed regression boundary; applying this
root must not retain a second late TypeAdapter conversion after root validation.
No comparator normalization, schema selector reduction, expected-output
substitution or backend-detecting input is proposed.
