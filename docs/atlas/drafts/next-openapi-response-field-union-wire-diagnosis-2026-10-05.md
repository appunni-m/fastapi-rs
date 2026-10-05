# Source diagnosis: OpenAPI model-versus-Any wire order

2026-10-05. Independent reviewer: `/root/dependency_records_native` (Sol).
Read-only diagnosis; no application/module import, compiler, build, parity rerun,
native-binary read or active file edit. Parent reports the frozen full normal
206-case run closed with 205 passes and one exact-byte failure. This note
independently examines that failed case, not the whole 206-case ledger.

## Actual retained observation

Comparison `13224e0d-2a94-4699-91d7-a1edac3c2864` (SHA256
`4424fd270f80732dd5e3ac6daeeb0689cd3275891369ac5fc15c291ae8d623fd`)
selects the first-ASGI workload's twelve cases: eleven pass, one fails, none
are not run. The failed OpenAPI GET observation has equal status/headers and
2057-byte bodies. Parsed JSON values are equal; exact bytes remain unequal.
The first different body byte is 206. Four dictionary orders differ:

| Location | Actual source order | Actual target order |
| --- | --- | --- |
| Three POST parameters | name, in, required, schema | required, schema, name, in |
| POST requestBody | required, content | content, required |

Source result `9de94eea-4165-42c2-a787-6f2987d92829` SHA256
`04beeddaa7b99a0ae6702acc729a139179c6de8b8475d1ab5106c32ec0774498`
and target result `10b7f4df-3ebf-42fa-9eab-096b1e256536` SHA256
`985c6bb8ddd1819ad210ce3c7fb1152b78108a04d22dd8c3dcd77552310daea7`
were independently rehashed against their comparison bindings. No selected
observation or comparator was changed. Parsed equality is diagnostic evidence,
not a substitute comparison.

## Cause: the complete path item selects Any

The pinned Operation annotations (`models.py:295–296`) have only
`Parameter | Reference` and `RequestBody | Reference`, respectively. Neither
contains a dictionary/Any fallback. The relevant enclosing union is
`OpenAPI.paths: dict[str, PathItem | Any]` (`models.py:425`).

Pinned Pydantic-core 2.46.4 explains why a valid PathItem dictionary can select
Any, despite all 22 AST declaration-order tables being correct:

1. Constructing a model from a Python dictionary lowers exactness to Strict
   (`validators/model.rs:179`).
2. Parameter.in uses ParameterInType (`models.py:222–226,259–261`). The native
   assembly and source utility provide its ordinary string value. Converting
   that string into the enum lowers exactness to Lax
   (`validators/enum_.rs:105–123`), which propagates through the nested model
   validations to the candidate PathItem.
3. Any validation retains the input object and lowers exactness only to Strict
   (`validators/any.rs:40–42`). It is not an Exact match.
4. Smart union compares exactness when either candidate lacks a model
   fields-set count (`validators/union.rs:139–156`). Strict Any beats the Lax
   PathItem candidate. A Strict model and Strict Any tie retains the earlier
   model branch, so parameter-free model-shaped inputs need not choose Any.
5. During dumping, strict model serialization rejects a raw dictionary
   (`serializers/type_serializers/model.rs:143–147,172–179`); union serialization
   tries choices left-to-right and Any uses ordinary inference
   (`serializers/type_serializers/union.rs:357–405`, `any.rs:45–47`). The selected
   raw path dictionary retains every nested dictionary's insertion order.

This is not a local Parameter/RequestBody order rule. The entire chosen path
item remains raw, including method order, operation order, responses and schema
extensions. The AST-only finalizer traversed it as a validated model and thus
introduced the four observed order changes. The new three cases can retain
the model branch because their selected dictionaries have no enum conversion;
that does not justify treating all `paths` entries as Any either.

Other explicit source Any unions have the same need for actual branch choice:
Operation.responses values are `Response | Any` (`models.py:298`), and
Components.callbacks values are a callback map, Reference or Any
(`models.py:409`). These decisions occur at their own locations. A selected
outer model does not imply every nested response selected its model branch.
Other coercions, rejected candidates, valid-field scores and Reference/model
unions cannot be reproduced by a field-order table alone.

## Correction decision and ownership

Do not preserve just Parameter/RequestBody order, globally skip paths, use a
fixture/route/parameter-count predicate, weaken exact bytes or add a
normalizer. Those approaches ignore the actual selected union branch.

The parent accepted using a private Rust-authored Pydantic model graph for the
final pass. This is the source mechanism: `openapi/utils.py:679` constructs
OpenAPI, then `encoders.py:243–258` calls model_dump in JSON mode, with aliases
and None exclusion, before the ordinary recursive encoder. Public Pydantic
create_model/typing/enum APIs may build private types from Rust-owned schema
data; no original FastAPI runtime import, generated Python helper or evaluated
source is needed. Pydantic then owns its ordinary validation, exactness,
union choice and serialization. The existing native assembly, retained response
batch, cache publication and ordinary encoder remain the integration boundary.

A hand-written enum-sensitive exactness walker would gate this witness but is
not an equivalent complete validator. Even valid dictionaries can coerce, and
candidate failures or other nested union choices change serialization. It was
considered and explicitly rejected as the production correction. No such
prospective shortcut patch was authored or applied.

TMP ownership is now coordinated: the runtime agent owns openapi_models.rs,
private model builder/registration and non-Schema descriptors; this reviewer
owns openapi_model_schema.rs (61 ordered Schema descriptors) and
openapi_model_email.rs (optional source EmailStr fallback); the integration
agent owns final-pass call sites and removal of the old recursive wire walker.
All remain prospective until independent review and parent gates.

Required normal diagnostics beyond the existing witness/new three should
exercise: a parameter-free body path that keeps model requestBody order; an
enum-bearing path with operation deprecation and multiple methods to expose
whole-path retention; and nested Response/Any selection with an ordinary
coercion/refusal stimulus. These are public semantic branches, not expected
outputs or active fixture changes. Full source model constraints/defaults/
aliases, optional email profile, namespace recursion and logger behavior must
be reviewed before claiming a complete graph.

## Source identities

FastAPI 0.141.1 models SHA256:
`b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`;
utils `81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527`;
encoders `4cc09230eca6435892f6bc25a2185e214dbedfe994d5103feb63ad269137caad`.
Pydantic-core source under `/private/tmp/fastapi-rs-pydantic-core-v2.13.4/`
declares version 2.46.4 in its Cargo manifest. Relevant Rust hashes:

| Source | SHA256 |
| --- | --- |
| validators/union.rs | `386e88e402805ba5b6ec8c315f1b9c3a3a145cf0825af988b9522ff447c5f0da` |
| validators/model.rs | `80211a6fafaedb16819fbba54c7b37627feef3613448bd950eaed912b75c4352` |
| validators/enum_.rs | `009e43c909e8d35193fb1547775e61bd8b013993fa516d41a5789aa2e24daef2` |
| validators/any.rs | `fa6fc6f2e42ae5b06da5a6800301b8988c004ba14a68cc67f242c218db0732bf` |
| serializers/type_serializers/union.rs | `9c586f3ac7e691d5fea3b3114d73ca839bee83479299ef8bc8630f633d1d4f42` |
| serializers/type_serializers/model.rs | `bf03a224757cd8c6095a169eceb2fa2039f3f8fe948c64c44b92cde8df910752` |
| serializers/type_serializers/any.rs | `e94cfe294326589e1e41b64f4ad30c3e01c145b69d67bde06bb82c38b91cbe03` |
