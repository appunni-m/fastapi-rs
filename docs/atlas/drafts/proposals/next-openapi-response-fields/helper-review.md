# Next OpenAPI pre-change runner: independent static review

2026-10-05. No helper, app, factory, native module, parity command, build or
installer was executed. No native binary bytes were read. Only this temporary
review was written.

## Frozen helper and input scope

| File | SHA256 |
| --- | --- |
| fastapi-next-openapi-response-field-pre-runner.py | 86b309b61b3983281b233c0660c2731c43b44cdc7ed3245f5cb8d4ac15e2d048 |
| Prior fastapi-additional-response-field-pre-runner.py | 9cadec4ae67d0fd5dfe581acce5dedb445365733220f7aef2e001a804f471a53 |
| Imported fastapi-lazy-dependency-coverage-runner.py | 4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5 |

A byte comparison after the three prescribed literal substitutions makes the
old and new runners identical: one output-directory string and the two family
strings. No executable control flow changed. The new selection is exactly one
whole ASGI workflow, `next-openapi-response-fields`, with `api=False`; there is no
case filter, special target dispatch, old-result union or coverage export.

Static reads of the admitted input/index reconcile **three ordinary parity
cases / 19 HTTP actions / three construction observations**. The case order and
case-contract order agree; every contract has parity mode and nonempty requirement
references. Indexed file hashes match actual admitted bytes:

- Input: `558a3d9cde89de0fd8342fe9a04deaef08a3caac836f5afd3a1b16d0c6829767`
- Recipe: `e1243762e877e182bffadeb4eed6668d852bfb4d1bc31f8c98a7cceb9f8ce132`
- Workload: `d1c2824c616533127910a459075af4b020e6e97a8d9f260dd838d3b0ef7733bf`

The utility module is loaded under `lazy_coverage_helpers`. Its guarded `main`
does not run on this import; the pre runner uses only hashing/extension-path
utilities. Importing it does not activate its separate fault/LLVM lane.

## Source gate and canonical receipt behavior

The runner delegates to canonical `oracle`, `target` and `compare` commands.
Within its sole family, target execution follows the complete oracle artifact
check. Source exit must be zero; source case cardinality/order must equal the
declared workflow; all three cases must complete with construction outcome `ok`;
and every planned action must be present, ordered and completed. This gates all
19 actions, including the public handled hook error and retry/cache actions.
It does not assert expected HTTP bodies, warning messages or schema documents.

Canonical CLI/workers independently validate schema, current input/workload/
manifest digests, exact case order, Python/package pins, source locations and
target imported module/distribution locations. The oracle checks clean pinned
FastAPI/Starlette source revisions. The target verifies Cargo's sibling source,
the imported native pair and a normal build. Schema 9 with no fault cases requires
`fault_injection_compiled == False`; oracle fault injection is N/A. The comparator
checks these identities and compares the unchanged selected observations.

Each subprocess's full stdout/stderr log and command/result are retained. If both
products exit zero, comparison is always attempted. Canonical compare writes its
immutable artifact before returning exit 1 for mismatches. The helper retains
that result in `normal-runs.json`, writes the final snapshot and checks identities
before its own final exit 1. A genuine parity failure is therefore preserved,
not normalized into a pass or discarded because it exits nonzero.

The output directory is newly created with `exist_ok=False`; canonical artifacts
use exclusive creation. No earlier closed receipt is replaced. A source gate
failure stops target and may leave only the initial snapshot/logs/canonical source
artifact; that incomplete directory is not successful closure. A target
infrastructure failure similarly cannot produce a successful comparison.

## Source/input/native freeze

Initial/final snapshots fix both FastAPI-RS and pinned Starlette-RS whole source
trees using target_worker's exact tracked/nonignored hashing rule. File paths,
file bytes, symlink targets and deleted tracked files participate. Tracked
metadata, manifest, recipes, workload and generated contract changes therefore
change the source digest. The selected materialized JSON input is separately
hashed even though ignored.

Both installed native extensions are uniquely selected and hashed into the same
named pair used by target_worker. Every target command's reported combined
source-tree and native-pair digests must equal the initial snapshot. Any
initial/final change or identity mismatch prevents successful closure. Original
Python oracle source is not included in these two target-tree snapshots; its
clean pinned revisions/import locations are independently enforced by the
canonical oracle worker.

There is no per-stage snapshot or build-configuration receipt in this pre helper.
Initial/final equality does not detect a transient edit restored between those
checks. Parent source/input/environment/binary freezing remains required. The
native pair identifies the installed files and actual imports, not a reconstructed
compiler invocation or clean Git-state assertion. This is a normal parity
diagnostic, not a coverage or benchmark measurement.

## Required inherited launch environment

Launch must retain:

`STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65`

The runner passes that path explicitly to target but otherwise inherits the
environment. Source and comparator manifest/API-contract checks resolve sibling
artifacts via this variable; target's flag does not bind those checks. Retain
`PYTHONDONTWRITEBYTECODE=1` and the prepared pinned environments; keep the normal
installed extension fixed. No profile collection is requested by this helper;
inherited LLVM profile configuration should not turn this into a measurement.

## Clearance and subsequent audit

No concrete orchestration, whole-workflow gating, result-shaping or builder/
installer blocker was found. Static clearance is conditional on the inherited
sibling pin and parent freeze. This review claims no source/target completion,
passing cases, current binary equality or live first divergence. After closure,
the actual artifacts, fixed snapshots, all three constructions/19 actions,
identity/hash bindings and selected mismatches require a separate read-only
evidence audit. No expected outputs were introduced.
