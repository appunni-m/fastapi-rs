# Corrected final-model targeted3 evidence audit

Closed stage: `parity-results/next-openapi-response-field-wave/post-final-model-v2`,
revision `62dacc5283a0cee282258e268f7545765679e974`. Actual comparison completes
**3 passed / 0 failed / 0 not_run**. Each side completes 3 successful constructor
observations, all 19 HTTP actions, and all 64 observations. No subset, skipped
step, expected-output substitution, or infrastructure error is present.

Run IDs: source `2a2c6b32-c277-405d-b1f0-8499d401897a`, target
`be4d19cd-8d55-4ca5-8a8c-3b5697233ddd`, comparison
`f6af91b9-32e0-47da-99fa-190b4c1ddb83`. Artifact SHA256 values are respectively
`f58430e4cecc7776c0b6c10b321e6a1c591570d7bab278d2ee0912b264ba9b92`,
`5d60ecf150d815d4e6ead997b691ce42bac172eff127d8dbd3496e465adcdf17`,
`a3f78e877899f11d08580a9008d34159d583275f77c552863c2da113347e85c3`.

Declared schemas, ordered case/action/observation contracts, indexed source
requirements, and input/recipe/workload/manifest hashes bind correctly. Input
remains `558a3d9c…`; recipe `e1243762…`; workload `d1c2824c…`. Oracle pins are
FastAPI 0.141.1 / Starlette 1.6.0 / CPython 3.12.13 / Pydantic 2.13.4 and core
2.46.4. Target reports `fault_injection_compiled=false`, pinned sibling
`b4c8a65c…`, and no original FastAPI distribution.

Initial/final saved snapshot bytes are equal (`fa643d75…`): combined source
`503211630df8f7e2bf624c55c217d08444658252311bff19bf6568b4736a4c0f`,
normal pair `e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0`,
FastAPI SO `d934ba09…`, sibling SO `fd5940e3…`. These are recorded snapshots;
the reviewer did not hash or import current native binaries.

Entire ordered, type-sensitive case payloads equal preserved pre-change source
`8a541cd1-51d9-4010-9c9b-8c10226e6725`, corrected source, and corrected target
(typed payload SHA256 `16dd4a2b…`). This includes exact body bytes, ordered
headers/full public ASGI send journals, warnings and exception details.

- Flat document is 1378 bytes (`bfd73c97…`); core calls remain 5, JSON calls
  become 10, warning journal 5→15; cache repeats add no schema calls.
- Shared document is 865 bytes (`7bdd3bc4…`); core calls remain 3, JSON calls
  become **6**, warning journal 3→9. All three $ref schemas retain extension
  siblings. Six calls do not prove one-pass hook deduplication.
- Refusal yields exact 409/181-byte body (`41f72ab5…`) with original exception
  class/message. Retry succeeds with 875 bytes (`469d0558…`); JSON totals
  3→9, warnings 6→12, successful cache identity `[null,true]`; later public/docs
  cache hits retain these counts. Ordinary body sends omit `more_body` exactly.

Audit JSON `8e131559…` and payload detail `444addb5…` retain complete bindings
and raw-body hashes. This is only the targeted3 gate. Full206 and direct4 live
folders remain unread; no 210-case, coverage, restoration, or benchmark claim
follows. Outer FieldInfo alias/title branches, broader unions/validation,
automatic422/default/4XX behavior, and mutable/reentrant schema/cache history
remain separate evidence boundaries.
