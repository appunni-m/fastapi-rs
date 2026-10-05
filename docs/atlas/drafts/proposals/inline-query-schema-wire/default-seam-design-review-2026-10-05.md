# Inline parameter schema: focused default ownership seam

2026-10-05. Source/Rust-text review only; no product imports, native binary reads,
application execution, builds, executable patch or fixture changes. This refines
`/private/tmp/fastapi-rs-inline-query-schema-native-risk-review-2026-10-05.md`.
The source-first two-case gate and unchanged-target PRE must close before any
implementation is authorized. Static design is not expanded support evidence.

## Current flow and source contract

- `CallableParameter` owns its constrained annotation, request adapter and raw
  optional default separately (`application_runtime.rs:208,5999-6048`).
  `None` in Rust means no captured ordinary default; `Some(PyNone)` is distinct.
  `clone_ref` preserves Python object identity through the route snapshot.
- `ParameterOpenApiPlan` (`1653,6411-6477`) currently drops actual Python None
  from ordinary defaults. `openapi_operation` (`4099-4148`) builds an annotation
  TypeAdapter in validation mode and passes title separately. The completed
  `OpenApiParameter` still carries a second, raw default owner.
- `openapi.rs:233-248` normalizes that schema with defaults removed, ranks its
  keys, then inserts the raw default. That late owner can also reinsert a value
  which Pydantic intentionally omitted or encoded differently.
- Source `dependencies/utils.py:492-545` constructs the input FieldInfo with the
  ordinary default. `_compat/v2.py:141-167` rebuilds its attributes in a public
  Pydantic Field and constructs the validation TypeAdapter. Pydantic
  `json_schema.py:1173-1243` generates the inner schema before encoding/inserting
  its static default; `get_default_value:1245-1260` does not call a factory.
  Source `_compat/v2.py:265-282` applies the outer nonref title after generation.
  Source `openapi/utils.py:159-234` inserts the mapped schema without a new raw
  default or inline key ranking. Final OpenAPI model/encoder behavior remains
  the authority for removal of None and wire serialization.

## Smallest proposed generic change

1. Record default delivery provenance when native annotation construction is
   performed: no external default, captured static default still external, or
   default already embedded by the native Field reconstruction. A small Rust
   enum/flag is preferable to inspecting completed schema keys, guessing from
   primitive types or walking arbitrary user annotations during OpenAPI.
2. Preserve every external static default as an owned Py value, including
   Python None. At the owned OpenAPI operation boundary, attach it with public
   a public Pydantic Field carrying the raw static default and its known outer
   default-delivery attributes, then `typing.Annotated.__class_getitem__` before
   the existing validation-mode generator. An annotation already completed
   with the same native default passes through. Constraints/config/metadata
   and public Pydantic merge errors remain intact; no Rust serialization or
   truthiness conversion of a default is introduced.
3. Let the generated schema exclusively own its encoded default. Remove
   `OpenApiParameter.default` and the late wire insertion; one current native
   constructor supplies this struct (`application_runtime.rs:4139`). Preserve
   Pydantic omissions/warnings/errors instead of adding a fallback default.
4. For parameter inline schemas, embed the generated dictionary directly, or
   use an insertion-preserving shallow copy which removes only the transported
   `$defs` wrapper after definition collection. Do not pass it through the
   recursive ranking/default-stripping visitor. Keep existing nonparameter
   paths and final private OpenAPI model plus Rust encoder unchanged.
5. Keep fallback title outside the early default Field. For ordinary selected
   names, it is applied after default generation. Source nonref title assignment
   overwrites an inner title using actual outer FieldInfo title/alias; current
   captured-string/missing-only title logic has broader provenance limits.
   A parameter-only helper may follow that source assignment using captured
   values, but must not change the shared response/body helper or claim exact
   arbitrary alias/title property timing without a separate public gate.

This retains request validation adapters, worker scheduling and runtime default
behavior. A retained source-equivalent input ModelField and shared whole-input
JSON batch are larger lifetime/order changes, not this minimum correction.

## Existing FieldInfo/default_factory boundary

