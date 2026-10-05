# Worker dispatch and callable classification

The independent proposals now have active copies under
`tests/fixtures/input-recipes/parity/` and `tests/fixtures/workloads/`:

- `dependency-callable-classification`: 23 parity cases / 54 actions.
- `worker-dispatch`: 18 parity cases / 54 actions.

The authored copies here preserve proposal history. During admission, the active
classifier recipe added handling-errors source evidence and ordered HTTP headers
so its inherited handler links satisfy the reviewed contract. Neither copy has
expected outputs or copied upstream tests.

The native classifier, once-await behavior, ordinary endpoint worker dispatch,
response validation context, loop serialization, and ordinary ASGI body field
shape are integrated. Formatting, strict Clippy, and the Python facade check pass.
The selected classifier and normal regression gates passed on measured revision
4b4a18c; see `../generator-awaitable-native-contract-review-2026-10-05.md`. The
complete worker gate remains blocked below. Classification history, mutable
descriptors, unselected await protocols, response adapter construction/reuse and
mutable placeholder provenance remain separate boundaries. Retained response
fields and immutable response-class precedence are now measured at `ebcdf2d`;
see `../response-field-native-contract-review-2026-10-05.md`.

## Confirmed sibling blocker

The worker workflow's target process panics when a sync endpoint adds a background
task to the loop-created pinned Starlette-RS collector. The latest committed
sibling also retains the same thread-bound task classes. The entire 18-case worker
gate remains unpassed; a crashed process is not partial passing evidence.

A minimal sibling patch and safety review are in
`../sibling-background-cross-thread/`. Strict Clippy accepted the proposal in an
isolated checkout. The configured pin and installed sibling remain unchanged;
live parity and an approved new dependency revision are still required.

## Completion gates

1. Regenerate atlas, manifest and index; run metadata, fixture and static checks.
2. Observe the pinned oracle and compare every declared observation in isolated
   identity-checked processes, retaining failures and unsupported cases.
3. Run existing regression selections and the separate target-only cleanup fault
   contracts on fixed inputs, source and binaries. Ordinary input-triggered worker
   errors are parity evidence, not injected-fault coverage.
4. Remeasure accepted coverage on this revision with matching flags/features.
   Normal and fault-enabled instrumentation remain separate lanes; do not union
   old revisions or infer per-case region attribution.
5. Benchmark equivalent workloads after their callback, validation, serialization,
   cleanup and raw-message gates pass. Keep adapter/lifecycle and sibling gaps
   explicit when interpreting results.

Full FastAPI compatibility remains unfinished.

## Reviewed next inputs

- `generator-awaitable/`: preserves the historical 13 cases / 40 actions and
  reviewed patch. The active workflow has 15 cases / 47 actions after two public
  Future-error controls were added without workload changes. Native integration
  and all 15 comparisons passed as part of 175 selected regression cases at
  4b4a18c. Generic throw arity, audit hooks and unselected protocols remain gaps.
- `response-field-lifecycle/`: historical 16-case / 61-action inputs and native
  design are retained. Active copies now cover registration-time adapters,
  retained reuse, metadata, schema errors/warnings and immutable direct/included
  response-class precedence. Native implementation passed all 16 comparisons
  within 191 selected normal cases at `ebcdf2d`. Dynamic refresh, concurrency,
  raw proxies and wider field traversal remain separate gaps.
- `response-field-traversal/`: historical independently reviewed seven-case /
  42-action inputs cover whole-branch failure/retry, parent/child field order,
  full/partial matches, misses, redirects and returned-Response setup. Normal
  user exceptions provide the failure stimulus; no fault hook or expected outputs
  are present. Active copies and 65 precise links to 11 existing public
  operations are admitted. All seven passed on the unchanged Rust implementation
  within 198 selected normal cases at `9c29938`; fresh normal instrumentation
  added 213 verified regions. See
  `../response-field-traversal-contract-review-2026-10-05.md`. Terminal405,
  dynamic refresh and workers remain outside this gate.
- `response-field-recovery/`: independently reviewed inactive three-case /
  30-action follow-on covers retained parent fields after child failure,
  independent contexts of the same original router and warning-filter restoration
  inside the public handler. Its canonical-loader YAML merge issue was corrected
  without changing the active loader. The fault companion is a feasibility note
  for the existing RuntimeError/500/later200 contract; it makes no cache assertion.

