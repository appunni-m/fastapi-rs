# Additional response fields: formatted integration review

2026-10-05. Read-only review at active HEAD `6da823585dbe4605ff1e04204eee287813eb34e8` after parent application
of the frozen prospective patch and cargo fmt. Only this /private/tmp note was
written. No active source edit, formatter, compiler, build, native-binary read,
installation, app/factory/native import, parity execution or unit test occurred
in this review. Parent-controlled compilation/live gates remain separate.

## Identity and comparison

Frozen patch SHA256: `fa23af094f51bfaa768be42171b341e6b185719ef6e6ee0413723e6976064cc1`.
Author review SHA256: `1cbda85a7185e5091990b2cadea9be64f38737814850456aaeabcfedab9eea10`.
Independent prospective review SHA256: `3a442168444b9327a01f41ac99afac2820cb087c7003920962c335edcad11158`.
The independent note supplies bounded static clearance, not live evidence.

| Core file | Prospective SHA256 | Active formatted SHA256 | Comparison |
| --- | --- | --- | --- |
| application_runtime.rs | `f93d808770555d206443514050530b2d30d487f7c19eff12f18c7bcef26a2f67` | `14c6f7cf93865b8cc719055587d895ae517937212d14f105a7b5e2f6e7a5dfef` | five formatting-only hunks |
| response_field.rs | `952bc9fb4510c58b2d1f173859baad8eebd31ee608a9ad22d64b25bc5fe91732` | `952bc9fb4510c58b2d1f173859baad8eebd31ee608a9ad22d64b25bc5fe91732` | byte-identical |
| openapi.rs | `28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0` | `28da4d201e060459537850eeb605c9d0b3eb2fe93224c9dfa19ac03450df24a0` | byte-identical |

The direct prospective/active diff contains exactly five hunks, all in
application_runtime.rs: wrapping two snapshot optional-ref chains, one app
snapshot optional-ref chain, an error-string constructor, a cast/error chain
and a Python format expression. Two constructors lose optional trailing commas
before their closing parentheses, and one map_err closure loses the redundant
block around its single error-constructor expression. Reading every hunk shows
no semantic code, literal or comment change. A mechanical comparison agrees
after removing whitespace, optional commas before closing parentheses and only
that exact known error closure block; visual review checks literals separately.
This comparison is not a Rust parser or compile result. The other two files are
byte-identical to their prospective copies. Current git diff --check for all
three paths exited zero. Active diff reports 380 insertions / 142 deletions;
this differs from the prospective 381 / 148 only because of formatting.

## Final construction and ownership check

- The saved decorator retains raw responses; it performs no extra parsing,
  truthiness, core hook or JSON hook until endpoint attachment. The attachment
  shallow-copies the outer dict, then visits ordered extras before callable
  assertion/CallablePlan and the primary field. Source routing.py1038-1074,
  1103-1114 has that relevant extra/plan/primary order. Each status owns an
  independently constructed ResponseField, including repeated annotations.
- Included routes retain raw declarations and Deferred bundles. Each reached
  context prepares extras before primary outside app borrows. Every own route
  bundle is prepared before the whole branch is published; failure drops locals
  outside the borrow and leaves that branch unready for retry. Parent/child
  readiness remains separate, matching routing.py1601-1624's selected branch
  behavior. No partially prepared vector is published.
- Short materialization borrows clone only input metadata/references. After all
  destinations/branch indexes are checked, publication moves owned bundles and
  retains replaced values in a retired vector. The vector is dropped only after
  the mutable app guard ends. Direct attachment declares its publishing guard
  after newly constructed field owners, so fallible registration releases that
  guard before those outer owners are destroyed. Preexisting operation-table
  partial-registration behavior is untouched.
- OpenAPI cache-hit truthiness runs after app/cache guard release. On misses,
  included bundles materialize first; app/route snapshots clone complete existing
  document/operation inputs under a short borrow. All new metadata reads, model
  inspection, retained-adapter JSON schema hooks, document assembly and ASGI root
  path/JSON encoding run outside app/cache borrows. Cache publication moves a
  complete schema under the lock and drops its retired reference afterward.
  A generation error does not replace the previous cache.
- Public openapi() and the ASGI /openapi.json branch use the same owned service;
  neither surrounds its new callbacks with an app guard. Snapshots retain extra
  adapters but do not rebuild them. Snapshot error drops only clone references
  still owned by the app; it cannot finalize a newly constructed field there.
- Raw alias fallback is None-only (pinned v2.py121-124); serialization_alias and
  explicit title use truthiness (130-133,267-279). The current alias.is_none()
  branch is correct, retaining an empty raw alias. Every non-$ref extra schema
  receives the retained field metadata/name title; the $ref branch is unchanged.
- Extra status body assertions retain Python int/comparison semantics for the
  existing integer-not-bool subset; no u16 narrowing is introduced. Runtime
  validation continues to use the primary owner only; actual response status
  does not select an additional validation field. Returned Response bypass and
  endpoint/dependency/yield control paths are unchanged.

No concrete new ordering, ownership/drop or selected immutable lifecycle3 logic
blocker was found in the formatted integration. Compile/lint and fresh parity
remain parent-owned; this note does not claim their success.

## Bounds and required evidence

Parent reports closed same-input source/unchanged-target pre3 with three complete
constructors / 15 complete HTTP actions, comparison 0 passed / 3 failed / 0
not-run at committed 6da8235. This note does not independently audit those live
receipts. Existing pre OpenAPI controls protect two selected output regressions.
After compilation, the required new3 + all prior198 + OpenAPI2 gate is 203 cases;
its actual receipts and identities must be checked separately.

Lifecycle3 makes no OpenAPI request: it exposes premature JSON-hook presence but
not positive JSON generation order/mode/title/shared definitions. The existing
TeaError gate reaches only $ref, and the descriptions matrix has no models.
Do not infer flat Annotated title/aliases or full shared-generation parity from
those inputs. Old primary/request/body/stream raw-adapter generation and shared
batching remain unchanged. Included CallablePlan/route metadata processing at
include time is a preexisting source-order/borrow boundary; the new extra field
publication does not fix it. Mutable records/annotations/routes/version refresh,
callback reentrancy, concurrency, custom mapping/status/unique-ID effects and
broader response metadata/signatures remain distinct gaps. The explicit
openapi_schema setter's preexisting retirement under its lock is untouched.
The separate pinned sibling BackgroundTasks worker ownership blocker remains.

Only /private/tmp documentation was changed by this review. The note is frozen
at the listed source identities; parent may later change them for compile/lint
repairs, which require a new readback rather than reusing this identity.
