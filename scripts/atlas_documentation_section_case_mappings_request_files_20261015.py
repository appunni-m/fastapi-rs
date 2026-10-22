"""Reviewed section mappings for the FastAPI request-files tutorial."""

_MULTIPART = "tests/fixtures/input-recipes/parity/request-multipart.yaml"
_REQUEST_FILES_OPENAPI = (
    "tests/fixtures/input-recipes/parity/request-files-openapi-documented-shapes.yaml"
)
_UPLOADFILE_IO = "tests/fixtures/input-recipes/parity/uploadfile-io-metadata.yaml"
_FILE_METADATA = (
    "tests/fixtures/input-recipes/parity/request-files-metadata-openapi-source-review-20261015.yaml"
)

_HTTP = ["http.body.bytes", "http.status"]
_OPENAPI = ["openapi.document", "openapi.paths"]


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    row = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        row["action_ids"] = actions
    return row


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


DOC_SECTION_CASE_MAPPINGS_REQUEST_FILES_20261015 = {
    ("tutorial/request-files.md", "request-files"): _workflow(
        "Request Files { #request-files }",
        1,
        176,
        _MULTIPART,
        ["fastapi.request-multipart.file.bytes-present"],
        ["dispatch"],
        _HTTP,
        (
            "The action sends one valid multipart file through a required `bytes` field declared "
            "with `File()` and observes the HTTP status and response bytes. The recipe uses the "
            "`standard-multipart` profile, including the pinned optional `python-multipart` "
            "dependency; it does not sample missing-parser behavior or measure memory use for "
            "large files. This H1 span includes the descendant sections; this row scopes the "
            "introductory file declaration, and each descendant is mapped separately."
        ),
        (
            "FastAPI 0.141.1 classifies the `File` parameter and provides the uploaded bytes to "
            "the endpoint. Multipart parsing and the generic ASGI request boundary belong to "
            "Starlette 1.6.0 and Starlette-RS."
        ),
    ),
    ("tutorial/request-files.md", "import-file"): _workflow(
        "Import `File` { #import-file }",
        19,
        24,
        _REQUEST_FILES_OPENAPI,
        ["fastapi.request-files.openapi-documented-shapes"],
        ["inspect-documented-request-schemas"],
        _OPENAPI,
        (
            "The workload imports `File` and `UploadFile` from `fastapi`, declares the "
            "documented request shapes, and observes their generated request paths. It does not "
            "claim symbol identity, aliases, or every import form."
        ),
        (
            "The pinned FastAPI tutorial imports both names from `fastapi`; the linked case "
            "exercises those imports while constructing an app and observing its OpenAPI "
            "request-body paths."
        ),
    ),
    ("tutorial/request-files.md", "define-file-parameters"): _workflow(
        "Define `File` Parameters { #define-file-parameters }",
        25,
        52,
        _MULTIPART,
        ["fastapi.request-multipart.file.bytes-present"],
        ["dispatch"],
        _HTTP,
        (
            "The selected request binds one multipart part to an `Annotated[bytes, File()]` "
            "parameter and returns its byte length. The input does not measure memory retention "
            "or compare `File` object identity and inheritance."
        ),
        (
            "The tutorial's `bytes` declaration is exercised through FastAPI request extraction. "
            "Starlette 1.6.0 and Starlette-RS own generic multipart parsing; FastAPI owns the "
            "`File` field classification and endpoint integration."
        ),
    ),
    ("tutorial/request-files.md", "file-parameters-with-uploadfile"): _workflow(
        "File Parameters with `UploadFile` { #file-parameters-with-uploadfile }",
        53,
        111,
        _MULTIPART,
        ["fastapi.request-multipart.file.upload-present"],
        ["dispatch"],
        _HTTP,
        (
            "The action supplies one file to an annotated `UploadFile` parameter and observes "
            "the endpoint's filename, content type, and consumed byte count. It does not exercise "
            "spooling thresholds, disk rollover, or the bare-`UploadFile` declaration shown in "
            "the prose. This parent span includes the `UploadFile` child, which maps the method "
            "sample separately."
        ),
        (
            "FastAPI integrates the annotated upload parameter with endpoint invocation. "
            "Starlette 1.6.0 owns multipart parsing and generic uploaded-file storage and "
            "metadata; "
            "the FastAPI-specific subclass and Pydantic integration are not identity-checked."
        ),
    ),
    ("tutorial/request-files.md", "uploadfile"): _workflow(
        "`UploadFile` { #uploadfile }",
        69,
        111,
        _UPLOADFILE_IO,
        [
            "fastapi.uploadfile-io.metadata-and-async-operations",
            "fastapi.uploadfile-io.null-metadata-and-async-operations",
        ],
        None,
        _HTTP,
        (
            "The two actions construct `UploadFile` with a BytesIO file and non-null or null "
            "metadata, then observe filename, size, headers, content type, blocking file reads, "
            "async partial/full reads, seek, write, size update, close return, and closed state. "
            "They do not submit a multipart upload, exercise `SpooledTemporaryFile` rollover, "
            "sample thread-pool scheduling, or call Pydantic's validation hooks."
        ),
        (
            "FastAPI 0.141.1 `fastapi/datastructures.py:21-64` defines the subclass and its file "
            "metadata, while lines 66-130 forward awaited read, write, seek, and close calls to "
            "Starlette; its Pydantic hooks at lines 132-150 are outside this sample. Starlette "
            "1.6.0 `starlette/datastructures.py:415-476` owns the generic file storage, size "
            "updates, and in-memory versus spooled-file behavior assigned to Starlette-RS."
        ),
    ),
    ("tutorial/request-files.md", "what-is-form-data"): _workflow(
        'What is "Form Data" { #what-is-form-data }',
        112,
        135,
        _MULTIPART,
        ["fastapi.request-multipart.file.bytes-present"],
        ["dispatch"],
        _HTTP,
        (
            "The request demonstrates a `File()` parameter receiving a file part from "
            "`multipart/form-data`. It does not cover URL-encoded text fields, a JSON `Body` "
            "mixed with files, browser form rendering, or generic form parser behavior."
        ),
        (
            "FastAPI selects the multipart file field for a `File` parameter. Starlette 1.6.0 "
            "owns generic form decoding and multipart parsing; the HTTP encoding constraints "
            "described by the warning are protocol behavior."
        ),
    ),
    ("tutorial/request-files.md", "optional-file-upload"): _workflow(
        "Optional File Upload { #optional-file-upload }",
        136,
        141,
        _MULTIPART,
        [
            "fastapi.request-multipart.file.optional-missing",
            "fastapi.request-multipart.file.optional-present",
        ],
        ["dispatch"],
        _HTTP,
        (
            "The selected absent and present requests exercise `Annotated[UploadFile | None, "
            "File()] = None` under the `standard-multipart` profile with pinned "
            "`python-multipart`. They do not claim optional `bytes` declarations, default-value "
            "compatibility variants, or parser-absent behavior."
        ),
        (
            "FastAPI owns optional file-field extraction and default handling. The multipart "
            "request parser is supplied by the Starlette 1.6.0/Starlette-RS request contract, "
            "with the optional parser installed by this recipe's profile."
        ),
    ),
    ("tutorial/request-files.md", "uploadfile-with-additional-metadata"): _workflow(
        "`UploadFile` with Additional Metadata { #uploadfile-with-additional-metadata }",
        142,
        147,
        _FILE_METADATA,
        ["fastapi.request-files.metadata-openapi.single-file"],
        ["inspect-single-file-metadata"],
        _OPENAPI,
        (
            "The OpenAPI action selects request-body paths and component schemas for described "
            "`bytes` and `UploadFile` parameters. It observes FastAPI's `File(description=...)` "
            "schema integration; it does not submit file bytes or test parameter extraction. "
            "The workload uses the `standard-multipart` profile."
        ),
        (
            "The pinned tutorial's additional metadata example is reflected in the selected "
            "OpenAPI component schemas. FastAPI generates these request-body descriptions; "
            "generic multipart parsing remains Starlette-owned."
        ),
    ),
    ("tutorial/request-files.md", "multiple-file-uploads"): _workflow(
        "Multiple File Uploads { #multiple-file-uploads }",
        148,
        173,
        _MULTIPART,
        ["fastapi.request-multipart.file.list-repeated"],
        ["dispatch"],
        _HTTP,
        (
            "The action sends two file parts with the same field name to a `list[UploadFile]` "
            "parameter and observes a response containing both sizes. It does not sample the "
            "parallel `list[bytes]` declaration, the HTML form, or response-class re-exports."
            " This parent span includes the additional-metadata child, mapped separately."
        ),
        (
            "FastAPI binds repeated file values to the declared list parameter. Starlette 1.6.0 "
            "and Starlette-RS own generic repeated-part parsing and uploaded-file mechanics."
        ),
    ),
    (
        "tutorial/request-files.md",
        "multiple-file-uploads-with-additional-metadata",
    ): _workflow(
        (
            "Multiple File Uploads with Additional Metadata "
            "{ #multiple-file-uploads-with-additional-metadata }"
        ),
        168,
        173,
        _FILE_METADATA,
        ["fastapi.request-files.metadata-openapi.multiple-files"],
        ["inspect-multiple-file-metadata"],
        _OPENAPI,
        (
            "The OpenAPI action selects request-body paths and component schemas for described "
            "`list[bytes]` and `list[UploadFile]` parameters. It observes the "
            "`File(description=...)` schema projection only; it does not send repeated file "
            "parts. The workload uses the `standard-multipart` profile."
        ),
        (
            "FastAPI projects each `File` description into the generated request schema for the "
            "declared multiple-file fields. Starlette 1.6.0 and Starlette-RS own generic parsing "
            "of repeated multipart parts."
        ),
    ),
    ("tutorial/request-files.md", "recap"): _excluded(
        "Recap { #recap }",
        174,
        176,
        (
            "The recap repeats the `File`, `bytes`, `UploadFile`, and form-data summary already "
            "mapped in the File-parameter, UploadFile, form-data, and multiple-file sections. "
            "It adds no new request shape or independently observable FastAPI behavior."
        ),
        (
            "The pinned span contains one summary sentence. Its declarations and request behavior "
            "are represented by preceding mappings, so a separate workflow would duplicate "
            "those observations."
        ),
    ),
}
