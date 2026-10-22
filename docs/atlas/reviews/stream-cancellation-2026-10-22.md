# Streaming cancellation parity refresh

The earlier `starlette-rs-streaming-taskgroup-callback` mismatch was recorded
against AnyIO 4.12.1 and an older FastAPI-RS target revision. The active
FastAPI 0.157.0 lock resolves AnyIO 4.14.2, so the input was rerun against the
pinned source and target profiles.

| Identity | Value |
| --- | --- |
| FastAPI oracle | 0.157.0, `386a28af2f87af1a32ac26d88f07b7f58ab2dfb1` |
| Starlette oracle | 1.6.0, `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` |
| FastAPI-RS | `2e5a688dd193241d12037cdef5a0b527a7da3949` |
| Starlette-RS | `4139a72449bf5751e8902fb1c7175ee7f191d338` |
| Python | CPython 3.12.13 |
| AnyIO | 4.14.2 on source and target |
| Input | `tests/fixtures/inputs/parity/stream-cancellation.json`, SHA-256 `42c43141f152d2d05d1136027ba3ecd90f3c8153c6f414f6adeee6990f9547f5` |
| Manifest | SHA-256 `a2e9f3213a7160f407e8d4fc6eaf891eac8351a89a5a8255ca6a75fa4839afb1` |
| Comparison | `parity-results/comparisons/d8ed2db6-c894-47ce-8c0e-1239137455b3.json` |

The exact comparison passed all 3 selected cases: raw async streaming, JSONL
streaming, and request-scoped yielded-dependency cleanup after cancellation.
The observed response status and headers, cancellation state, and post-cancel
cleanup response matched. This removes the recorded mismatch for the active
dependency lock; it does not claim parity for other streaming or disconnect
combinations. No Starlette-RS source was changed.

## Current-main refresh (2026-10-23)

The three-case workflow was rerun against current main after the earlier Kata
blocker note. FastAPI 0.157.0 and Starlette 1.6.0 matched FastAPI-RS at target
`378cf2900933b577fcb1182dc1ec0209bab20565`, with Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338` and AnyIO 4.14.2 on both sides.
The current fixture manifest SHA-256 is
`827764700cc27233098327b1e9e9e638269c86a6fda58bca5f576a19b318360a`.

| Evidence | Identity |
| --- | --- |
| Comparison | `parity-results/comparisons/bd221dd7-9379-4695-9aa8-7d01fe824400.json` |
| Comparison SHA-256 | `d8e52df7d7897b06081ba00f3fc2a813373afd0f5e23b35449b4e3bd48e9bb86` |
| Input SHA-256 | `42c43141f152d2d05d1136027ba3ecd90f3c8153c6f414f6adeee6990f9547f5` |
| Result | 3/3 matched; zero failed or not-run cases |
| Target source-tree SHA-256 | `54da9c478c6029d0b6f15505b8e5e06907152b72d634e2045173bd37952706e4` |
| Target binary SHA-256 | `77755183189547b31b00e0944d1dd85bacfb68fa30d02b785e729e04095b2032` |

This fresh run confirms only the three declared cases on the active profile;
it does not establish parity for other streaming, callback, or disconnect
combinations. The older failure note remains historical to its target and
dependency identity. No FastAPI-RS or Starlette-RS implementation was changed.
