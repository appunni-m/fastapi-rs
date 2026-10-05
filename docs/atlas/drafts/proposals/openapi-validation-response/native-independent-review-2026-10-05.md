# Independent automatic validation response native patch review

2026-10-05. Read-only review of prospective patch against active HEAD
`a34714f47749b6f96d5d7829dc16b0d444efaa5e` and pinned FastAPI 0.141.1. No
active/author edits, app/native imports, execution, build, formatter, install or
unit framework. Source4/24 and prechange comparison receipts belong to the
parent and the separate receipt reviewer, not this static clearance.

## Frozen binding

| File | SHA256 |
|---|---|
| base_runtime | `d1bdcd3f66118c38df96fbb75528264d298335d27f2ca275dcc699bdc4a280a2` |
| base_openapi | `da0e07473764fde52d86ce36fa962e6156710b3de73007c4607d7fa2c8f0dfd7` |
| prospective_runtime | `8847050134c52f21cadd77d911e68cc63311deba7ea4be58a05e9a7bed3d436f` |
| prospective_openapi | `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d` |
| patch | `e06e0f074f9e5b98f0538891522cd745f68a3f44e2bab2f6e835bb8b5dcd4afc` |

Both base copies equal active files; recomputed unified diff exactly equals the
frozen patch. Independent `git apply --check` exited 0. Compile/lint and live
parity remain pending parent gates. Source evidence is routing.py:1038-1054,
utils.py:26-40, openapi/utils.py:474-538; reviewed source identities are preserved
in the separate architecture note SHA256
`3f4131b1ecc1729f70a62252fb9f86c17120c6fe492204fea16bdb277e3c40bc`.

## Bounded clearance

No concrete selected-four blocker found.

- AdditionalResponseField retains the original `Py<PyAny>` status owner;
  clone_ref propagates it alongside the record/field through branch state and
  snapshots. None remains an actual object. The field builder removes both
  the integer-only rejection and eager status stringification.
- The existing dict assertion/metadata restriction/model read remain ordered.
  Only a truthy model calls the new helper. It checks raw None, then
  case-sensitive frozen-set membership, then int/numeric eligibility. No u16
  restriction is added. Raw status remains the assertion/name format operand.
- After the shared schema batch, additional_response_openapi first applies
  str.upper and DEFAULT-to-default, retaining its Python key owner. This
  precedes mapped-field schema retrieval; the second str.upper/range-or-int
  status lookup then runs even though the restricted explicit description wins.
  Exceptions propagate via PyResult, not fallback/skip/case dispatch.
- Wire merge uses the canonical Python key directly, retaining insertion order
  and in-place replacements. Automatic 422 moves after the complete extra loop
  and tests the actual dict keys 422, 4XX, default with ordered short circuit.
  Its response/definition group is created only when the branch executes.
- New callback work stays in field preparation/owned OpenAPI snapshots outside
  app/cache borrows; whole-branch publication, failed construction retry and
  successful-only schema cache publication remain unchanged. No borrowed key
  owner escapes, new long lock, unsafe operation or original-runtime import
  appears in the diff. Final private model/encoder and shared schema behavior
  are unchanged.

## Preserved limits

The selected four use immutable ordinary int/string keys, description-only
records, required query validation and no extra-field schemas. They gate order,
range/default admission, automatic422 suppression and real docs/request wire,
not arbitrary status protocols.

The v1 callee-order finding is corrected in v2: the helper resolves and retains
http.client.responses.get before evaluating int(raw), then invokes the saved
bound callable. The independent v1-to-v2 delta is exactly that change/comment;
openapi.rs is byte-identical. No selected-four blocker remains.

Snapshot normalization still runs before primary wire assembly/setdefault,
and does not add source deepcopy/raw-field map lookup/deep-update behavior.
These generic histories are outside selected stimuli and must remain
unclaimed; raw owner retention alone does not close them. New frozen-set
creation does not prove arbitrary hash-collision probe history.

Existing description/model-only nonempty metadata restrictions are retained.
The global schemas.entry.or_insert policy is unchanged and does not emulate
source route-local ValidationError group insertion followed by global update;
user-definition collisions have no positive gate here. Empty flattened input
models/body-only eligibility, general record merging and mutable key/record
histories remain separate. No normalizer, comparator, input, fault hook or
public classification changed in this patch.

## Review chronology

The initial patch read was v1 (78913b3e...). During final identity capture the
author advanced prospective files to v2 (e06e0f07...), so the first draft's
v2 hash table coexisted with the stale v1 callee-order finding. That draft and
its receipt are preserved byte-exact as independent-review-first-draft and
independent-static-first-draft, not presented as final clearance. This final
review reread the actual v2 helper, checked the sole v1-to-v2 semantic delta,
verified unchanged openapi.rs, and reran read-only git apply --check (exit 0).
No live/compile claim follows from either draft.