- `additional-response-field-lifecycle/`: historical independently authored
  three-case / 15-GET-action inputs observe saved-decorator attachment, separate
  original/left/right field construction, second-extra ordinary hook refusal
  and full branch retry. Active copies are byte-identical; reviewed metadata adds
  26 precise links to ten existing operations, including public Request injection.
  Registration of the handler is exercised in all three cases; only retry invokes
  it. The isolated pinned source completed; the unchanged target failed all three
  comparisons. The owned Rust field-bundle repair at `827612f` then passed these
  three within 203 selected normal cases. Fresh instrumentation added 105 regions;
  the separate six fault contracts and all seven benchmark workloads also passed
  their gates. See `../additional-response-field-native-contract-review-2026-10-05.md`
  for the mixed timing results and exact identities. Defined JSON hooks expose
  premature calls only; positive OpenAPI phases/shared definitions and included
  dependency-plan timing remain separate gates. Independent input, source/native
  design and orchestration reviews are preserved here.

- `next-openapi-response-fields/`: independently authored and reviewed three-case /
  19-HTTP-action inputs are admitted with 19 links across seven existing operations.
  They retain exact body bytes, complete documents, raw sends, warnings and errors
  for retained hooks/shared definitions, Annotated metadata versus generated outer
  titles, and ordinary JSON-hook refusal/public retry/cache. Request invocation is
  mapped only to retry; all three register handlers. Inner Annotated Field metadata
  does not establish nondefault outer FieldInfo title/alias branches. Fresh pinned
  oracle and unchanged-target receipts completed all three cases and 19 actions,
  recording three parity failures. The retained-field patch, private Rust-authored
  OpenAPI model graph and pinned-build correction now pass these three within
  210 declared normal cases, with separate fault, coverage and benchmark evidence.
  The [measured report](../openapi-final-model-native-contract-review-2026-10-05.md)
  retains the failed stages and remaining legacy schema key-order gap.
  No expected outputs, private field mutation or comparator normalization is used.

- `openapi-validation-response/`: independently authored and reviewed four-case /
  24-HTTP-action proposal for automatic validation responses and declared
  `422`/`4XX`/`default` responses. Whole documents, exact sends, query validation,
  constructor outcomes and all 28 warning phases are selected. The authored copies
  remain in the historical proposal folder. Reviewed copies are now admitted to active
  inputs with 24 fixture links across six public APIs. Canonical regeneration and
  the four-source-construction / 24-action gate precede unchanged-target diagnosis;
  the unchanged target failed all four cases. The native correction now passes
  all four within 214 distinct normal cases, with separate fault, coverage and
  benchmark evidence. See the
  [measured report](../openapi-validation-response-native-contract-review-2026-10-05.md).
  This covers the selected description-only declarations, not modeled ranges,
  arbitrary key callbacks, full response deep merge or schema-name collisions.

- `inline-query-schema-wire/`: independently authored/reviewed two-case /
  eight-GET-action inputs for direct and async-dependency default-bearing query
  fields. Byte-identical active copies are admitted with 14 links across eight
  existing public APIs. Raw document/endpoint response bytes, whole documents,
  ordered send types, errors, construction and ten warning phases are selected.
  The public journal retains prior lossless sends and document-object identity;
  the final response cannot recursively include its own send/exit. Canonical
  admission and source-first reachability precede unchanged-target diagnosis.
  No parity or implementation claim follows from admission. Array/items schema
  ordering, metadata/hooks/factories, custom defaults and broader field lifetimes
  remain separate gates.

Both historical proposals passed recipe-loader/Ruff admission and independent
static review; their authored copies remain outside active inputs with no
expected outputs. Awaitable and response-field lifecycle active copies are
admitted and measured. The traversal follow-on has its own independent static
review. Historical authored copies remain outside active inputs; active traversal
copies now have fresh live receipts. The recovery follow-on still requires its
own reviewed mappings and live observations. Positive OpenAPI retained-hook,
shared-definition, generated outer-title and cache retry behavior now has bounded
live evidence. Selected automatic validation-response/status-key behavior now
has fresh live evidence. A separate independently reviewed two-case raw HTTP
gate is admitted for default-bearing direct/dependency query schemas; it awaits
source-first live evidence. Existing structural selectors remain unchanged.
