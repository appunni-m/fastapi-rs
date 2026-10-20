# UploadFile Pydantic parity review

Review date: 2026-10-20

## Scope status

This is a time-bound review of the three-case comparison artifact
`f3dbbcda-ffd2-4ba1-962b-e41fafb7eb0b`. The active
`uploadfile-pydantic-contract` recipe now has six cases, including a separate
custom `__format__` input. The three-case receipt below does not cover that
input, and this review does not claim exhaustive behavior for every custom
metaclass.

## Scope and pinned identities

This review covers the Rust `UploadFile._validate` formatting change, the custom-metaclass input case, and comparison artifact `f3dbbcda-ffd2-4ba1-962b-e41fafb7eb0b.json`. No builds or tests were run.

The checked source revisions are FastAPI 0.141.1 `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS `4139a72449bf5751e8902fb1c7175ee7f191d338`; each checkout's `HEAD` matched the requested revision. FastAPI-RS `HEAD` is `ea37e85d74189ee56377dd4a2ba4cd293d44a92a`.

## Formatting finding

FastAPI's pinned [`UploadFile._validate`](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/datastructures.py#L133) raises `ValueError(f"Expected UploadFile, received: {type(value)}")` for non-Starlette values. The Rust implementation in `fastapi-rs/src/datastructures.rs` changed the type object's conversion from PyO3 `.repr()` to `.str()`.

That change fixes the tested distinction. The workload's `_DisagreeingMeta` returns `custom-str-type` from `__str__` and `custom-repr-type` from `__repr__`, with no `__format__` override. The oracle and target results both report the exact response message `Value error, Expected UploadFile, received: custom-str-type`; the prior `repr()` path would select the other spelling.

There is a narrower semantic gap in the claim that `str(type(value))` is equivalent to FastAPI's f-string for every metaclass. An unconverted f-string uses the format protocol and passes an empty format spec to `__format__`; Python's [`f-string` reference](https://docs.python.org/3.12/reference/lexical_analysis.html#f-strings) documents this, and [`format()`](https://docs.python.org/3.12/library/functions.html#format) dispatches through `type(value).__format__(value, format_spec)`. A custom metaclass can therefore make `__format__` return a different string from `__str__`. The reviewed three-case artifact distinguishes `str` from `repr` but does not cover this format-protocol case; the active recipe now includes one separate custom `__format__` input, which covers that behavior for the sampled metaclass only.

**Assessment:** the Rust change matches the source for the newly covered custom `__str__`/`__repr__` case and for default formatting behavior. It does not establish full f-string equivalence for arbitrary custom metaclasses. Exact coverage would require matching `format(type(value), "")` semantics or adding a distinct `__format__` case and implementing its result.

## Identity-checked parity evidence

The comparison artifact references source run `0dccd6a8-1609-4927-bc70-24408196c374` and target run `62ffec0b-167a-41ae-b825-ba4adbf82feb`. Its recorded SHA-256 values match the corresponding result files. The artifact's manifest, input, and workload digests also match the current files: `7246b262…55c17`, `a09cbf96…97519`, and `41f485d3…73564`. The target result's combined source-tree digest, `be4ded95…feb477`, matches a read-only recomputation over the current FastAPI-RS and Starlette-RS trees.

The oracle result identifies FastAPI 0.141.1, Starlette 1.6.0, CPython 3.12.13, and the requested FastAPI and Starlette commits. The target identifies FastAPI-RS 0.1.0 on the same Python and platform, records FastAPI-RS revision `ea37e85d74189ee56377dd4a2ba4cd293d44a92a`, Starlette-RS revision `4139a72449bf5751e8902fb1c7175ee7f191d338`, source-tree and loaded-binary digests, and no FastAPI or upstream Starlette repository imports. The recorded commands use separate oracle and target virtual environments and invoke the public `fastapi` target surface.

The comparator's `compare_workflow_results` validates the oracle/target identity pair, package profiles, pinned repository revisions, and shared manifest, input, and workload identities before comparing observations. The artifact is completed with 3 selected cases passed, 0 failed, and no infrastructure errors: JSON Schema, acceptance of a Starlette base `UploadFile`, and rejection with the custom type spelling. This identity-checked receipt remains valid for its recorded three-case scope; it does not include the later custom `__format__` case.
