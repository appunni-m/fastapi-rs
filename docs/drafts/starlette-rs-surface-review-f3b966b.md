# Historical FastAPI-RS crosswalk delta for Starlette-RS f3b966b

## Reviewed revisions

- FastAPI 0.141.1: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0 oracle: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Starlette-RS target: `f3b966b03135ed3c4ea9fad0a203c080f1ae5ffe`.
- Contract ID: `starlette-1.6.0-asgi-http-config-session-slice` (unchanged).

## Host-routing addition at f3b966b

The f3b966b Starlette-RS commit added the Rust `HostPattern` matcher and a native
parity-adapter path for one Host route. Its narrow native fixture selects
`starlette.routing.Router.route-dispatch.host-parameter-port-ignored` with
`{tenant}.example.test:3600` and `Host: acme.example.test:5600`; this keeps the
string capture and ignores both ports. The crate adds no external dependency.
The sibling manifest continues to mark general Host route dispatch as
Python-package-only, while the port-insensitive parameter case is selected for
both profiles. This does not establish multi-route ordering, reverse URL
generation, WebSocket matching, or typed Host captures.

Evidence: `starlette-rs/src/host.rs:9-12,41-56`,
`starlette-rs/src/bin/starlette-rs-parity-adapter.rs:637-650`, and the pinned
manifest requirements under `starlette.routing.Router.route-dispatch`.

FastAPI 0.141.1 accepts generic Starlette `Host` objects through
`APIRouter(routes=...)` and `include_router`: its prefixed case checks request
dispatch and `url_path_for`, while its unprefixed case checks dispatch
(`tests/test_router_include_context.py:723-744` and `:837-855`). FastAPI-RS now
has an independent input-only port projection case linked to that source
module. At that review point, the source oracle returned the captured tenant;
the target stopped during app construction because `APIRouter(routes=...)` was
not yet accepted. The comparison exposed a concrete FastAPI-RS construction
gap and did not exercise the new Host matcher through FastAPI. The current
fixture also observes nested reverse URL formatting; see the 30e4d07 delta.

Generic Host implementation and its broader route behavior remain owned by
Starlette-RS. FastAPI-RS needs to accept the FastAPI route shape before an
identity-checked end-to-end Host integration comparison can reach that generic
behavior.
