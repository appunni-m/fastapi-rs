# Remaining legacy inline schema order: bounded diagnosis

2026-10-05; lightweight static reading during live benchmark freeze. No apps, model imports, builds, parity runs, large evidence parsing, active edits or native reads. This note is separate from the inactive automatic/additional-422 proposal.

## Preserved observation and exact scope

The frozen normal evidence note (`/private/tmp/fastapi-rs-openapi-final-model-normal-evidence-audit.md`, SHA-256 `9ac20df6bc4e25c1bcc6c1f33222ef542118740ea65d01fae59f0e33fefd50ca`) records 29 old map-order differences reduced to 11, all in `fastapi.dependencies.tutorial-review.openapi-projection`. The supplementary receipt (`b035bad13be33ae7f9203537a71121699133e73551bc11c9033341e63811001b`, lines 544–706 read as text) identifies:

- `/library/`, `/members/`, `/catalog/class/`, `/catalog/untyped/`, `/catalog/inferred/`: `skip` and `limit` inline query schemas, ten occurrences.
- `/search/`: callable-instance dependency's `phrase` schema, one occurrence.

Each has source keys `[type, default, title]` and target `[type, title, default]`; selected values/types/arrays otherwise agree. These 11 are the exact surviving subset of the old 29; the 18 Parameter container orders are repaired. The unchanged recipe selects HTTP status and structural OpenAPI pointers, not raw response bytes (`dependency-tutorial-review-upstream.yaml:337–373`), so its declared pass is truthful for that contract. This does not establish whole-document wire equality or exclude differences outside its pointers.

## Earliest visible ordering stage

The likely cause is inline **validation/input field assembly before final OpenAPI model validation**, with a concrete source/target timing discrepancy:

1. Source `_compat/v2.py:141–167` reconstructs a field's attributes, including its default, into fresh `Field(...)`/`Annotated[...]` before creating the retained TypeAdapter. `get_definitions`, lines 285–336, feeds those core schemas to `GenerateJsonSchema.generate_definitions`.
2. Pinned Pydantic `json_schema.py:1173–1187,1233` obtains the inner schema then appends encoded `default`. Its `generate_definitions:384–399` remaps each input schema without sorting that mapping; only returned definitions receive `sort(...)`. For these primitive defaults, generated input order is therefore type/default.
3. Source `_compat/v2.py:254–282` gets the existing mapped schema and, for non-reference fields, assigns fallback `title` afterward. `openapi/utils.py:187–231` inserts that schema into the parameter dictionary unchanged. This produces the observed type/default/title order.
4. Native `application_runtime.rs:4114–4148` generates parameter schemas from `parameter.annotation` and passes a title, while retaining `parameter.default` separately. `pydantic_schema_from_adapter:8377–8428` uses `generate_definitions` but attaches a missing title before the separate default reaches document assembly.
5. Native `openapi.rs:233–247` normalizes the parameter schema with defaults stripped, then appends `parameter.default`. `normalize_schema:801–850` sorts by `schema_key_rank`; the table puts title before default (`963–965`). Thus the inline dictionary already has type/title/default when inserted into the parameter document. Even removing that sort alone would leave the earlier title and late default order for these inputs.

The new final model pass (`openapi.rs:535–536`) is doing the needed source model validation/dump. Source `OpenAPI.paths` remains `dict[str, PathItem | Any]` (`openapi/models.py:425–427`), and the preserved repaired Parameter container order demonstrates these selected path values retain the raw dictionary branch. Consequently it also retains the upstream inline-schema order. The old `schema_key_rank` comment that every Schema is serialized through declared order (`openapi.rs:976–980`) is too broad for inline schema dictionaries carried inside that raw branch. A global final reorder would recreate the union-order defect already repaired.

The response owner/batch is a different path: `response_field.rs:243–305` retains actual serialization adapters, batches them through Pydantic, and applies title after mapping lookup. Reusing its architectural pattern for input fields would need explicit validation mode, source FieldInfo/default/config ownership and lifetime analysis. This diagnosis does not establish that response schemas, arbitrary metadata titles, aliases, references, serialized defaults, warnings or shared input-definition callbacks have complete source parity.

## Independent future public HTTP gate

Propose a small new input-only workload, independently authored rather than modifying the legacy selector: **two ordinary cases / two factories / eight HTTP actions**. Case data chooses public placement only: direct endpoint parameters versus the same declared values supplied by an ordinary `Depends` function. Use differently named primitive inputs with deterministic nonzero integer defaults, an empty-string default, and a nullable `None` control; use a returned public `JSONResponse` and `response_model=None` to avoid adding response-model or additional-status work.

Each case: (1) GET `/openapi.json` before executing the endpoint; (2) GET the endpoint with defaults; (3) GET `/openapi.json` again to exercise the public cached document; (4) GET the endpoint with explicit valid query values. Keep function/path declaration order deterministic. Select exact HTTP status, ordered headers and entire base64 body, ordered ASGI message types, and actual application exceptions on every action; optionally retain the whole structural OpenAPI pointer as a supplemental semantic projection. Use the reviewed public ASGI wrapper pattern to journal lossless sends and actual warning/error events without reading private routes, field caches, adapters or source internals.

No expected key sequence, expected body, source snapshot, fixture-ID branch, backend detection or normalization belongs in the recipe/workload. Source-first isolated execution supplies actual observations; unchanged target execution then establishes whether the raw HTTP gate detects this predicted discrepancy or any additional unprojected differences. Leave the current structural recipe intact. Map only exercised existing public APIs; no promotion of private `_compat.ModelField`, Schema or GenerateJsonSchema.

A future production repair should establish default-bearing validation-field generation and preserve generated inline dictionary order before the source title step, rather than globally moving keys. Plain defaults are the initial bounded gate; explicit/inner metadata titles, non-serializable defaults, serializers, aliases/references, namespace mutation and shared field lifetimes need their own source-backed inputs/design. No repair or active admission is proposed during the current measurement/benchmark freeze.
