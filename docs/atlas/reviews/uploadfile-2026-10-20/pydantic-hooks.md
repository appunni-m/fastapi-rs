# UploadFile Pydantic v2 hook audit

Audit date: 2026-10-20

## Pinned identities

The source authority pins FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, Pydantic 2.13.4, and pydantic-core 2.46.4. The oracle Python is CPython 3.12.13. These identities are recorded in `metadata.yaml:6-46`; the target runtime directly pins Pydantic and pydantic-core in `pyproject.toml:13-18` and `requirements/target-runtime-cpython-3.12.13.in:11-17`.

This is a read-only source comparison. No oracle or target process was run for this audit.

## Source contract

### Validation

FastAPI imports Starlette's `UploadFile` as `StarletteUploadFile` and declares its own subclass at `../fastapi/fastapi/datastructures.py:18-21`.

`UploadFile._validate` at `../fastapi/fastapi/datastructures.py:132-136` checks `isinstance(value, StarletteUploadFile)`. For any such object it returns the same input reference; `cast()` affects only typing. For other inputs it raises `ValueError` with the message `Expected UploadFile, received: {type(value)}`. The check therefore admits Starlette's base instances and subclasses, not just FastAPI's subclass.

The hook `__get_pydantic_core_schema__` at `../fastapi/fastapi/datastructures.py:144-150` ignores both `source` and `handler` and returns `with_info_plain_validator_function(cls._validate)`. FastAPI's v2 compatibility module re-exports that factory from pydantic-core at `../fastapi/fastapi/_compat/v2.py:32-37`.

At the pinned pydantic-core version, `with_info_plain_validator_function` builds a `function-plain` schema with a `with-info` validator function; optional schema, serialization, metadata, and reference entries are omitted when not supplied (`../pydantic/pydantic-core/python/pydantic_core/core_schema.py:2453-2497`). FastAPI supplies only the function. Its Pydantic JSON Schema hook below is what supplies a JSON Schema representation for this plain validator; Pydantic's generic `function_plain_schema` path has no input schema to fall back to and otherwise marks the plain schema invalid for JSON Schema (`../pydantic/pydantic/json_schema.py:1143-1157`).

The request form parser constructs `starlette.datastructures.UploadFile` for multipart parts with a `filename` (`../starlette/starlette/formparsers.py:225-237`); a part without a filename is decoded to a string (`../starlette/starlette/formparsers.py:190-203,238-242`). FastAPI's upload annotation detection also checks against Starlette's `UploadFile` base (`../fastapi/fastapi/_compat/shared.py:145-153`). This explains the accepted parser object and the active text-field rejection case.

### JSON Schema

`__get_pydantic_json_schema__` at `../fastapi/fastapi/datastructures.py:138-142` returns exactly `{"type": "string", "contentMediaType": "application/octet-stream"}`. It ignores both `core_schema` and `handler`; its result has no explicit `format`, `contentEncoding`, or mode-dependent branch. Field metadata or the surrounding FastAPI OpenAPI document may add outer schema structure, but that is outside this hook's returned mapping.

The class defines these Pydantic v2 hooks and `_validate`; it does not define `__get_validators__` in the class body (`../fastapi/fastapi/datastructures.py:21-150`).

## Present FastAPI-RS implementation evidence

The Python module re-exports `_core.UploadFile` (`fastapi-rs-py/python/fastapi/datastructures.py:19-23`). Rust registers it as a runtime-created subclass of `starlette.datastructures.UploadFile`, installs `_validate` and both Pydantic hooks as class methods, and publishes the class (`fastapi-rs/src/datastructures.rs:430-529`).

The Rust validator at `fastapi-rs/src/datastructures.rs:369-399` performs the same Starlette-base `isinstance` check and returns a clone of the same Python object reference. The core-schema helper at `fastapi-rs/src/datastructures.rs:401-414` calls the same pinned pydantic-core factory with `cls._validate`. The JSON Schema helper at `fastapi-rs/src/datastructures.rs:416-427` returns the same two keys and values as the source hook.

Source-level comparison indicates matching acceptance, return-reference, and schema-hook behavior for ordinary inputs. One narrow expression difference remains: source interpolation formats `type(value)` through `str()`, while Rust explicitly formats it through `repr()` (`../fastapi/fastapi/datastructures.py:134-135`; `fastapi-rs/src/datastructures.rs:387-396`). Those forms coincide for ordinary built-in type objects. A class whose metaclass supplies different `__str__` and `__repr__` behavior can distinguish them. This is a source comparison risk, not a runtime-confirmed failure.

## Existing parity evidence and selectors

