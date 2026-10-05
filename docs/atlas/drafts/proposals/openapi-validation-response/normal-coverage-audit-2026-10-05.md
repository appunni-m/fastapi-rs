# Response-status / automatic-422: closed normal coverage audit

Independent read-only audit, 2026-10-05. Scope is the parent-acknowledged CLOSED
folder `parity-results/coverage/openapi-validation-response-normal/d508878-first/`.
Receipt/state checks ran before benchmark timing; bulk LLVM reconstruction and
hash checks resumed only after its closure. No product/native import, app, build,
parity rerun, LLVM execution, compiled-binary read or active edit. All native
fingerprints below are saved receipt bindings.

## Selection and actual work

| Fresh selection | Ordinary cases | HTTP actions | Covered regions / 32,605 |
|---|---:|---:|---:|
| baseline | 12 | 12 | 12,749 |
| previous | 5 | 9 | 10,057 |
| records | 5 | 8 | 11,284 |
| classifier | 23 | 54 | 10,527 |
| awaitable | 15 | 47 | 10,032 |
| response | 16 | 61 | 9,155 |
| traversal | 7 | 42 | 8,982 |
| additional | 3 | 15 | 8,718 |
| nextfields | 3 | 19 | 8,872 |
| batch | 4 | 24 | 10,199 |
| Total | 93 | 291 | workflow covered counts must not be added |

All ten source/target/comparison triples are completed, infrastructure-error-free
and declare all 93 selected comparisons passed with no fail/not_run. Each product
has all 291 actions completed and 690 step observations. The 71 explicitly selected
construction observations comprise 70 successes and one matching ordinary
FastAPIError for an unsupported response annotation; that negative case has zero
planned actions. The 22 legacy cases do not select distinct constructor probes.
All 71 fixed-state checks are true in exact order (10×7 plus final completion),
from 2026-10-05T15:39:51.478393+00:00 through 2026-10-05T15:41:22.886120+00:00.

Current index/input/recipe/workload digests and nonempty requirement refs match
the saved selections. The complete ordered case ledger and actual result hashes,
run IDs, paths, source/target lane statuses and passing context summaries agree.
No injected cases, subsets, expected-output substitution or comparator changes
enter this lane. This selected coverage run is separate from the closed 214
normal/direct behavioral gate and its retained 11 legacy map-order gaps.

## One frozen instrumented build

- Root revision: `d50887853d382bd9d9e03c7e82a504614ff02aba`;
  exact sibling: `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.
- Combined source: `d1299254a34d2c31b0a8ed1b676825a85b749421aa27a9e8084e5c6afecbf8f7`.
  Both source trees and all 21 Rust digests match prebuild, backup-source records
  and every context. The recorded Rust hashes also match the currently immutable
  source files at audit time; all bound input/policy digests and root HEAD agree.
- Recomputed build ID:
  `fastapi-rs-instrumented-sha256:3acfcbd4f48dfd09914700ca445a50e9b0ddc846269dd4ff07c04b3d07a1079f`.
- Saved instrumented installed/export FastAPI:
  `f38d0ae4f2f74b81bfb094909f1b02e0aab4899e2bc049cde3bdc52271dbc8fe`;
  sibling: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`;
  pair: `fe94462d3fa84ec803af8654a51abb36ab33771bddf2860717ec74fd0923fdd2`.
- Actual saved isolated identity reports fault_injection_compiled:false and the
  intended normal `_core.abi3.so` path. New schemas record false; legacy omissions
  share this pair. Source identities retain the pinned FastAPI 0.141.1,
  Starlette 1.6.0, Python 3.12.13 and Pydantic 2.13.4/core 2.46.4 values.

The closed build log records successful staged release compilation (25.50s),
installation and the exact pinned sibling. Prebuild/config declare disabled
wrapper, `-C instrument-coverage`, incremental off, normal extension feature,
Rust 1.98.1 and aarch64 macOS. Profiles and export are actual instrumentation
evidence. The log does not recover the full original shell environment/Cargo
invocation; complete environment attribution remains the prebuild receipt.

