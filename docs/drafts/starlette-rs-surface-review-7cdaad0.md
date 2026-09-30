# FastAPI-RS crosswalk delta for Starlette-RS 7cdaad0

## Reviewed revisions

- FastAPI 0.141.1: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0 oracle: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Starlette-RS target: `7cdaad022233e2aa55008bab9309a29803f4e26d`.
- Contract ID: `starlette-1.6.0-asgi-http-config-session-slice` (unchanged).

The pin adds the native `NamedRouteTable`, `NamedRouteError`, and
`RouteUrlPath` types and declares partial Rust-native support for
`Router.url_path_for`. It resolves the first direct named HTTP route whose
parameter names match exactly, formats built-in converter values, and returns
an HTTP path with empty host metadata. Nested `Mount` and `Host` routes,
WebSocket routes, custom converters, and Python exception mapping remain
outside the native operation. The change adds no external dependency. The
30e4d07 Host direct-path addition remains a separate partial operation; its
nested route branch is still outside the native contract.

FastAPI 0.141.1 inherits `url_path_for` from Starlette and uses a direct named
route with the `path` converter in
`tests/test_starlette_urlconvertors.py:60-63`. That source test is now linked
to the existing input-only workflow
`tests/fixtures/input-recipes/parity/starlette-url-converters-upstream.yaml`.
The case projects the generated path into an ASGI response so the isolated
oracle and target can observe it; the YAML contains inputs and selectors only.

Identity-checked live parity on this pin produced these results:

- The FastAPI 0.141.1 / Starlette 1.6.0 oracle completed all five converter
  workflow cases without product errors (`2c529bc7-ef61-4196-9bef-b396fb28f086`).
- FastAPI-RS completed four of five; the URL path case failed because
  `fastapi_rs._core.FastAPI` has no `url_path_for` attribute
  (`41d4885b-17c8-4e3a-9062-2086075ef5e7`). The comparison passed 4/5
  (`4ef1b320-8bbd-4bad-b415-5d51ab29a817`).
- The prefixed Host/Mount routing workflow completed all five oracle cases,
  while the target failed construction in all five because
  `APIRouter(routes=...)` is unsupported. The comparison passed 0/5
  (`a63a5ef0-6614-4f40-a00f-ca399f329d5f`,
  `6ff0ce92-7835-4f5c-9f97-d253ea0d3c14`,
  `d8fd021d-7571-411d-82ca-93dd6137fcf5`). It does not exercise Host matching
  or nested reverse lookup in FastAPI-RS.

`NamedRouteTable` supplies a generic native primitive, but FastAPI-RS must
still connect FastAPI's public `FastAPI.url_path_for` behavior to that
primitive, map converter values at the boundary, and return Starlette-compatible
`URLPath` metadata. The sibling capability alone does not make this FastAPI
case pass.

Evidence: the pinned sibling
`starlette-rs/src/named_route_table.rs`,
`tests/fixtures/manifest.yaml` requirement
`starlette.routing.Router.url_path_for`, and
`tests/fixtures/sources/parity/reverse-url-routing.yaml`.
