# UploadFile public-surface review

Review date: 2026-10-20. This is a read-only source review; no build or parity workflow was run.

## Pins checked

- FastAPI source at `../fastapi`, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; its package version is `0.141.1` (`../fastapi/fastapi/__init__.py:3`).
- Starlette source at `../starlette`, tag `1.6.0`, commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`; `starlette.__version__` is `1.6.0` (`../starlette/starlette/__init__.py:1`).

The inventory and atlas were used to locate candidate names and existing decisions. Support statements below come from pinned source, documentation, reviewed metadata, and fixture selectors; inventory rows alone are not parity evidence.

## Verified names and identity

- `fastapi.UploadFile` is the root import alias of `.datastructures.UploadFile` (`../fastapi/fastapi/__init__.py:7-10`). FastAPI defines that class at `../fastapi/fastapi/datastructures.py:21` as a subclass of `StarletteUploadFile`, imported from `starlette.datastructures` at line 18. The documented import is `from fastapi import UploadFile`, and the API page targets `fastapi.UploadFile` (`../fastapi/docs/en/docs/reference/uploadfile.md:1-11`).
- The public FastAPI object is therefore the FastAPI subclass, not an alias of `starlette.datastructures.UploadFile`. Its two FastAPI paths, `fastapi.UploadFile` and `fastapi.datastructures.UploadFile`, name the same class. The pinned root identity workload checks precisely `UploadFile is datastructures.UploadFile` (`tests/fixtures/workloads/root_alias_identity.py:104-110`); the source establishes that the class itself subclasses Starlette.
- `fastapi.datastructures.StarletteUploadFile` is also bound as a module attribute by the upstream import at line 18, but the reviewed atlas classifies it as an internal dependency, with no FastAPI-facing documentation or explicit consumer import contract (`tests/fixtures/compatibility-atlas.json:18998-19023`). It is not a second documented UploadFile export and is not a root export.

## Signatures and members

FastAPI does not override `__init__`; the constructor comes from Starlette 1.6.0 (`../starlette/starlette/datastructures.py:415-426`):

```python
UploadFile(
    file: BinaryIO,
    *,
    size: int | None = None,
    filename: str | None = None,
    headers: Headers | None = None,
) -> None
```

FastAPI adds class annotations with `Annotated[..., Doc(...)]` for `file: BinaryIO`, `filename: str | None`, `size: int | None`, `headers: Headers`, and `content_type: str | None` (`../fastapi/fastapi/datastructures.py:55-64`). The first four values are stored by the inherited constructor; `content_type` is inherited as a property derived from the headers (`../starlette/starlette/datastructures.py:423-434`).

The FastAPI overrides are all async (`../fastapi/fastapi/datastructures.py:66-130`):

| Method | Pinned signature |
| --- | --- |
| `write` | `(self, data: Annotated[bytes, Doc(...)]) -> None` |
| `read` | `(self, size: Annotated[int, Doc(...)] = -1) -> bytes` |
| `seek` | `(self, offset: Annotated[int, Doc(...)]) -> None` |
| `close` | `(self) -> None` |

Each delegates to the corresponding Starlette base method. The base constructor initializes `filename`, `file`, `size`, and headers (defaulting to empty `Headers`); `content_type` reads the `content-type` header. The base handles spooled-file rollover, updates a known `size` during writes, and uses direct file operations while in memory and the thread pool after rollover (`../starlette/starlette/datastructures.py:428-479`). Its inherited `__repr__` includes class name, filename, size, and headers (lines 478-479).

FastAPI also supplies Pydantic protocol hooks: `_validate` accepts a Starlette `UploadFile` instance and preserves it, `__get_pydantic_core_schema__` returns an info-aware plain-validator schema, and `__get_pydantic_json_schema__` returns `{"type": "string", "contentMediaType": "application/octet-stream"}` (`../fastapi/fastapi/datastructures.py:132-150`). The atlas classifies `_validate` as private and the two schema hooks as protocol-internal, rather than end-user callable methods (`tests/fixtures/compatibility-atlas.json:19292-19375`).

No deprecation annotation, warning, or deprecation statement appears on the root binding, class, four methods, or direct UploadFile reference page (`../fastapi/fastapi/__init__.py:7-10`; `../fastapi/fastapi/datastructures.py:21-150`; `../fastapi/docs/en/docs/reference/uploadfile.md:1-22`). The pinned surface has no declared UploadFile deprecation in the reviewed source.

## Documented behavior

The reference page documents the root import and lists `file`, `filename`, `size`, `headers`, `content_type`, `read`, `write`, `seek`, and `close` as class members (`../fastapi/docs/en/docs/reference/uploadfile.md:5-22`). The request-files tutorial says:

- A parameter typed as `UploadFile` receives a file; unlike `bytes`, it uses a spooled file held in memory up to a limit and then stored on disk, which suits large uploads (`../fastapi/docs/en/docs/tutorial/request-files.md:47-67`).
- It exposes the original filename, content type, and underlying `SpooledTemporaryFile`; `read`, `write`, `seek`, and `close` are async and must be awaited. Normal `def` handlers can use `.file` directly (`../fastapi/docs/en/docs/tutorial/request-files.md:69-98`).
- The tutorial describes the FastAPI subclass as inheriting Starlette's class and adding Pydantic compatibility (`../fastapi/docs/en/docs/tutorial/request-files.md:100-109`). Uploads are multipart form data and require `python-multipart` (`../fastapi/docs/en/docs/tutorial/request-files.md:5-15`).

Two documentation details need care when mapping the pinned contract. The tutorial says `write(data)` accepts `str` or `bytes` (`request-files.md:77-80`), while the FastAPI signature annotates `data` as `bytes` (`datastructures.py:66-76`). The tutorial and method docstrings describe async methods broadly as running in a thread pool (`request-files.md:100-103`; `datastructures.py:77-83`), while Starlette 1.6.0 executes the in-memory branch directly and offloads the rolled-to-disk branch (`starlette/datastructures.py:451-476`).

## Current manifest and fixture mapping

- `metadata.yaml:1060-1067` links `fastapi.datastructures.UploadFile` to the Starlette `file-operations` and `ownership-graph` contracts and states that generic methods delegate to the Starlette base while Pydantic integration is FastAPI-owned.
- `metadata.yaml:2089-2097` maps the FastAPI root alias to `fastapi.root-alias-identity.http-reexports`. That recipe returns exact HTTP status/body (`tests/fixtures/input-recipes/parity/root-alias-identity.yaml:9-42`); its workload computes the boolean identity relation at `tests/fixtures/workloads/root_alias_identity.py:104-110`.
- `tests/fixtures/input-recipes/parity/direct-api-uploadfile-signatures.yaml:7-102` collects exact Python signature selectors for the root class, module class, and four async methods. The manifest links the root and class signature cases at `metadata.yaml:15461-15473` and `15619-15631`.
- `tests/fixtures/input-recipes/parity/uploadfile-io-metadata.yaml:7-88` supplies two input cases for selected metadata and async operations. The workload constructs the class over `BytesIO`, checks selected fields, methods, and object identity, and returns JSON (`tests/fixtures/workloads/uploadfile_io_metadata.py:5-54`). Manifest rows record these cases as the supported slice and mark the binding partial (`metadata.yaml:15442-15477`, `15604-15635`). This is not multipart parsing or spooled-disk coverage.
- The manifest explicitly leaves exact class/method annotations, class documentation, Pydantic hooks, and alternate file storage modes unverified (`metadata.yaml:15446-15450`, `15608-15612`). Separate per-member rows add narrower gaps such as header variants, filename/size inputs, EOF, other offsets, and write/close errors (`metadata.yaml:15637-15889`).
- An input recipe for multipart text-value rejection exists at `tests/fixtures/input-recipes/parity/uploadfile-pydantic-type-validation.yaml:1-48`, with a workload at `tests/fixtures/workloads/uploadfile_pydantic_type_validation.py:1-13`. It is not listed among the `fixture_refs` for the UploadFile binding or its members in `metadata.yaml`; no parity result was checked in this review.

## Target paths

- The Python root facade reexports `UploadFile` from `fastapi_rs._core` and includes it in literal `__all__` (`fastapi-rs-py/python/fastapi/__init__.py:1-47`). The datastructures facade directly reexports the same native value and includes it in its `__all__` (`fastapi-rs-py/python/fastapi/datastructures.py:19-23`).
- Rust owns the FastAPI-specific binding in `fastapi-rs/src/datastructures.rs`: it constructs `Annotated` class/method annotations and docs (lines 98-203), installs validation/schema callbacks (369-427), then creates a subclass over `starlette.datastructures.UploadFile` and registers the methods/hooks (430-529). This matches the manifest division where Starlette-RS owns generic file behavior and FastAPI-RS owns FastAPI-specific integration.
- Request handling recognizes Starlette upload instances for `bytes` file parameters and reads them (`fastapi-rs/src/application_runtime.rs:13088-13104`); UploadFile annotations are included in complex-type classification (`13503-13507`) and subclass detection (`13822-13828`).

## Gaps and unknowns for the next contract pass

1. The current mapped UploadFile cases support root/module alias identity, constructor and four method signatures, and a selected `BytesIO` operation slice. They do not establish runtime `__module__`, `__qualname__`, full MRO/base identity, the inherited representation contract, or exact class/member annotation and docstring parity.
2. The Rust binding creates the class and Pydantic hooks, and an input-only multipart validation recipe exists, but the UploadFile manifest rows do not reference that recipe. Link it to an appropriate FastAPI requirement or explicitly keep the hook/validation gap open after identity-checked isolated execution.
3. In-memory versus rolled-to-disk behavior, spool thresholds, alternate file objects, duplicate/case-varied headers, parser-supplied metadata, error propagation, and cancellation remain outside the focused mapped slice. Generic file mechanics belong to the Starlette-RS crosswalk; FastAPI-specific validation/request behavior needs its own mapping.
4. Resolve the two doc/source wording differences above while preserving both the published docs and pinned implementation facts in review evidence.

These are coverage boundaries, not observed target failures; no parity runs or builds were performed.
