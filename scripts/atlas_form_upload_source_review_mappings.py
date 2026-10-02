"""Source-reviewed mappings for the assigned file and form tutorial tests.

This sidecar records reviewed inputs and observation links only. It does not
alter the compatibility-atlas builder, manifest, or generated artifacts.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
RECIPE_PATH = "tests/fixtures/input-recipes/parity/request-form-upload-source-review-2026.yaml"
WORKLOAD_PATH = "tests/fixtures/workloads/request_form_upload_source_review_independent.py"
OPENAPI_CASE = "fastapi.request-form-upload.source-review.openapi-all-routes"
UPLOADFILE_READ_SEEK_CASE = "fastapi.request-form-upload.uploadfile.read-seek-replay"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "pinned source oracle for FastAPI-specific route behavior",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic Request, form parser, UploadFile, response, and TestClient contract",
    },
    "starlette-rs": {
        "distribution_version": "0.1.0",
        "commit": "245a2e10a0bf96348798da880bd8a06a71ecdb89",
        "python_distribution": "starlette-rs-py",
        "role": "implements the pinned Starlette 1.6.0 generic contract",
    },
    "python": {
        "minimum": ">=3.10",
        "oracle": "CPython 3.12.13",
        "basis": "FastAPI 0.141.1 pyproject.toml requires-python; request-file fixtures use Python 3.10 syntax",
    },
    "pydantic": {
        "version": "2.13.4",
        "pydantic_core_version": "2.46.4",
        "role": "public scalar/model validation and model schema dependency where applicable",
    },
    "python-multipart": {
        "minimum": ">=0.0.18",
        "resolved_profile": "0.0.32",
        "optional_extras": [
            "fastapi[standard]",
            "fastapi[standard-no-fastapi-cloud-cli]",
            "fastapi[all]",
        ],
        "role": "optional parser dependency required for Form, File, and multipart form parsing; not FastAPI control flow",
    },
    "httpx": {
        "source_testclient_extra": ">=0.23.0,<1.0.0",
        "resolved_source_profile": "0.28.1",
        "role": "upstream TestClient transport dependency from the FastAPI standard extra; generic transport contract remains Starlette-RS-owned",
    },
}

# Focused source evidence for the new ASGI workflow. Digests pin the cited
# source files; line spans identify the documented and tested method sequence.
UPLOADFILE_READ_SEEK_REVIEW = {
    "case_id": UPLOADFILE_READ_SEEK_CASE,
    "recipe_path": RECIPE_PATH,
    "workload_path": WORKLOAD_PATH,
    "source_identity": {
        "fastapi": SOURCE_IDENTITIES["fastapi"],
        "starlette": SOURCE_IDENTITIES["starlette"],
    },
    "action_ids": ["plain-request", "annotated-request"],
    "observation_selectors": ["http.status", "http.body.bytes"],
    "source_evidence": [
        {
            "repository": "fastapi",
            "path": "docs/en/docs/tutorial/request-files.md",
            "start_line": 77,
            "end_line": 92,
            "sha256": "4faafb4853d46b41cb9bc4c7c57e3ab293bcb9ce318b3b369162c4e239425ab6",
            "role": "documents async UploadFile.read(size), seek(0), and reading the contents again",
        },
        {
            "repository": "fastapi",
            "path": "tests/test_datastructures.py",
            "start_line": 55,
            "end_line": 66,
            "sha256": "ae154958b8f4b6926a55ca7ad815f9d93695794eb1a778fc31dabb245295c8ca",
            "role": "pinned test exercises UploadFile read, EOF, seek, and reread",
        },
        {
            "repository": "fastapi",
            "path": "fastapi/datastructures.py",
            "start_line": 86,
            "end_line": 122,
            "sha256": "5cfba09e88c7738374ede1795e9d534e774fda032fd5f1b893ed0be1576beca7",
            "role": "FastAPI UploadFile exposes awaitable read(size) and seek(offset) methods",
        },
        {
            "repository": "starlette",
            "path": "starlette/datastructures.py",
            "start_line": 461,
            "end_line": 470,
            "sha256": "f9e310036299d6a427443ca96ba118e58486e5927cd4c3bac0ffb815626e52cd",
            "role": "Starlette 1.6.0 owns generic UploadFile byte reads and cursor seeking",
        },
    ],
    "scope": (
        "The recipe uploads one multipart file through plain and Annotated FastAPI route declarations. "
        "The independent workload reads a prefix and remainder, rewinds with seek(0), and rereads. "
        "The recipe contains request bytes only; no response value is stored as an expectation."
    ),
}

OWNER_BOUNDARY = {
    "source_oracle": (
        "Original FastAPI 0.141.1 is isolated source-oracle/development material only; "
        "the target has zero FastAPI runtime dependency or import."
    ),
    "fastapi_control_flow": (
        "Rust-owned in fastapi-rs: route body-field selection, Form/File integration, "
        "requiredness, validation-error response integration, and OpenAPI request-body projection."
    ),
    "python_facade": (
        "fastapi-rs-py may expose direct native re-exports and literal __all__ only; "
        "it contains no parser, validation, routing, response, or fallback control flow."
    ),
    "generic_starlette_contract": (
        "Starlette 1.6.0 is the sole generic request/response/TestClient contract; "
        "starlette-rs implements that contract. FastAPI owns only its integration edges."
    ),
    "pydantic": (
        "Pydantic 2.13.4 owns its public scalar/model validation and model JSON-schema "
        "mechanics; FastAPI owns extraction of FormData and its endpoint/OpenAPI integration."
        " pydantic-core is not a FastAPI-RS public API."
    ),
}

COMPATIBILITY_GATES = [
    (
        "The source tests parameterize both legacy default-value declarations and "
        "typing.Annotated declarations. The independent workload includes both forms "
        "for the reviewed file/form endpoints, but uses new paths and handlers."
    ),
    (
        "The recipes send concrete ASGI bodies directly. They do not exercise HTTPX "
        "or TestClient's multipart encoding, response wrapper, or transport behavior; "
        "those generic behaviors remain Starlette 1.6.0/Starlette-RS-owned."
    ),
    (
        "HTTP response bytes are selected because the current workflow contract "
        "supports them. This is stricter than upstream response.json() assertions "
        "and can distinguish JSON encoding or whitespace."
    ),
    (
        "The OpenAPI case observes the whole document for the independent combined "
        "workload. It does not claim literal equality with each tutorial app's "
        "operation IDs, titles, route set, or inline snapshot."
    ),
    (
        "All recipe requests run with the pinned python-multipart profile. They do "
        "not establish behavior when the optional parser is absent or when an "
        "incorrectly named multipart distribution is installed."
    ),
    (
        "FastAPI 0.141.1 requires Python >=3.10. The selected oracle is CPython "
        "3.12.13; no compatibility claim is made below 3.10 or for another Python "
        "minor runtime."
    ),
    (
        "Pydantic model validation is exercised for form models, including extra="
        "forbid. The complete Pydantic API, arbitrary custom validators, and "
        "pydantic-core internals are outside this test slice."
    ),
    (
        "This review performs only static source, link, and recipe-schema checks. "
        "No oracle/target parity run or compatibility pass is claimed."
    ),
]

_TEST_MODULES = {
    "tests/test_tutorial/test_request_files/test_tutorial001.py": {
        "title": "Required bytes and UploadFile parameters",
        "docs": "docs/en/docs/tutorial/request-files.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_form_no_body": "fastapi.request-form-upload.required-file.no-body",
            "test_post_body_json": "fastapi.request-form-upload.required-file.json-body",
            "test_post_file": "fastapi.request-form-upload.required-file.bytes-present",
            "test_post_large_file": "fastapi.request-form-upload.required-file.large-bytes-present",
            "test_post_upload_file": "fastapi.request-form-upload.required-file.upload-present",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_client"],
    },
    "tests/test_tutorial/test_request_files/test_tutorial001_02.py": {
        "title": "Optional bytes and UploadFile parameters",
        "docs": "docs/en/docs/tutorial/request-files.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_form_no_body": "fastapi.request-form-upload.optional-file.bytes-absent",
            "test_post_uploadfile_no_body": "fastapi.request-form-upload.optional-file.upload-absent",
            "test_post_file": "fastapi.request-form-upload.optional-file.bytes-present",
            "test_post_upload_file": "fastapi.request-form-upload.optional-file.upload-present",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_client"],
    },
    "tests/test_tutorial/test_request_files/test_tutorial001_03.py": {
        "title": "File metadata descriptions",
        "docs": "docs/en/docs/tutorial/request-files.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_file": "fastapi.request-form-upload.described-file.bytes-present",
            "test_post_upload_file": [
                "fastapi.request-form-upload.described-file.upload-present",
                UPLOADFILE_READ_SEEK_CASE,
            ],
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_client"],
    },
    "tests/test_tutorial/test_request_files/test_tutorial002.py": {
        "title": "Repeated files as bytes and UploadFile values",
        "docs": "docs/en/docs/tutorial/request-files.md",
        "features": ["app-routing", "openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_form_no_body": "fastapi.request-form-upload.multiple-files.no-body",
            "test_post_body_json": "fastapi.request-form-upload.multiple-files.json-body",
            "test_post_files": "fastapi.request-form-upload.multiple-files.bytes-present",
            "test_post_upload_file": "fastapi.request-form-upload.multiple-files.upload-present",
            "test_get_root": "fastapi.request-form-upload.files.root-page",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_app", "get_client"],
    },
    "tests/test_tutorial/test_request_files/test_tutorial003.py": {
        "title": "Repeated files with OpenAPI descriptions",
        "docs": "docs/en/docs/tutorial/request-files.md",
        "features": ["app-routing", "openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_files": "fastapi.request-form-upload.described-multiple-files.bytes-present",
            "test_post_upload_file": "fastapi.request-form-upload.described-multiple-files.upload-present",
            "test_get_root": "fastapi.request-form-upload.files.root-page",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_app", "get_client"],
    },
    "tests/test_tutorial/test_request_forms/test_tutorial001.py": {
        "title": "Required scalar Form parameters",
        "docs": "docs/en/docs/tutorial/request-forms.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_body_form": "fastapi.request-form-upload.form-fields.valid",
            "test_post_body_form_no_password": "fastapi.request-form-upload.form-fields.missing-password",
            "test_post_body_form_no_username": "fastapi.request-form-upload.form-fields.missing-username",
            "test_post_body_form_no_data": "fastapi.request-form-upload.form-fields.empty",
            "test_post_body_json": "fastapi.request-form-upload.form-fields.json-body",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_client"],
    },
    "tests/test_tutorial/test_request_forms_and_files/test_tutorial001.py": {
        "title": "Required file and scalar Form fields in one multipart body",
        "docs": "docs/en/docs/tutorial/request-forms-and-files.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_form_no_body": "fastapi.request-form-upload.mixed-form-files.empty",
            "test_post_form_no_file": "fastapi.request-form-upload.mixed-form-files.token-only",
            "test_post_body_json": "fastapi.request-form-upload.mixed-form-files.json-body",
            "test_post_file_no_token": "fastapi.request-form-upload.mixed-form-files.one-file-missing-fields",
            "test_post_files_and_token": "fastapi.request-form-upload.mixed-form-files.complete",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_app", "get_client"],
    },
    "tests/test_tutorial/test_request_form_models/test_tutorial001.py": {
        "title": "Pydantic model populated from form fields",
        "docs": "docs/en/docs/tutorial/request-form-models.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_body_form": "fastapi.request-form-upload.form-model.valid",
            "test_post_body_form_no_password": "fastapi.request-form-upload.form-model.missing-password",
            "test_post_body_form_no_username": "fastapi.request-form-upload.form-model.missing-username",
            "test_post_body_form_no_data": "fastapi.request-form-upload.form-model.empty",
            "test_post_body_json": "fastapi.request-form-upload.form-model.json-body",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_client"],
    },
    "tests/test_tutorial/test_request_form_models/test_tutorial002.py": {
        "title": "Pydantic form model with extra fields forbidden",
        "docs": "docs/en/docs/tutorial/request-form-models.md",
        "features": ["openapi-docs", "request-validation", "response-serialization"],
        "tests": {
            "test_post_body_form": "fastapi.request-form-upload.form-model.valid",
            "test_post_body_extra_form": "fastapi.request-form-upload.form-model.extra-forbidden",
            "test_post_body_form_no_password": "fastapi.request-form-upload.form-model.missing-password",
            "test_post_body_form_no_username": "fastapi.request-form-upload.form-model.missing-username",
            "test_post_body_form_no_data": "fastapi.request-form-upload.form-model.empty",
            "test_post_body_json": "fastapi.request-form-upload.form-model.json-body",
            "test_openapi_schema": OPENAPI_CASE,
        },
        "helpers": ["get_client"],
    },
}

_CASE_ACTIONS: dict[str, tuple[str, ...]] = {
    "fastapi.request-form-upload.required-file.no-body": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.required-file.json-body": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.required-file.bytes-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.required-file.large-bytes-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.required-file.upload-present": (
        "plain-request",
        "annotated-request",
    ),
    UPLOADFILE_READ_SEEK_CASE: ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.optional-file.bytes-absent": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.optional-file.upload-absent": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.optional-file.bytes-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.optional-file.upload-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.described-file.bytes-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.described-file.upload-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.multiple-files.no-body": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.multiple-files.json-body": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.multiple-files.bytes-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.multiple-files.upload-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.described-multiple-files.bytes-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.described-multiple-files.upload-present": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.files.root-page": ("get-page",),
    "fastapi.request-form-upload.form-fields.valid": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.form-fields.missing-password": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.form-fields.missing-username": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.form-fields.empty": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.form-fields.json-body": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.mixed-form-files.empty": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.mixed-form-files.token-only": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.mixed-form-files.json-body": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.mixed-form-files.one-file-missing-fields": (
        "plain-request",
        "annotated-request",
    ),
    "fastapi.request-form-upload.mixed-form-files.complete": ("plain-request", "annotated-request"),
    "fastapi.request-form-upload.form-model.valid": (
        "plain-request",
        "annotated-request",
        "strict-plain-request",
        "strict-annotated-request",
    ),
    "fastapi.request-form-upload.form-model.missing-password": (
        "plain-request",
        "annotated-request",
        "strict-plain-request",
        "strict-annotated-request",
    ),
    "fastapi.request-form-upload.form-model.missing-username": (
        "plain-request",
        "annotated-request",
        "strict-plain-request",
        "strict-annotated-request",
    ),
    "fastapi.request-form-upload.form-model.empty": (
        "plain-request",
        "annotated-request",
        "strict-plain-request",
        "strict-annotated-request",
    ),
    "fastapi.request-form-upload.form-model.json-body": (
        "plain-request",
        "annotated-request",
        "strict-plain-request",
        "strict-annotated-request",
    ),
    "fastapi.request-form-upload.form-model.extra-forbidden": (
        "plain-request",
        "annotated-request",
        "strict-plain-request",
        "strict-annotated-request",
    ),
    OPENAPI_CASE: ("get-openapi",),
}

_HTTP_SELECTORS = ["http.status", "http.body.bytes"]
_OPENAPI_SELECTORS = ["http.status", "http.body.bytes", "openapi.document"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    if function_name.startswith("test_"):
        role = f"pinned FastAPI 0.141.1 test stimulus/assertions for {function_name}"
    elif function_name == "get_app":
        role = "fixture loads the selected docs-source FastAPI app; setup only"
    else:
        role = "fixture builds Starlette TestClient for the selected docs-source app; setup only"
    return _source(test_path, node.lineno, node.end_lineno or node.lineno, role)


def _link(case_id: str) -> dict[str, Any]:
    if case_id not in _CASE_ACTIONS:
        raise KeyError(f"unknown review workflow case: {case_id}")
    selectors = _OPENAPI_SELECTORS if case_id == OPENAPI_CASE else _HTTP_SELECTORS
    return {
        "recipe_path": RECIPE_PATH,
        "case_id": case_id,
        "action_ids": list(_CASE_ACTIONS[case_id]),
        "observation_selectors": list(selectors),
    }


def _links(case_ids: list[str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for case_id in case_ids:
        link = _link(case_id)
        key = (link["case_id"], tuple(link["action_ids"]))
        if key not in seen:
            seen.add(key)
            result.append(link)
    return result


def _common_sources(doc_path: str) -> list[dict[str, Any]]:
    return [
        _source(
            doc_path,
            1,
            len((FASTAPI_ROOT / doc_path).read_text(encoding="utf-8").splitlines()),
            "pinned tutorial contract for the request/file/form surface",
        ),
        _source(
            "pyproject.toml",
            12,
            12,
            "FastAPI 0.141.1 requires Python >=3.10",
        ),
        _source(
            "pyproject.toml",
            59,
            106,
            "optional extras include python-multipart for forms and uploads and httpx for TestClient",
        ),
        _source(
            "fastapi/params.py",
            663,
            742,
            "File specializes Form and declares multipart media type and OpenAPI metadata",
        ),
        _source(
            "fastapi/dependencies/utils.py",
            88,
            129,
            "FastAPI checks for the optional python-multipart package and rejects the incorrect multipart distribution",
        ),
        _source(
            "fastapi/dependencies/utils.py",
            516,
            535,
            "FastAPI recognizes Form fields and prepares endpoint model fields",
        ),
        _source(
            "fastapi/dependencies/utils.py",
            912,
            998,
            "FastAPI extracts repeated multipart values, reads byte file fields, and validates form/model values",
        ),
        _source(
            "fastapi/routing.py",
            425,
            473,
            "FastAPI routes Form bodies through request.form and parses JSON body input before dependency validation",
        ),
        _source(
            "fastapi/openapi/utils.py",
            231,
            263,
            "FastAPI builds requestBody content media type, schema, and requiredness",
        ),
        _source(
            "fastapi/openapi/utils.py",
            331,
            385,
            "FastAPI projects body fields into OpenAPI operations",
        ),
        _source(
            "fastapi/testclient.py",
            1,
            1,
            "FastAPI exposes Starlette TestClient through its source import path",
        ),
        _source(
            "fastapi/__init__.py",
            7,
            25,
            "FastAPI root exports the app, UploadFile, File, Form, and related consumer names",
        ),
        _source(
            "fastapi/responses.py",
            6,
            12,
            "the response classes used by this workload are direct Starlette re-exports",
        ),
        _source(
            "starlette/requests.py",
            268,
            311,
            "Starlette 1.6.0 parses multipart and URL-encoded request forms and owns generic parser errors",
        ),
        _source(
            "starlette/formparsers.py",
            57,
            204,
            "Starlette 1.6.0 uses python-multipart to decode fields and spool uploaded files",
        ),
        _source(
            "starlette/datastructures.py",
            410,
            476,
            "Starlette 1.6.0 owns generic UploadFile metadata, storage, and file methods",
        ),
        _source(
            "starlette/datastructures.py",
            482,
            498,
            "Starlette 1.6.0 FormData is the generic parsed form container",
        ),
        _source(
            "starlette/responses.py",
            55,
            81,
            "Starlette 1.6.0 owns generic response header/body construction",
        ),
        _source(
            "starlette/responses.py",
            163,
            201,
            "Starlette 1.6.0 sends response ASGI messages and serializes JSONResponse bytes",
        ),
        _source(
            "starlette/testclient.py",
            327,
            370,
            "Starlette 1.6.0 TestClient owns generic ASGI response collection and HTTPX response construction",
        ),
    ]


def _function_review(
    test_path: str,
    function_name: str,
    case_ids: list[str],
    features: list[str],
    title: str,
) -> dict[str, Any]:
    fixture = not function_name.startswith("test_")
    links = _links(case_ids)
    selectors = sorted({selector for link in links for selector in link["observation_selectors"]})
    if fixture:
        rationale = (
            f"{function_name} is pytest setup for {title}. It selects/imports the "
            "upstream docs app or constructs TestClient; the linked independent "
            "cases preserve both plain default and Annotated route declarations. "
            "The fixture itself has no standalone HTTP observation."
        )
    elif function_name == "test_openapi_schema":
        rationale = (
            "The source performs GET /openapi.json and snapshots the full tutorial "
            "app schema. The linked input records the HTTP status, exact response "
            "bytes, and full OpenAPI document for the independent combined route set."
        )
    elif UPLOADFILE_READ_SEEK_CASE in case_ids:
        rationale = (
            "The source test establishes a multipart request parameter typed as "
            "UploadFile. The additional read(size)/seek(0)/reread sequence is "
            "grounded in the focused documentation and test spans recorded in "
            "UPLOADFILE_READ_SEEK_REVIEW. The independent workflow uses a new "
            "request body and route paths and sends the same input through plain "
            "and Annotated declarations."
        )
    else:
        rationale = (
            f"The source function {function_name} exercises {title}. Its input-only "
            "workflow uses new field values, filenames, and paths, and sends the "
            "same request shape through plain and Annotated declarations."
        )
    return {
        "review_status": "reviewed_partial",
        "function_role": "pytest_fixture_setup" if fixture else "source_test",
        "feature_ids": list(features),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "workflow_cases": links,
        "supporting_sources": [_test_span(test_path, function_name)],
        "contract_gate": (
            "Partial: the independent case observes only the declared HTTP/OpenAPI "
            "selectors; source-specific paths, inline snapshot literals, and "
            "TestClient request construction remain outside this mapping."
        ),
    }


def _build_review_mappings() -> dict[str, dict[str, Any]]:
    modules: dict[str, dict[str, Any]] = {}
    for test_path, spec in _TEST_MODULES.items():
        function_case_ids: dict[str, list[str]] = {
            name: [case_id] if isinstance(case_id, str) else list(case_id)
            for name, case_id in spec["tests"].items()
        }
        all_test_case_ids = [
            case_id for case_ids in function_case_ids.values() for case_id in case_ids
        ]
        for helper in spec["helpers"]:
            function_case_ids[helper] = all_test_case_ids

        tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
        source_functions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if source_functions != set(function_case_ids):
            missing = sorted(source_functions - set(function_case_ids))
            stale = sorted(set(function_case_ids) - source_functions)
            raise ValueError(
                f"top-level function mapping mismatch for {test_path}: "
                f"unmapped={missing}, nonexistent={stale}"
            )

        functions = {
            name: _function_review(
                test_path,
                name,
                case_ids,
                spec["features"],
                spec["title"],
            )
            for name, case_ids in function_case_ids.items()
        }
        links = _links(all_test_case_ids)
        modules[test_path] = {
            "review_status": "reviewed_partial",
            "title": spec["title"],
            "constraints": {
                "python": ">=3.10",
                "oracle_python": "CPython 3.12.13",
                "python-multipart": "optional dependency, resolved profile 0.0.32",
                "testclient_httpx": "optional standard extra, resolved profile 0.28.1",
            },
            "feature_ids": list(spec["features"]),
            "observation_selectors": sorted(
                {
                    selector
                    for mapping in functions.values()
                    for selector in mapping["observation_selectors"]
                }
            ),
            "rationale": (
                f"{spec['title']}. FastAPI owns the Rust-side parameter/body and "
                "validation integration. Starlette 1.6.0, implemented by "
                "Starlette-RS, owns generic request parsing, UploadFile, responses, "
                "and TestClient. Pydantic owns model validation/schema behavior "
                "where these cases use form models."
            ),
            "functions": functions,
            "workflow_cases": links,
            "supporting_sources": [
                *[_test_span(test_path, function_name) for function_name in function_case_ids],
                *_common_sources(spec["docs"]),
            ],
            "stimulus_notes": (
                f"Input-only recipe {RECIPE_PATH}; independent workload {WORKLOAD_PATH}. "
                "Every test function maps to a case and selectors. Fixture functions "
                "map to the module's full set of reviewed test cases as setup provenance."
            ),
            "contract_gate": "Partial source review. " + " ".join(COMPATIBILITY_GATES),
        }
    return modules


FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS = _build_review_mappings()
__all__ = [
    "COMPATIBILITY_GATES",
    "FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS",
    "OWNER_BOUNDARY",
    "RECIPE_PATH",
    "SOURCE_IDENTITIES",
    "UPLOADFILE_READ_SEEK_CASE",
    "UPLOADFILE_READ_SEEK_REVIEW",
    "WORKLOAD_PATH",
    "validate_static_review",
]


def validate_static_review() -> dict[str, int]:
    """Validate source/function/case links and recipe shape without running apps."""
    import yaml
    from jsonschema import Draft202012Validator

    from scripts.parity.contract import WORKFLOW_SCHEMAS, read_json

    recipe_file = PROJECT_ROOT / RECIPE_PATH
    try:
        recipe = yaml.safe_load(recipe_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read {RECIPE_PATH}: {exc}") from exc
    schema_path = WORKFLOW_SCHEMAS.get(recipe.get("schema"))
    if schema_path is None:
        raise ValueError(f"unsupported recipe schema in {RECIPE_PATH}")
    errors = sorted(
        Draft202012Validator(read_json(schema_path)).iter_errors(recipe),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ValueError(f"recipe schema errors: {details}")

    case_by_id = {case["case_id"]: case for case in recipe["cases"]}
    if len(case_by_id) != len(recipe["cases"]):
        raise ValueError("recipe contains duplicate case IDs")
    if recipe["workload"].get("file") != WORKLOAD_PATH:
        raise ValueError("recipe does not point to the reviewed independent workload")
    if recipe["workload"].get("factory") != "create_app":
        raise ValueError("recipe does not select the reviewed workload factory")
    action_ids_by_case = {
        case_id: {action["action_id"] for action in case["actions"]}
        for case_id, case in case_by_id.items()
    }
    selectors_by_case_action: dict[str, dict[str, set[str]]] = {}
    for case_id, case in case_by_id.items():
        selectors_by_case_action[case_id] = {}
        for action in case["actions"]:
            selectors: set[str] = set()
            for observation in action["observations"]:
                if observation["kind"] == "http_response":
                    if "status" in observation["selectors"]:
                        selectors.add("http.status")
                    if "body" in observation["selectors"]:
                        selectors.add("http.body.bytes")
                    if "headers" in observation["selectors"]:
                        selectors.add("http.headers.ordered")
                elif observation["kind"] == "openapi":
                    if "" in observation["json_pointers"]:
                        selectors.add("openapi.document")
                    else:
                        selectors.add("openapi.request_schema")
            selectors_by_case_action[case_id][action["action_id"]] = selectors
    function_count = 0
    test_function_count = 0
    fixture_function_count = 0
    linked_case_ids: set[str] = set()
    for test_path, module in FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS.items():
        for function_name, mapping in module["functions"].items():
            function_count += 1
            if mapping["function_role"] == "source_test":
                test_function_count += 1
            else:
                fixture_function_count += 1
            if not mapping.get("supporting_sources"):
                raise ValueError(f"missing function source evidence: {test_path}:{function_name}")
            if not mapping.get("workflow_cases"):
                raise ValueError(f"missing function workflow link: {test_path}:{function_name}")
            for link in mapping["workflow_cases"]:
                if link["recipe_path"] != RECIPE_PATH:
                    raise ValueError(f"wrong recipe link for {test_path}:{function_name}")
                case_id = link["case_id"]
                if case_id not in case_by_id:
                    raise ValueError(f"unknown case {case_id} for {test_path}:{function_name}")
                if not set(link["action_ids"]).issubset(action_ids_by_case[case_id]):
                    raise ValueError(f"unknown action link for {test_path}:{function_name}")
                available_selectors = set().union(
                    *(
                        selectors_by_case_action[case_id][action_id]
                        for action_id in link["action_ids"]
                    )
                )
                if not set(link["observation_selectors"]).issubset(available_selectors):
                    raise ValueError(
                        f"selector link is absent from the recipe for {test_path}:{function_name}"
                    )
                source_paths = {
                    evidence["path"] for evidence in case_by_id[case_id]["source_evidence"]
                }
                if test_path not in source_paths:
                    raise ValueError(f"case source_evidence omits {test_path} for {function_name}")
                linked_case_ids.add(case_id)

    source_rows = [
        source
        for module in FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS.values()
        for source in module["supporting_sources"]
    ]
    for source in source_rows:
        source_path = source["path"]
        if source_path.startswith("starlette/"):
            source_file = PROJECT_ROOT.parent / "starlette" / source_path
        else:
            source_file = FASTAPI_ROOT / source_path
        source_lines = source_file.read_text(encoding="utf-8").splitlines()
        if not (1 <= source["start_line"] <= source["end_line"] <= len(source_lines)):
            raise ValueError(f"source line span is outside {source_path}")

    read_seek_case = case_by_id.get(UPLOADFILE_READ_SEEK_CASE)
    if read_seek_case is None:
        raise ValueError("missing UploadFile read/seek workflow case")
    if [action["action_id"] for action in read_seek_case["actions"]] != list(
        UPLOADFILE_READ_SEEK_REVIEW["action_ids"]
    ):
        raise ValueError("UploadFile read/seek action mapping is stale")
    case_sources = {source["path"] for source in read_seek_case["source_evidence"]}
    required_sources = {
        "tests/test_tutorial/test_request_files/test_tutorial001_03.py",
        "tests/test_datastructures.py",
        "docs/en/docs/tutorial/request-files.md",
    }
    if not required_sources.issubset(case_sources):
        raise ValueError("UploadFile read/seek case omits a reviewed source citation")
    case_selectors = set().union(
        *(
            selectors_by_case_action[UPLOADFILE_READ_SEEK_CASE][action_id]
            for action_id in UPLOADFILE_READ_SEEK_REVIEW["action_ids"]
        )
    )
    if case_selectors != set(UPLOADFILE_READ_SEEK_REVIEW["observation_selectors"]):
        raise ValueError("UploadFile read/seek selectors differ from the focused review")

    source_roots = {
        "fastapi": FASTAPI_ROOT,
        "starlette": PROJECT_ROOT.parent / "starlette",
    }
    for source in UPLOADFILE_READ_SEEK_REVIEW["source_evidence"]:
        source_path = source_roots[source["repository"]] / source["path"]
        source_bytes = source_path.read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != source["sha256"]:
            raise ValueError(f"source digest changed for {source['path']}")
        source_lines = source_bytes.decode("utf-8").splitlines()
        if not (1 <= source["start_line"] <= source["end_line"] <= len(source_lines)):
            raise ValueError(f"source line span is outside {source['path']}")

    workload_file = PROJECT_ROOT / WORKLOAD_PATH
    workload_tree = ast.parse(workload_file.read_text(encoding="utf-8"))
    workload_factories = {
        node.name
        for node in workload_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if "create_app" not in workload_factories:
        raise ValueError(f"missing independent workload factory in {WORKLOAD_PATH}")
    if set(case_by_id) != set(_CASE_ACTIONS):
        raise ValueError("recipe case IDs and reviewed action registry differ")
    if linked_case_ids != set(case_by_id):
        raise ValueError("recipe contains an unlinked case")

    large_case = case_by_id["fastapi.request-form-upload.required-file.large-bytes-present"]
    for action in large_case["actions"]:
        body = action["receive_events"][0]["body"]
        payload = body.partition("\r\n\r\n")[2].partition("\r\n--FormUploadReview2026--\r\n")[0]
        if len(payload) != 65537:
            raise ValueError("large-file recipe case does not contain a 65,537-byte part")
    if not linked_case_ids.issubset(case_by_id):
        raise ValueError("source mapping points outside recipe cases")

    return {
        "modules": len(FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS),
        "functions": function_count,
        "test_functions": test_function_count,
        "fixture_functions": fixture_function_count,
        "recipes": 1,
        "cases": len(case_by_id),
        "workloads": 1,
        "read_seek_source_spans": len(UPLOADFILE_READ_SEEK_REVIEW["source_evidence"]),
    }