The prior behavioral gate/backup contains release FastAPI 05fd1420… and pair
e1b2a359… with the same source. Those identities stay distinct from this normal
instrumented measurement. Fault/restoration and fresh benchmark evidence remain
separate; this note does not rehash or infer the current installed binary.

## Raw export fidelity and saved MCP acceptance

Each selection has one actual target profile with verified checksum. Exact merge
and export argument lists use only that profile, its own profdata and the one
configured normal export path. The separate native-identity profile is excluded.
All ten LLVM stderr files are empty. Independent reconstruction of filename
canonicalization, native file/function filtering and file-summary totals equals
each published report. Every report contains 20 native files, 1,483 function
records and denominator 32,605. Sibling/Python/external file coverage is excluded.

The saved actual MCP request equals the hints: this build’s fresh baseline,
eight previous fresh reports in order (lifecycle, records, classifier, awaitable,
response, traversal, additional, next-fields), and fresh batch. Contexts retain
one source/build/pair, their actual passing result references and report hashes.
No older build or fault context enters the request. Actual result isError:false,
status improved, incremental evidence verified: accepted union **15,096/32,605**,
batch-covered **10,199**, newly covered **42**, combined **15,138/32,605**.
The arithmetic and individual report totals agree; this audit does not implement
an independent LLVM union engine. Preserve regression_checked:false.

These are aggregate workflow regions, not individual case ownership, complete
matrix coverage or a replacement for normal behavioral gates. Definition-name
collisions, modeled status keys, response deepmerge/protocol histories and other
unexercised source branches remain separate input gates.

## Retained evidence hashes

Relative to the CLOSED folder:

- `runs.json`: `31f6d88805bd014eb1f800bd436a5f82550275e790bfc9efeb129925fe2b86cc`.
- `case-ledger.json`: `775cb1f3160c2b86a1cc6db2e91ae8939169969e1bfde03cefa1455276412175`.
- `source-build-state-checks.json`: `b7959a599657e051caa147f936d204e01e03c8891f8f1b627bbc2b3ddad224be`.
- `initial-source-build-snapshot.json`: `69cb4148c87bbf5ea9d0e342a2de4da442155a89d2ade31633c60f1130d8d020`.
- `build-configuration.json`: `5f5b49328a00468902729e5ed394eab49f6e639d5ad5d4516e037a5f9a7bd2a8`.
- `native-build-identity.json`: `cc93a90735be27f749cf4581b7ccae8876cb6f23b1727198e5173378181d9db4`.
- `coverage-mcp-comparison.json`: `6cd6ea9c1674ed065d49703c58fc62205b1656ac3a51a536ea96093a53c5df01`.
- `comparison-hints.json`: `6fb336f75d4058e583d00ad36e5545b823ace855487382f78cd9d6ad829034b2`.

TMP check artifacts/scripts under `/private/tmp`:

- `fastapi-rs-openapi-validation-response-closed-normal-coverage-checks.json`: `8b8a7503a9a9af54e82e37c34f3ca80937f2b0bbcd41475786786848a1a7fc39`.
- `fastapi-rs-openapi-validation-response-normal-llvm-fidelity.json`: `9df57f35f3d732bcbe9d02d943b8c11ccdbbe2e6999f2f1c08c5007c67ab4bf1`.
- `fastapi-rs-openapi-validation-response-normal-command-source-proof.json`: `d61f13c423b5b334b8c8a4ec96009794b507ef795314a2be16bf3f16d82d4938`.
- `fastapi-rs-validation-response-closed-coverage-audit.py`: `82d1c42c46f64ec04f3f15256f755c3382485073745d745dfb1395a9a88bcded`.
- `fastapi-rs-openapi-validation-response-normal-llvm-fidelity.py`: `502172b6c77512e9944e6bd7b2889efd7a1f76b87e955dd1ee2c71a54ebbad0d`.

The fidelity report records raw/published/context/result hashes and exact
reconstruction for all ten reports. The source/command proof binds all saved
Rust/input hashes and profile-command exclusions. No concrete receipt, build,
selection, filter or provider-request blocker was found.
