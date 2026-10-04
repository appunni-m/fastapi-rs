# Starlette-RS latest pin and parity audit — 2026-10-04

FastAPI-RS now pins Starlette-RS 0.1.0 at `7703245507b68a05756e39e1135df9e5aa3e38ef`, the latest verified remote `main` head selected for this run. The clean source checkout used for generation and target parity matches that commit. The existing sibling checkout was left untouched.

From the prior `a345f8c` pin, the sibling contract adds four generic, input-only cases: module-level `Config.environ` mutation and read freezing; HTTPException header forwarding through a class handler; WebSocketException reason forwarding after acceptance; and a custom WebSocketException class handler controlling the close event. These change sibling metadata, fixtures, parity support, and coverage evidence, but not Starlette-RS runtime code, dependencies, API catalog, or API review. Commit `f9bade1` refreshes sibling documentation and benchmark evidence. Commit `50b6d50` adds the custom WebSocket exception-handler case plus parity adapter and contract support. The selected `7703245` commit refreshes benchmark evidence. FastAPI-RS does not claim these generic cases as standalone FastAPI API support.

## Identity-checked FastAPI parity

Both comparisons used manifest SHA-256 `af8a2335946571a9605e2440e0a8a77830e43e7afe12da96de668435128da9e4`. The oracle was FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` with Starlette 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. The target was FastAPI-RS revision `c496ca40733c252e427e5e53f848b23ddc5a424a` (source-tree SHA-256 `08faa35e282e3bae8f9ecc2cfba7bc6dd8ed8b43ae61117e513cb61d67f10bcb`; binary SHA-256 `b114b8716b8289cf42f2ad39fc13fdb6890c55b17ed3bdcf7757756b7c493389`) with Starlette-RS `7703245507b68a05756e39e1135df9e5aa3e38ef`.

The new `fastapi.websocket-exception.custom-handler-close` input (`80dce3c0a855b4c7b6a78db4656f13b8973bac63f392a8affca31c7bd31411d7`) completed on both sides. Oracle run `22a054af-b4b1-4b55-9dd6-be030311afda`, target run `0a840335-77fc-4b3a-b522-a811e396d900`, and comparison `56aac774-31dd-4beb-97be-506fb0d0dd86` report 0/1 passing. The only difference is socket identity/state in the workload trace: the oracle handler receives the endpoint's same `CONNECTED` WebSocket, while FastAPI-RS gives the handler a different `CONNECTING` WebSocket; after handler close, the endpoint socket remains `CONNECTED` on the target. Close code, reason, event order, messages, exception code, and reason match. There were no infrastructure errors.

The existing `public-errors-http-websocket-wave` input (`93570c9e572a530050157c142219c4adc7b294256a7f4932bfae6c11703dc55a`) passed 4/4. Oracle run `db596741-23cd-4151-a146-017e2c4e7f65`, target run `511ec0d3-0643-4fb2-828c-fff0499e0bdd`, and comparison `7228b4ae-8af2-4bf5-bbb1-37f586a8066e` record the result. The reviewed scope now maps the custom handler input but continues to mark WebSocket object identity/state as a partial-parity gap.

No unit-test suite was run.
