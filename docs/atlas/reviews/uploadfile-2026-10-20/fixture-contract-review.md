# UploadFile Pydantic fixture contract review

Review date: 2026-10-20. This was a read-only review of the recipe, workload, metadata references, generated mappings, and recorded parity result. No builds or tests were run.

## Findings

The three cases in `tests/fixtures/input-recipes/parity/uploadfile-pydantic-contract.yaml` are valid input-only observations:

- `json-schema` calls `TypeAdapter(UploadFile).json_schema()`.
- `accept-starlette-base` validates a Starlette base-class instance and projects same-object and base-instance booleans.
- `reject-custom-type` validates one unrelated value whose metaclass gives `str(type(value))` and `repr(type(value))` different results, then projects the validation message.

Each recipe action is a single deterministic HTTP request with `status` and `body` selectors and exact comparison. The manifest and metadata normalize those to `http.status` and `http.body.bytes`. The workload contains no expected values or assertions; the input recipe and materialized JSON describe only the requests and observations. A search of the pinned FastAPI tests found no matching `TypeAdapter(UploadFile)` test, and the workload contains no copied upstream test body.

The recorded comparison `parity-results/comparisons/f3dbbcda-ffd2-4ba1-962b-e41fafb7eb0b.json` completed all three cases with 3 passed, 0 failed, and no infrastructure errors. The oracle result identifies FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, CPython 3.12.13, Pydantic 2.13.4, and pydantic-core 2.46.4. The target result records FastAPI-RS revision `ea37e85d74189ee56377dd4a2ba4cd293d44a92a`, Starlette-RS revision `4139a72449bf5751e8902fb1c7175ee7f191d338`, source-tree digest `be4ded95f19e6f0ca4b9093758f109a77644b565371c9e54e4cbb84ed2feb477`, and target-binary digest `58891a61cfe5bf9385781b6ce88d75e9e5fe6f0d15561b801fc2b78a44a7f62a`. Both workers reference the same manifest, input, and workload hashes. The exact selected responses match the oracle: the JSON schema contains `type: string` and `contentMediaType: application/octet-stream`; the accepted instance reports both booleans true; and the rejected custom type reports `custom-str-type` in the validation message.

The result is snapshot-specific. At the reviewed checkout, `HEAD` is the target revision recorded in the result, but `fastapi-rs/src/datastructures.rs` has a working-tree change from `repr()` to `str()` in the invalid-type diagnostic. The passing diagnostic case therefore should be attributed to the recorded target source/binary snapshot, not to the commit hash alone.

## Mapping and scope

`metadata.yaml:15604-15658` links all three case IDs to `fastapi.datastructures.UploadFile`, marks the target contract partial, and describes the selected schema, base-instance acceptance, and custom-type diagnostic slice. It explicitly leaves the broader invalid-input matrix, class/member annotations and documentation, and alternate storage modes unverified. This wording does not claim exhaustive Pydantic behavior. For precision, the “custom type” claim means one deliberately selected non-Starlette value and its projected message, not the validator's full diagnostic surface.

The generated materialized index records the workflow and matching recipe, workload, and input hashes at `tests/fixtures/materialized-input-index.json:40350-40382`; its source-item coverage mapping is `partial` and names the three cases plus the same two normalized selectors at `:73575-73588`. `tests/fixtures/fixture-backlog.json:83764-83777` likewise records a partial three-case sample with those selectors. The generated references are internally consistent with the manifest and the metadata fixture refs.

One evidence-mapping caveat remains: every recipe case names only `docs/en/docs/reference/uploadfile.md` as `upstream_documentation`, so the generated `requirement_refs` point to `source:documented-page:reference/uploadfile.md`. That page documents the import, route-parameter use, and class member list; it does not document direct `TypeAdapter` JSON Schema generation, acceptance and identity preservation for a Starlette base instance, or the custom-type validation message. The FastAPI source does contain the relevant Pydantic hooks at `../fastapi/fastapi/datastructures.py:132-150`, and the symbol-level metadata source evidence already covers the class at `metadata.yaml:15614-15619`. However, the per-case source evidence and generated requirement mapping do not currently express that source-backed contract. Keep these cases linked to the UploadFile source contract, or split them from the documented-page mapping so the generated index does not imply that those details are documented on the reference page.

## Review conclusion

The cases are structurally sound, output-free, selector-aligned, and supported by a passing identity-recorded comparison for its captured target snapshot. The partial-contract wording is appropriately bounded. The source-to-requirement mapping should be clarified before using these cases as evidence for the documented UploadFile reference page's behavior.
