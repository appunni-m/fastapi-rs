# Inline query schema: source/native risk and minimum design

2026-10-05. Source/Rust-text reading only at d50887853d382bd9d9e03c7e82a504614ff02aba.
No binaries or apps imported/read/executed, no build/install/unit framework,
active edit or patch. Authoring the two-case input is not independent admission.
Another reviewer must admit it and source-first two constructors/eight actions
must close before any native correction is authored or claimed. Existing parent
normal214/current measurement gates remain separate.

Pinned FastAPI0.141.1, Python3.12.13/Pydantic2.13.4 and Starlette1.6.0 remain;
Pydantic source is cf67d4b3193c3fe43ede18612ed62785eee11382. Source/native file
bindings used by this static review:

| File | SHA256 |
|---|---|
| pydantic/json_schema.py | `75ade143dbd03cb1213ecac39d49628df4357ee0825621959d4cceac064b803b` |
| fastapi/_compat/v2.py | `b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9` |
| fastapi/dependencies/utils.py | `13693375ab95e32424e5434c21f928463634af5ee1261cf3e04031381bdf47d9` |
| fastapi/openapi/utils.py | `81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527` |
| fastapi/openapi/models.py | `b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d` |
| fastapi/encoders.py | `4cc09230eca6435892f6bc25a2185e214dbedfe994d5103feb63ad269137caad` |
| application_runtime.rs | `0cd89081d79ca2d59b94e01839eb5e5e30778f18683c86822919a054e03bca11` |
| openapi.rs | `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d` |

## Actual stage trace

1. Source dependencies/utils.py:492-535 creates Query with the actual ordinary
   default, then passes that FieldInfo/default to create_model_field. Both
   direct and Depends-owned declarations reach this same field path. Missing
   default and actual None are distinct.
2. Source _compat/v2.py:141-167 decomposes FieldInfo, reconstructs Field from its
   attributes/default, then builds TypeAdapter(Annotated[...], config). Adapter
   construction is at registration, with the specific source warning filter.
   The default is part of its core schema, not late document decoration.
3. Pydantic json_schema.py:1173-1233 calls generate_inner, obtains static default,
   uses encode_default and appends its encoded value. Validation mode does not
   take the serialization-mode plain serializer branch. encode_default:2332-2358
   calls TypeAdapter(type(default), config).dump_python(mode=json) where needed,
   then pydantic-core JSON conversion; raw user objects are not equivalent to
   these encoded defaults. NoDefault/default-factory behavior and serialization
   refusal warnings belong to Pydantic.
4. Pydantic generate_definitions:384-399 returns each mapped input without sort;
   only definitions are sorted. FastAPI _compat/v2.py:254-282 then obtains the
   effective alias/mapping and assigns its title on nonref schemas. The source
   title assignment can replace an existing inner title; it is not globally a
   missing-title-only rule. Plain selected names have no competing titles.
5. Source openapi/utils.py:160-235 inserts mapped schema into the parameter dict
   unchanged. OpenAPI paths PathItem|Any (models.py:425-427), the actual final
   OpenAPI model and encoder decide wire. Encoder.py:243-258,281-315 excludes
   None dictionary values at final encoding. Pre-dropping None before schema
   generation therefore is not a source-stage substitute, even if some final
   wire data later omits it.
6. Current Rust CallablePlan builds a request validation adapter at
   application_runtime.rs:6040 from constrained annotation. For ordinary plain
   parameters constrained_parameter_annotation:7945-8013 returns bare type;
   their default is owned separately. A Query marker can already contribute a
   Pydantic Field(default); flattened model fields reconstruct FieldInfo. Do
   not assume every current annotation is bare.
7. ParameterOpenApiPlan at1653 and openapi_parameters_with_model_fields:6411-6477
   copy annotation/config/default, but filter actual None out of ordinary
   schema defaults. openapi_operation:4121-4148 creates another annotation-only
   adapter and passes title separately. pydantic_schema_from_adapter:8425-8477
   copies mapped keys, adds transported $defs, and adds title if absent/nonref.
8. openapi.rs:233-248 normalizes with preserve_defaults=false, recursively sorts
   against Schema field order, then inserts the separate raw default after
   title. normalize_schema:806-855 also handles refs/default stripping/binary
   and numeric adjustments. Removing its sort alone leaves the earlier title
   and late raw default; moving literal keys recreates a wire heuristic.

