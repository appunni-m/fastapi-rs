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
