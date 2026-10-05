# Prospective private OpenAPI Schema and EmailStr companions

Date: 2026-10-05. This is an author review of temporary source, not independent
review or compatibility evidence. The two Rust files are frozen, unformatted,
uncompiled and unexecuted. No active repository or sibling file was changed.

## Frozen files and interface

- `openapi_model_schema.rs`: SHA256
  `61fce7d296203569b5e4f85b1a41f78dd9ca489030a7a95da3e5527fd1b398db`.
- `openapi_model_email.rs`: SHA256
  `bc1e793e253722163924e32e6daf73785bfdd3f6639a13b234c7e9150a1ddcd0`.
- Main peer `openapi_models.rs`: SHA256
  `c3df23ba6819364fb8e39c1a07fd628fb1edb229ecf67b93a0234b48d5771b1d`.

The companion interfaces are
`schema_fields(py: Python<'_>) -> PyResult<Py<PyDict>>` and
`email_type(py: Python<'_>) -> PyResult<Py<PyAny>>`. Both are private crate APIs.
The integration author declares the two modules. No public facade export or
`add_class` registration is needed for the private callback objects.

The main builder adds its extra-allowing BaseModel base and source module label
to the Schema kwargs, creates the class, then rebuilds the graph using the full
namespace before publishing only its retained OpenAPI root. The Schema helper
does not create or publish a partial class. All graph and model construction
callbacks run without an application or cache borrow.

## Source and construction data

Pinned `fastapi/openapi/models.py` SHA256 is
`b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`.
Schema declarations are lines 123–204, its recursive alias is line 209, and its
explicit rebuild is line 433. The helper supplies all 61 Python field names in
declaration order, separate aliases, nullable annotation members, and defaults.
All defaults are None. Twelve aliases use Pydantic Field metadata; eight integer
constraints use `ge=0`, and `multipleOf` uses `gt=0`. There is no u16 narrowing or
prevalidation of user values.

Source PEP 604 unions are constructed with public `operator.or_`; the eleven
direct `Optional['SchemaOrBool']` fields use public `typing.Optional`. Builtin
generic subscriptions and Literal/Annotated subscriptions are public APIs.
SchemaType retains the seven ordered source strings. The example annotation
retains the exact `typing_extensions.deprecated` metadata and message.

Fixed ForwardRefs are limited to `SchemaOrBool`, `Discriminator`, `XML`, and
`ExternalDocumentation`. They are annotation data for the caller's namespace
rebuild; no user annotation, original FastAPI code, or Python source is evaluated
by Rust. CPython 3.12.13 `typing.py:974–978` supports ForwardRef union composition.
The main builder retains the direct types and recursive aliases in the namespace.

The source order does not imply independent validation of every Schema branch.
Inventory equality is a static construction check, and complete namespace/core
schema generation must still succeed through the real native import.

## Optional EmailStr profile and fallback

Pinned `models.py:16–54` attempts the optional `email_validator` import, asserts
its module truth value, and selects Pydantic EmailStr. It catches ImportError
from that selection, preserving other failures. The helper follows that branch
and captures `logging.getLogger('fastapi')`, the object defined by source
`fastapi/logger.py:3`, before selection. It does not import original FastAPI.

The closed normal result commands select `.venv-oracle/bin/python` and
`.venv-target/bin/python`. Static site-packages path inventories find no
`email_validator*` entries in those two environments or `.venv-build-tools`.
The separate `.venv-oracle-standard` profile has email-validator 2.3.0 paths.
The run identities record required packages, not a complete installed inventory;
the static path inventory supplements rather than replaces those identities.
No package was imported to obtain this evidence. The runtime helper selects the
source optional profile dynamically, including its actual ImportError boundary.

When needed, the helper creates a native heap subclass of str named EmailStr with
the source module label. Native callable objects wrapped in builtin classmethod
implement the five source hooks. `_validate` and `validate` call the captured
logger's `warning` method with the exact source string, then call str on the
original value. The core hook passes the bound `_validate` to public
`pydantic_core.core_schema.with_info_plain_validator_function`; source
`fastapi/_compat/__init__.py:39` exports that same v2 helper. The JSON hook ignores
the handler as source does and returns ordered `type='string', format='email'`.
The legacy validator iterable yields one lazy `cls.validate` lookup through a
private native iterator. The source does not return an EmailStr instance after
plain validation; neither does this helper.

Errors from logging, attribute lookup, string conversion, or schema construction
propagate as their actual PyErr. There is no warning suppression, normalization,
fallback after a non-ImportError, generic validator emulation, or broad exception
mapping. PyO3 refs own the logger/class/value handles. Callback types use safe
Rust, contain no locks or app/cache references, and add no unsafe or lint
suppression.

## Static audit and required gates

`audit-schema-email-descriptors.py` reads the pinned source as AST and the Rust
files as text. It checks names/order/aliases/type kinds/defaults/constraints,
literal order, optional form selection, fixed references, exact deprecated and
logging strings, fallback hook names, catch profile, and absence of prohibited
constructs. `schema-email-static-receipt.json` records the actual frozen hashes
and static path inventory. Only stdlib parsing/data/hash code was executed under
CPython 3.12.13 with bytecode writes disabled; no model or workload import, Rust
compiler, formatter, build, application or parity stage was run.

Independent peer review and the parent's actual module import must validate the
native classmethod binding and all rebuilt Pydantic schemas. Parent owns combined
applicability, formatting, strict Clippy, contracts, fresh source/target gates for
the new three and prior 203 cases, and any selected coverage/fault evidence. The
first whole 206 run's 205/1 result and exact raw-order regression remain retained.
This author note does not predict a live result.

## Explicit boundaries

These are private final-validation classes, not a new public
`fastapi.openapi.models` facade. Python FunctionType/generator identity, exact
signature reflection, frame/traceback metadata, pickle/import bindings, mutable
class or module history, monkeypatched import APIs, audit hooks, and arbitrary
generator send/throw/close on the legacy validator iterable are unproved. The
legacy native iterator preserves ordinary lazy iteration but is not a Python
generator. Native callback keyword/error binding is not claimed as a public
fallback method contract. Extra import/bootstrap timing and already-loaded
Pydantic state are not selected observations.

Full recursion, every numeric/URL/enum/error/warning branch, optional-installed
profile parity, adversarial callback reentry, and concurrent free-threaded use
need their own public gates. Existing generic encoder, document assembly, route
and shared adapter generation, caching, direct get_openapi subset, and remaining
source model export gaps stay separately owned. No expected output or selector
reduction has been introduced.
