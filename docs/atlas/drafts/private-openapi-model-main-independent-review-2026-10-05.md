# Independent main OpenAPI graph source review

Date: 2026-10-05. Read-only independent review of the peer-owned main Rust
proposal. The reviewer authored the Schema/email companions and does not claim
independent review of those files. No compiler, formatter, model import,
application, parity stage, native binary inspection, or tracked edit occurred.

## Exact binding

- Main `openapi_models.rs`: SHA256
  `c3df23ba6819364fb8e39c1a07fd628fb1edb229ecf67b93a0234b48d5771b1d`.
- Main patch: `dd8b1d597ce90dec3433f7228b682ca34d6c2e1b742c043ab53cc865a8903cac`.
- Main author note:
  `d94207472d0f902d32cbdf1a96f7d2cef1c1c864d8e1f6b7c3ea99547b1fb184`.
- Pinned source `fastapi/openapi/models.py`:
  `b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`.
- Independent semantic receipt:
  `2150bd6b652e613da3e1520babe1c3b0b66f40d4d2da64ea73cbfe2735358020`.
- Independent audit script:
  `5daaf301f469d85fb6743eefbbcadb00c55f8ded17099f40f7d16fc29c5b8a05`.

The new main file has no preexisting Rust file base. Companion interfaces remain
`schema_fields(py) -> PyResult<Py<PyDict>>` and
`email_type(py) -> PyResult<Py<PyAny>>`; their separately frozen hashes are
`61fce7d296203569b5e4f85b1a41f78dd9ca489030a7a95da3e5527fd1b398db`
and `bc1e793e253722163924e32e6daf73785bfdd3f6639a13b234c7e9150a1ddcd0`.

## Direct source-data audit

The peer's existing annotation/default comparison uses values emitted into
`model-source-facts.json` by its generator. That portion is a generator
consistency check. This review separately parses the pinned Python AST and the
actual Rust descriptor expressions into ordered semantic data. It reads no
generator-produced facts and does not import any model or execute descriptor
expressions. `independent-main-source-audit.py` is the retained static parser.

All 43 definition positions match the source: 35 main-owned model classes, the
companion Schema position, three ordinary enums, three aliases, and one Example
TypedDict. All 139 main-owned declared fields match names/order, annotation
structure and union member order, defaults, and aliases directly from the AST.
This includes 135 model fields plus four Example entries. The Schema companion
contains the remaining 61 source fields; its author audit is separate.

Concrete sensitive branches checked:

- `ParameterInType`, `SecuritySchemeType`, and `APIKeyIn` are ordinary Enum
  classes with ordered explicit string values, not StrEnum or str-mixin enums.
  ParameterInType's raw string coercion remains available to the same pinned
  Pydantic smart-union machinery that selected the source raw path dictionary.
- Required ordinary fields use annotation-only create_model arguments; required
  aliases use Field(alias=...) with no default. None, mutable empty-dict scopes,
  bearer text, and actual enum-member defaults are distinct.
- `BaseModelWithConfig` config is extra='allow'; descendants use their source
  bases. Reference and Discriminator use plain BaseModel. Inherited field order
  and field overrides are delegated to Pydantic rather than hand-flattened.
- ServerVariable.enum keeps Annotated Field(min_length=1), not a list-length
  check outside the model. Its nullable/default-None distinction is retained.
- Source PEP 604 forms use operator.or_; Encoding's explicit
  typing.Union['Header', Reference] retains its distinct spelling. Literal and
  builtin generics retain ordered members and container kinds.
- OpenAPI.paths is PathItem|Any; Operation.responses is Response|Any;
  Components.callbacks is dict[str,PathItem]|Reference|Any. Link's Any-first
  unions and SecurityScheme's five ordered classes are also exact. No Any
  branch is inferred from dictionary shape or route features.
- Example uses typing_extensions.TypedDict(total=False) and the source
  extra='allow' config. Its descriptor Required tag is not passed as a default;
  create_example uses annotations and total=False, leaving its keys optional.

Static equality verifies declaration data and implementation reading verifies
how it is consumed. It does not establish equivalence of generated Pydantic
core schemas or public outcomes before the real native import and live gates.

## Namespace and Pydantic calls

Pydantic 2.13.4 main.py:1735–1836 accepts precisely the dynamic model arguments
used here. Its default base is BaseModel, so the sole extra_allow branch for
BaseModelWithConfig is correct without passing both __base__ and __config__.
Every other model supplies its exact already-created base. Fixed main refs are
Header and PathItem; all named annotations already exist at their declaration
position, and every fixed ref exists in the final namespace.

The builder retains builtins, Any/AnyUrl/EmailStr/BaseModel, all generated model
classes/enums, Example, and the three aliases in one owned namespace. Schema is
created before SchemaOrBool as in source. Registration supplies that complete
namespace to model_rebuild before root publication. Source performs explicit
rebuilds for Schema, Operation and Encoding at models.py:433–435. The proposal
calls every model's rebuild with default force=False; Pydantic main.py:633–702
returns immediately for complete models and rebuilds unresolved models with the
given namespace. It does not force repeated rebuilds per document.

Pydantic's namespace resolver (_namespace_utils.py:59–69,232–295) can tolerate
the absent target source module global table and consult the supplied parent
namespace for fixed refs. This is needed because the classes are private dynamic
models labelled fastapi.openapi.models rather than executed original module
definitions. Parent module globals, public import bindings, mutable reflection
history and automatic source frames are not claimed equivalent.

Only the OpenAPI root is published as `_FastApiOpenApiModel` on the native module
after every rebuild succeeds. Finalization calls that root with the assembled
dict as kwargs, matching source OpenAPI(**output) at utils.py:679. The retained
root and class schemas own ordinary Py refs. All local objects retire outside an
application/cache borrow; this module holds no app reference, lock, mutable
global Python reference, or Rust static containing interpreter-owned values.
No unsafe, panic shortcut, lint suppression, source evaluator, original FastAPI
import, expected-output replacement or input-specific predicate is added.

The caller must own its assembled snapshot and release app/cache borrows before
root validation and the recursive encoder. The existing native encoding.rs
BaseModel branch calls model_dump(mode='json',by_alias,exclude_none) then recursively
encodes the resulting data, consistent with source encoders.py:243–258 for the
selected alias/exclusion options. Security definitions must already be encoded
at their source assembly boundary; accepting unrelated native security classes
as graph class instances would silently broaden the source union. That
integration correction is separately reviewed.

## Conclusion and limits

No concrete main declaration, namespace, ownership, PyO3 call-shape or source
ordering blocker was found by reading. This is bounded static clearance for
integration and compilation, not a target compatibility or full source model
API claim. Parent owns combined apply checks, formatting, Clippy, real module
import/rebuild, exact failed baseline OpenAPI action, new three cases and all
prior 203 regression gates. The first complete 206 result remains 205 passed /
one failed, with unchanged parsed JSON and unequal raw bytes; this review does
not alter or reinterpret that receipt.

Private graph/reflection, bootstrap timing and optional email profiles, arbitrary
mapping/model inputs, mutable Pydantic state, all error locations/messages and
coercion/warning branches, model export/pickle identity, recursion/callback
reentry/concurrency remain separately unproved. The dynamic graph delegates
those validation algorithms to pinned Pydantic; declaration coverage alone
cannot close their public evidence gap. Document assembly, automatic 422,
late direct get_openapi options, shared adapter schema generation, normalizers,
cache behavior and the integration encoder remain separately owned seams.
