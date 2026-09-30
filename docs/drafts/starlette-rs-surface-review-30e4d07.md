# FastAPI-RS crosswalk delta for Starlette-RS 30e4d07

> Historical snapshot for the Host reverse-path addition at `30e4d07`.
> The current pin is `7cdaad022233e2aa55008bab9309a29803f4e26d`; see
> [the Router reverse-lookup delta](starlette-rs-surface-review-7cdaad0.md).

## Reviewed revisions

- FastAPI 0.141.1: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0 oracle: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Starlette-RS target: `30e4d07d24b6564cf8ecda8bb754dbf281678245`.
- Contract ID: `starlette-1.6.0-asgi-http-config-session-slice` (unchanged).

## Host reverse URL formatting

Commit `30e4d07` extends `HostPattern` with `format_host` and
`format_url_path`. The native support formats Host routes' direct-name path,
preserves configured ports, and leaves nested child-route lookup unsupported.
The sibling manifest selects `Host.url_path_for.direct-path` for both the
Rust-native and Python-package profiles; `Host.url_path_for.nested-route`
remains Python-package-only. The commit adds no new external dependency.

FastAPI 0.141.1 exercises the nested route case when a generic Starlette `Host`
is passed through `APIRouter(routes=...)` and `include_router`. The prefixed
source case checks request dispatch and `url_path_for` path/host fields
(`tests/test_router_include_context.py:723-744`); the unprefixed case checks
dispatch (`:837-855`). The existing FastAPI-RS input-only workflow also
observes the captured host parameter and nested reverse URL path/host, with a
configured host port different from the incoming port.

Live identity-checked parity used input
`tests/fixtures/inputs/parity/starlette-routing-runtime-upstream.json`. Oracle
run `350678ad-cef8-4fbf-b2c2-ebf2031f72d7` completed all five cases. Target run
`6d3b1760-9e3e-487e-a4ec-e3ff817b4112` produced product errors in all five;
comparison `76271b52-b3f2-4768-8d67-0442b4b2e8a4` passed 0/5. The construction
error is `TypeError: APIRouter.__new__() got an unexpected keyword argument
'routes'`. Therefore these runs do not exercise Host matching or reverse
formatting in FastAPI-RS. The sibling's generic Rust-native contract remains
narrower: it covers direct Host path formatting, not FastAPI's nested named-
route lookup.

Evidence: `starlette-rs/src/host.rs:17-34,115-155`,
`tests/fixtures/manifest.yaml` requirements under `starlette.routing.Host`,
and `tests/fixtures/sources/parity/host-routing.yaml`.