## Smallest generic correction to consider after the gate

Keep request validation/scheduling untouched. Add one private parameter-schema
assembly helper at the existing owned OpenAPI operation boundary:

- Carry ordinary actual default owners, including Some(PyNone), in the plan.
  Rust None means required/no declared default only. Never coerce default to a
  Rust scalar, evaluate its truthiness or pre-serialize it. Preserve annotation,
  metadata/config and title provenance.
- When the plan provides a static declared default, append a public Pydantic
  Field(default=raw) to an Annotated annotation before TypeAdapter generation.
  Public Pydantic owns merging with an existing Field/default and the encoded
  JSON schema; flattened model FieldInfo annotations already carry defaults.
  Whether to reconstruct a full FieldInfo instead needs separate lifetime/
  metadata evidence; no duplicate Field/default or factory claim is implied.
- Generate in validation mode through the existing private source-compatible
  GenerateJsonSchema class. Preserve its returned field mapping. Apply the
  plain fallback title after generation; do not put fallback title into an
  early Field or inject default into the completed wire dictionary. A full
  outer-title/alias overwrite repair requires FieldInfo provenance, beyond the
  selected plain names, and should not be silently bundled.
- The wire parameter should receive a complete generated schema. Remove its
  separate late raw-default injection; there is only one OpenApiParameter
  constructor (application_runtime.rs:4139). Remove that redundant field or
  mark defaults as schema-owned, so an encoded omission cannot be overwritten
  by a later raw value.
- Preserve the generated inline dictionary's keys/values directly. Retain
  definition collection from its transported $defs and remove only that
  internal wrapper from the embedded field schema, using an ordered shallow
  copy if needed. The generator's ref_template is already the component path;
  its bytes override already owns binary behavior. No new recursive wire
  visitor, final key-ranking sort, schema key list or fixture predicate is
  needed. Keep components/body/response normalization and final OpenAPI model
  pass unchanged unless an independent source gate authorizes those changes.

This is a generic production parameter-schema seam, not a primitive-type/name
whitelist. It fixes generation/default ownership first and preserves the
resulting mapping; the two-case wire oracle will determine actual effects.
A broader retained input ModelField plus shared validation/serialization batch
would match source lifetime/hooks more fully, but is not a minimal order repair
and needs independent metadata, warnings, hook order and model-definition gates.
Do not advertise the small helper as that architecture.

## Risk, ownership and required proof

A schema helper is allowed to invoke public Pydantic Field/TypeAdapter methods
from Rust. Python runtime files remain literal native re-exports; no Python
helper/eval/control flow or original FastAPI runtime import. Use owned Py values
and short Bound references, fallible tuple/dict construction and PyResult/?;
no unwrap/unsafe/lint blanket. Execute adapter/default serialization/title work
outside app/cache locks and native borrowed route state. Preserve successful-
only schema publication; an error/warning is observed, not bypassed by a second
schema path. Release failed temporary schema/adapter/default owners outside
those borrowed sections. Request adapters and worker validation remain as-is.

Default Field may already be inside constrained or flattened annotations; its
merge/title/default_factory behavior must be inspected during implementation,
not dispatched by fixture shape. Another TypeAdapter at documentation time is
an existing lifetime gap relative to retained source adapters, and the current
per-field generator is not source shared-batch hook order. Arbitrary metadata
or hook histories are outside these two simple signatures.

Dropping the parameter normalizer changes more than key order: constrained
numbers, refs, nullable containers, bytes, model fields and transported defaults
need prior normal214 regression alongside the fresh two-case gate. Keep the
old nonparameter paths intact. Pydantic may emit serializability warnings or
raise for broader defaults; do not reinsert a default it intentionally omits.
Explicit None controls must run through Pydantic and final encoder normally.
Canonical public get_openapi subset/interfaces should remain unchanged; no
other OpenApiParameter constructor was found. This static design does not
establish new warnings/ref/alias/serializer/default-factory fidelity.

Frozen input proposal remains /private/tmp/fastapi-rs-inline-query-schema-wire-proposal-2026-10-05/
with workload016c0963..., recipe31601137..., plan446052fd... and counts2/8.
No output values/key sequence, expected schema, comparator change, normalizer
or case/backend condition is authorized. Source-first and preserved unchanged-
target receipts precede implementation, then independent patch review and the
root's normal regression/static checks precede any measurement claim.