| Input/workflow | Current observations | What it covers for these hooks |
| --- | --- | --- |
| `tests/fixtures/input-recipes/parity/uploadfile-pydantic-type-validation.yaml`, case `fastapi.uploadfile.pydantic-validation.reject-text-form-value` (`:8-43`) | HTTP `status` and `body`, exact comparison | A multipart field without a filename reaches an `UploadFile` parameter as a text value and exercises rejection through the route. The materialized input index contains this case (`tests/fixtures/materialized-input-index.json:40350-40369`). It does not directly observe the Pydantic core schema, the raw JSON Schema hook, accepted base-class identity, or other direct validator inputs. |
| `tests/fixtures/input-recipes/parity/request-uploads.yaml`, case `fastapi.request-uploads.request-files.openapi-schema` (`:261-302`) | HTTP `status` and the entire OpenAPI JSON document (`json_pointers: ['']`), exact comparison | Exercises OpenAPI generation for a route annotated with `UploadFile`, including the hook's schema contribution, but observes the combined FastAPI document rather than the hook in isolation. |
| `tests/fixtures/input-recipes/parity/request-uploads.yaml`, upload cases `fastapi.request-uploads.request-files-001-02.test-post-upload-file` and `fastapi.request-uploads.request-files-002.test-post-files` (`:132-217`) | HTTP `status` and `body`, exact comparison | Exercises accepted single and repeated multipart uploads through routes; response values expose selected filename effects, not whether validation preserved the parser's exact object reference. |
| `tests/fixtures/input-recipes/parity/direct-api-uploadfile-signatures.yaml`, `fastapi.direct-api-uploadfile.class-signature` (`:23-38`) | `python.signature`, exact comparison | Checks the public class signature only; it does not inspect the hook methods or validate values. |
| `tests/fixtures/input-recipes/parity/root-alias-identity.yaml`, `fastapi.root-alias-identity.http-reexports` (`:9-42`) | HTTP `status` and `body`, exact comparison | Checks `fastapi.UploadFile` versus `fastapi.datastructures.UploadFile` as one root/module identity relation. It does not establish identity with Starlette's class or the return behavior of `_validate`. |

The per-symbol reviewed overlay currently marks `fastapi.datastructures.UploadFile` as `partial-contract`, explicitly lists Pydantic hooks as unverified, and links only the class-signature and UploadFile I/O recipes (`metadata.yaml:15604-15635`). The new validation input is materialized, but it is not a fixture reference in that per-symbol contract. The broader OpenAPI request-files case likewise is not linked from this UploadFile overlay. Accordingly, the present inputs are useful evidence to review, but they do not close the reviewed Pydantic-hook gap.

## Gap assessment

* No reviewed case directly observes `TypeAdapter(UploadFile)` or model-field validation across Starlette base instances, FastAPI instances, and other Starlette subclasses.
* No current case observes preservation of the exact parsed `UploadFile` reference after validation.
* The active rejection case exercises one form-produced text value and a response-level error, not the direct validator's full input/error surface or the Pydantic error context around it.
* OpenAPI generation is observed at the whole-document level. There is no isolated observation of the raw `TypeAdapter` JSON Schema in validation and serialization modes, nor of the plain-validator core-schema structure.
* Source and target use different formatting operations for the invalid value's type object (`str` versus `repr`). The custom-metaclass input described below can resolve whether this matters to the supported contract.

## Independent input-only case proposals

These are case designs only. They specify inputs and observation selectors, with no expected outputs.

| Case | Input design | Observation surface |
| --- | --- | --- |
| Parser value identity | Send one named multipart file to a route that accepts both `Request` and `UploadFile`; have the route read the cached form value and expose only identity and selected metadata booleans. Starlette caches the parsed `FormData` on the request (`../starlette/starlette/requests.py:268-322`). | ASGI response `status` and `body` selectors. |
| Direct accepted-instance matrix | An ASGI workload receives a scenario label, constructs a Starlette `UploadFile` base instance, a FastAPI `UploadFile` instance, or an unrelated subclass of the Starlette base, then validates it with pinned `TypeAdapter(UploadFile)`. The route projects returned type and input/result identity to JSON-safe fields. | HTTP `status` and `body` selectors. |
| Direct rejected-value matrix | An ASGI workload selects a text value, bytes, `None`, mapping, or integer and sends it through pinned `TypeAdapter(UploadFile)` validation. The route projects selected exception details to JSON-safe fields. | HTTP `status` and `body` selectors. |
| Validator diagnostic formatting | An ASGI workload constructs an instance of a non-Starlette class whose metaclass gives `__str__` and `__repr__` distinct values, then uses direct Pydantic validation and projects the captured error details. | HTTP `status` and `body` selectors. |
| Plain core-schema shape | An ASGI workload builds pinned `TypeAdapter(UploadFile)` and returns only the core-schema node kind, function kind, and presence/absence of optional schema/serialization entries. | HTTP `status` and `body` selectors; the embedded callback object is not serialized. |
| Raw JSON Schema by mode and composition | An ASGI workload generates `TypeAdapter` JSON Schema for `UploadFile` in validation and serialization modes, then for `UploadFile | None` and `list[UploadFile]` in both modes. | HTTP `status` and `body` selectors, with independent requests for each mode/composition. |

The current exact OpenAPI document case remains useful for integrated behavior. The proposed direct Pydantic cases would isolate the hook contract and allow the per-symbol UploadFile overlay to link evidence without relying on the inventory or broad documentation mapping.
