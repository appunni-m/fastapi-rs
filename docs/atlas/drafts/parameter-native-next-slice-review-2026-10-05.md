# Next parameter class slice — 2026-10-05

Implement distinct `params.Depends`/`params.Security` classes first, then `ParamTypes`, `Param(FieldInfo)`, and `Query(Param)`. Native class identity and displayed signatures each establish only their observed contract; neither proves full replacement.

Source pins: `../fastapi` HEAD/exact tag are `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` / `0.141.1`. Pydantic HEAD is `cf67d4b3193c3fe43ede18612ed62785eee11382` (`2.13.4`). Reviewed profile is CPython `3.12.13`, Pydantic `2.13.4`, pydantic-core `2.46.4`. Applied `AGENTS.md` and the Rust development skill.

## Current gap

- `parameters.rs:25-202` defines getter-only `_ParameterMetadata`; all nine factories return it. Both dependency factories set `kind="depends"`. No consumer extracts the Rust type; consumers read dynamic attributes.
- `fastapi-rs-py/python/fastapi/params.py` exports the same functions as `param_functions.py`, omitting Param, ParamTypes, and Security. Upstream params exposes classes; root and param_functions expose factories. Preserve root-to-factory identity while separating classes from factories.
- `parameters.rs::register` attaches exact reflection metadata to partial-wrapped Depends/Security callables. Their return type remains wrong. Other factories omit keywords/annotations.
- `metadata.yaml:4046-4408` records partial factories and unimplemented field constructors. Its historical counts are not fresh results for current body/path signatures. Root corrected the reviewed File/Form gap strings to `File -> Form -> Body -> FieldInfo` and `Form -> Body -> FieldInfo` during this review.

## Smallest useful slice: Depends and Security

Source: `../fastapi/fastapi/params.py:745-754`, `param_functions.py:2283-2460`; class reflection already exists in `tests/fixtures/runtime-api-surface.json`.

| Object | Exact parameter order/defaults; annotations abbreviated |
|---|---|
| `params.Depends` | `(dependency: Callable[..., Any] \| None = None, use_cache: bool = True, scope: Literal['function', 'request'] \| None = None) -> None` |
| `params.Security` | `(dependency=None, use_cache=True, scope=None, scopes: Sequence[str] \| None = None) -> None` |
| root / `param_functions.Depends` | `(dependency=None, *, use_cache=True, scope=None) -> Any` |
| root / `param_functions.Security` | `(dependency=None, *, scopes=None, use_cache=True) -> Any` |

All class fields are positional-or-keyword. Security inherits Depends and accepts scope in its class constructor, although its factory has no scope option. Class initializers include self and a None return annotation; factory annotations carry Doc metadata. Classes are frozen dataclasses with type-sensitive equality, repr, tuple-based hash, dataclass fields, and match arguments. Freezing is shallow: scopes lists stay mutable and unhashable. Constructors store values without checking annotations. Upstream dependency inference uses `dataclasses.replace` (`dependencies/utils.py:467-471`).

Prefer `type`-created heap classes with native descriptors for initialization, repr/equality/hash, and frozen writes/deletes. Initialize Python object-valued fields through `object.__setattr__`; ordinary instance dictionaries preserve the source's explicit bypass. Native frozen behavior must reject every write on the defining class and inherited declared-field writes on subclasses; see pinned CPython `dataclasses.py::_frozen_get_del_attr`. Native equality accepts only the same runtime class; tuple hashing must preserve unhashable-field errors. Construct annotations, match arguments, and introspection Field records from Rust. Keep dataclass protocol gaps until fields/asdict/replace operate correctly through native initialization.

A native `#[pyclass(subclass)]` Depends plus Security inheritance is possible, but PyO3 frozen controls Rust borrowing. Getter-only native storage does not reproduce source dictionaries, subclass frozen rules, or `object.__setattr__`. Do not use `dataclasses.dataclass` to generate Python methods: observable FastAPI record control flow belongs in Rust. Standard-library value/introspection calls remain distinct from generating those methods.

Export classes under separate native binding names, directly re-export them as params.Depends/Security, and keep factory exports separate. Update CallablePlan::build and parameter_source to recognize actual classes. Read scopes only from Security. Filter dependency records out of constrained_parameter_annotation: removing kind currently makes it pass a new dependency record to Pydantic as annotation metadata.

## First FieldInfo family: Param and Query

Source: `params.py:19-134,221-300`; Query factory `param_functions.py:357-698`. Query factory has 29 parameters including extra and returns Any. Query.__init__ has 31 including self, class-only annotation, and extra; its return annotation is empty. Other factory counts: Path 29, Header 30, Cookie 29, Body 31, Form/File 30. Header inserts convert_underscores after serialization_alias; the earlier request/auth draft's insertion prose is inaccurate.

Yes: Rust can create `Param` with `builtins.type(name, (FieldInfo,), namespace)`, then Query over Param, using the actual pinned `pydantic.fields.FieldInfo`. This needs no target-authored Python helper. These are Python heap classes assembled by native logic, not PyO3 structs inheriting Python classes. Set real module/name, Param.in_ annotation, Query.in_=ParamTypes.query enum value, normal instance dictionaries, and mutable inherited slots. types.new_class is also possible; type suffices for these plain bases.

