# Prospective raw response status and automatic-422 repair

2026-10-05, version 2. Unapplied, unformatted and uncompiled native draft. Only
`application_runtime.rs` and `openapi.rs` are proposed. No workload, metadata,
facade, dependency, sibling or active source was edited; no product/model import,
build, parity stage or unit framework was run. `git apply --check` passes against
the clean admission revision `a34714f47749b6f96d5d7829dc16b0d444efaa5e`.

## Exact composition

All paths below are under
`/private/tmp/fastapi-rs-openapi-validation-response-native/`.

| File | SHA256 |
|---|---|
| `base/application_runtime.rs` | `d1bdcd3f66118c38df96fbb75528264d298335d27f2ca275dcc699bdc4a280a2` |
| `base/openapi.rs` | `da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7` |
| `prospective/application_runtime.rs` | `8847050134c52f21cadd77d911e68cc63311deba7ea4be58a05e9a7bed3d436f` |
| `prospective/openapi.rs` | `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d` |
| `native.patch` | `e06e0f074f9e5b98f0538891522cd745f68a3f44e2bab2f6e835bb8b5dcd4afc` |

Complete v1 base/prospective copies and patch are preserved under `v1/`. The v1
patch is `78913b3edcdbf5f884a2e83d96cb27af3df98b3d2f7d47f704ea032afac3ce02`.
Version 2 changes only status-text fallback evaluation: it saves the bound
`http.client.responses.get` callable before evaluating `int(raw_status)`, then
calls that saved method. Source evaluates the callee before its argument.

## Source and actual evidence

Pinned FastAPI 0.141.1 `routing.py:1038-1054` asserts each extra record is a dict,
tests its model, and only for a truthy model performs body eligibility and field
construction. `utils.py:26-40` handles None, case-sensitive set membership in six
range/default strings, then int comparison without a u16 upper bound. Extra
field names and keys retain the original declaration value.

`openapi/utils.py:474-516` canonicalizes the document key with str/upper and
DEFAULT-to-default before schema lookup. Its status-text expression at 506-508
performs a second str/upper range-dictionary lookup and, if needed, the bound
HTTP-status dictionary get with int argument, even when explicit description
later wins. Lines 517-538 decide automatic 422 after all declared responses,
testing actual merged keys 422/4XX/default. Validation definitions are added
only on that branch.

Closed unchanged-target evidence is retained under
`parity-results/openapi-validation-response-wave/pre-change/`; comparison
`6049170b-f3a8-4de8-997f-819e58a5de29` reports four ordinary failures. Source
reached four successful constructors and 24 requests. Target reached two
constructors/12 requests and raised two ordinary integer-only status errors,
leaving 12 actions unrun. The automatic integer case first differs only in
document response-key order; declared 422 also retains automatic content and
validation definitions. Query-response bytes agree in both reached cases.
The independent PRE audit is
`/private/tmp/fastapi-rs-openapi-validation-response-pre-evidence-audit-2026-10-05.md`,
SHA256 `5abc1ce3df7a4ef23dbdd4fd4c602f44afb76aafe2bed4c846f6cb75f46c81a3`.

## Native changes and ownership

- `AdditionalResponseField` retains `Py<PyAny>` status, and `clone_ref` keeps the
  original Python owner. Attachment no longer rejects integer alternatives or
  calls str on description-only keys. Existing dict/description/model metadata
  restrictions and model truthiness remain unchanged.
- The new body helper is invoked only in the existing truthy-model branch.
  It checks None, uses native Python frozenset membership, then calls builtins
  int and the same lower/excluded integer tests. No integer narrowing or custom
  key class/name test is introduced. Safe PyO3 0.29.2 new/contains APIs and their
  prelude trait were checked by source reading; compilation remains pending.
- The OpenAPI projection canonicalizes raw status before its retained field
  schema lookup, then evaluates the second status-text protocol. The six range
  labels are ordinary native-authored data; HTTP status descriptions come from
  the standard-library `http.client.responses`. The projection continues to
  require an explicit nonempty description, so that later winning description
  does not need a new fallback metadata contract.
- `OpenApiAdditionalResponse.status` owns the canonical Python value, and the
  actual response dictionary uses that value for get/set. Additional responses
  merge first; the automatic condition then uses Python dict membership in
  source short-circuit order. Primary response assembly, shared adapters,
  final private OpenAPI model/encoder and public cache service are unchanged.
- No lock or application borrow is introduced. Attachment helpers run in the
  existing out-of-borrow construction phase; projection works on owned route
  snapshots. Existing include bundle publication/retired-owner disposal stay
  unchanged. New temporary owners and ordinary exceptions use existing Rust
  scope/error routing. No unsafe, lint suppression, Python helper, source import,
  expected document or case/backend dispatch is added.

## Retained gaps and gates

This repairs the observed plain integer/range/default declarations through
generic production value handling, but the four cases do not prove arbitrary
key callback histories. Source raw dictionary field lookup/hash behavior and
interleaving key insertion/schema/status-text callbacks differ from the existing
snapshot/projection architecture. The native range table is fresh ordinary data,
not the mutable original module-global dictionary. These are separate protocol
history gaps. The saved-get correction removes an avoidable new order mismatch
without claiming those histories.

The prior explicit description/model-only policy, lack of full deepcopy and
deep_dict_update, empty/fallback descriptions, content/headers/links/extensions,
alias/include/model-range positive inputs, optional/body-only/empty-model
parameter flattening and custom handler histories are unchanged. The global
definition `or_insert` behavior still differs from source route-local definition
updates for user schema-name collisions; this unselected gap is deliberately
retained. Four description-only cases establish no adapter-cache state.

Independent reviewers must bind the final v2 hashes. Parent must apply/format,
compile with strict static contracts and perform actual native import and fresh
four-case plus unchanged regression gates before any compatibility claim.
Preserve the PRE artifacts and all failed intermediate checks. This draft alone
establishes source-backed intent and applicability only.
