# FastAPI-RS scope and depth

## Product boundary

FastAPI-RS is intended to replace FastAPI for Python applications that import
`fastapi`. The tracked reference is FastAPI 0.141.1 at
[`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`](https://github.com/fastapi/fastapi/tree/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f).
The matching source checkout is local research input, not a project submodule
or vendored source tree.

The target stack is FastAPI-RS plus the separately developed Starlette-RS,
which is assumed to replace Starlette completely at the Starlette 1.6.0
contract (`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`). Use Starlette 1.6.0
alone in the FastAPI oracle and target profiles; do not silently fall back to
another upstream Starlette version. FastAPI-RS must not silently fall back to
upstream Starlette in parity or benchmark runs. Pydantic v2 is a
separate compatibility boundary; its Rust `pydantic-core` handles validation
and serialization, while the `pydantic` Python package defines models and
schemas. Reusing Pydantic is the working plan, not a completed compatibility
decision.

The Python-facing framework has to accept ordinary Python annotations,
callables, decorators, dependencies, and Pydantic models. A Rust core alone
does not remove those Python interoperability requirements. Preserve the public
`fastapi` namespace and treat any Rust module as an implementation detail unless
the manifest establishes a separate Rust public API.

## What the size means

The pinned release contains 48 Python package source files, 492 test files,
about 461 Python documentation examples, and about 155 English documentation
pages. FastAPI's runtime metadata declares five direct dependencies; its lock
file covers a much larger optional, documentation, and development tool graph.
The framework's observable contract includes more than exported names:

- application and router configuration, path-operation decorators, dependency
  solving, validation, and serialization;
- HTTP, WebSocket, background-task, lifespan, exception, and middleware
  interactions delegated through Starlette;
- OpenAPI output, security schemes, docs endpoints, and schema edge cases;
- Python signatures, generated attributes, error types and messages where
  public, and documented deprecations.

FastAPI calls both public and private Starlette interfaces. Replacing
Starlette therefore needs a compatibility map for the interfaces FastAPI
consumes, not merely a matching import package name. The API inventory must
separate FastAPI-owned behavior from behavior delegated to the Starlette-RS
contract.

## Build order

1. Pin the FastAPI oracle, Python runtime, Pydantic line, and target identity.
2. Complete the public surface and dependency inventories; publish the
   dependency and license decisions.
3. Create the single operation-level manifest and input-only parity corpus.
4. Establish an end-to-end Python facade plus Rust binding slice, then grow
   parity across routes, dependency injection, validation, responses,
   WebSockets, lifecycle, and OpenAPI.
5. Add and run benchmarks only for workloads that pass the matching parity
   gate. Report framework-only and end-to-end server measurements separately.
6. Expand through upstream tests and documentation examples, preserving visible
   exclusions until they are supported.

## Rough effort range

These are planning estimates, not delivery promises. They assume one experienced
contributor working on FastAPI-RS and that Starlette-RS and Pydantic remain
usable dependencies:

| Milestone | Rough range | Includes |
| --- | ---: | --- |
| Contract foundation | 2–4 weeks | inventory, pinned identities, dependency/license map, parity and benchmark harness design |
| Narrow MVP | 4–8 weeks after the foundation | common HTTP routes, core dependency injection and validation, Pydantic integration, basic OpenAPI |
| Broad documented compatibility | 6–12+ months | full public surface, advanced validation/security, WebSockets, lifespan/middleware, custom responses/routes, broad OpenAPI and edge cases |
| Full replacement claim | Open-ended | upstream-suite-level compatibility across supported Python/Pydantic versions and target deployment environments |

Replacing Starlette or Pydantic inside this project would invalidate those
assumptions and expand the scope substantially. Those projects have separate
contracts and are not part of this repository's implementation.

## Completion evidence

Compatibility is measured against the pinned live FastAPI oracle through public
Python calls. The denominator is the complete documented/public API inventory;
the contract records unsupported operations rather than omitting them. HTTP,
WebSocket, lifecycle, validation, serialization, and OpenAPI behavior require
their own parity evidence. A benchmark score is meaningful only with equivalent
features, matched workload inputs, and a passing correctness gate.