PyO3 0.29.2 explicitly excludes arbitrary Python bases from pyclass extends (`guide/src/class.md:410-415`); builtin inheritance also has limited-API restrictions (`:525-526`), relevant to abi3-py310. Safe dynamic API calls avoid object layout assumptions and unsafe code.

Install native initializer/repr descriptors. Existing patterns: `security.rs::ConstructorInit` (:966-1008) binds through types.MethodType; `attach_constructor_introspection` (:1828-1875); dynamic classes in datastructures.rs::register and errors.rs::register. The security argument binder needs adaptation for extra. A signature alone does not bind calls or reproduce duplicate/positional argument errors. Repr uses runtime subclass name and str(default).

Native Param initialization must perform source warning conditions, alias fallbacks, pattern-or-regex, schema-extra-or-extra, and exact _Unset filtering before `FieldInfo.__init__(self, **kwargs)`. Pydantic owns slot initialization, constraint metadata, default/default-factory conflict, and inherited methods. FieldInfo stores gt/pattern/etc in metadata, not direct attributes; preserve it through Pydantic instead of the current whitelist reconstruction.

Upstream _Unset is `DefaultPlaceholder(None)` (`datastructures.py:153-186`); current _ParameterUnset is different. Refactor/reuse existing PyFastApiDefaultPlaceholder in application_runtime.rs and initialize it before signatures. Query omission is PydanticUndefined; explicit None is a real default. Path accepts Ellipsis and rejects other defaults. Exact factory annotations require source-derived reviewed data and correct referenced identities.

## All current marker consumers

Direct readers are in application_runtime.rs; symbols are stable anchors while concurrent changes move lines.

| Consumer | Required adaptation |
|---|---|
| CallablePlan::build | Recognize endpoint-default markers and Annotated metadata, currently gated by kind. |
| CallablePlan::prepend_dependencies | App/router/route parameterless dependency lists share parameter_source. |
| marker_default | Replace default_is_set/None fallback with undefined identity; account for factory requiredness. |
| parameter_source | Dependencies/cache/scope/security and all field locations/aliases/header conversion. |
| parameter_media_type; parameter_body_embed | Body/Form/File media types and embed. |
| parameter_description; parameter_title; parameter_deprecated; parameter_include_in_schema | Selected schema projections, largely Query today. |
| constrained_parameter_annotation | Separate dependencies, new FieldInfo, legacy markers, and other metadata; preserve constraints once. |
| header_model_convert_underscores | Header model flag currently keyed by kind. |

Indirect consumers include parameter_model_fields and copied_pydantic_field_default; HTTP, WebSocket, dependencies, and OpenAPI consume their CallableParameter plans. No additional direct reader was found in security.rs, openapi.rs, or the binding crate. Use one Rust classification/view helper during coexistence; adding kind to FieldInfo leaves readers asking for nonexistent gt/pattern attributes.

## Missing evidence and implementation order

Existing exact inputs: parameter-factory-signatures.yaml (eight factories), parameter-class-constructor-signatures.yaml (seven field initializers), and separate Depends/Security signature recipes. Root alias receipts observe root-to-param_functions identity, not factory return classes. Request/annotation/model/tutorial receipts cover selected HTTP/OpenAPI behavior rather than class protocols.

Add input-only recipes before claims:

- Depends/Security imports, subclass/return identity, class/initializer signatures, positional binding, arbitrary values, repr/equality/hash, frozen writes/deletes, mutable scopes, and fields/asdict/replace if claimed. Exercise default/Annotated/inferred/parameterless dependencies, caching, scope cleanup, and OAuth scope projection.
- Param/Query MRO/enum identity, factory/class distinction, undefined/None/Ellipsis, aliases/priority, constraints metadata, warnings, examples/schema extras, inherited methods, mutation/copy/subclass construction, and shared marker reuse. Pydantic preserves/copies FieldInfo subclasses (`fields.py:438-446,816-831`).
- Query constructor/binding failures and missing/valid/invalid request values plus schemas. Default factories need per-request handling: current CallableParameter.default is captured during route analysis. Constructor support does not prove invocation timing, copied mutable defaults, multiple-marker precedence, or all route options.

The direct API worker projects signatures/JSON/call outcomes/BaseModels, not arbitrary marker or FieldInfo results (`scripts/parity/api_worker.py:314-340,587-603`). Use identical ASGI workloads projecting public behavior to JSON receipts, or first review a dedicated observation schema. Do not normalize unknown objects into strings or put expected outputs into recipes.

Order: reviewed overlays/inputs; dependency classes and reader adaptation; isolated parity and existing regressions; sentinel/descriptor foundation; Param/Query plus routing; exact factory annotations and binding; Path/Header/Cookie, then Body/Form/File. Future changes require metadata/facade/static checks, make fmt clippy, parity-inputs/index-update/validate, identity-checked parity, and atlas update as applicable. Keep unexercised contracts partial.
