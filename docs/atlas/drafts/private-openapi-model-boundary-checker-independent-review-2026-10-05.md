# Native import boundary: root independent review

2026-10-05. Root read all58 additions/15 deletions against the active checker
base7c0a8c87b96207c3aa63068dbcd497eb9366c6f2a0ca728c7d69a564bf911363.
Frozen proposalcce45ff5073b9f3923bd29a591cbe31a4a1ad005e64a927ea1c54ccfed831f11;
patchbf5991a9a8eb90f499e7c99f762386012d9dfa3b0fce7376a74f89c3317ed690.
Root checked patch applicability, applied it byte-exact, and ran the canonical
source-only runtime-boundary CLI successfully (exit0). No unit/synthetic tests.
The earlier failed canonical run is preserved in openapi-final-model-static.log.

finditer now checks every FastAPI literal in every Rust file. Metadata exceptions
are bound to the exact scanned value position; a neighboring import literal is
not covered. Fixed module constants require every identifier use to be a direct
module/__module__ metadata value. Aliasing or importing the constant fails that
condition. Logger data requires the exact direct logging import/getLogger/call1
chain, with the matched string at its data argument. Dynamic Python execution,
original FastAPI dependencies/installed-package checks and all Python façade
checks are unchanged. No import path is allowed by name, file, case or workload.

Root found no concrete blocker. This remains a conservative textual contract;
it does not establish arbitrary Rust semantic analysis. No split-string workaround
or hidden original import is introduced. The current5-file native patch only
uses the reviewed model labels, logger data and existing direct metadata.
Fresh native import and identity-checked public parity remain required.

Additional direct public get_openapi controls use existing whole reviewed inputs:
openapi-get-openapi-public-api and openapi-get-openapi-single-route, two cases
and two probes each. Their separate helper preserves the full206 runner's
execution/snapshot code byte-exact and changes only OUT and these two selections:
e725af28a14fdfef56726e87ae72f460f066cd17c7dd0486c33a03fb018d3c81.
Those four cases are outside the existing206 denominator and must be reported
separately until actual closed artifacts justify a distinct210-case total.

Ruff then formatted only the checker; AST including all literals is exactly equal
to the frozen proposal. The active formatted checksum is
cce136a70577684e60897732497a5b1398902ec056824d58ff2184f6dc4760ee. The initial format-check
failure is preserved separately; final formatting/Clippy gate remains required.