- `constrained_parameter_annotation:7945-8013` may already add
  `Field(default=...)` for Query. Capture that fact from its native construction
  flow; do not blindly append a second field on this path. Retained unrelated
  user metadata is not an excuse to skip an ordinary external default: public
  Pydantic must still perform source-backed merging/error handling.
- Flattened model fields use `FieldInfo.asdict()` then reconstruct all
  attributes/metadata (`pydantic_field_schema_annotation:8788-8822`). Their
  annotation already owns static default, explicit None or default_factory.
  Mark this input complete and preserve those attributes. Do not call
  `get_default`, evaluate a factory or append an external default for it.
  `query_model_field_openapi_default:8868-8888` becomes redundant once its raw
  late-wire owner is removed; required status remains separately obtained from
  `FieldInfo.is_required`.
- Source `_compat/v2.py:100-110` explicitly carries outer
  `default_factory=None` into fresh Field for ordinary implicit parameters.
  Pydantic `fields.py:234-236,548-570` distinguishes omitted attributes from
  explicit None during merging. `Field(default=raw)` alone can accidentally
  retain an inner factory and introduce a conflict (`249-252`); source outer
  factory=None resets that inherited attribute. Carry this known delivery
  attribute instead of guessing from a finished schema. A complete flattened
  field retains its actual factory; do not clear it. Existing constrained
  construction did not capture every source outer attribute, so reuse does not
  prove arbitrary Annotated/factory merge fidelity. Do not catch such errors
  with a fallback, manually call a factory or advertise new factory support.
- Existing ordinary factory/required inference and full FastAPI FieldInfo
  reconstruction are not repaired merely by this seam. Flattened reconstruction
  already differs in attribute/metadata evaluation timing: it invokes Field
  before expanding metadata, while the source expands metadata first. Keep
  this callback-history limitation explicit rather than treating reuse as proof.

## Subscription, lifetime and risks

Commit `2135bee7c6fa558eccb98384acc517c113cd6338` replaced an explicit nonexistent
`Annotated.__getitem__` lookup with `__class_getitem__`. The new helper should
call that public method with one tuple argument containing annotation and
Field. Construct the inner tuple fallibly, then pass it as a single positional
argument; do not copy the body helper's generic `get_item` spelling blindly or
unpack the tuple into two method arguments. Existing body behavior is outside
this proposal.

`PyFastApi::openapi_document:4050-4057` already snapshots route/default owners
before callbacks. Put Field/Annotated/TypeAdapter/generator work after that
borrow ends. Carry owned `Py<PyAny>` through plans and use temporary Bound values
only within the Python scope; clone references, not default values. Fallible
constructors/PyResult propagation are required. Publish only the completed
OpenAPI document; failed schema owners and replaced references drop outside
app/cache borrows (`openapi:3233-3263`). No new lock or user callback under a
borrow is needed. Existing reentrant cache/version history remains separate.

Removing parameter normalization affects refs, nullable containers, constrained
numbers, bytes and inline model schemas, beyond the two plain signatures.
The existing bytes generator/component reference template already owns those
source rules, but prior 214 normal regressions must still gate the change.
Definition collection still has its existing normalization/default/collision
policy; this proposal does not prove a shared model-definition repair. Do not
widen those paths or reintroduce ordering visitors when a regression exposes a
separate gap. Another documentation-time TypeAdapter remains different from
source retained registration adapters, with warning/core-hook/default encoding
history unproved outside selected inputs. Preserve error/warning observations;
no unsupported bypass, fixture/backend/class-name dispatch or expected fields.

## Frozen text bindings

- application_runtime.rs: `0cd89081d79ca2d59b94e01839eb5e5e30778f18683c86822919a054e03bca11`.
- openapi.rs: `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d`.
- Pydantic fields.py: `6bc66125f23c143e934030fbf9c58c9b5657950bdad3031d4f6132e55bd57be3`.
- Pydantic json_schema.py: `75ade143dbd03cb1213ecac39d49628df4357ee0825621959d4cceac064b803b`.
- FastAPI _compat/v2.py: `b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9`.
