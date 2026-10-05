# OpenAPI final-model bootstrap failure audit

The parent closed these stages at revision `51fa96a` as bootstrap failures.
They provide **no target parity result** and do not establish the planned
210 distinct cases. This note reads only the closed logs, saved snapshots,
ledgers, and completed oracle artifacts; it does not import applications,
launch workers, or read current native bytes.

| Closed stage | Completed oracle receipts | Oracle observations | Logged target outcome |
| --- | ---: | --- | --- |
| `post-final-model` | 1 workflow, 3 cases | 3 constructors, 19 completed actions, 64 observations | 1 worker exit 2, no artifact |
| `final-normal-v2` | 29 workflows, 109 cases | 27 constructors (6 error controls), 242 completed action records, 15 completed probes, 299 observations | 27 worker exits 2, no artifacts |
| `public-controls` | 2 workflows, 4 cases | 4 completed probes, 5 observations | 2 worker exits 2, no artifacts |

Every logged target error is `AttributeError: type object 'Annotated' has no
attribute '__getitem__'`. No target identity, construction/action result,
comparison artifact, or comparison summary exists in these receipts. The
post/control helpers subsequently report `target source_tree_sha256 differs`:
their target result has only the bootstrap-error output, so this is a
secondary missing-identity guard failure, not a measured fingerprint mismatch.
The parent reports helper exit 1 for these two stages and termination 143 for
the incomplete full suite after worker descendants were stopped.

Post/control initial and final saved snapshot bytes are equal. All three
initial snapshots bind source `1e6f76d1e6d259b365c6293fe48b072f9da4b59357918b04d8ef9c6d1f85a72c`
and native pair `c6e4596218fae7d4f296ee5cec3c27be4f0eca4fc894fdd5f05a939327f41dd9`
(FastAPI SO `c5510c2b…`, sibling SO `fd5940e3…`). The full-suite final snapshot
and `normal-runs.json` are absent; its initial plan has 44 workflows. The 29
logged completed oracle receipts cannot stand in for that full plan.

All 32 completed oracle artifacts pass their declared JSON schemas, ordered
case/action/probe bindings, input/index/recipe/workload/manifest hashes, and
recorded FastAPI 0.141.1 / Starlette 1.6.0 / CPython 3.12.13 / Pydantic 2.13.4
pins. Snapshot input aliases are matched by the exact digest, with their actual
keys recorded. These source-only checks assign no target outcome. Existing
failed `1c66469` evidence and all partial logs/artifacts remain separate.

The companion `fastapi-rs-openapi-final-model-bootstrap-audit.json` records
every inspected file digest, actual run ID, snapshot, oracle count, and logged
worker error. Its SHA256 is
`df91c842c53ec9c9a4e57dc51f53538fdfef889280e5ec376490589d9ed7d174`.
Corrected-build gates require new closed source/target/comparison receipts;
none are inferred here.
