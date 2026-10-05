# Same-request lazy dependency overrides — reviewed contract

Source review against FastAPI 0.141.1, commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, CPython 3.12.13. This is a
reviewed implementation boundary; execution claims require fresh parity evidence.

## Source evidence

- `fastapi/dependencies/utils.py:271` (`get_dependant`) reads the selected
  callable's signature and recursively captures its complete child declarations
  before dependency execution. It captures each child's callable, raw
  `use_cache`, declared scope, and security scopes at this point.
- `fastapi/dependencies/utils.py:586` (`solve_dependencies`, edge loop beginning
  at 620) reads the provider's current override dictionary at each reached edge.
  A nonempty dictionary rebuilds the edge, including when its callable has no
  override entry; an empty dictionary retains the captured original dependant.
  The selected effective dependant then solves children and validates its inputs.
- After successful child/input solving, that loop computes the original edge's
  cache key, reads its original raw policy once, and either consumes a hit or
  classifies/invokes the already selected effective callable. First successful
  insertion is independent of policy truth. Failed edges do not suppress later
  siblings' solving.
- `fastapi/dependencies/models.py:82` defines original-dependant cache identity;
  `:138`, `:168`, and `:198` define identity-keyed classification caches (4096).
  `routing.py:1056` captures route body fields/embedding before requests;
  `routing.py:395`/`:428` use that captured request-body parsing decision.

## Required implementation ordering

1. Shallow execution nodes retain their captured original edge. On first advance,
   obtain the provider's current dictionary, select/rebuild that effective edge,
   and capture its full child declarations. Initialize each child's effective
   override only when the child is reached. Retain the selected parent plan,
   callable, and prepared arguments through child execution and async resumes.
2. Refresh whole-dictionary assignment as well as in-place mutation. Release
   application borrows before signature hooks, policy callbacks, user calls, and
   async continuation. A dictionary cloned for an entire invocation is stale
   after `app.dependency_overrides = {...}`.
3. Remove eager effective-tree reanalysis/classification from the synchronous
   pre-scan. An earlier policy may repair a later invalid override or replace a
   later synchronous callable with an async/yield callable. The no-dependency
   route can retain a direct path.
4. Keep children and validation before the original edge's policy/cache check,
   including on cache hits. Execution classification belongs on the miss branch;
   source-required scope checks during initial plan construction still apply.
   Preserve first insertion for false policies, including literal Python `None`.
5. A current edge's own policy changing its override/signature does not reselect
   or revalidate that edge. Subsequent edges see current overrides. Reanalysis
   failures must occur when that edge is reached, allowing earlier effects and
   entered yield resources to be observed and cleaned up.

## Small public counterexamples

- Earlier policy replaces the entire dictionary to install a later async/yield
  override; the later edge must use that replacement.
- Earlier policy changes a later callable's `__signature__` and adds an unrelated
  override entry: the later edge revalidates the new signature. Clearing the map
  instead retains its original captured signature.
- A selected parent has ordered children A/B. A's policy changes B's Depends
  marker callable or policy after the parent's initial capture: current B keeps
  its captured outer declaration; a later fresh parent rebuild observes the
  mutation. Child override selection remains deferred to B's turn.
- Earlier policy repairs/removes a later invalid override: it must execute before
  the later override is analyzed. Use an override entry, or separate root edges,
  so the invalid callable is not part of the parent's mandatory initial capture.
- An edge's own policy changes its override; its current call stays selected,
  while a later same-original-call edge sees the new plan even on a cache hit.

## Remaining boundaries requiring separate evidence

- Mutating a callable's `__call__`, `__wrapped__`, `__code__`, or partial structure
  can interact with source classification-cache history. Ordinary replacement
  with a different callable does not prove those same-object protocols.
- Custom override providers, dictionary subclasses overriding `get`/truthiness,
  custom callable hashing/equality, non-string scopes, and direct mutation of
  exposed Dependant graphs require additional protocol/identity evidence.
- A dynamic signature does not refresh route request-body parsing, embedding,
  response-model/OpenAPI metadata, or endpoint plans. This slice must preserve
  the source's registration-time route preprocessing boundary.
- Native dependency method FunctionType/code/globals/closure/wrapper reflection
  exclusions remain independent of this scheduler change.

## Implementation review

The prospective runtime change was independently reviewed before integration.
No actionable issue was found within the ordinary dictionary, callable, and
query boundary above. First advance initializes once;
parent child declarations are captured before traversal while child effective
plans stay deferred; selected plans persist across awaits; completed children and
roots avoid policy rereads. Live-provider dictionary clones and resumed graph
execution hold no application borrow across user callbacks. Yield stack selection
uses the original declared scope. This was a read-only diff/control-flow audit,
without compilation, formatting, or execution.

## Reviewed independent inputs

`dependency-override-cache-policy-mutation.yaml` declares 18 source/target parity
cases and one target-only cleanup fault contract (36 public actions). It covers
whole-map replacement/removal, awaited changes, newly selected coroutine/yield
calls, captured child declarations, cache-hit revalidation, validation failures,
late malformed signatures, cleanup, and public reset/recovery.

The malformed-signature input uses an independently authored callable instance
with a deterministic public `repr`. The live error class and untouched message
remain exact response observations. CPython 3.12.13 `inspect.py:2547–2560` parses
a string `__signature__`; `_signature_fromstr` at `:2255` raises `ValueError`
using that callable's representation. No address normalization or fixed expected
error output is used. The initial function-based attempt produced a live
address-bearing `ValueError` and is retained as an unsuccessful oracle receipt
in `parity-results/oracle/bb364063-eb15-4065-b64b-df912b7aab15.json`.

The corrected source-only oracle receipt
`parity-results/oracle/66216c66-c680-484e-a730-0c8750580d86.json` completed all
18 parity cases without product or construction errors; the fault contract is
not applicable to the oracle. The negative case observes the exact public
error response, entered resource cleanup, public override reset, and a successful
later request. Target agreement requires the separate fresh differential run.
