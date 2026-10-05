# Independent response-status / automatic-422 v2 patch review

2026-10-05. Read-only review of frozen prospective files, not the moving active
integration. No build, formatting, product import, app/parity execution, sibling
change or active-file edit. This is bounded static clearance; compilation and
fresh live gates remain the parent’s responsibility.

## Exact reviewed files

All files are under `/private/tmp/fastapi-rs-openapi-validation-response-native/`.

| File | SHA256 |
|---|---|
| `base/application_runtime.rs` | `d1bdcd3f66118c38df96fbb75528264d298335d27f2ca275dcc699bdc4a280a2` |
| `base/openapi.rs` | `da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7` |
| `prospective/application_runtime.rs` | `8847050134c52f21cadd77d911e68cc63311deba7ea4be58a05e9a7bed3d436f` |
| `prospective/openapi.rs` | `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d` |
| `native.patch` | `e06e0f074f9e5b98f0538891522cd745f68a3f44e2bab2f6e835bb8b5dcd4afc` |
| `author-review.md` | `bc72cd611db3c8919379e812ac9bbe5f72e78093b42387c75690f2280608157f` |

The full v2 patch was read against these saved bases. A direct v1/v2 text diff
contains only the status-text fallback callee-order correction: obtain the bound
`http.client.responses.get` before invoking `int(raw_status)`. No other v2
executable delta was found. No moving active-source equality is asserted here.

## Bounded result

No concrete new ownership, logic or call-order blocker was found for the four
selected ordinary description-only cases. Pinned source `routing.py:1038–1054`
and `utils.py:26–40` keep the raw extra key, test model first, and perform body
eligibility/name/serialization-field construction only for a truthy model. The
new owner/clone preserves that raw object. None and case-sensitive range/default
membership precede `int`; integer eligibility has no u16 upper bound. Primary
status handling is untouched. The existing dict and explicit nonempty
`description`/`model` policy remains restricted.

Pinned `openapi/utils.py:474–516` canonicalizes with the first `str(...).upper()`
and DEFAULT→default before mapped field lookup, then evaluates a second
str/upper range lookup or HTTP-status get/int expression even when explicit
description wins. The v2 bound-callee correction matches Python evaluation
order on that fallback. The retained schema batch, field names and final private
model/encoder are unchanged. Python-owned canonical keys now feed actual PyDict
get/set rather than a prematurely converted Rust String.

The extras-first dictionary assembly and short-circuit membership checks for
422/4XX/default match the selected source decision at `openapi/utils.py:517–536`.
This also consults the actual primary key rather than only the explicit status
flag. It preserves ordinary validation-request handling, which is independent
of documentation response declarations.

New Python protocol calls run in existing attachment/projection phases outside
application/cache borrows. Snapshot clones keep owners; included branches still
prepare a whole bundle before publication. `materialize_included_response_fields`
retains prepared owners across publication checks and drops replaced states only
after releasing the mutable borrow. No new callback/drop under a borrow was
introduced by this patch. Failure routing uses existing Rust scopes. No unsafe,
new dependencies, facade/public binding/signature change, fixture/case dispatch,
expected document or original FastAPI runtime import occurs in the diff.

## Boundaries that remain

- Current four inputs have no truthy extra models, so the new raw body helper,
  model range names and adapter behavior need independent positive/negative gates.
- Source raw `response_fields` dictionary hashing/lookup and setdefault/schema/
  status-text interleaving differ from the retained Vec/snapshot projection.
  Custom mutable key callbacks, schema callbacks changing records, reentry and
  module-global status-range mutations are not covered. The fresh range table
  does not reproduce mutable source-module history.
- Full response deepcopy, recursive dict/list merge, content/headers/links/
  extensions and empty/fallback descriptions remain outside the existing policy.
  Overlapping modeled responses can still replace schema rather than deep-merge.
- The global `or_insert` definition policy remains a known source difference:
  source path-local canonical validation definitions later overwrite global
  user-name collisions (`openapi/utils.py:323,530–535,646–647`). No collision
  correctness claim is justified here.
- Optional/body-only/empty-model flattening, include/model-range input families,
  handler histories, multi-method grouping and primary u16 representation remain
  separate boundaries. No full OpenAPI or arbitrary-key protocol claim follows.

The actual PRE counts are source4 successful constructions/24 requests versus
target2 successful constructions/12 requests plus2 ordinary constructor errors
and12 planned action not_run; those are retained failures, not injected faults.
Fresh selected4, whole regression and separate direct API gates are required
before stating measured parity.
