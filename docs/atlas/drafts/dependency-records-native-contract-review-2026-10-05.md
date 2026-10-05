# Native dependency records — reviewed contract

This slice preserves the returned objects of the public `fastapi.Depends` and
`fastapi.Security` factories at FastAPI 0.141.1. The atlas continues to classify
the exact `fastapi.params.Depends` and `fastapi.params.Security` import paths as
private/internal. Their classification does not remove the observable factory
return contract or promote the classes into the public denominator.

## Source rules

- `fastapi/params.py:745-754` defines frozen dataclasses. `Security` inherits
  `Depends`; class construction stores arbitrary object values without
  annotation validation. The class constructors accept positional fields in
  dependency/use_cache/scope/scopes order.
- `fastapi/param_functions.py:2283-2460` defines separate factories with
  keyword-only options. Root exports and `param_functions` share factory
  identities; factory and record class identities are distinct.
- CPython 3.12.13 `dataclasses.py` supplies the observable protocol: field
  metadata, repr, same-runtime-class equality, tuple hashing, shallow freezing,
  dictionaries, inherited subclass behavior, `fields`, `asdict`, and `replace`.
- `fastapi/dependencies/utils.py:130-145` validates parameterless dependency
  callability and omits `use_cache` when building those edges. The record still
  stores its supplied value; the edge uses the default cache policy.
- `fastapi/dependencies/models.py:82-115` includes sorted distinct effective
  OAuth scopes in cache identity when own scopes, a security scheme, or a
  scope-using descendant makes them relevant. Ordinary dependencies ignore
  irrelevant inherited scopes. Overrides retain the original outer edge's
  cache identity while rebuilding their callable plans.
- `fastapi/dependencies/utils.py:405-471` chooses the final recognized FastAPI
  annotation, rejects conflicting default declarations, and copies/replaces
  an inferred dependency without mutating the caller's original frozen record.

## Native design and evidence boundary

Rust creates heap classes and native descriptors. Python runtime modules only
re-export those classes and factories. Standard-library field/introspection
objects are used as values; `dataclasses.dataclass` does not generate target
Python methods. Runtime readers identify records by class identity, keep raw
constructor values, and evaluate cache/scopes at dependency analysis time.

The input recipe `dependency-record-public-protocol.yaml` projects public
operations through identical ASGI workloads. It contains stimuli and exact
selectors, with no stored expected results. The cleanup fault remains
target-only and cannot count as an oracle parity pass. Existing dependency,
security, override, lifecycle, and signature workflows are regression inputs.

Native descriptor objects differ from source Python function objects in
`FunctionType`, code/globals/closure introspection, repr `__wrapped__`, and
mutable function-default protocols. Factory objects retain their existing
`functools.partial` representation. Native descriptor `__signature__` does not
change when `__annotations__` is mutated. Those differences remain gaps.
Arbitrary constructor values do not
prove arbitrary nonstring scope/scopes execution. Broader FieldInfo parameter
classes, SecurityScopes injection, custom callable hash/equality, dynamic
wrapper changes, and unexercised dependency graphs remain incomplete. Execution claims
belong in fresh identity-checked result artifacts, not this contract review.

The runtime currently snapshots `use_cache` truthiness during route analysis.
Source `dependencies/utils.py:640-680` stores the raw policy and evaluates it
after child solving and input validation on each successful request edge.
Mutable policies and side-effectful or failing `__bool__` remain a separate
execution gap; constructor raw-value observations and ordinary boolean cache
inputs do not prove those behaviors. Parameterless lists skip the supplied
policy in both implementations.

## Broader regression follow-up

The first broader run selected 137 parity cases across 36 workflows: 130
passed and seven failed. Those failures identified three existing gaps:
`Path(default=...)` binding, `add_api_route(methods=...)` registration, and
duplicate query parameters in generated OpenAPI. Preserve that failed run as
evidence and rerun the same inputs after the bounded repairs.

`Path` now accepts the raw positional-or-keyword Ellipsis default and checks
its identity before warnings or marker construction, matching
`fastapi/params.py:185`. Its native factory still has 10 parameters compared
with the source factory's 29, and it is not a FieldInfo-derived class.
OpenAPI parameter projection follows `fastapi/openapi/utils.py:364-376`:
deduplicate by `(in, name)`, retain the first key position, use the last value,
then give the last required value priority without changing its schema.
The existing construction and required-parameter workflows retain their exact
selectors. Direct route-registration methods remain private/internal in the
reviewed atlas; native registration fixes do not promote them into the public
manifest or establish full multi-method route-object parity.

The callable workflow also exposed blockers after registration: source
`fastapi/dependencies/utils.py:392-394` unpacks a TypeAliasType once before
selecting Annotated metadata. Native analysis now follows that rule for the
pinned standard-library and typing_extensions alias classes. Async callable
instances retain their original callable object and use the existing
coroutine scheduling path, including dependency overrides; yielded instances
continue through the generator cleanup path. The unchanged callable workflow
covers ordinary instances, bound methods, functions, partial functions,
wrapped functions, a dependency-bearing alias, and string annotations.
Complex wrapped/partial callable-instance classification and mutable callable
classification caches remain unverified. Native direct registration uses one
route row per normalized method, so grouped route introspection, shared
generated operation IDs, and analysis side-effect counts remain gaps.
