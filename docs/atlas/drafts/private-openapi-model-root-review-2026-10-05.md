# Private OpenAPI final-model integration: root review

2026-10-05. Source review before application, formatting, compiler or runtime gates.
The first closed regression remains 205 passed / 1 failed / 0 not_run.

## Frozen scope

| Prospective file | SHA256 |
| --- | --- |
| openapi_models.rs | c3df23ba6819364fb8e39c1a07fd628fb1edb229ecf67b93a0234b48d5771b1d |
| openapi_model_schema.rs | 61fce7d296203569b5e4f85b1a41f78dd9ca489030a7a95da3e5527fd1b398db |
| openapi_model_email.rs | bc1e793e253722163924e32e6daf73785bfdd3f6639a13b234c7e9150a1ddcd0 |
| openapi.rs | da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7 |
| lib.rs | 1f46ec965e3646c03a2da56ad6548dd8735f2a21b77ee5a02e7c49a2e1698be4 |

Combined patch SHA256: 74ade11faf1f67b8085bda235a28cfbc72a3e91578a8e3a5e2b0e3e1d56bdb5c.
The two existing-file bases match active 1c66469 exactly; all three new files are
absent. Root ran git apply --check successfully after checking all five hashes.

## Source-backed decisions

The source OpenAPI.paths field is PathItem | Any, and Parameter.in_ is an ordinary
Enum. Pydantic smart-union selection can retain the entire input path mapping
following lax enum conversion. The removed role-order traversal cannot reproduce
this choice. The actual pinned engine now receives a private Rust-authored model
graph with source declaration/union order, bases, defaults, aliases and constraints.
Source models.py hash is b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d.

Root read graph construction, annotation resolution, create_model field arguments,
functional Enum and TypedDict construction, all Schema descriptors, native email
callbacks and both integration diffs. Main author descriptor receipt is partly a
generator consistency audit; it is not independently sufficient annotation proof.
A separate peer audit compares pinned AST directly to Rust semantic declarations
for 43 definitions and 139 main fields. The other peer directly checks 61 Schema
fields, 12 aliases, eight ge=0 constraints and one gt=0 constraint. Reviewed data
cover 200 source declarations; this count is not a public model support claim.

The graph uses public Pydantic create_model/model_rebuild, typing annotation APIs
and ordinary enum.Enum. It evaluates no helper source or original FastAPI code;
fixed ForwardRefs are annotation data resolved through the complete namespace.
Root publication occurs only after model rebuilding succeeds. Python references
are owned locally or by the retained native-module root, with no interpreter-owned
Rust static, unsafe code, application borrow, cache lock or blanket suppression.

The final boundary matches utils.py:679: OpenAPI(**output), then the existing Rust
jsonable_encoder with by_alias=True/exclude_none=True. Per-operation security
scheme encoding is moved before insertion/dedup, matching utils.py:140–146.
Existing response-field batching, schema normalization, source metadata signatures
and cache publication remain intact. Removing the second late externalDocs
TypeAdapter permits the real model to determine URL conversion and error location.
No route/name/fixture heuristic, expected output, selector or comparator change is
included. Python facade, input recipes, metadata and dependencies are unchanged.

Email selection catches only source ImportError; non-ImportError failures propagate.
Its fallback owns the ordinary fastapi logger and uses native classmethod callables
for validation/schema behavior. The lazy native validator iterator does not claim
Python generator identity or send/throw/close compatibility. Native classmethod
binding, annotation reconstruction and recursive core schemas require actual import.

## Required live gates and boundaries

Root found no concrete source-review blocker. Format and strict Clippy must pass;
actual build/import and fresh exact three-case plus whole 206-case parity remain
required. Preserve failed first-run artifacts; the new helpers differ only in OUT:
post helper fc8c5100544b86a3b945f27dc5e1f53521433caaea2b49f3f780159347bb7788;
whole helper 9a3322935cc204ecf5cdfbfc0c6b7c8f830cd38f7822ed86f334f7aa16257028.
Coverage must use fresh same-build workflows, and fault instrumentation must stay
separate. Fresh seven-workload benchmark evidence is still required.

Private class construction does not establish public OpenAPI model export,
reflection, pickle/import identity, mutated class history, all optional profiles,
all validation/error branches, free-threaded behavior or full API compatibility.
Existing body/request schema collection and unselected callback phase ordering
remain separate assembly boundaries. Automatic422/default/4XX inputs remain inactive.
The sibling worker/background panic and dependency pin remain unresolved.
