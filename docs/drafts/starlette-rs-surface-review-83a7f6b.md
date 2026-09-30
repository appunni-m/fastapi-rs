# Historical FastAPI-RS crosswalk delta for Starlette-RS 83a7f6b

## Reviewed revisions

- FastAPI 0.141.1: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0 oracle: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Starlette-RS target: `83a7f6b9f4024483231c3509f3211dd05f6726ac`.

## Contract delta at the 83a7f6b snapshot

The latest Starlette-RS commit adds an input-only Python-package case for an
unmatched HTTP route whose `HTTPException(404)` is handled by a registered
exception handler (`tests/fixtures/sources/parity/asgi-exception-handlers.yaml:710–857`;
requirement `starlette.asgi.exception-handler.router-miss-404` in
`tests/fixtures/manifest.yaml:962–970`). The case selects the exception handler
and Router miss together; it does not add a FastAPI target implementation.
The commit changes the Starlette-RS parity contract and manifest, but adds no
Rust or Python runtime implementation files.

FastAPI already has an independently authored generic route-miss case:
`tests/fixtures/input-recipes/parity/routing-surface.yaml::fastapi.routing.not-found`.
It observes exact response status, headers, body, and ASGI send order, and the
source-backed backlog assigns generic route-miss behavior to Starlette
(`tests/fixtures/fixture-backlog.json`, `fastapi.routing.not-found`). This is
enough to retain the ordinary FastAPI 404 crosswalk edge; the Starlette case
must not be copied as if `Starlette(...)` were the FastAPI public constructor.

A FastAPI-specific handler-on-miss case would cover an additional integration:
FastAPI's `exception_handlers` registration plus the generic Router miss.
The current FastAPI-RS constructor contract does not establish this input
(`tests/fixtures/manifest.yaml:1952–2026`). Keep it as an implementation
backlog item until the target accepts and dispatches FastAPI exception handlers.

## Body-size boundary remains separate

The earlier `56beb29` contract adds Starlette application and generic
route-level `max_body_size` coverage. FastAPI 0.141.1 accepts the application
keyword only through unused `**extra`, and `APIRoute` has no such parameter;
the detailed source distinction remains in
[`starlette-rs-surface-review-56beb29.md`](starlette-rs-surface-review-56beb29.md).
Do not map Starlette's route-limit fixture directly onto FastAPI path
operations.

This delta records the sibling's latest contract and FastAPI ownership edges.
It contains no expected outputs and makes no new parity claim.
