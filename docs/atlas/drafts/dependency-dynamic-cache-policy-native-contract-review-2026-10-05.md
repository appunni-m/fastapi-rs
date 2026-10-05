# Dynamic dependency cache policies — reviewed contract

FastAPI 0.141.1 captures the raw `use_cache` object during dependency analysis
(`fastapi/dependencies/utils.py:271-347`). Solving resolves children, validates
the edge's inputs, skips failed edges, then evaluates truthiness once before
cache membership (`:640-680`). Even a false policy can populate an empty cache;
later results do not replace its first value. Cached parents still resolve
children and validate their own inputs. Endpoint input validation follows
dependency solving. Parameterless declarations omit the supplied policy and
use literal True (`:130-145`).

Native plans must retain the captured object identity without coercion.
Mutating that object affects later decisions; replacing a declaration's field
does not replace the original outer edge policy. Overrides retain that outer
policy and cache identity while rebuilt children capture their own policies.
Truthiness errors propagate through the existing yielded-resource cleanup,
and an await/resume must not evaluate the same successful edge twice.

The independent `dependency-dynamic-cache-policy.yaml` inputs project policy,
validation, invocation, identity, and cleanup traces through public HTTP
interfaces. They cover synchronous and asynchronous edges, nested child
mutation, overrides between requests, failed edges and successful siblings,
`__bool__`/`__len__` failures and recovery, and app/router/route parameterless
declarations. Its existing post-resolution injection is target-only fault
evidence and cannot count as an oracle parity pass. Recipes contain no expected
outputs; execution claims require fresh identity-checked results.

Eager override analysis remains a separate gap: a policy on an earlier edge
can mutate `dependency_overrides` and affect a later edge during the same
source request, while native graph construction currently rebuilds the later
edge early. Same-request override-map mutation, signature/property access
counts, mutable callable-classification caches, custom callable hash/equality,
and arbitrary OAuth-scope execution are outside this bounded slice.
